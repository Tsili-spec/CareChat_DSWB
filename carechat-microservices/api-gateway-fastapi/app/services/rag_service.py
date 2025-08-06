"""
RAG (Retrieval-Augmented Generation) Service for Healthcare Assistant
Provides context-aware responses using clinical summaries dataset
Based on Track2 implementation adapted for MongoDB system
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path

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
        self.project_root = Path(__file__).parent.parent.parent  # Go up to api-gateway-fastapi/
        self.data_dir = self.project_root / "Data"
        
        # Set data paths - try to find clinical data files
        if data_path is None:
            # Try test dataset first, fallback to full dataset
            test_path = self.data_dir / "clinical_summaries_test.csv"
            full_path = self.data_dir / "clinical_summaries.csv"
            
            if test_path.exists():
                self.data_path = str(test_path)
                self.file_suffix = "_test"
            elif full_path.exists():
                self.data_path = str(full_path)
                self.file_suffix = ""
            else:
                logger.warning("No clinical data files found. RAG will use mock data.")
                self.data_path = None
                self.file_suffix = "_mock"
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
        
    async def initialize(self):
        """Initialize the RAG system - load model, data, and embeddings"""
        try:
            logger.info("Initializing Healthcare RAG Service...")
            
            # Create data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Try to load embedding model (optional)
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.warning("SentenceTransformers not available. RAG will use mock responses.")
                self.embedding_model = None
            
            # Load and process clinical data
            await self._load_clinical_data()
            
            # Load or create embeddings if model is available
            if self.embedding_model:
                await self._load_or_create_embeddings()

            logger.info("✅ Healthcare RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ RAG Service initialization failed: {e}")
            # Continue with mock data
            self.clinical_data = self._create_mock_data()
    
    async def _load_clinical_data(self):
        """Load and preprocess clinical summaries dataset"""
        try:
            if self.data_path and os.path.exists(self.data_path):
                logger.info(f"Loading clinical data from: {self.data_path}")
                self.clinical_data = pd.read_csv(self.data_path)
                logger.info(f"Loaded {len(self.clinical_data)} clinical summaries")
            else:
                logger.warning("No clinical data file found. Using mock data.")
                self.clinical_data = self._create_mock_data()
                
        except Exception as e:
            logger.error(f"Error loading clinical data: {e}")
            # Fallback to mock data
            self.clinical_data = self._create_mock_data()
    
    def _create_mock_data(self) -> pd.DataFrame:
        """Create mock clinical data for testing"""
        mock_data = {
            'diagnosis': [
                'Hypertension',
                'Type 2 Diabetes',
                'Common Cold',
                'Gastroenteritis',
                'Migraine'
            ],
            'summary_text': [
                'Patient presents with elevated blood pressure. Regular monitoring and lifestyle changes recommended.',
                'Blood glucose levels consistently high. Medication adjustment and dietary counseling provided.',
                'Upper respiratory symptoms with mild fever. Rest and symptomatic treatment advised.',
                'Gastrointestinal upset with nausea and diarrhea. Hydration and dietary modifications recommended.',
                'Recurrent headaches with photophobia. Trigger identification and prevention strategies discussed.'
            ],
            'patient_age': [45, 58, 32, 28, 35],
            'patient_gender': ['M', 'F', 'M', 'F', 'F'],
            'body_temp_c': [36.8, 37.1, 38.2, 37.5, 36.9],
            'blood_pressure_systolic': [145, 138, 120, 115, 125],
            'heart_rate': [78, 82, 88, 92, 75]
        }
        return pd.DataFrame(mock_data)
    
    def _create_searchable_text(self, row) -> str:
        """Create comprehensive searchable text from clinical data"""
        parts = []
        
        # Add diagnosis
        if pd.notna(row['diagnosis']):
            parts.append(f"Diagnosis: {row['diagnosis']}")
        
        # Add summary text
        if pd.notna(row['summary_text']):
            parts.append(f"Summary: {row['summary_text']}")
        
        # Add vital signs context
        vitals = []
        if 'body_temp_c' in row and pd.notna(row['body_temp_c']):
            vitals.append(f"Temperature: {row['body_temp_c']}°C")
        
        if 'blood_pressure_systolic' in row and pd.notna(row['blood_pressure_systolic']):
            vitals.append(f"Blood Pressure: {row['blood_pressure_systolic']} mmHg")
        
        if 'heart_rate' in row and pd.notna(row['heart_rate']):
            vitals.append(f"Heart Rate: {row['heart_rate']} bpm")
        
        if vitals:
            parts.append(f"Vital Signs: {', '.join(vitals)}")
        
        # Add demographic context
        if 'patient_age' in row and 'patient_gender' in row and pd.notna(row['patient_age']) and pd.notna(row['patient_gender']):
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
            # Check if cache files exist and are newer than source data
            cache_valid = (
                os.path.exists(self.embeddings_path) and
                os.path.exists(self.processed_data_path) and
                (not self.data_path or not os.path.exists(self.data_path) or
                 os.path.getmtime(self.embeddings_path) > os.path.getmtime(self.data_path))
            )
            
            if cache_valid:
                logger.info("Loading cached embeddings...")
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                with open(self.processed_data_path, 'rb') as f:
                    processed_data = pickle.load(f)
                logger.info("✅ Cached embeddings loaded successfully")
            else:
                logger.info("Creating new embeddings...")
                await self._create_embeddings()
                
        except Exception as e:
            logger.error(f"Error with embeddings: {e}")
            # Continue without embeddings
            self.embeddings = None
    
    async def _create_embeddings(self):
        """Create embeddings for all clinical summaries"""
        try:
            if self.clinical_data is None or self.embedding_model is None:
                logger.warning("Cannot create embeddings - missing data or model")
                return
            
            # Create searchable text for each row
            searchable_texts = []
            for _, row in self.clinical_data.iterrows():
                searchable_text = self._create_searchable_text(row)
                searchable_texts.append(searchable_text)
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.embedding_model.encode(searchable_texts)
            self.embeddings = embeddings
            
            # Cache embeddings and processed data
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(embeddings, f)
            with open(self.processed_data_path, 'wb') as f:
                pickle.dump(searchable_texts, f)
            
            logger.info(f"✅ Created and cached {len(embeddings)} embeddings")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            self.embeddings = None
    
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
            if self.clinical_data is None:
                return []
            
            if self.embeddings is None or self.embedding_model is None:
                # Fallback to simple keyword matching
                return self._keyword_search(query, top_k)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Calculate similarities using cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top-k most similar documents
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            relevant_summaries = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Minimum similarity threshold
                    summary = self.clinical_data.iloc[idx].to_dict()
                    summary['similarity_score'] = float(similarities[idx])
                    relevant_summaries.append(summary)
            
            return relevant_summaries
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        query_lower = query.lower()
        relevant_summaries = []
        
        for _, row in self.clinical_data.iterrows():
            score = 0
            if 'diagnosis' in row and pd.notna(row['diagnosis']):
                if query_lower in row['diagnosis'].lower():
                    score += 2
            if 'summary_text' in row and pd.notna(row['summary_text']):
                if query_lower in row['summary_text'].lower():
                    score += 1
            
            if score > 0:
                summary = row.to_dict()
                summary['similarity_score'] = score / 3.0  # Normalize
                relevant_summaries.append(summary)
        
        # Sort by score and return top-k
        relevant_summaries.sort(key=lambda x: x['similarity_score'], reverse=True)
        return relevant_summaries[:top_k]
    
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
            context_parts.append(f"\n**{diagnosis}:**")
            for summary in summaries:
                if 'summary_text' in summary and pd.notna(summary['summary_text']):
                    context_parts.append(f"- {summary['summary_text']}")
        
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
            # Retrieve relevant clinical context
            relevant_summaries = await self.retrieve_relevant_context(user_message)
            
            if relevant_summaries:
                # Format context
                rag_context = self.format_rag_context(relevant_summaries, user_message)
                
                # Insert RAG context into the prompt
                enhanced_prompt = f"{base_prompt}\n\n{rag_context}\n\nCurrent message:"
                return enhanced_prompt
            
            return base_prompt
            
        except Exception as e:
            logger.error(f"Error creating RAG-enhanced prompt: {e}")
            return base_prompt

# Global RAG service instance
rag_service = HealthcareRAGService()
