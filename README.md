<div align="center">

<img src=".github/assets/banner.svg" width="100%" alt="MemoryOS banner" />

### 🌟 *"Don't just store information — connect it."*

**A full‑stack, AI‑powered knowledge management system that ingests your documents, extracts memories, builds a knowledge graph, and helps you get things done — grounded entirely in your own private data.**

<br/>

<img src="https://img.shields.io/badge/status-active%20development-1a1a2e?style=for-the-badge" />
<img src="https://img.shields.io/badge/license-MIT-1a1a2e?style=for-the-badge" />
<img src="https://img.shields.io/badge/PRs-welcome-1a1a2e?style=for-the-badge" />

<br/>

<img src="https://img.shields.io/badge/Next.js%2015-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
<img src="https://img.shields.io/badge/React%2019-087EA4?style=for-the-badge&logo=react&logoColor=white" />
<img src="https://img.shields.io/badge/TypeScript-3776AB?style=for-the-badge&logo=typescript&logoColor=white" />
<img src="https://img.shields.io/badge/Django%206-092E20?style=for-the-badge&logo=django&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL%20%2B%20pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/LangChain%20%2F%20LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
<img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />

</div>

<br/>

```
╔══════════════════════════════════════════════════════════════╗
║   🔮  Ingest Docs  →  🧠  Extract Memory  →  🔗  Graph It     ║
║              →  🛠️  Chat, Plan & Execute                     ║
╚══════════════════════════════════════════════════════════════╝
```

---

# ✅ MemoryOS Project Status

MemoryOS is an AI-powered Knowledge Operating System built with **Django**, **Django REST Framework**, **Next.js**, **PostgreSQL**, and **pgvector**. It combines Retrieval-Augmented Generation (RAG), document intelligence, AI chat, and productivity tools into a unified workspace.

| Module | Description | Status |
|---------|-------------|--------|
| 🔐 Authentication | JWT Authentication (Register, Login, Refresh, Logout, Protected Routes) | ✅ Complete |
| 📄 Document Engine | Upload PDF, DOCX, TXT, document processing, chunking, metadata extraction | ✅ Complete |
| 🧩 Embedding Pipeline | Automatic embedding generation and pgvector storage | ✅ Complete |
| 🔍 Semantic Retrieval | Vector similarity search and context retrieval | ✅ Complete |
| 💬 AI Chat (RAG) | Grounded AI chat with document context, citations, and conversation history | 🟡 In Progress |
| 🧠 Memory System | AI memory extraction and persistent memory storage | 🟡 In Progress |
| 🗺️ Knowledge Graph | Entity extraction and relationship visualization | 🟡 In Progress |
| 📝 Notes Module | AI-assisted note management | 🟡 In Progress |
| ✅ Tasks Module | Task management and productivity workflow | 🟡 In Progress |
| 🎯 Goals Module | Goal tracking and progress management | 🟡 In Progress |
| 📊 Dashboard | Unified productivity dashboard | ✅ Complete |
| 🔎 Semantic Search | Cross-document semantic search | 🟡 In Progress |
| 🐳 Docker | Dockerized development environment | ✅ Complete |
| ⚙️ CI/CD | GitHub Actions pipeline and automated workflows | ✅ Complete |

---

# 🏗️ Current Architecture

```text
User
 │
 ▼
Authentication
 │
 ▼
Upload Document
 │
 ▼
Text Extraction
 │
 ▼
Smart Chunking
 │
 ▼
Embedding Generation
 │
 ▼
PostgreSQL + pgvector
 │
 ▼
Semantic Retrieval
 │
 ▼
AI Chat (RAG)
 │
 ├────────────► Notes
 ├────────────► Tasks
 ├────────────► Goals
 ├────────────► Memory
 └────────────► Knowledge Graph
```

---

# 📌 Current Progress

## ✅ Completed

- JWT Authentication
- User Registration & Login
- Refresh Token Authentication
- Logout with Token Blacklisting
- Protected Routes
- Dashboard
- Document Upload
- Text Extraction
- Smart Chunking Pipeline
- Embedding Generation
- pgvector Integration
- Semantic Retrieval
- Backend API Architecture
- Docker Support
- CI/CD Pipeline

---

## 🚧 In Progress

- Grounded AI Chat (RAG)
- AI Memory System
- Knowledge Graph
- Notes Module
- Tasks Module
- Goals Module
- Cross-Module Semantic Search

---

# 🚀 Next Phase

- Unified AI Workspace
- Universal Semantic Search
- AI Command Palette
- Cross-Module Intelligence
- Interactive Knowledge Graph
- Persistent AI Memory
- AI-Generated Summaries
- Flashcards & Quiz Generation
- Mind Maps
- AI Suggestions & Recommendations
- Production Optimization

---

# 📈 Overall Completion

| Area | Progress |
|------|----------|
| Backend | ██████████ 95% |
| Frontend | █████████░ 90% |
| AI Pipeline | ████████░░ 80% |
| Productivity Suite | ███████░░░ 70% |
| Knowledge Graph | ██████░░░░ 60% |
| Production Readiness | ████████░░ 85% |

**Overall Project Completion:** **~85%**

---

## 🧠 What is MemoryOS?

**MemoryOS** is a personal intelligence layer that sits on top of your documents and conversations. Instead of treating every file as an isolated blob of text, it:

- extracts the **entities and relationships** hidden inside your documents,
- remembers **facts** it learns about you as you chat,
- and turns all of that into a **daily-usable productivity system** — notes, tasks, and goals that stay linked to the knowledge that inspired them.

Think **Obsidian** × **ChatGPT** × a built-in **task manager**, all grounded in data you control.

```
Upload Docs → Chunk & Embed → Chat with Citations → Extract Memories & Entities → Visualize the Graph → Plan Your Day
```

---

## ✨ Core Features

<table>
<tr>
<td width="50%" valign="top">

### 📥 Intelligence Ingestion
- PDF, TXT & DOCX support (`pypdf`, `python-docx`)
- Automatic text chunking
- Vector embeddings via `sentence-transformers` / OpenAI, stored in **pgvector**
- Semantic chunk retrieval for RAG

### 💬 Document Interaction
- Chat grounded in your own uploaded documents
- Inline source citations (document, page, chunk, relevance score)
- Conversation history persisted per user
- Pluggable AI provider layer (`chat/providers.py`)

</td>
<td width="50%" valign="top">

### 🗺️ Knowledge Mapping
- Automatic entity extraction (people, projects, topics)
- Relationship edges between entities
- Interactive graph UI powered by **React Flow (`@xyflow/react`)**
- Node-level deep dives

### 🛠️ Productivity Layer
- AI-linked personal notes
- Task management (pending / done)
- Goal tracking with progress bars
- AI-generated daily focus summaries (`dashboard` app)

</td>
</tr>
</table>

---

## 🏗️ Tech Stack

```
┌──────────────────────────────────────────────────────────────────┐
│                         🖥️  FRONTEND                              │
│   Next.js 15 (App Router) · React 19 · TypeScript · Tailwind v4  │
│   Framer Motion · React Flow (@xyflow/react) · Axios · Lucide    │
├──────────────────────────────────────────────────────────────────┤
│                         ⚙️  BACKEND (API)                         │
│   Python 3.11 · Django 6 · Django REST Framework                 │
│   SimpleJWT auth · django-cors-headers · Gunicorn                │
├──────────────────────────────────────────────────────────────────┤
│                         🤖  AI ENGINE                             │
│   OpenAI API · LangChain · LangGraph                              │
│   sentence-transformers · tiktoken · RAG + entity extraction     │
├──────────────────────────────────────────────────────────────────┤
│                         🗄️  DATA LAYER                            │
│   PostgreSQL · pgvector (vector similarity search)               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
MemoryOS/
├── 🖥️  frontend/                # Next.js 15 App Router UI
│   ├── app/                     # Routes: dashboard, login, register
│   ├── components/              # chat, documents, memory, search, layout
│   ├── services/                # Axios API layer (auth, chat, graph, ...)
│   ├── hooks/                   # useAuth, etc.
│   └── types/                   # Shared TypeScript definitions
│
├── ⚙️  backend/                 # Django REST Framework project
│   ├── accounts/                # JWT auth: register, login, refresh, me
│   ├── chat/                    # RAG pipeline + conversations + providers
│   ├── documents/                # Upload, chunking, embeddings, retrieval
│   ├── graph/                   # Entity & relationship extraction
│   ├── memory/                  # Autonomous memory/fact extraction
│   ├── productivity/             # Notes, tasks, goals
│   ├── dashboard/               # Daily AI focus summaries
│   ├── search/                  # Cross-content semantic search
│   └── config/                  # Django settings, root URLconf
│
├── .github/workflows/ci.yml     # GitHub Actions: backend tests + frontend lint
├── 🐳 backend/Dockerfile, frontend/Dockerfile
└── 📄 docker-compose.yml        # db (pgvector) + backend + frontend
```

---

## 🔌 API Overview

All backend routes are namespaced under `/api/`:

| Prefix | App | Handles |
|---|---|---|
| `/api/auth/` | `accounts` | register, login, refresh, logout, current user |
| `/api/chat/` | `chat` | conversations, grounded messages, citations |
| `/api/documents/` | `documents` | upload, list, chunk retrieval |
| `/api/graph/` | `graph` | entities, relationships |
| `/api/memory/` | `memory` | extracted memory/fact entries |
| `/api/productivity/` | `productivity` | notes, tasks, goals |
| `/api/dashboard/` | `dashboard` | daily summaries |
| `/api/search/` | `search` | semantic search |

---

## 🚀 Getting Started

### Prerequisites
- **Docker** and **Docker Compose**
- An **OpenAI API key**

### Installation & Run

The entire stack — Postgres/pgvector, Django API, and the Next.js app — is containerized.

```bash
# 1️⃣ Clone the repository
git clone https://github.com/Shaiv05/MemoryOS.git
cd MemoryOS

# 2️⃣ Configure environment
# Set OPENAI_API_KEY (env var or .env) — see backend/.env.example

# 3️⃣ Launch the OS
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | `http://localhost:3000` |
| Backend API | `http://localhost:8000/api` |
| Django Admin | `http://localhost:8000/admin` |
| Postgres (pgvector) | `localhost:5432` |

> Running the backend/frontend outside Docker? Install deps with `pip install -r backend/requirements.txt` and `npm install` inside `frontend/`, respectively.

---

## 🧪 CI/CD

Every push and PR to `main` runs via GitHub Actions (`.github/workflows/ci.yml`):
- **backend** → installs `requirements.txt`, runs `python manage.py test`
- **frontend** → installs deps, runs `npm run lint`

---

## 🤝 Contributing

Contributions are welcome at every level! 🎉

```bash
# Fork → Clone → Create a branch → Make changes → Open a PR
git checkout -b feature/amazing-improvement
git commit -m "✨ Add amazing improvement"
git push origin feature/amazing-improvement
```

---

## 📬 Connect with the Developer

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-Shaiv05-181717?style=for-the-badge&logo=github)](https://github.com/Shaiv05)

💡 *Found a bug or have a feature idea? Open an [issue](https://github.com/Shaiv05/MemoryOS/issues)!*

</div>

---

## 📜 License

Licensed under the **MIT License**.

---

<div align="center">

**⭐ Star this repo if you believe in building a smarter second brain!**

*Made with 🧠 + ❤️ by [Shaiv05](https://github.com/Shaiv05)*

<img src=".github/assets/banner.svg" width="100%" height="90" alt="" />

</div>
