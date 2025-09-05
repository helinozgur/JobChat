# JobChat: ATS-Optimized Resume Analysis & AI Career Coaching Platform

A sophisticated web application that analyzes resume compatibility with job postings using ATS algorithms and provides personalized career guidance through AI-powered coaching.

## Overview

JobChat combines advanced natural language processing with applicant tracking system (ATS) analysis to help professionals optimize their resumes for specific job opportunities. The platform features an integrated AI career coach that delivers contextual, profession-specific guidance based on resume analysis.

## Core Features

### Resume-Job Matching Engine
- **ATS Compatibility Scoring**: Implements TF-IDF vectorization to calculate semantic similarity between resumes and job descriptions
- **Skills Gap Analysis**: Identifies missing keywords and competencies critical for target positions
- **Profession Detection**: Employs machine learning algorithms to automatically classify professional domains from resume content
- **Coverage Analytics**: Measures alignment between candidate qualifications and job requirements

### AI-Powered Career Coaching
- **Contextual Recommendations**: Provides profession-specific guidance based on detected career track
- **Real-time Consultation**: Utilizes server-sent events for responsive chat interactions
- **Strategic Planning**: Offers actionable insights for skill development, project planning, and career advancement
- **Interview Preparation**: Delivers role-specific interview guidance and preparation strategies

### Multi-language Support
- **Internationalization Framework**: Complete Turkish and English localization
- **Dynamic Language Switching**: Runtime language preference management
- **Culturally Adapted Content**: Region-specific career advice and terminology

## Technical Architecture

### Backend Infrastructure
```
Flask Application (Python 3.8+)
├── Web Framework: Flask 2.3.3
├── AI Integration: Ollama + Qwen2.5 7B
├── Document Processing: PyPDF2 3.0.1
├── Web Scraping: BeautifulSoup4 4.12.2
├── Session Management: Flask-Session 0.5.0
└── CORS Handling: Flask-CORS 4.0.0
```

### Frontend Stack
```
Modern Web Technologies
├── JavaScript ES6+: Vanilla implementation
├── CSS3: Custom responsive design system
├── HTML5: Semantic markup structure
└── Real-time Communication: Server-Sent Events
```

### AI/ML Components
```
Natural Language Processing Pipeline
├── Language Model: Qwen2.5 7B (Local deployment)
├── Text Vectorization: TF-IDF implementation
├── Similarity Computation: Cosine similarity metrics
└── Classification: Custom profession detection algorithm
```

## System Requirements

### Hardware Specifications
- **Memory**: 8GB RAM minimum (16GB recommended for optimal AI performance)
- **Storage**: 5GB available disk space
- **CPU**: Multi-core processor (x64 architecture)

### Software Dependencies
- **Python**: Version 3.8 or higher
- **Ollama**: AI model runtime environment
- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+

## Installation Guide

### Environment Setup
```bash
# Clone repository
git clone https://github.com/username/jobchat.git
cd jobchat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### AI Model Configuration
```bash
# Install Ollama (visit https://ollama.ai)
curl -fsSL https://ollama.ai/install.sh | sh

# Download language model
ollama pull qwen2.5:7b

# Verify installation
ollama list
```

### Application Configuration
Create `.env` file in project root:
```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-cryptographically-secure-key

# Ollama Integration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# Analysis Parameters
PROF_CONF_THRESHOLD=0.7
MAX_FILE_SIZE=10485760
```

### Launch Application
```bash
python run.py
```
Access application at `http://localhost:8001`

## Project Structure

```
jobchat/
├── app/                          # Core application package
│   ├── __init__.py              # Application factory pattern
│   ├── config.py                # Configuration management
│   ├── routes/                  # API endpoint definitions
│   │   ├── analyze.py           # Resume analysis endpoints
│   │   ├── chat.py              # AI coaching interface
│   │   ├── status.py            # System health monitoring
│   │   └── root.py              # Frontend routing
│   └── utils/                   # Business logic modules
│       ├── cv_processor.py      # PDF parsing and text extraction
│       ├── job_scraper.py       # Web scraping for job postings
│       ├── ats_analyzer.py      # ATS scoring algorithms
│       └── ai_coach.py          # AI coaching logic
├── static/                      # Frontend assets
│   ├── css/
│   │   └── styles.css           # Responsive design system
│   └── js/
│       ├── app.js               # Application logic
│       └── i18n.js              # Internationalization
├── templates/
│   └── index.html               # Single-page application template
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── run.py                       # Application entry point
```

## Configuration Options

### AI Model Parameters
```python
# Model confidence thresholds
PROF_CONF_THRESHOLD = 0.7    # Profession detection accuracy
SIMILARITY_THRESHOLD = 0.6    # Resume-job matching sensitivity

# Performance tuning
MAX_TOKENS = 2048            # AI response length limit
TEMPERATURE = 0.7            # Response creativity balance
```

### Security Settings
```python
# File upload restrictions
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

# Session security
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # XSS protection
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
```

## API Documentation

### Resume Analysis Endpoint
```http
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- job_url: string (required) - Target job posting URL
- cv: file (required) - PDF resume file

Response:
{
  "success": boolean,
  "profession_detection": {
    "needs_manual_input": boolean,
    "confidence": number,
    "required_fields": string[]
  },
  "company": {
    "company": string|null,
    "role_title": string|null,
    "industry": string|null,
    "location": string|null
  },
  "profession": {
    "name": string,
    "display_name": string,
    "description": string
  },
  "analysis": {
    "score": number,
    "similarity": number,
    "coverage": number,
    "missing": string[],
    "issues": string[],
    "suggestions": string[],
    "sections": object
  },
  "skills": {
    "job_skills": string[],
    "cv_skills": string[],
    "matched_skills": string[],
    "alias_maps": object,
    "noise": object
  },
  "cv_preview": string
}
```

### AI Coaching Interface
```http
GET /api/chat?question=string
Accept: text/event-stream

Response Stream:
data: {"message": {"content": "partial response"}}
data: {"error": "error message", "done": true}  // on error
data: {"done": true}  // on completion
```

### Profession Override Endpoint
```http
POST /api/profession/override
Content-Type: application/json

Body:
{
  "name": string,
  "display_name": string,
  "description": string,
  "keywords": string[],
  "technologies": string[]
}

Response:
{
  "ok": boolean,
  "profession": object
}
```

### System Status Endpoint
```http
GET /api/status

Response:
{
  "status": "healthy",
  "version": "3.0.0-modular",
  "has_session": boolean,
  "profession": string,
  "profession_confidence": number|null,
  "needs_manual_profession": boolean,
  "ollama_configured": boolean,
  "ollama_model": string
}
```

## Deployment

### Production Environment
```bash
# Use production WSGI server
pip install gunicorn

# Launch with optimal settings
gunicorn --workers 4 --bind 0.0.0.0:8001 run:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "run:app"]
```


**Maintainer**: [Helin  Inceoglu]  
**Contact**: [helinozgur.com]  