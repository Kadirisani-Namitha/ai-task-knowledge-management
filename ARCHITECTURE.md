# AI-Powered Task & Knowledge Management — Architecture

## Overview

A modular monolithic application consisting of a FastAPI backend and a React + Vite frontend.
The backend handles task management, user management, document ingestion, and semantic search.

---

## Repository Layout

```
ai-task-knowledge-management/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, security utilities, logging setup
│   │   ├── db/             # Engine, session factory, declarative base
│   │   ├── models/         # SQLAlchemy ORM models (one file, all 5 entities)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── api/            # FastAPI routers — one file per resource
│   │   ├── services/       # Business logic orchestration
│   │   ├── repositories/   # Data-access layer — DB queries only
│   │   ├── ai/             # Embedding, chunking, FAISS vector store
│   │   └── utils/          # File handling, text extraction helpers
│   ├── alembic/            # Database migrations
│   ├── alembic.ini
│   ├── seed.py             # Development seed script
│   ├── main.py             # Application entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios client + per-resource API modules
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── context/        # Auth context
│   │   └── utils/          # Shared helpers
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── .env.example
├── ARCHITECTURE.md
└── README.md
```

---

## Layer Responsibilities

### API Layer (`app/api/`)
- Declares FastAPI routers
- Handles HTTP concerns: request parsing, response serialization, HTTP status codes
- Delegates all logic to the service layer
- No business logic, no direct database access

### Service Layer (`app/services/`)
- Implements business rules
- Orchestrates calls between repositories, the AI layer, and other services
- Raises typed exceptions that the API layer translates to HTTP responses

### Repository Layer (`app/repositories/`)
- All SQLAlchemy queries live here
- Accepts and returns ORM model instances or scalar values
- No HTTP, no business logic

### AI Layer (`app/ai/`)
- `chunker.py` — splits document text into overlapping chunks
- `embedder.py` — wraps Sentence Transformers; produces float32 vectors
- `vector_store.py` — FAISS index: load, persist, add, search
- `pipeline.py` — orchestrates: text → chunks → embeddings → index

---

## Data Flow

### Document Upload
```
POST /api/v1/documents/upload
  → validate file type and size
  → store file on disk (path recorded in DB)
  → extract plain text (PyMuPDF / python-docx / plaintext)
  → chunk text (fixed-size with overlap)
  → embed each chunk (sentence-transformers all-MiniLM-L6-v2)
  → upsert into FAISS index (in-memory + persisted to disk)
  → persist document metadata to MySQL
  → persist chunk-to-document mapping to MySQL
```

### Semantic Search
```
GET /api/v1/search?q=...
  → embed query
  → FAISS similarity search → top-k (chunk_id, score) pairs
  → resolve chunk_id → document_id via DB
  → load document metadata from MySQL
  → return ranked SearchResult list
```

---

## Database Schema

Five tables with normalized relationships and appropriate indexes.

See `app/models/models.py` for the authoritative ORM definition.

| Table          | Key columns                                       |
|----------------|---------------------------------------------------|
| roles          | id, name (UNIQUE)                                 |
| users          | id, username, email, password_hash, role_id (FK)  |
| tasks          | id, title, status, assigned_to (FK), created_by (FK) |
| documents      | id, filename, file_path, uploaded_by (FK)         |
| activity_logs  | id, user_id (FK), action, entity_type, entity_id  |

---

## Authentication

- JWT Bearer tokens (HS256, configurable expiry)
- Token payload: `sub` = user_id (int as string), `exp`
- **Role is verified against the DB row on every protected request**, never from the JWT payload
- Passwords hashed with bcrypt (passlib)

---

## Environment Variables

All configuration is read from environment variables (or `.env` in development).
No credentials appear in source code. See `.env.example` for the full list.
