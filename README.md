# 🎓 EduSlide AI

**Personalized AI Presentation Generator**

EduSlide AI is a powerful platform designed to generate high-quality, content-rich educational presentations instantly. It combines **Groq's Llama 3.3** for content generation with **Freepik** for high-quality stock images, all wrapped in a modern, user-friendly interface.

---

## ✨ Features

- **🤖 AI-Powered Content**: Generates structured, educational content using **Llama 3.3** (via Groq).
- **🖼️ Smart Image Engine**: Automatically fetches context-aware stock images from **Freepik**.
- **🎯 Exact Slide Control**: Guarantees precise slide counts (e.g., exactly 15 slides) using intelligent padding and truncation logic.
- **📝 Speaker Notes**: Generates deep, conversational speaker notes (approx. 100 words/slide) for professional delivery.
- **🎨 Custom Styles**: Supports multiple audience levels (School to Professional) and presentation styles (Academic, Storytelling, Visual, etc.).
- **⚡ Dynamic Architecture**: Backend automatically finds available ports to avoid conflicts.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python)
- **AI Model**: Groq (Llama 3.3-70b-versatile)
- **Images**: Freepik API
- **Vector DB**: Qdrant (for RAG - *Requires running Qdrant instance*)
- **Validation**: Pydantic
- **Presentation**: `python-pptx`

---

## 🚀 Setup & Installation

Prerequisites
Python 3.11+ (recommended)
Git
pip (Python package manager)

### 1. Clone & Environment
```bash
# Clone the repository
git clone <repository-url>
cd eduslide-ai

# Create virtual environment
python -m venv .venv
# Activate: .venv\Scripts\activate (Windows) OR source .venv/bin/activate (Linux/Mac)

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Create a `.env` file in the root directory with the following keys:

```ini
# Core AI (Required)
GROQ_API_KEY=your_groq_key_here

# Image Services (Required for visual content)
FREEPIK_API_KEY=your_freepik_key_here

# Optional Services
GEMINI_API_KEY=your_gemini_key_here  # For smart search queries (Recommended)
```

### 3. Run the Application
We provide a PowerShell script that handles everything (Port selection + Backend + Frontend).

```powershell
./start.ps1
```

**What this script does:**
1.  Finds an available port for the backend (starting from 8000).
2.  Writes the port to `.backend_port` for the frontend to read.
3.  Launches the **Backend** (FastAPI) in a new window.
4.  Launches the **Frontend** (Streamlit) in a new window.
5.  Opens your browser to `http://localhost:8501`.

---

## 🧪 Testing

The project includes a comprehensive test suite in the `tests/` directory to verify all components.

### Running Tests
To run specific functional tests:

```bash
# Test the full end-to-end generation (Simulates 5 slides request)
python tests/test_full_presentation.py

# Test Image Search Logic
python tests/test_freepik.py
```

### Test Files Overview
| File | Purpose |
|------|---------|
| `test_full_presentation.py` | **Main integration test.** Generates a real PPTX flow, prints slide content, and checks image provider selection. |
| `test_freepik.py` | Verifies stock image search connection and ranking logic. |
| `test_content_search.py` | Tests RAG/Vector search functionality (Qdrant integration). |
| `test_integration.py` | Health checks and basic API availability tests. |

---

## 📂 Project Structure

```
eduslide-ai/
├── backend/
│   ├── app/
│   │   ├── api/            # API Routes
│   │   ├── core/           # Config & Settings
│   │   ├── models/         # Pydantic Schemas
│   │   └── services/       # Core Logic (LLM, Image, PPTX)
│   └── main.py             # App Entry Point
├── frontend/
│   ├── streamlit_app.py    # Main UI
│   ├── config.py           # UI Config
│   └── api_client.py       # Backend Connector
├── tests/                  # Test Suite
├── .env                    # Secrets (Not committed)
├── start.ps1               # Startup Script
└── requirements.txt        # Python Dependencies
```

---

**Built for IIT Bombay Eduthon 2025** ❤️
