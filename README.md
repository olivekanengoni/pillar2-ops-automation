# Pillar 2: Ops Automation Platform

AI-powered automation system for family office operations.

## Features

Message classification (5 categories)
RAG-based SOP search (ChromaDB)
Automated task creation (Todoist)
Audit logging (PostgreSQL - Neon)
n8n workflow orchestration

## Tech Stack

- **Input:** Webhook (WhatsApp, Email)
- **Backend:** Python 3.11 + FastAPI
- **AI:** Claude 3.5 Sonnet
- **Vector DB:** ChromaDB
- **Task Management:** Todoist API
- **Database:** PostgreSQL (Neon)
- **Orchestration:** n8n
- **Audit:** PostgreSQL


## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:
```
TODOIST_API_TOKEN=your_new_token_here
DATABASE_URL=your_new_database_url_here
```

### 3. Sample SOP pre-loaded into chromadb


### 4. Start FASTAPI Server or run on n8n workflow automation (As shown in demo)
This provides the `/process` endpoint for testing task intake.

```bash
uvicorn app:app --reload

Server runs at `http://localhost:8000`


## API Endpoints

- `POST /classify` - Classify messages
- `POST /search-policy` - Search SOPs
- `POST /create-task` - Create Todoist task
- `POST /process-complete` - End-to-end processing

## n8n Workflow

Import the workflow from n8n or configure:

1. Webhook trigger
2. HTTP Request to API
3. Todoist node
4. Postgres logging

## Architecture

See `solution_architecture.pdf` for complete system design.

## Trial Day Demo

This system demonstrates:
1. RAG-based AI assistant answering from SOPs
2. Automated task creation with policy guidance
3. Complete audit trail
4. End-to-end workflow automation

## License

Private - Family Office Use Only
