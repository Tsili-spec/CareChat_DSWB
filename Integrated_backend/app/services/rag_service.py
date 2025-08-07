"""
RAG (Retrieval-Augmented Generation) Service for Healthcare Assistant
Provides context-aware responses using clinical summaries dataset
"""
import pandas as pd
import numpy as np
import faiss
import logging
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class HealthcareRAGService:
    def __init__(self, data_path: str = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG service with clinical summaries dataset
        
        Args:
            data_path: Path to clinical summaries CSV file (auto-detected if None)
            model_name: SentenceTransformer model for embeddings
        """
        # Auto-detect project root and data directory
        self.project_root = Path(__file__).parent.parent.parent  # Go up to Integrated_backend/
        self.data_dir = self.project_root / "data"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Set data paths
        if data_path is None:
            # Look for clinical data in our data directory
            test_path = self.data_dir / "clinical_summaries_test.csv"
            full_path = self.data_dir / "clinical_summaries.csv"
            
            if test_path.exists():
                self.data_path = str(test_path)
                self.file_suffix = "_test"
            elif full_path.exists():
                self.data_path = str(full_path)
                self.file_suffix = ""
            else:
                # Create sample clinical data if none exists
                self._create_sample_clinical_data()
                self.data_path = str(self.data_dir / "clinical_summaries.csv")
                self.file_suffix = ""
        else:
            self.data_path = data_path
            self.file_suffix = "_test" if "test" in data_path else ""
        
        self.model_name = model_name
        self.embedding_model = None
        self.index = None
        self.clinical_data = None
        self.embeddings = None
        
        # Set cache file paths
        self.index_path = str(self.data_dir / f"faiss_index{self.file_suffix}.bin")
        self.embeddings_path = str(self.data_dir / f"embeddings{self.file_suffix}.pkl")
        self.processed_data_path = str(self.data_dir / f"processed_clinical_data{self.file_suffix}.pkl")
        
        # Medical condition keywords for RAG trigger
        self.medical_keywords = {
            'covid-19', 'typhoid', 'anemia', 'dengue', 'malaria', 'hypertension',
            'diabetes', 'fever', 'headache', 'nausea', 'fatigue', 'pain',
            'infection', 'symptoms', 'diagnosis', 'treatment', 'medication',
            'blood pressure', 'temperature', 'heart rate', 'test results'
        }
        
    def _create_sample_clinical_data(self):
        """Create sample clinical data if none exists"""
        sample_data = [
            {
                'diagnosis': 'Hypertension',
                'summary_text': 'Patient presents with elevated blood pressure, headaches, and dizziness',
                'body_temp_c': 36.8,
                'blood_pressure_systolic': 150,
                'heart_rate': 85,
                'patient_age': 45,
                'patient_gender': 'male'
            },
            {
                'diagnosis': 'Type 2 Diabetes',
                'summary_text': 'Patient reports increased thirst, frequent urination, and fatigue',
                'body_temp_c': 37.0,
                'blood_pressure_systolic': 135,
                'heart_rate': 78,
                'patient_age': 52,
                'patient_gender': 'female'
            },
            {
                'diagnosis': 'Common Cold',
                'summary_text': 'Patient has runny nose, sore throat, and mild cough',
                'body_temp_c': 37.2,
                'blood_pressure_systolic': 120,
                'heart_rate': 72,
                'patient_age': 28,
                'patient_gender': 'female'
            },
            {
                'diagnosis': 'Gastroenteritis',
                'summary_text': 'Patient experiencing nausea, vomiting, and abdominal pain',
                'body_temp_c': 38.1,
                'blood_pressure_systolic': 110,
                'heart_rate': 88,
                'patient_age': 35,
                'patient_gender': 'male'
            },
            {
                'diagnosis': 'Migraine',
                'summary_text': 'Severe headache with sensitivity to light and sound',
                'body_temp_c': 36.9,
                'blood_pressure_systolic': 125,
                'heart_rate': 75,
                'patient_age': 30,
                'patient_gender': 'female'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_csv(self.data_dir / "clinical_summaries.csv", index=False)
        logger.info("Created sample clinical data")
        
    async def initialize(self):
        """Initialize the RAG system - load model, data, and embeddings"""
        try:
            logger.info("Initializing Healthcare RAG Service...")
            
            # Load embedding model
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
            
            # Load and process clinical data
            await self._load_clinical_data()
            
            # Load or create embeddings and FAISS index
            await self._load_or_create_embeddings()
            
            logger.info("Healthcare RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    async def _load_clinical_data(self):
        """Load and preprocess clinical summaries dataset"""
        try:
            if os.path.exists(self.processed_data_path):
                logger.info("Loading processed clinical data from cache...")
                with open(self.processed_data_path, 'rb') as f:
                    self.clinical_data = pickle.load(f)
            else:
                logger.info("Processing clinical summaries dataset...")
                df = pd.read_csv(self.data_path)
                
                # Clean and preprocess data
                df = df.dropna(subset=['diagnosis', 'summary_text'])
                df['diagnosis'] = df['diagnosis'].str.strip()
                df['summary_text'] = df['summary_text'].str.strip()
                
                # Create comprehensive text for embedding
                df['searchable_text'] = df.apply(self._create_searchable_text, axis=1)
                
                # Group by diagnosis for better retrieval
                df['diagnosis_lower'] = df['diagnosis'].str.lower()
                
                self.clinical_data = df.to_dict('records')
                
                # Cache processed data
                with open(self.processed_data_path, 'wb') as f:
                    pickle.dump(self.clinical_data, f)
                
                logger.info(f"Processed {len(self.clinical_data)} clinical summaries")
                
        except Exception as e:
            logger.error(f"Error loading clinical data: {str(e)}")
            raise
    
    def _create_searchable_text(self, row) -> str:
        """Create comprehensive searchable text from clinical data"""
        parts = []
        
        # Add diagnosis
        if pd.notna(row['diagnosis']):
            parts.append(f"Diagnosis: {row['diagnosis']}")
        
        # Add summary text
        if pd.notna(row['summary_text']):
            parts.append(f"Symptoms: {row['summary_text']}")
        
        # Add vital signs context
        vitals = []
        if pd.notna(row['body_temp_c']):
            temp_status = "fever" if row['body_temp_c'] > 37.5 else "normal temperature"
            vitals.append(f"body temperature {temp_status}")
        
        if pd.notna(row['blood_pressure_systolic']):
            bp_status = "high blood pressure" if row['blood_pressure_systolic'] > 140 else "normal blood pressure"
            vitals.append(bp_status)
        
        if pd.notna(row['heart_rate']):
            hr_status = "elevated heart rate" if row['heart_rate'] > 100 else "normal heart rate"
            vitals.append(hr_status)
        
        if vitals:
            parts.append(f"Vitals: {', '.join(vitals)}")
        
        # Add demographic context
        if pd.notna(row['patient_age']) and pd.notna(row['patient_gender']):
            parts.append(f"Patient: {row['patient_age']} year old {row['patient_gender']}")
        
        return ". ".join(parts)
    
    async def _load_or_create_embeddings(self):
        """
        Load existing embeddings or create new ones
        
        CACHING BEHAVIOR:
        - Embeddings are cached to .pkl files and only regenerated if:
          1. Cache files don't exist
          2. Source CSV data is newer than cache files
          3. Cache files are corrupted
        - On subsequent server restarts, cached embeddings are loaded instantly
        - This saves significant startup time (minutes -> seconds)
        """
        try:
            # Check if cache exists and is valid
            cache_exists = (os.path.exists(self.embeddings_path) and 
                          os.path.exists(self.index_path))
            
            if cache_exists:
                # Check if source data is newer than cache
                cache_time = os.path.getmtime(self.embeddings_path)
                data_time = os.path.getmtime(self.data_path)
                
                if data_time > cache_time:
                    logger.info("Source data is newer than cache, rebuilding embeddings...")
                    await self._create_embeddings()
                    return
                
                logger.info("Loading existing embeddings and FAISS index...")
                
                # Load embeddings
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                
                # Load FAISS index
                self.index = faiss.read_index(self.index_path)
                
                logger.info(f"Loaded {len(self.embeddings)} embeddings from cache")
            else:
                logger.info("No cache found, creating new embeddings...")
                await self._create_embeddings()
                
        except Exception as e:
            logger.error(f"Error with embeddings cache: {str(e)}")
            logger.info("Rebuilding embeddings due to cache error...")
            await self._create_embeddings()  # Fallback to creating new ones
    
    async def _create_embeddings(self):
        """Create embeddings for all clinical summaries"""
        try:
            # Extract searchable texts
            texts = [item['searchable_text'] for item in self.clinical_data]
            
            logger.info(f"Creating embeddings for {len(texts)} clinical summaries...")
            
            # Create embeddings in batches
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.embedding_model.encode(batch_texts)
                all_embeddings.extend(batch_embeddings)
                
                if i % 1000 == 0:
                    logger.info(f"Processed {i}/{len(texts)} embeddings...")
            
            self.embeddings = np.array(all_embeddings)
            
            # Create FAISS index
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(self.embeddings)
            self.index.add(self.embeddings)
            
            # Save embeddings and index
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
            
            faiss.write_index(self.index, self.index_path)
            
            logger.info(f"Created and saved {len(self.embeddings)} embeddings")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def should_use_rag(self, user_message: str) -> bool:
        """
        Determine if RAG should be used based on user message content
        
        Args:
            user_message: User's question/message
            
        Returns:
            Boolean indicating whether to use RAG
        """
        message_lower = user_message.lower()
        
        # Check for medical keywords
        for keyword in self.medical_keywords:
            if keyword in message_lower:
                return True
        
        # Check for question patterns that benefit from RAG
        rag_patterns = [
            'what is', 'what does', 'explain', 'tell me about',
            'symptoms of', 'treatment for', 'how to treat',
            'side effects', 'medication for', 'diagnosis',
            'why do i have', 'what causes', 'how common'
        ]
        
        for pattern in rag_patterns:
            if pattern in message_lower:
                return True
        
        return False
    
    async def retrieve_relevant_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant clinical summaries for a query
        
        Args:
            query: User's question
            top_k: Number of relevant summaries to retrieve
            
        Returns:
            List of relevant clinical summary dictionaries
        """
        try:
            if not self.embedding_model or not self.index:
                logger.warning("RAG system not initialized, skipping retrieval")
                return []
            
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search for similar embeddings
            scores, indices = self.index.search(query_embedding, top_k)
            
            # Get relevant clinical summaries
            relevant_summaries = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score > 0.3:  # Similarity threshold
                    summary = self.clinical_data[idx].copy()
                    summary['relevance_score'] = float(score)
                    summary['rank'] = i + 1
                    relevant_summaries.append(summary)
            
            logger.info(f"Retrieved {len(relevant_summaries)} relevant summaries for query: {query[:50]}...")
            return relevant_summaries
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def format_rag_context(self, relevant_summaries: List[Dict[str, Any]], user_query: str) -> str:
        """
        Format retrieved summaries into context for the LLM
        
        Args:
            relevant_summaries: List of relevant clinical summaries
            user_query: Original user question
            
        Returns:
            Formatted context string
        """
        if not relevant_summaries:
            return ""
        
        context_parts = []
        context_parts.append("**Clinical Context from Medical Records:**")
        
        # Group by diagnosis for better organization
        diagnosis_groups = {}
        for summary in relevant_summaries:
            diagnosis = summary.get('diagnosis', 'Unknown')
            if diagnosis not in diagnosis_groups:
                diagnosis_groups[diagnosis] = []
            diagnosis_groups[diagnosis].append(summary)
        
        for diagnosis, summaries in diagnosis_groups.items():
            context_parts.append(f"\n**{diagnosis} Cases:**")
            
            for i, summary in enumerate(summaries[:2], 1):  # Limit to 2 per diagnosis
                # Create case description
                case_parts = []
                
                if summary.get('summary_text'):
                    case_parts.append(f"Symptoms: {summary['summary_text']}")
                
                # Add vital signs if relevant
                vitals = []
                if summary.get('body_temp_c') and summary['body_temp_c'] > 37.5:
                    vitals.append(f"fever ({summary['body_temp_c']:.1f}°C)")
                
                if summary.get('blood_pressure_systolic') and summary['blood_pressure_systolic'] > 140:
                    vitals.append(f"high BP ({summary['blood_pressure_systolic']:.0f})")
                
                if vitals:
                    case_parts.append(f"Key vitals: {', '.join(vitals)}")
                
                # Add patient context
                if summary.get('patient_age') and summary.get('patient_gender'):
                    case_parts.append(f"Patient: {summary['patient_age']:.0f}yr {summary['patient_gender']}")
                
                if case_parts:
                    context_parts.append(f"Case {i}: {' | '.join(case_parts)}")
        
        context_parts.append(f"\n**Instructions:** Use this clinical context to explain medical concepts related to the user's question: \"{user_query}\"")
        context_parts.append("Focus on explaining in simple terms what these conditions mean and how they typically present.")
        
        return "\n".join(context_parts)
    
    async def get_rag_enhanced_prompt(self, user_message: str, base_prompt: str) -> str:
        """
        Create RAG-enhanced prompt by retrieving relevant context
        
        Args:
            user_message: User's question
            base_prompt: Base system prompt
            
        Returns:
            Enhanced prompt with relevant clinical context
        """
        try:
            if not self.should_use_rag(user_message):
                return base_prompt + f"\n\nUser Question: {user_message}"
            
            # Retrieve relevant context
            relevant_summaries = await self.retrieve_relevant_context(user_message)
            
            if not relevant_summaries:
                return base_prompt + f"\n\nUser Question: {user_message}"
            
            # Format context
            rag_context = self.format_rag_context(relevant_summaries, user_message)
            
            # Combine base prompt with RAG context
            enhanced_prompt = f"""{base_prompt}

{rag_context}

User Question: {user_message}

Please explain in simple, compassionate terms using the clinical context above when relevant. Always include the standard disclaimer."""
            
            logger.info(f"Enhanced prompt with RAG context for query: {user_message[:50]}...")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error creating RAG-enhanced prompt: {str(e)}")
            return base_prompt + f"\n\nUser Question: {user_message}"

# Global RAG service instance
rag_service = HealthcareRAGService()
