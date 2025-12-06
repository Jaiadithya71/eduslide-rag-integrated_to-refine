"""
Interactive query system for the RAG application.
"""
from load_vectorstore import VectorStoreLoader
import sys

def main():
    # Initialize vector store
    DB_PATH = "./data/qdrant_db_multi_subject"
    
    print("=" * 60)
    print("EduSlide RAG Query System")
    print("=" * 60)
    
    try:
        loader = VectorStoreLoader(DB_PATH)
        loader.initialize()
        
        print("\nSystem ready! Type 'quit' to exit.\n")
        
        while True:
            # Get query
            query = input("\nEnter your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                print("Please enter a valid query.")
                continue
            
            # Search
            results = loader.search(query, limit=3)
            
            # Display
            print("\n" + "=" * 60)
            for result in results:
                print(f"\n📄 Result {result['rank']} (Relevance: {result['score']:.2%})")
                print(f"   Source: {result['source']} | Page: {result['page']}")
                print(f"   Text: {result['text'][:150]}...")
                if result['images']:
                    print(f"   🖼️  {len(result['images'])} images available")
            print("=" * 60)
        
        loader.close()
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure you've downloaded the vector database to:")
        print(f"  {DB_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()