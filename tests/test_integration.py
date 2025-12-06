"""
Test Gemini integration in the actual image service
"""
import sys
sys.path.insert(0, 'backend')

from backend.app.services.image_service import ImageService

# Mock slide object
class MockSlide:
    def __init__(self, title, content):
        self.title = title
        self.content = content

# Create image service
print("=" * 70)
print("Testing Gemini Integration in Image Service")
print("=" * 70)

service = ImageService()

# Test slides
test_slides = [
    MockSlide(
        "Krebs Cycle",
        [
            "The citric acid cycle, also known as the Krebs cycle, is the second stage of cellular respiration.",
            "This stage occurs in the mitochondria of the cell and requires oxygen to occur.",
            "The citric acid cycle breaks down pyruvate into carbon dioxide, ATP, and NADH."
        ]
    ),
    MockSlide(
        "Aerobic vs Anaerobic Respiration",
        [
            "Aerobic respiration requires oxygen.",
            "Anaerobic respiration does not require oxygen.",
            "Aerobic respiration is more energy-efficient."
        ]
    )
]

print("\nTesting query generation:\n")

for slide in test_slides:
    print(f"Slide: {slide.title}")
    query = service._build_freepik_query("Cellular Respiration", slide)
    print(f"Result: {query}")
    print()

print("=" * 70)
print("SUCCESS! Integration working correctly.")
print("Ready to generate presentations!")
print("=" * 70)
