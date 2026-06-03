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

Patient Question
    ↓
FastAPI Chat API
    ↓
LangGraph Agent
    ↓
Retrieval Node
    - Gets patient profile from PostgreSQL
    - Gets relevant discharge records from Pinecone
    - Loads chat history
    ↓
Triage Node
    - Sends context to Gemini
    - Generates response
    - Assigns triage level
    ↓
Emergency?
    - Yes: SendGrid sends alert email
    - No: continue
    ↓
Response Node
    - Saves chat history
    ↓
Frontend displays response

LangGraph Flow
START
  ↓
retrieval_node
  ↓
triage_node
  ↓
if triage_level == 3:
      alert_node
      ↓
      response_node
else:
      response_node
  ↓
END
Triage Levels
1 = Self-care
2 = See a doctor within 48 hours
3 = Emergency / call 911
Project Structure
post-care-agent/
├── frontend/
│   └── index.html
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── routers/
│   │   ├── upload.py
│   │   └── chat.py
│   ├── agents/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── retrieval.py
│   │   ├── triage.py
│   │   ├── alert.py
│   │   └── response.py
│   └── services/
│       ├── excel_parser.py
│       ├── pinecone_service.py
│       ├── embedder.py
│       ├── gemini_service.py
│       ├── sendgrid_service.py
│       └── chat_history_service.py
├── sample_patients.xlsx
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
Key Files
File	Purpose
backend/main.py	Starts FastAPI app and serves frontend
backend/config.py	Loads environment variables
backend/database.py	Creates PostgreSQL connection and tables
backend/models.py	Defines Patient database model
backend/routers/upload.py	Handles Excel upload
backend/routers/chat.py	Handles chat API and history
backend/agents/graph.py	Defines LangGraph workflow
backend/agents/retrieval.py	Retrieves patient context
backend/agents/triage.py	Calls Gemini for response and triage
backend/agents/alert.py	Sends emergency email alert
backend/agents/response.py	Saves conversation history
backend/services/pinecone_service.py	Stores and searches vectors
backend/services/embedder.py	Creates text embeddings
backend/services/sendgrid_service.py	Sends alert emails
Environment Variables

Create a .env file:

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/postcare
SYNC_DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postcare

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash-lite

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=post-care-agent

SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender@example.com
ALERT_RECIPIENT_EMAIL=backup_alert@example.com

Do not commit your real .env file.

Run with Docker
docker compose up --build

Open:

http://localhost:8000
How to Use
Upload sample_patients.xlsx or another valid Excel file.
Select a patient ID.
Ask a post-care question.
View the AI response, triage level, sources, and alert status.

Example questions:

Can I take ibuprofen?
What should I eat after surgery?
When is my follow-up appointment?
I have fever and redness near my incision. What should I do?
API Endpoints
Method	Endpoint	Purpose
GET	/api/health	Health check
POST	/api/upload	Upload Excel patient data
POST	/api/chat	Ask a patient-specific question
GET	/api/history/{patient_id}	Get chat history
Sample Chat Request
{
  "patient_id": "P001",
  "session_id": "P001",
  "message": "I have fever near my incision. What should I do?"
}
Sample Chat Response
{
  "patient_id": "P001",
  "session_id": "P001",
  "response": "Based on your discharge records, this may require urgent medical attention...",
  "triage_level": 3,
  "triage_label": "Emergency",
  "alert_sent": true,
  "sources": ["red_flags"]
}
