#!/usr/bin/env python3
"""
Test script for LangChain RAG implementation
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.langchain_rag_service import langchain_rag_service

async def test_langchain_rag():
    """Test the LangChain RAG service"""
    print("🧪 Testing LangChain Healthcare RAG Service")
    print("=" * 50)
    
    try:
        # Initialize the service
        print("🔄 Initializing LangChain RAG service...")
        await langchain_rag_service.initialize()
        print("✅ LangChain RAG service initialized successfully")
        
        # Test medical queries
        test_queries = [
            "What is diabetes?",
            "Tell me about fever symptoms",
            "What causes high blood pressure?",
            "How is COVID-19 diagnosed?",
            "What are the symptoms of typhoid?",
            "Hello, how are you?" # Non-medical query
        ]
        
        print("\n🧪 Testing RAG queries:")
        print("-" * 30)
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            should_use_rag = langchain_rag_service.should_use_rag(query)
            print(f"🔍 Should use RAG: {should_use_rag}")
            
            if should_use_rag:
                # Test retrieval
                try:
                    if langchain_rag_service.retriever:
                        docs = langchain_rag_service.retriever.get_relevant_documents(query)
                        print(f"📋 Retrieved {len(docs)} relevant documents")
                        
                        if docs:
                            print(f"📄 Top result: {docs[0].metadata.get('diagnosis', 'Unknown')}")
                    
                    # Test enhanced prompt
                    enhanced_prompt = await langchain_rag_service.get_rag_enhanced_prompt(
                        user_message=query,
                        base_prompt="You are a helpful healthcare assistant."
                    )
                    print(f"📝 Enhanced prompt length: {len(enhanced_prompt)} characters")
                    
                except Exception as e:
                    print(f"❌ Error testing query: {e}")
            
            print("-" * 30)
        
        # Check generated files
        print("\n📁 Checking generated files:")
        data_dir = project_root / "data"
        
        files_to_check = [
            "langchain_faiss_large.faiss",
            "langchain_faiss_large.pkl", 
            "langchain_processed_data_large.pkl"
        ]
        
        for file_name in files_to_check:
            file_path = data_dir / file_name
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"✅ {file_name}: {size_mb:.2f} MB")
            else:
                print(f"❌ {file_name}: Not found")
        
        print("\n🎉 LangChain RAG test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during RAG test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_langchain_rag())
