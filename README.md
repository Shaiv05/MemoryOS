<div align="center">

<!-- Animated Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=🧠%20MemoryOS&fontSize=60&fontColor=fff&animation=twinkling&fontAlignY=35&desc=Your%20Personal%20Knowledge%20Operating%20System&descAlignY=60&descSize=20" width="100%"/>

<!-- Badges Row -->
<p align="center">
  <img src="https://img.shields.io/badge/Status-🚀%20V1.0%20Complete-emerald?style=for-the-badge&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Version-1.0.0-blueviolet?style=for-the-badge&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge&labelColor=1a1a2e" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
</p>

<br/>

> ### 🌟 *"Don't just store information — connect it."*
> #### A complete AI-powered knowledge management system that extracts, remembers, and visualizes **for you**.

<br/>

```
  ╔══════════════════════════════════════════════╗
  ║   🔮  Ingest  →  🔗  Graph  →  🛠️  Execute   ║
  ╚══════════════════════════════════════════════╝
```

</div>

---

## ✅ Project Status

<div align="center">

> ### 🎉 **Core Phases 1-10 are fully operational!**
> MemoryOS has transitioned from a document chatbot into a full-scale Productivity & Knowledge OS.

| Module | Status |
|--------|--------|
| 🔐 Advanced Auth | ✅ Complete |
| 📄 RAG Document Engine | ✅ Complete |
| 💬 Grounded AI Chat | ✅ Complete |
| 🧠 Memory Fact System | ✅ Complete |
| 🗺️ Knowledge Graph | ✅ Complete |
| 🚀 Productivity Suite | ✅ Complete |
| 🐳 Docker & CI/CD | ✅ Complete |

</div>

---

## 🧠 What is MemoryOS?

**MemoryOS** is a next-generation personal intelligence layer. It doesn't just store your files; it understands the relationships between your documents, identifies key entities, and manages your daily productivity through AI-driven insights.

Think **Obsidian** meets **ChatGPT** with a built-in **Task Manager** — all grounded in your own private data. 🔥

```
Upload Docs  →  Extract Entities  →  Build Knowledge Graph  →  Generate Daily Summaries
```

---

## ✨ Core Features

<table>
<tr>
<td width="50%">

### 📥 Intelligence Ingestion
- 📄 PDF, TXT, and DOCX support
- 🧩 Intelligent text chunking
- ⚡ Vector embeddings (pgvector)
- 🤖 Semantic retrieval

</td>
<td width="50%">

### 💬 Document Interaction
- 💬 Chat with your knowledge base
- 📍 Precise source citations (S1, S2...)
- 🧠 Autonomous memory extraction
- 🔄 Conversation persistence

</td>
</tr>
<tr>
<td width="50%">

### 🗺️ Knowledge Mapping
- 🌐 Interactive Knowledge Graph
- 👥 Entity extraction (People, Projects)
- 🔗 Relationship visualization
- 🔍 Deep-dive node details

</td>
<td width="50%">

### 🛠️ Productivity Layer
- 📝 AI-linked Personal Notes
- 🏁 Task Management (Pending/Done)
- 🎯 Goal Tracking with Progress bars
- 📊 Daily AI Focus Summaries

</td>
</tr>
</table>

---

## 🏗️ Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│                    🖥️  FRONTEND                          │
│         Next.js 14+  •  TypeScript  •  Tailwind CSS      │
│         Framer Motion  •  React Flow (Graph)             │
├─────────────────────────────────────────────────────────┤
│                    ⚙️  BACKEND (API)                      │
│         Python 3.11  •  Django  •  DRF                   │
│         JWT Auth  •  DRF Throttling (Security)           │
├─────────────────────────────────────────────────────────┤
│                    🤖  AI ENGINE                         │
│         OpenAI API  •  Sentence-Transformers             │
│         RAG Pipeline  •  Entity Extraction               │
├─────────────────────────────────────────────────────────┤
│                    🗄️  DATABASE                          │
│         PostgreSQL  •  pgvector (Vector Store)           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```bash
MemoryOS/
├── 🖥️  frontend/          # Next.js App Router UI
│   ├── app/               # Pages & Dashboard routes
│   ├── components/        # UI, Chat, Memory, Graph units
│   ├── services/          # API layer (Axios)
│   └── types/             # TypeScript definitions
│
├── ⚙️  backend/           # Django REST Framework
│   ├── chat/              # RAG & Conversation logic
│   ├── graph/             # Entity & Edge extraction
│   ├── productivity/      # Notes, Tasks, & Goals
│   ├── documents/         # Processing & Embeddings
│   └── config/            # Core Django settings
│
├── 🐳  Dockerfile         # Container configs
└── 📄  docker-compose.yml # Orchestration stack
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose**
- **OpenAI API Key**

### Installation & Run

The entire stack is containerized for a single-command setup.

```bash
# 1️⃣ Clone the repository
git clone https://github.com/Shaiv05/MemoryOS.git
cd MemoryOS

# 2️⃣ Configure Environment
# Add your OPENAI_API_KEY to docker-compose.yml or a .env file

# 3️⃣ Launch the OS
docker-compose up --build
```

Access the app at `http://localhost:3000` and the API at `http://localhost:8000`.

---

## 🤝 Contributing

We **welcome contributions** at every level! 🎉

```bash
# Fork → Clone → Create branch → Make changes → PR!
git checkout -b feature/amazing-improvement
git commit -m "✨ Implement smart connection"
git push origin feature/amazing-improvement
```

---

## 📬 Connect with the Developer

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-Shaiv05-181717?style=for-the-badge&logo=github)](https://github.com/Shaiv05)

💡 *Found a bug? Have a feature idea? Open an [issue](https://github.com/Shaiv05/MemoryOS/issues)!*

</div>

---

## 📜 License

This project is licensed under the **MIT License**.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer&animation=twinkling" width="100%"/>

**⭐ Star this repo if you believe in building a smarter second brain!**

*Made with 🧠 + ❤️ by [Shaiv05](https://github.com/Shaiv05)*

</div>
