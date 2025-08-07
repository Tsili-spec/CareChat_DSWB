"""
LangChain-based RAG (Retrieval-Augmented Generation) Service for Healthcare Assistant
Provides context-aware responses using clinical summaries dataset with LangChain
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pickle
import os

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

class LangChainHealthcareRAGService:
    def __init__(self, data_path: str = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize LangChain RAG service with clinical summaries dataset
        
        Args:
            data_path: Path to clinical summaries CSV file (auto-detected if None)
            model_name: HuggingFace model for embeddings
        """
        # Auto-detect project root and data directory
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Set data paths
        if data_path is None:
            test_path = self.data_dir / "clinical_summaries_test.csv"
            full_path = self.data_dir / "clinical_summaries.csv"
            capital_data_path = self.project_root / "Data" / "clinical_summaries.csv"
            
            if capital_data_path.exists():
                self.data_path = str(capital_data_path)
                self.file_suffix = "_large"
            elif test_path.exists():
                self.data_path = str(test_path)
                self.file_suffix = "_test"
            elif full_path.exists():
                self.data_path = str(full_path)
                self.file_suffix = ""
            else:
                self._create_sample_clinical_data()
                self.data_path = str(self.data_dir / "clinical_summaries.csv")
                self.file_suffix = ""
        else:
            self.data_path = data_path
            self.file_suffix = "_custom"
        
        self.model_name = model_name
        
        # LangChain components
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self.clinical_data = None
        self.documents = None
        
        # Cache file paths
        self.vectorstore_path = str(self.data_dir / f"langchain_faiss{self.file_suffix}")
        self.processed_data_path = str(self.data_dir / f"langchain_processed_data{self.file_suffix}.pkl")
        
        # Medical condition keywords for RAG trigger
        self.medical_keywords = {
            'covid-19', 'covid', 'coronavirus', 'typhoid', 'anemia', 'dengue', 'malaria', 
            'hypertension', 'diabetes', 'fever', 'headache', 'nausea', 'fatigue', 'pain',
            'infection', 'symptoms', 'diagnosis', 'treatment', 'medication', 'disease',
            'blood pressure', 'temperature', 'heart rate', 'test results', 'medical',
            'health', 'illness', 'condition', 'syndrome', 'disorder', '病気', '症状'
        }
        
        # Healthcare prompt template
        self.healthcare_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a knowledgeable healthcare assistant. Use the following clinical context from real medical records to provide helpful, accurate information.

Clinical Context:
{context}

Question: {question}

Instructions:
- Provide clear, compassionate medical information based on the clinical context
- Explain medical terms in simple language
- Include relevant details from similar cases when helpful
- Always include this disclaimer: "This information is for educational purposes only. Please consult with a healthcare professional for personalized medical advice."
- If the question is not medical in nature, provide a helpful general response

Answer:"""
        )
    
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
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_csv(self.data_dir / "clinical_summaries.csv", index=False)
        logger.info("Created sample clinical data")
    
    async def initialize(self):
        """Initialize the LangChain RAG system"""
        try:
            logger.info("Initializing LangChain Healthcare RAG Service...")
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"Loaded HuggingFace embeddings: {self.model_name}")
            
            # Load and process clinical data
            await self._load_clinical_data()
            
            # Create or load vector store
            await self._create_or_load_vectorstore()
            
            # Setup retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            logger.info("LangChain Healthcare RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain RAG service: {str(e)}")
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
                
                # Create comprehensive text for each clinical case
                df['searchable_text'] = df.apply(self._create_searchable_text, axis=1)
                
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
            parts.append(f"Clinical Summary: {row['summary_text']}")
        
        # Add vital signs context
        vitals = []
        if pd.notna(row.get('body_temp_c')):
            temp = row['body_temp_c']
            temp_status = "fever" if temp > 37.5 else "normal temperature"
            vitals.append(f"body temperature {temp:.1f}°C ({temp_status})")
        
        if pd.notna(row.get('blood_pressure_systolic')):
            bp = row['blood_pressure_systolic']
            bp_status = "hypertension" if bp > 140 else "normal blood pressure"
            vitals.append(f"systolic BP {bp:.0f} mmHg ({bp_status})")
        
        if pd.notna(row.get('heart_rate')):
            hr = row['heart_rate']
            hr_status = "tachycardia" if hr > 100 else "normal heart rate"
            vitals.append(f"heart rate {hr:.0f} bpm ({hr_status})")
        
        if vitals:
            parts.append(f"Vital Signs: {', '.join(vitals)}")
        
        # Add patient demographics
        if pd.notna(row.get('patient_age')) and pd.notna(row.get('patient_gender')):
            parts.append(f"Patient Demographics: {row['patient_age']:.0f} year old {row['patient_gender']}")
        
        return ". ".join(parts)
    
    async def _create_or_load_vectorstore(self):
        """Create or load FAISS vector store using LangChain"""
        try:
            # Check if vector store exists
            if os.path.exists(f"{self.vectorstore_path}.faiss"):
                logger.info("Loading existing FAISS vector store...")
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS vector store loaded successfully")
            else:
                logger.info("Creating new FAISS vector store...")
                await self._create_vectorstore()
                
        except Exception as e:
            logger.error(f"Error with vector store: {str(e)}")
            logger.info("Creating new vector store due to error...")
            await self._create_vectorstore()
    
    async def _create_vectorstore(self):
        """Create new FAISS vector store from clinical data"""
        try:
            # Convert clinical data to LangChain Documents
            documents = []
            for i, record in enumerate(self.clinical_data):
                doc = Document(
                    page_content=record['searchable_text'],
                    metadata={
                        'diagnosis': record.get('diagnosis', 'Unknown'),
                        'patient_age': record.get('patient_age'),
                        'patient_gender': record.get('patient_gender'),
                        'body_temp_c': record.get('body_temp_c'),
                        'blood_pressure_systolic': record.get('blood_pressure_systolic'),
                        'heart_rate': record.get('heart_rate'),
                        'record_id': i
                    }
                )
                documents.append(doc)
            
            logger.info(f"Creating FAISS vector store from {len(documents)} documents...")
            
            # Create vector store
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            # Save vector store
            self.vectorstore.save_local(self.vectorstore_path)
            
            logger.info("FAISS vector store created and saved successfully")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def should_use_rag(self, user_message: str) -> bool:
        """Determine if RAG should be used based on user message content"""
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
        
        return any(pattern in message_lower for pattern in rag_patterns)
    
    async def get_rag_enhanced_prompt(self, user_message: str, base_prompt: str) -> str:
        """Create RAG-enhanced prompt using LangChain retrieval"""
        try:
            if not self.should_use_rag(user_message):
                return base_prompt + f"\n\nUser Question: {user_message}"
            
            if not self.retriever:
                logger.warning("RAG retriever not initialized, skipping retrieval")
                return base_prompt + f"\n\nUser Question: {user_message}"
            
            # Retrieve relevant documents
            relevant_docs = self.retriever.get_relevant_documents(user_message)
            
            if not relevant_docs:
                return base_prompt + f"\n\nUser Question: {user_message}"
            
            # Format context from retrieved documents
            context_parts = []
            context_parts.append("**Clinical Context from Medical Records:**")
            
            for i, doc in enumerate(relevant_docs[:3], 1):  # Limit to top 3 results
                diagnosis = doc.metadata.get('diagnosis', 'Unknown')
                context_parts.append(f"\n**Case {i} - {diagnosis}:**")
                context_parts.append(doc.page_content)
            
            context = "\n".join(context_parts)
            
            # Create enhanced prompt using the healthcare template
            enhanced_prompt = self.healthcare_prompt.format(
                context=context,
                question=user_message
            )
            
            logger.info(f"Enhanced prompt with LangChain RAG for query: {user_message[:50]}...")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error creating LangChain RAG-enhanced prompt: {str(e)}")
            return base_prompt + f"\n\nUser Question: {user_message}"
    
    async def query_with_retrieval(self, question: str) -> str:
        """Direct query using LangChain's retrieval chain"""
        try:
            if not self.retriever:
                return "RAG system not initialized. Please try again later."
            
            # Create a simple retrieval chain
            def format_docs(docs):
                return "\n\n".join([d.page_content for d in docs])
            
            # Create the chain
            rag_chain = (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | self.healthcare_prompt
                | StrOutputParser()
            )
            
            # This would need an LLM to complete, but we'll return the enhanced prompt for now
            context_docs = self.retriever.get_relevant_documents(question)
            context = "\n\n".join([doc.page_content for doc in context_docs[:3]])
            
            return self.healthcare_prompt.format(context=context, question=question)
            
        except Exception as e:
            logger.error(f"Error in LangChain query: {str(e)}")
            return f"Error processing query: {str(e)}"

# Global LangChain RAG service instance
langchain_rag_service = LangChainHealthcareRAGService()
