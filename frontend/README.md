# 🎓 EduSlide AI - Frontend
**Streamlit-based Frontend for EduSlide AI Presentation Generator**
IIT Bombay Eduthon 2025 - Phase 2
---
## 📋 Prerequisites
- Python 3.9 or higher
- Backend server running on `http://localhost:8000`
- Virtual environment (recommended)
---
## 🚀 Quick Start
### 1. Install Dependencies
```bash
# Navigate to frontend directory
cd frontend
# Install required packages
pip install -r requirements.txt
```
### 2. Configure Backend URL (Optional)
Create a `.env` file in the frontend directory:
```env
BACKEND_URL=http://localhost:8000
```
### 3. Run the Application
```bash
# Run Streamlit app
streamlit run streamlit_app.py
```
The application will open automatically in your browser at `http://localhost:8501`
---
## 🎯 Features
### ✨ Core Features
- **AI-Powered Content Generation**: Natural language prompts to slides
- **Audience Adaptation**: Tailored content for different education levels
- **Multiple Presentation Styles**: Academic, Business, Storytelling, etc.
- **Automatic Image Integration**: Contextual images from Pexels API
- **Speaker Notes**: Optional AI-generated presenter notes
- **Multi-language Support**: English, Hindi, Bilingual
### 🎨 UI Components
- **Interactive Form**: Step-by-step presentation configuration
- **Real-time Validation**: Input validation and error handling
- **Progress Tracking**: Visual feedback during generation
- **Slide Preview**: View generated slides before download
- **Generation History**: Track past presentations
- **Backend Health Check**: Monitor API connectivity
---
## 📁 Project Structure
```
frontend/
├── streamlit_app.py      # Main Streamlit application
├── config.py             # Configuration management
├── api_client.py         # Backend API communication
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
└── README.md            # This file
```
---
## 🔧 Configuration
### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | FastAPI backend URL |
### Application Settings
Edit `config.py` to customize:
- Audience types
- Presentation styles
- Language options
- Slide count limits
- UI text and labels
---
## 📖 How to Use
### Step 1: Enter Topic
Describe what you want to teach. Be specific for better results.
**Example:**
```
"Photosynthesis for Class 10 students with diagrams showing the 
light-dependent and light-independent reactions"
```
### Step 2: Select Audience
Choose from:
- School Students (6-10)
- High School (11-12)
- College/University
- Professional Training
- Technical Briefing
- Business Presentation
### Step 3: Configure Settings
- Number of slides (3-20)
- Presentation style
- Language preference
- Content complexity
- Image inclusion
- Speaker notes
### Step 4: Generate
Click "Generate Presentation" and wait for AI to create your slides.
### Step 5: Download
Download your PowerPoint file (.pptx) and use it immediately!
---
## 🎨 Presentation Styles
### 1. Academic
Formal, structured content with citations and research-based information
### 2. Storytelling
Narrative-driven with engaging examples and emotional connection
### 3. Business Pitch
Persuasive, data-driven with clear value propositions
### 4. Technical Deep-Dive
Detailed technical content with diagrams and specifications
### 5. Workshop/Interactive
Hands-on approach with exercises and participation prompts
### 6. Minimalist
Clean, simple design with focus on key points
---
## 🔍 Troubleshooting
### Backend Connection Error
**Problem:** "Cannot connect to backend"
**Solution:**
1. Ensure backend is running: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. Check `BACKEND_URL` in config
3. Verify no firewall blocking port 8000
### Streamlit Not Found
**Problem:** `streamlit: command not found`
**Solution:**
```bash
pip install streamlit
```
### Port Already in Use
**Problem:** Port 8501 already in use
**Solution:**
```bash
streamlit run streamlit_app.py --server.port 8502
```
---
## 🧪 Testing
### Manual Testing Checklist
- [ ] Backend health check shows connected
- [ ] Can enter and validate topic
- [ ] All dropdown options work
- [ ] Slider adjusts slide count
- [ ] Generate button triggers API call
- [ ] Progress bar shows during generation
- [ ] Results display correctly
- [ ] Download button works
- [ ] Slide preview shows content
- [ ] History tracks generations
---
## 📊 API Integration
The frontend communicates with the FastAPI backend through:
### Endpoints Used
- `GET /health` - Backend health check
- `POST /api/v1/generate` - Generate presentation
- `GET /api/v1/download/{id}` - Download presentation
- `GET /api/v1/preview/{id}` - Get slide preview
### Request Format
```json
{
  "topic": "string",
  "audience_type": "string",
  "num_slides": 8,
  "style": "string",
  "language": "string",
  "complexity": "string",
  "include_images": true,
  "include_notes": false
}
```
---
## 🎓 Educational Use
Perfect for:
- Teachers creating lesson presentations
- Students preparing project presentations
- Workshop facilitators
- Corporate trainers
- Academic researchers
- Content creators
---
## 🚀 Performance Tips
1. **Start Small**: Test with 5-6 slides first
2. **Specific Topics**: More specific = better results
3. **Image Loading**: Disable images for faster generation
4. **Browser**: Use Chrome/Firefox for best experience
5. **Internet**: Stable connection needed for API calls
---
## 📝 Notes
- First generation may take longer (API warm-up)
- Image quality depends on Pexels availability
- Speaker notes are optional (faster without)
- History is session-based (clears on refresh)
---
## 🤝 Contributing
For IIT Bombay Eduthon 2025 project.
**Team Members:** [Add your names]
**Project:** Personalized Presentation Generation for Education
---
## 📄 License
Educational project for IIT Bombay Eduthon 2025
---
## 🎯 Next Steps (Phase 3)
- [ ] Add Qdrant vector database integration
- [ ] Implement advanced content structuring
- [ ] Add quiz generation from slides
- [ ] Voice input support
- [ ] Multi-language deep integration
- [ ] Custom templates support
- [ ] Slide editing capability
- [ ] Batch presentation generation
---
**Made with ❤️ for IIT Bombay Eduthon 2025**