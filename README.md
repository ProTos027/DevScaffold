# DevScaffold: Intelligent Multi-Agent Project Sculptor 🏗️🚀

DevScaffold is an advanced agentic coding platform that transforms natural language intent into high-fidelity, runnable repositories. It uses a structured multi-agent pipeline powered by Google Gemini to ensure deterministic architectural consistency and high code quality.

## 🌟 Key Features

- **Intent-to-Code Pipeline**: Converts fuzzy user prompts into precise architectural specifications.
- **Architectural Manifests (Folder Contracts)**: A dedicated agent defines the file structure and inter-component dependencies before a single line of code is written.
- **Pure LLM Boilerplating**: Eschews static templates for dynamic, framework-agnostic generation (supports Spring Boot, FastAPI, Express, Django, etc.).
- **Real-Time Progress Tracking**: Watch the pipeline work through Stage 1 (Spec) to Stage 7 (Assembling) in real-time.
- **Deterministic Complexity Reduction**: Every stage in the pipeline strictly decreases entropy, ensuring the final code matches the initial intent.

## 🏗️ Architecture

The pipeline consists of specialized Gemini agents:

1.  **Spec Builder**: Parses natural language into an `Intent Spec`.
2.  **Validator**: Ensures the spec is architecturally sound.
3.  **Contract Builder**: Plans high-level components and responsibilities.
4.  **Dependency Graph Builder**: Determines the optimal build order.
5.  **Folder Contract Builder**: Defines the concrete file structure (The "Blueprint").
6.  **Code Generator**: Writes the implementation files anchored to the Folder Contracts.
7.  **Assembler**: Packages the results into a downloadable ZIP.

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, Django, Django REST Framework, PostgreSQL.
- **Frontend**: React, Vite, CSS Modules.
- **AI Engine**: Google Gemini (v1.5/2.0/2.5) via Google GenAI SDK.
- **Infrastructure**: Redis, Celery (Roadmap).

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL
- Google Gemini API Key

### Backend Setup

1.  Navigate to `backend/`.
2.  Create a virtual environment: `python -m venv venv`.
3.  Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux).
4.  Install dependencies: `pip install -r requirements.txt`.
5.  Configure `.env` (use `.env.example` as a template).
6.  Run migrations: `python manage.py migrate`.
7.  Start server: `python manage.py runserver`.

### Frontend Setup

1.  Navigate to `frontend/`.
2.  Install dependencies: `npm install`.
3.  Start dev server: `npm run dev`.

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---
