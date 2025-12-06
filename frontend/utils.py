"""
Utility functions for the Streamlit frontend
"""
import streamlit as st
from datetime import datetime
import json
from typing import Dict, Any

def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'presentation_data' not in st.session_state:
        st.session_state.presentation_data = None
    
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []
    
    if 'current_presentation_id' not in st.session_state:
        st.session_state.current_presentation_id = None
def add_to_history(topic: str, params: Dict[str, Any], status: str):
    """Add generation request to history"""
    history_item = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": topic,
        "params": params,
        "status": status
    }
    st.session_state.generation_history.insert(0, history_item)
    
    # Keep only last 10 items
    if len(st.session_state.generation_history) > 10:
        st.session_state.generation_history = st.session_state.generation_history[:10]
def format_slide_content(slides: list) -> str:
    """Format slides for preview display"""
    formatted = ""
    for i, slide in enumerate(slides, 1):
        formatted += f"### Slide {i}: {slide.get('title', 'Untitled')}\n\n"
        formatted += f"{slide.get('content', '')}\n\n"
        if slide.get('image_url'):
            formatted += f"🖼️ Image included\n\n"
        if slide.get('notes'):
            formatted += f"📝 Speaker Notes: {slide.get('notes')}\n\n"
        formatted += "---\n\n"
    return formatted
def display_info_card(title: str, content: str, icon: str = "ℹ️"):
    """Display an information card"""
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0; color: #1f77b4;">{icon} {title}</h4>
        <p style="margin: 0.5rem 0 0 0; color: #555;">{content}</p>
    </div>
    """, unsafe_allow_html=True)
def display_success_message(message: str):
    """Display success message with custom styling"""
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
        margin: 1rem 0;
    ">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)
def display_error_message(message: str):
    """Display error message with custom styling"""
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
        margin: 1rem 0;
    ">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)
def display_warning_message(message: str):
    """Display warning message with custom styling"""
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
        margin: 1rem 0;
    ">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)
def get_style_description(style: str) -> str:
    """Get description for presentation style"""
    descriptions = {
        "Academic": "Formal, structured content with citations and research-based information",
        "Storytelling": "Narrative-driven with engaging examples and emotional connection",
        "Business Pitch": "Persuasive, data-driven with clear value propositions",
        "Technical Deep-Dive": "Detailed technical content with diagrams and specifications",
        "Workshop/Interactive": "Hands-on approach with exercises and participation prompts",
        "Minimalist": "Clean, simple design with focus on key points"
    }
    return descriptions.get(style, "Custom presentation style")
def get_audience_description(audience: str) -> str:
    """Get description for audience type"""
    descriptions = {
        "School Students (6-10)": "Simple language, visual aids, interactive elements",
        "High School (11-12)": "Moderate complexity, exam-oriented, practical examples",
        "College/University": "Academic rigor, research-based, critical thinking focus",
        "Professional Training": "Industry-relevant, skill-building, practical applications",
        "Technical Briefing": "Expert-level, technical depth, specifications and standards",
        "Business Presentation": "Executive summary, ROI focus, strategic insights"
    }
    return descriptions.get(audience, "General audience")
def estimate_generation_time(num_slides: int, include_images: bool) -> str:
    """Estimate time to generate presentation"""
    base_time = num_slides * 5  # 5 seconds per slide
    if include_images:
        base_time += num_slides * 3  # Additional 3 seconds per image
    
    if base_time < 60:
        return f"~{base_time} seconds"
    else:
        minutes = base_time // 60
        return f"~{minutes} minute(s)"
def validate_topic(topic: str) -> tuple[bool, str]:
    """Validate the topic input"""
    if not topic or len(topic.strip()) < 3:
        return False, "Topic must be at least 3 characters long"
    
    if len(topic) > 500:
        return False, "Topic is too long (max 500 characters)"
    
    return True, "Valid"