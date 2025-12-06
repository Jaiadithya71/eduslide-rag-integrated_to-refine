"""
RAG Service - Retrieves relevant educational content from vector store
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from src.load_vectorstore import VectorStoreLoader

class RAGService:
    def __init__(self):
        """Initialize RAG service with vector store"""
        self.db_path = Path(__file__).parent.parent.parent.parent / "data" / "qdrant_db_multi_subject"
        self.loader = None
        self.initialized = False
        
    def initialize(self):
        """Load vector store (call once at startup)"""
        if self.initialized:
            return
            
        try:
            print(f"[RAG] Initializing vector store from {self.db_path}")
            self.loader = VectorStoreLoader(str(self.db_path))
            self.loader.initialize()
            self.initialized = True
            print("[RAG] ✓ Vector store initialized successfully")
        except Exception as e:
            print(f"[RAG] ❌ Failed to initialize: {e}")
            raise
    
    def retrieve_context(
        self, 
        topic: str, 
        num_results: int = 5
    ) -> Dict[str, any]:
        """
        Retrieve relevant educational content for a topic
        
        Args:
            topic: The presentation topic
            num_results: Number of documents to retrieve
            
        Returns:
            Dictionary with context and metadata
        """
        if not self.initialized:
            self.initialize()
        
        try:
            # Search vector store
            results = self.loader.search(topic, limit=num_results)
            
            if not results:
                return {
                    "context": "",
                    "sources": [],
                    "images": [],
                    "has_context": False
                }
            
            # Aggregate context from results
            context_parts = []
            sources = []
            images = []
            
            for result in results:
                # Add text content
                context_parts.append(f"**From {result['source']} (Page {result['page']}):**\n{result['text']}")
                
                # Track sources
                sources.append({
                    "source": result['source'],
                    "page": result['page'],
                    "score": result['score']
                })
                
                # Collect images
                if result.get('images'):
                    images.extend(result['images'])
            
            # Join all context
            full_context = "\n\n".join(context_parts)
            
            return {
                "context": full_context,
                "sources": sources,
                "images": list(set(images)),  # Remove duplicates
                "has_context": True,
                "num_sources": len(sources)
            }
            
        except Exception as e:
            print(f"[RAG] Error retrieving context: {e}")
            return {
                "context": "",
                "sources": [],
                "images": [],
                "has_context": False,
                "error": str(e)
            }
    
    def close(self):
        """Close vector store connection"""
        if self.loader:
            self.loader.close()
            self.initialized = False


# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service