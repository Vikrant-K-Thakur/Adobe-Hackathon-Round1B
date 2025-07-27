# Adobe Hackathon - Round 1B: Persona-Based Document Insights

##  Overview
This is the submission for Round 1B of the Adobe India Hackathon 2025. It extracts **persona-based insights** from a set of PDF documents using semantic ranking.

## What It Does
- Accepts user persona + job-to-be-done + PDFs
- Ranks most relevant sections across documents
- Returns section titles and refined content
- Optimized for HR, travel planners, teachers, etc.

## Features
- Multi-PDF semantic matching with Sentence Transformers
- Title extraction with contextual validation
- Multiple high-quality insights per document
- Offline, fast, CPU-only processing

## Tech Stack
- Python 3.9
- Flask
- PyMuPDF (`fitz`)
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Docker

## Folder Structure
.
├── app.py # Flask endpoint for /generate-insights
├── generate_insights.py # Main logic for section ranking and text extraction
├── utils/
│ ├── pdf_helper.py # PDF parsing and section extraction
│ └── nlp_helper.py # Embedding and semantic ranking
├── Dockerfile # Container setup
├── requirements.txt # Required libraries
└── README.md # This file

## How to Run

### Option 1: Docker
```bash
docker build --platform linux/amd64 -t adobe-round1b .
docker run -p 5000:5000 --rm adobe-round1b

Option 2: Local Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
API Usage
POST /generate-insights
Postman Setup:
Method: POST

URL: http://localhost:5000/generate-insights

Body → form-data:

persona: e.g. "HR professional"

job: e.g. "Create and manage fillable forms for onboarding"

pdfs: [Upload 3–10 PDFs]
