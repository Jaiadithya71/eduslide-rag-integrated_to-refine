"""
Test Gemini 2.5 Flash for generating search queries
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

print("=" * 70)
print("Testing Gemini 2.5 Flash for Search Query Generation")
print("=" * 70)

genai.configure(api_key=GEMINI_API_KEY)

# Test slides
test_slides = [
    {
        "topic": "Cellular Respiration",
        "title": "Krebs Cycle",
        "content": [
            "The citric acid cycle, also known as the Krebs cycle, is the second stage of cellular respiration.",
            "This stage occurs in the mitochondria of the cell and requires oxygen to occur.",
            "The citric acid cycle breaks down pyruvate into carbon dioxide, ATP, and NADH."
        ]
    },
    {
        "topic": "Cellular Respiration",
        "title": "Aerobic vs Anaerobic Respiration",
        "content": [
            "Aerobic respiration requires oxygen.",
            "Anaerobic respiration does not require oxygen.",
            "Aerobic respiration is more energy-efficient."
        ]
    }
]

# Use gemini-2.5-flash
model = genai.GenerativeModel('gemini-2.5-flash')

for slide in test_slides:
    print(f"\nSlide: {slide['title']}")
    
    prompt = f"""Generate a concise search query (max 10 words) for finding an educational diagram about this topic:

Topic: {slide['topic']}
Title: {slide['title']}
Content: {slide['content'][0]}

Focus on key scientific terms. Output ONLY the search query, nothing else."""
    
    try:
        response = model.generate_content(prompt)
        query = response.text.strip()
        
        print(f"Generated Query: {query}")
        
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("SUCCESS! Gemini 2.5 Flash works!")
print("=" * 70)
