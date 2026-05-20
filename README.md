# MEDINSIGHT AI

MedInsight AI is an AI-powered healthcare assistance web application designed to simplify medical information and make basic healthcare knowledge more accessible to common users. The platform enables users to analyze medical reports, interpret scan images, search medicine details, track health trends, and interact with an AI-powered health assistant through a single integrated interface.

The primary goal of the project is to bridge the gap between complex medical terminology and user understanding by presenting medical insights in a simplified, structured, and user-friendly manner.

---

## Features
### Medical Report Analyzer
- Upload medical reports in PDF or image format
- Extracts report text using OCR
- Detects abnormal test values
- Classifies results into Low, Normal, or High
- Generates AI-powered explanations in simple language
- Supports multilingual explanations

### Medical Scan Analyzer
- Upload scan images such as X-rays
- AI-assisted interpretation using Gemini API
- Provides simplified analysis of uploaded scans

### Medicine Lookup
- Search medicines and drug information
- Retrieves data from OpenFDA API
- Simplifies complex medicine information for users

### AI Health Assistant
- AI-powered conversational assistant
- Answers general healthcare-related queries
- Uses Retrieval-Augmented Generation (RAG) for contextual responses

### Trend Tracking
- Add and manage patient profiles
- Store and compare multiple medical reports
- Visualize health metrics over time using graphs
- Detect trends and changes in test values

### Authentication System
- User login and signup functionality
- Persistent login support
- Secure user-based data management

---

## Technology Stack
### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

### Backend
- Python 3
- Flask
- Flask-CORS

### AI & NLP
- Groq AI API
- Gemini Flash API
- LangChain
- HuggingFace Sentence Transformers

### OCR & Text Processing
- Tesseract OCR
- Regex-based parsing

## Database & Vector Storage
- Supabase
- Pinecone

## APIs
- OpenFDA Drug Label API
- REST APIs

## Deployment & Version Control
- Render
- Git
- GitHub

---

## System Architecture

The application follows a modular architecture where each healthcare feature operates as an independent module connected through a centralized Flask backend.

Core modules include:
- Report Analysis Module
- OCR & Parsing Module
- AI Interpretation Module
- Medicine Lookup Module
- Trend Tracking Module
- AI Assistant Module
- Scan Interpretation Module

The backend communicates with external APIs and AI services to process and generate results dynamically.

---

```bash
MedInsight-AI/
│
├── app.py
├── requirements.txt
├── store_index.py
│
├── src/
│   ├── ai_assistant/
│   │   ├── helper.py
│   │   ├── prompt.py
│   │
│   ├── report_analyzer/
│   │   ├── ocr_utils.py
│   │   ├── report_parser.py
│   │   ├── range_checker.py
│   │   ├── ai_interpreter.py
│   │   ├── scan_interpreter.py
│   │
│   └── database/
│       └── db.py
│
├── templates/
├── static/
├── uploads/
└── Data/
