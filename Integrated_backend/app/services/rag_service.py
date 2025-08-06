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
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class HealthcareRAGService:
    def __init__(self, data_path: str = None):
        """
        Initialize RAG service with clinical summaries dataset
        
        Args:
            data_path: Path to clinical summaries CSV file (auto-detected if None)
        """
        # Auto-detect project root and data directory
        self.project_root = Path(__file__).parent.parent.parent  # Go up to Integrated_backend/
        self.data_dir = self.project_root / "Data"
        
        # Set data paths
        if data_path is None:
            # Check for available datasets
            test_path = self.data_dir / "clinical_summaries_test.csv"
            full_path = self.data_dir / "clinical_summaries.csv"
            
            if test_path.exists():
                self.data_path = str(test_path)
                logger.info(f"Using test dataset: {self.data_path}")
            elif full_path.exists():
                self.data_path = str(full_path)
                logger.info(f"Using full dataset: {self.data_path}")
            else:
                logger.warning(f"Clinical data not found in {self.data_dir}")
                self.data_path = None
        else:
            self.data_path = data_path
        
        self.clinical_data = None
        self.initialized = False
        
        # Medical condition keywords for RAG trigger
        self.medical_keywords = {
            'covid-19', 'typhoid', 'anemia', 'dengue', 'malaria', 'hypertension',
            'diabetes', 'fever', 'headache', 'nausea', 'fatigue', 'pain',
            'infection', 'symptoms', 'diagnosis', 'treatment', 'medication',
            'blood pressure', 'temperature', 'heart rate', 'test results',
            'maladie', 'fièvre', 'mal de tête', 'traitement', 'médicament'
        }
        
    async def initialize(self):
        """Initialize the RAG system - load clinical data"""
        try:
            logger.info("Initializing Healthcare RAG Service...")
            
            if self.data_path and os.path.exists(self.data_path):
                # Load clinical data
                await self._load_clinical_data()
                logger.info("Healthcare RAG Service initialized successfully")
            else:
                logger.warning("Clinical dataset not found. RAG will use basic medical context.")
                self.clinical_data = self._get_basic_medical_context()
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            # Initialize with basic context as fallback
            self.clinical_data = self._get_basic_medical_context()
            self.initialized = True
    
    async def _load_clinical_data(self):
        """Load and preprocess clinical summaries dataset"""
        try:
            logger.info("Loading clinical summaries dataset...")
            df = pd.read_csv(self.data_path)
            
            # Clean and preprocess data - combine diagnosis and summary_text for richer context
            if 'summary_text' in df.columns:
                df['summary_text'] = df['summary_text'].fillna('')
                df['diagnosis'] = df['diagnosis'].fillna('')
                
                # Combine diagnosis and summary_text for richer clinical context
                combined_summaries = []
                for _, row in df.iterrows():
                    diagnosis = row['diagnosis'].strip()
                    summary = row['summary_text'].strip()
                    
                    if diagnosis and summary:
                        combined = f"{diagnosis}: {summary}"
                    elif diagnosis:
                        combined = diagnosis
                    elif summary:
                        combined = summary
                    else:
                        combined = "No clinical information available"
                    
                    combined_summaries.append(combined)
                
                self.clinical_data = combined_summaries[:100]  # Limit to first 100 for performance
                logger.info(f"Loaded {len(self.clinical_data)} clinical summaries with combined diagnosis+summary")
            elif 'summary' in df.columns:
                df['summary'] = df['summary'].fillna('')
                self.clinical_data = df['summary'].tolist()[:100]  # Limit to first 100 for performance
                logger.info(f"Loaded {len(self.clinical_data)} clinical summaries")
            else:
                logger.warning("No 'summary_text' or 'summary' column found in dataset")
                self.clinical_data = self._get_basic_medical_context()
                
        except Exception as e:
            logger.error(f"Error loading clinical data: {str(e)}")
            self.clinical_data = self._get_basic_medical_context()
    
    def _get_basic_medical_context(self) -> List[str]:
        """Get basic medical context when dataset is not available"""
        return [
            "Common symptoms like fever, headache, and fatigue can indicate various conditions.",
            "High blood pressure (hypertension) requires regular monitoring and medication compliance.",
            "Diabetes management involves blood sugar monitoring, proper diet, and medication.",
            "Malaria is common in Cameroon and presents with fever, chills, and body aches.",
            "Typhoid fever symptoms include prolonged fever, weakness, and abdominal pain.",
            "Regular checkups at Douala General Hospital help prevent complications.",
            "Always consult healthcare providers for proper diagnosis and treatment.",
            "Medication adherence is crucial for treatment effectiveness.",
            "Preventive care includes vaccinations and health screenings.",
            "Emergency symptoms require immediate medical attention."
        ]
    
    def should_use_rag(self, query: str) -> bool:
        """
        Determine if RAG should be used based on query content
        
        Args:
            query: User query to analyze
            
        Returns:
            True if query appears medical-related
        """
        if not self.initialized:
            return False
            
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.medical_keywords)
    
    async def get_rag_enhanced_prompt(self, user_query: str, original_prompt: str, top_k: int = 3) -> str:
        """
        Get RAG-enhanced prompt with relevant clinical context for medically accurate responses
        
        This implements the core RAG logic to access and explain static clinical summaries,
        enabling the chatbot to provide medically accurate, culturally appropriate responses.
        
        Args:
            user_query: Original user query
            original_prompt: Original formatted prompt
            top_k: Number of relevant contexts to include
            
        Returns:
            Enhanced prompt with clinical context for better medical interpretation
        """
        if not self.should_use_rag(user_query) or not self.clinical_data:
            logger.debug(f"RAG not used for query: '{user_query}' (should_use_rag: {self.should_use_rag(user_query)}, has_data: {bool(self.clinical_data)})")
            return original_prompt
        
        try:
            # Retrieve relevant clinical summaries
            relevant_contexts = self._search_similar_content(user_query, top_k)
            
            if not relevant_contexts:
                logger.info(f"No relevant clinical contexts found for: '{user_query}'")
                return original_prompt
            
            # Build enhanced prompt with clinical knowledge
            clinical_context = "\n\n**📋 Relevant Clinical Information from Douala General Hospital:**\n"
            for i, context in enumerate(relevant_contexts, 1):
                clinical_context += f"{i}. {context}\n"
            
            clinical_context += "\n**🏥 Instructions for Clinical Interpretation:**\n"
            clinical_context += "- Use the above clinical information to provide context-aware responses\n"
            clinical_context += "- Interpret medical findings in simple, patient-friendly language\n"
            clinical_context += "- Always emphasize the need for professional medical consultation\n"
            clinical_context += "- Provide culturally appropriate guidance for Cameroon/Douala context\n"
            
            # Insert clinical context strategically in the prompt
            if "You are a" in original_prompt:
                parts = original_prompt.split("You are a", 1)
                enhanced_prompt = parts[0] + clinical_context + "\n\nYou are a" + parts[1]
            else:
                enhanced_prompt = clinical_context + "\n\n" + original_prompt
            
            logger.info(f"✅ RAG enhanced prompt with {len(relevant_contexts)} clinical contexts for medical query")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt with RAG: {str(e)}")
            return original_prompt
    
    def _search_similar_content(self, query: str, top_k: int = 3) -> List[str]:
        """
        Enhanced search for similar content using fuzzy keyword matching and clinical relevance
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant clinical summaries
        """
        if not self.clinical_data:
            return []
        
        try:
            query_lower = query.lower()
            query_words = set(word.strip('.,!?;:') for word in query_lower.split())
            
            # Enhanced scoring with medical term prioritization
            scored_summaries = []
            for summary in self.clinical_data:
                if isinstance(summary, str) and summary.strip():
                    summary_lower = summary.lower()
                    summary_words = set(word.strip('.,!?;:') for word in summary_lower.split())
                    
                    # Calculate multiple scoring factors
                    exact_overlap = len(query_words.intersection(summary_words))
                    
                    # Medical condition matching (higher weight)
                    medical_matches = 0
                    for keyword in self.medical_keywords:
                        if keyword in query_lower and keyword in summary_lower:
                            medical_matches += 2  # Higher weight for medical terms
                    
                    # Partial word matching for medical relevance
                    partial_matches = 0
                    for q_word in query_words:
                        if len(q_word) > 3:  # Only for meaningful words
                            for s_word in summary_words:
                                if q_word in s_word or s_word in q_word:
                                    partial_matches += 1
                    
                    # Combined score
                    total_score = exact_overlap + medical_matches + (partial_matches * 0.5)
                    
                    if total_score > 0:
                        scored_summaries.append((total_score, summary))
            
            # Sort by score and return top results
            scored_summaries.sort(key=lambda x: x[0], reverse=True)
            
            # Log the search results for debugging
            if scored_summaries:
                logger.info(f"RAG found {len(scored_summaries)} relevant summaries for query: '{query}'")
                for i, (score, summary) in enumerate(scored_summaries[:top_k]):
                    logger.debug(f"  {i+1}. Score: {score:.1f} - {summary[:100]}...")
            else:
                logger.info(f"RAG found no relevant summaries for query: '{query}'")
            
            return [summary for score, summary in scored_summaries[:top_k]]
            
        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            return []

# Global instance
rag_service = HealthcareRAGService()
