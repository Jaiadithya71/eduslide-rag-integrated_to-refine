"""
Load the pre-computed Qdrant vector store without re-indexing.
"""
import os
from pathlib import Path
from langchain_qdrant import QdrantVectorStore  # Updated import
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreLoader:
    def __init__(self, db_path: str, collection_name: str = "textbook_content_multi_subject"):
        """
        Initialize the vector store loader.
        
        Args:
            db_path: Path to the Qdrant database folder
            collection_name: Name of the collection to load
        """
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.client = None
        self.embeddings = None
        self.doc_store = None
        
    def initialize(self):
        """Load embeddings model and connect to vector store."""
        print(f"Loading vector store from: {self.db_path}")
        
        # Ensure database exists
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        # Close any existing client
        if self.client is not None:
            try:
                self.client.close()
                print("Previous client instance closed.")
            except Exception as e:
                print(f"Error closing client: {e}")
        
        # Initialize Qdrant client
        self.client = QdrantClient(path=str(self.db_path))
        print("✓ Qdrant Client initialized")
        
        # Load embeddings model
        print("Loading embedding model (this may take 10-20 seconds)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Change to 'cuda' if you have GPU
        )
        print("✓ Embedding model loaded")
        
        # Connect to vector store - UPDATED to use QdrantVectorStore
        self.doc_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,  # Note: parameter name is 'embedding' not 'embeddings'
        )
        print(f"✓ Connected to collection: {self.collection_name}")
        
        return self
    
    def search(self, query: str, limit: int = 4):
        """
        Perform similarity search.
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        if self.doc_store is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        print(f"\nSearching for: '{query}'...")
        
        # Embed query
        query_vector = self.embeddings.embed_query(query)
        
        # Search using the correct method
        try:
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )
            
            # Check if we got results
            if not search_results or not hasattr(search_results, 'points'):
                print(f"⚠️  No results found for query: '{query}'")
                return []
            
            # Format results
            results = []
            for i, hit in enumerate(search_results.points):
                payload = hit.payload
                metadata = payload.get('metadata', {})
                
                result = {
                    'rank': i + 1,
                    'score': hit.score,
                    'source': metadata.get('source', 'Unknown'),
                    'page': metadata.get('page_number', 'Unknown'),
                    'text': payload.get('page_content', '')[:300],
                    'images': metadata.get('related_images', [])
                }
                results.append(result)
            
            print(f"✓ Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def close(self):
        """Close the client connection."""
        if self.client:
            self.client.close()
            print("Client connection closed.")

if __name__ == "__main__":
    # Example usage
    DB_PATH = "./data/qdrant_db_multi_subject"
    
    # Initialize
    loader = VectorStoreLoader(DB_PATH)
    loader.initialize()
    
    # Test search
    results = loader.search("What are the geographical divisions of India?")
    
    # Display results
    for result in results:
        print(f"\n--- Result {result['rank']} (Score: {result['score']:.2f}) ---")
        print(f"Source: {result['source']} (Page {result['page']})")
        print(f"Text: {result['text']}...")
        if result['images']:
            print(f"✅ {len(result['images'])} linked images")
        else:
            print("❌ No images")
    
    # Close
    loader.close()