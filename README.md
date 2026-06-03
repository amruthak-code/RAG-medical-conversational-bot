# RAG-medical-conversational-bot
# Post-Care Agent

Post-Care Agent is an AI-powered post-discharge care assistant that helps patients ask questions about their discharge instructions, medications, red flags, diet restrictions, and follow-up schedule.

The system uses a Retrieval-Augmented Generation architecture with a LangGraph-based agent workflow. Patient profile data is stored in PostgreSQL, discharge instructions are stored as embeddings in Pinecone, and Gemini is used to generate grounded responses with triage classification. If a patient message is classified as an emergency, the system sends an alert email using SendGrid.

---

## Features

- Upload patient discharge data using an Excel file
- Store structured patient information in PostgreSQL
- Store discharge summaries, medications, red flags, diet restrictions, and follow-up schedules in Pinecone
- Ask patient-specific post-care questions through a web chat interface
- Retrieve relevant discharge records using semantic search
- Generate AI responses using Google Gemini
- Classify patient concerns into triage levels
- Send emergency alerts through SendGrid
- Save and load chat history
- Simple web frontend served by FastAPI

---

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript
- Fetch API

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Pandas
- OpenPyXL

### AI and Agent Workflow

- Google Gemini
- LangGraph
- LangChain
- Sentence Transformers
- Pinecone Vector Database

### External Services

- SendGrid for emergency email alerts
- Docker and Docker Compose for containerized setup

---

## System Architecture

```text
Excel Upload
    ↓
FastAPI Backend
    ↓
Excel Parser
    ↓
PostgreSQL stores structured patient profile data
    ↓
Sentence Transformer creates embeddings
    ↓
Pinecone stores discharge record vectors
