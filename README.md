# gitRAG

**RAG-based GitHub Repo Analysis Platform**  
*Analyse any public GitHub repository with LLM-powered chat and advanced semantic search.*
https://gitrag-fo9z.onrender.com/
---


https://github.com/user-attachments/assets/99065742-a793-4ec5-8bb5-231f37d3d50e


---


## Overview

### **Situation**
As a participant in open-source competitions and project exhibitions (EPICS, university projects), I often struggled to deeply understand large codebases—especially when onboarding new repositories from group members or exploring unfamiliar open-source projects. Sifting through thousands of files, dependencies, and scattered documentation was **tedious and overwhelming**, making it hard to answer even basic questions like "Where is X implemented?" or "How does this module work?"

### **Task**
I needed a platform that would let me:
- Instantly chat with any GitHub repo to ask questions about code, architecture, or logic.
- Quickly visualize and explore repo structure, file contents, and metadata.
- Perform semantic code search (not just by filename/text).
- Support multiple users and projects securely for my team and in competitions.

### **Action**
I independently designed and built **gitRAG**—an end-to-end, multi-tenant platform that ingests any public GitHub repo, chunks and indexes its code using embeddings and vector search, and enables users to interactively chat, search, and analyse codebases using a modern LLM (via LangChain and OpenAI API).

- **Built secure, scalable backend** using FastAPI, PostgreSQL (Aiven), PineconeDB, and LangChain.
- **Developed a modern React frontend** with hierarchical file explorer, real-time AI chat, and repo analytics.
- **Integrated Google/GitHub OAuth2** for authentication, and per-user encrypted API key management for privacy.
- **Engineered ingestion pipelines** to chunk, embed, and index 50MB+ codebases with 10,000+ files.
- **Tested and deployed** the platform on multiple real-world repos for open-source events and university project groups.

### **Result**
- Significantly reduced onboarding time for new repositories—now get context, explanations, and code Q&A in seconds.
- Enabled my team and myself to confidently tackle larger, more complex projects in hackathons and coursework.
- gitRAG is now a robust, reusable tool for anyone needing rapid understanding of unfamiliar codebases.

---

## Features

- **LLM-powered code chat:** Ask questions about repo structure, functions, or files—get contextual, AI-driven answers.
- **Semantic code search:** Find relevant code snippets using meaning, not just keywords.
- **Hierarchical file explorer:** Browse and preview the full repo tree with metadata and analytics.
- **Multi-user & multi-repo support:** Secure, per-user data isolation with Google/GitHub OAuth2.
- **Repo analytics:** Visualize language breakdown, file types, contributors, and more.
- **Encrypted API key management:** User API keys are encrypted and never exposed.
- **Blazing fast:** Sub-second query responses (vector search and retrieval).
- **Modern UI:** Built with React, TailwindCSS, and Three.js (for 3D hero effect).

---

## Tech Stack

- **Frontend:** React.js, TailwindCSS, Vite, Three.js
- **Backend:** FastAPI (Python), LangChain, PostgreSQL (Aiven), PineconeDB
- **AI/Vector Search:** OpenAI API, PineconeDB, LangChain
- **Auth:** Google OAuth2, GitHub OAuth2
- **Integrations:** GitHub API (repo fetching, metadata), Node.js (utility scripts)

---

## Demo

<img width="1919" height="969" alt="image" src="https://github.com/user-attachments/assets/7b48f5f0-2e21-44c0-aa8f-2a39c9283d46" />

<img width="1919" height="969" alt="image" src="https://github.com/user-attachments/assets/0bab392a-7d85-41b6-b7f3-b8bb801ae0c3" />

<img width="1919" height="970" alt="image" src="https://github.com/user-attachments/assets/f50438ea-2e60-4acf-be11-0e7921df9953" />

<img width="1919" height="970" alt="image" src="https://github.com/user-attachments/assets/003a5f25-4783-42bd-8d3d-2de7d42b14ca" />

<img width="1919" height="970" alt="image" src="https://github.com/user-attachments/assets/521fd041-2b37-4eee-8741-18f5214262d4" />

---

## How it Works (RAG Pipeline)

1. **Login** with Google or GitHub OAuth2 (secure, per-user).
2. **Paste any public GitHub repo URL** and your OpenAI API key (encrypted).
3. **Ingestion:**  
   - Fetches repo files via GitHub API
   - Chunks code using custom logic (by file type/size)
   - Generates vector embeddings (LangChain + OpenAI API)
   - Stores chunks and metadata in PineconeDB and PostgreSQL
4. **Analysis & Chat:**  
   - Use AI chat to ask any question about the repo (“What does X function do?” “Show me auth logic”)
   - Semantic search finds and retrieves the most relevant code chunks
   - LLM (via LangChain) generates contextual, accurate answers using retrieved code
5. **Explore:**  
   - Hierarchical explorer shows real file tree, lets you preview content and metadata
   - Repo analytics panel for high-level insights

---
## Example Use Cases

- **Hackathons/open-source events:** Instantly understand any team repo or competition project.
- **University coursework:** Quickly onboard and analyze group project submissions.
- **Personal learning:** Explore popular open-source projects by chatting and searching their code.
- **Team code reviews:** Get instant explanations and context for PRs and legacy code.
