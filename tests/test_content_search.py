"""
Test Enhanced Stock Search with Slide Content
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.image_service import image_service

# Create a mock slide object
class MockSlide:
    def __init__(self, title, content, slide_type="content"):
        self.title = title
        self.content = content
        self.type = slide_type
        self.image_query = ""

def test_content_aware_search():
    """Test Freepik stock search with slide content"""
    print("=" * 70)
    print("Testing Content-Aware Stock Image Search (FREE)")
    print("=" * 70)
    
    # Test slides with different content
    test_slides = [
        MockSlide(
            title="Photosynthesis Process",
            content=[
                "Light-dependent reactions occur in the thylakoid membranes",
                "Chlorophyll absorbs light energy and converts it to chemical energy",
                "Calvin cycle uses ATP and NADPH to produce glucose"
            ]
        ),
        MockSlide(
            title="Water Cycle",
            content=[
                "Evaporation: Water turns into vapor from oceans and lakes",
                "Condensation: Water vapor forms clouds in the atmosphere",
                "Precipitation: Rain, snow, or hail falls back to Earth"
            ]
        ),
        MockSlide(
            title="Human Digestive System",
            content=[
                "Food enters through the mouth and esophagus",
                "Stomach breaks down food with acid and enzymes",
                "Small intestine absorbs nutrients into bloodstream"
            ]
        )
    ]
    
    results = []
    
    for slide in test_slides:
        print(f"\n{'='*70}")
        print(f"📄 Slide: {slide.title}")
        print(f"📝 Content:")
        for bullet in slide.content:
            print(f"   • {bullet[:60]}...")
        
        print(f"\n🔍 Building search query from content...")
        
        try:
            # Build query (this will show the enhanced query)
            query = image_service._build_freepik_query("Education", slide)
            print(f"   Query: {query}")
            
            # Search for image
            url = image_service._search_freepik_for_slide(
                topic="Education",
                slide=slide,
                slide_index=0,
                used_urls=set()
            )
            
            if url:
                print(f"\n✅ Found: {url}")
                results.append({
                    'slide': slide.title,
                    'query': query,
                    'url': url,
                    'status': 'SUCCESS'
                })
            else:
                print(f"\n❌ No image found")
                results.append({
                    'slide': slide.title,
                    'query': query,
                    'url': None,
                    'status': 'FAILED'
                })
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                'slide': slide.title,
                'query': '',
                'url': None,
                'status': f'ERROR: {e}'
            })
    
    # Save results
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}")
    
    with open('content_aware_search_results.txt', 'w', encoding='utf-8') as f:
        f.write("Content-Aware Stock Image Search Results\n")
        f.write("="*70 + "\n\n")
        
        for result in results:
            summary = f"\nSlide: {result['slide']}\n"
            summary += f"Query: {result['query']}\n"
            summary += f"Status: {result['status']}\n"
            summary += f"URL: {result['url']}\n"
            summary += "-"*70 + "\n"
            
            print(summary)
            f.write(summary)
        
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        f.write(f"\n\nSuccess Rate: {success_count}/{len(results)}\n")
        print(f"\n✅ Success Rate: {success_count}/{len(results)}")
    
    print(f"\n✅ Results saved to: content_aware_search_results.txt")
    print("="*70)

if __name__ == "__main__":
    test_content_aware_search()
