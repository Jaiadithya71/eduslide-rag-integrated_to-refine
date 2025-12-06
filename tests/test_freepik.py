"""
Test script to verify Freepik API integration - saves results to file
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.image_service import image_service

def test_freepik_search():
    """Test basic Freepik image search"""
    results = []
    results.append("=" * 60)
    results.append("Freepik API Integration Test")
    results.append(f"Test Time: {datetime.now()}")
    results.append("=" * 60)
    
    # Test queries
    test_queries = [
        "photosynthesis diagram",
        "water cycle illustration",
        "human digestive system anatomy",
        "solar system planets",
        "mathematical equation graph"
    ]
    
    success_count = 0
    freepik_count = 0
    
    for query in test_queries:
        results.append(f"\n🔍 Searching for: '{query}'")
        try:
            url = image_service.search_image(query)
            if url:
                results.append(f"✅ Found image: {url}")
                success_count += 1
                # Check if it's from Freepik or placeholder
                if 'freepik' in url.lower() or 'img.freepik' in url or 'cdnpk' in url:
                    results.append("   ✓ Using Freepik API")
                    freepik_count += 1
                elif 'picsum' in url:
                    results.append("   ⚠️  Using placeholder (Freepik API may have failed)")
            else:
                results.append("❌ No image found")
        except Exception as e:
            results.append(f"❌ Error: {e}")
            import traceback
            results.append(traceback.format_exc())
    
    results.append("\n" + "=" * 60)
    results.append(f"Test Summary:")
    results.append(f"  Total queries: {len(test_queries)}")
    results.append(f"  Successful: {success_count}")
    results.append(f"  From Freepik: {freepik_count}")
    results.append(f"  From Placeholder: {success_count - freepik_count}")
    results.append("=" * 60)
    
    # Print to console
    for line in results:
        print(line)
    
    # Save to file
    with open('freepik_test_results.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))
    
    print("\n✅ Results saved to: freepik_test_results.txt")

if __name__ == "__main__":
    test_freepik_search()
