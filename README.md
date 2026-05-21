# MEDINSIGHT AI

MedInsight AI is an AI-powered healthcare assistance web application designed to simplify medical information and make basic healthcare knowledge more accessible to common users. The platform enables users to analyze medical reports, interpret scan images, search medicine details, track health trends, and interact with an AI-powered health assistant through a single integrated interface.

The primary goal of the project is to bridge the gap between complex medical terminology and user understanding by presenting medical insights in a simplified, structured, and user-friendly manner.

---

## Live Demo

[Click here for live demo](medinsight-ai-0oe1.onrender.com)

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

### Database & Vector Storage
- Supabase
- Pinecone

### APIs
- OpenFDA Drug Label API
- REST APIs

### Deployment & Version Control
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

## Project Structure

```bash
MedInsight-AI/
│
├── research/
│   └── trials.ipynb
│
├── src/
│   ├── ai_assistant/
│   │   ├── helper.py
│   │   ├── prompt.py
│   │   └── template.py
│   │
│   ├── report_analyzer/
│   │   ├── ai_interpreter.py
│   │   ├── ocr_utils.py
│   │   ├── range_checker.py
│   │   ├── report_parser.py
│   │   └── scan_interpreter.py
│   │
│   └── __init__.py
│
├── static/
│   ├── assets/
│   │   ├── account 1.png
│   │   ├── account.png
│   │   ├── chatbot_icon.png
│   │   ├── medical_report_icon.png
│   │   ├── medicine_icon.png
│   │   ├── medinsight ai logo nobg 1.png
│   │   ├── medinsight ai logo nobg.png
│   │   ├── trends_icon.png
│   │   └── x-ray_icon.png
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── health_data.js
│
├── templates/
│   ├── about_us.html
│   ├── ai_assistant.html
│   ├── contact.html
│   ├── error.html
│   ├── ethics.html
│   ├── index.html
│   ├── landingpage.html
│   ├── login.html
│   ├── medicine_lookup.html
│   ├── report_analyzer.html
│   ├── scan_analyzer.html
│   ├── signup.html
│   ├── terms.html
│   └── trend_tracking.html
│
├── .gitignore
├── .python-version
├── .Procfile
├── README.md
├── app.py
├── aptfile
├── build.sh
├── requirements.txt
├── runtime.txt
├── setup.py
└── store_index.py
```

---

## Working Principle
### Medical Report Analysis Workflow
1. User uploads a report
2. OCR extracts report text
3. Parser identifies test names and values
4. Range checker classifies abnormalities
5. AI generates simplified explanations
6. Results are displayed to the user

### AI Assistant Workflow
1. User asks a query
2. Relevant medical context is retrieved from Pinecone
3. LangChain processes the retrieved context
4. Groq AI generates a contextual response

---

## Installation
### Clone Repository
```bash
git clone <repository-url>
cd MedInsight-AI
```

### Create Virtual Environment
```bash
python -m venv venv
```

### Activate Environment
#### Windows
```bash
venv\Scripts\activate
```

#### Linux/macOS
```bash
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variables
Create a .env file and configure:
```bash
GROQ_API_KEY=
GEMINI_API_KEY=
PINECONE_API_KEY=
HUGGINGFACEHUB_API_TOKEN=
SUPABASE_URL=
SUPABASE_ANON_KEY=
```

---

## Running the Application
### Start Flask Server
```bash
python app.py
```

### Run Pinecone Indexing
```bash
python store_index.py
```

---

## Future Improvements
- Improved OCR accuracy
- Expanded medical test database
- Mobile responsive interface
- Chat history in AI assistant
- File upload support in chatbot
- Medicine reminder system
- Diet recommendations based on abnormal values
- Downloadable PDF summaries
- Support for additional languages
- Automatic patient detail extraction

---

## Limitations
- Limited support for niche medical tests
- OCR accuracy depends on report quality
- Scan analysis depends on external AI APIs
- Medicine data formatting can be improved
- AI assistant currently lacks chat persistence

---

## Learning Outcomes
This project helped strengthen knowledge in:
- Full-stack web development
- API integration
- OCR-based text extraction
- AI-assisted healthcare applications
- Retrieval-Augmented Generation (RAG)
- Database management
- UI/UX design
- Modular backend architecture

---

## Authors
Developed as part of an academic and research-oriented healthcare assistance project focused on simplifying medical understanding through artificial intelligence.

**Akshara R**
* **GitHub:** [@akshara-ramesh](https://github.com)
* * **LinkedIn:** [Akshara R](https://linkedin.com)
* * **Email:** akshararamesh0512@gmail.com

**Anagha K**
* **GitHub:** [@anagha7337](https://github.com)
* * **LinkedIn:** [Anagha K](https://linkedin.com)
* * **Email:** anaghak7337@gmail.com

**Uthara Menon**
* **GitHub:** [@u7hara](https://github.com)
* * **LinkedIn:** [Uthara Menon](https://linkedin.com)
* * **Email:** uthararagamalika@gmail.com
