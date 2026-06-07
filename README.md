# open-chat-agents

A production-ready chatbot POC built with **FastAPI**, **Next.js**, **LangChain**, and **Gemma3** — demonstrating how to architect AI-powered conversational systems with clean separation of concerns, streaming responses, and persistent chat history.

---

## Purpose

This project showcases a full-stack conversational AI solution designed for real-world scenarios. It demonstrates:

- **LLM orchestration** via LangChain with a local Gemma3 model (Ollama)
- **Streaming responses** using Server-Sent Events (SSE) for a responsive chat experience
- **Conversation persistence** with PostgreSQL storing sessions and message history
- **Content moderation** guard that rejects inappropriate language before hitting the LLM
- **Clean architecture** on the backend: routes → services → repositories → models

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| LLM Orchestration | LangChain + LangChain-Ollama |
| LLM | Gemma3 (via Ollama) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |

---

## Architecture

```
frontend/                          backend/
├── src/                           ├── app/
│   ├── app/          Next.js      │   ├── api/v1/routes/    HTTP layer
│   ├── components/   UI           │   ├── services/         Business logic
│   ├── services/     API calls    │   ├── repositories/     DB access
│   └── types/        Contracts    │   ├── models/           SQLAlchemy ORM
│                                  │   ├── schemas/          Pydantic contracts
│                                  │   └── core/             Config & DB session
```

**Request flow:**

```
Browser → Next.js → POST /api/v1/chat/stream → ChatService
                                                    ├── ModerationService  (guard)
                                                    ├── MessageRepository  (persist)
                                                    └── LangChain + Gemma3 (generate)
                                                            ↓ SSE stream
Browser ← chunks arriving word by word ←────────────────────
```

---

## Requirements

- **Python 3.12**
- **Node.js 20+**
- **Docker** (for PostgreSQL)
- **Ollama** — [install here](https://ollama.com)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/washingtonsousa/open-chat-agents.git
cd open-chat-agents
```

### 2. Start the LLM

Install Ollama, then pull and serve the Gemma3 model:

```bash
ollama pull gemma3
ollama serve
```

### 3. Start PostgreSQL

```bash
docker run -d --name chatbot-pg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=chatbot \
  -p 5432:5432 \
  postgres:16-alpine
```

### 4. Set up the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

cp .env.example .env            # edit if needed
alembic upgrade head            # run migrations

uvicorn app.main:app --reload --host 0.0.0.0
```

Backend will be available at `http://localhost:8000`.
Interactive API docs at `http://localhost:8000/docs`.

### 5. Set up the frontend

```bash
cd frontend
cp .env.local.example .env.local   # edit if needed
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`.

---

## Environment Variables

### Backend — `backend/.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `gemma3` | Model name served by Ollama |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |
| `DEBUG` | `false` | Enables SQLAlchemy query logging |

### Frontend — `frontend/.env.local`

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` | Backend base URL |

---

## Running with Docker Compose

To spin up the full stack (PostgreSQL + backend + frontend) in one command:

```bash
docker-compose up --build
```

> **Note:** Ollama must be running on the host machine. The backend container reaches it via `host.docker.internal:11434`.

After the containers are up, run the migrations once:

```bash
docker-compose exec backend alembic upgrade head
```

---

## Key Features

- **Streaming chat** — responses appear word by word via SSE, no waiting for the full reply
- **Session management** — create, list, and delete conversations; full history is persisted
- **Content moderation** — profanity and inappropriate language are intercepted before reaching the LLM, with a polite rejection message returned to the user
- **Conversation context** — the entire session history is sent to the LLM on each turn, enabling coherent multi-turn conversations

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sessions/` | Create a new session |
| `GET` | `/api/v1/sessions/` | List all sessions |
| `GET` | `/api/v1/sessions/{id}` | Get a session |
| `DELETE` | `/api/v1/sessions/{id}` | Delete a session and its messages |
| `POST` | `/api/v1/chat/stream` | Send a message (SSE streaming) |
| `GET` | `/api/v1/chat/{session_id}/history` | Get message history |

---

## License

MIT
