"""
Test Full Presentation Generation with Content-Aware Images
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_presentation_generation():
    """Generate a test presentation and check image matching"""
    
    print("=" * 70)
    print("Testing Full Presentation Generation")
    print("=" * 70)
    
    # Test request
    payload = {
        "topic": "Photosynthesis Process for Class 10 Students",
        "audience_type": "school_students",
        "num_slides": 5,
        "presentation_style": "academic",
        "language": "english",
        "complexity": "intermediate",
        "include_images": True,
        "include_notes": False
    }
    
    print(f"\n📝 Generating presentation...")
    print(f"   Topic: {payload['topic']}")
    print(f"   Slides: {payload['num_slides']}")
    print(f"   Style: {payload['presentation_style']}")
    
    try:
        # Call API
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 201:
            data = response.json()
            
            print(f"\n✅ SUCCESS! Presentation generated")
            print(f"   ID: {data['presentation_id']}")
            print(f"   Slides: {data['total_slides']}")
            print(f"   Time: {data['generation_time']:.2f}s")
            
            # Check images
            print(f"\n📸 Image Analysis:")
            print(f"   {'='*66}")
            
            for i, slide in enumerate(data['slides'], 1):
                print(f"\n   Slide {i}: {slide['title']}")
                
                # Show first bullet
                if slide.get('content') and len(slide['content']) > 0:
                    print(f"   Content: {slide['content'][0][:60]}...")
                
                # Show image
                if slide.get('image_url'):
                    url = slide['image_url']
                    if 'freepik' in url or 'b2bpic' in url:
                        print(f"   ✅ Image: Freepik (content-aware)")
                    elif 'picsum' in url:
                        print(f"   ⚠️  Image: Placeholder")
                    else:
                        print(f"   Image: {url[:50]}...")
                else:
                    print(f"   ❌ No image")
            
            # Save results
            with open('presentation_test_results.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n✅ Full results saved to: presentation_test_results.json")
            print(f"   Download URL: {BASE_URL}/download/{data['presentation_id']}")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_presentation_generation()
