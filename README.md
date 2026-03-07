# DevScaffold: Intelligent Multi-Agent Project Sculptor 🏗️🚀

DevScaffold is an advanced agentic coding platform that transforms natural language intent into high-fidelity, runnable repositories. It uses a structured multi-agent pipeline powered by Google Gemini to ensure deterministic architectural consistency and high code quality.

## 🌟 Key Features

- **Intent-to-Code Pipeline**: Converts fuzzy user prompts into precise architectural specifications using a 5-stage assembly line.
- **Creative Vision Propagation**: stylistic nuances (e.g., "90s terminal", "cosmic gold") are preserved across all agents.
- **Absolute Dark Mode**: Premium, dark-themed UI by default, enforced at both the platform and generated code levels.
- **Architectural Manifests**: A centralized "Source of Truth" (Manifest) ensures all agents align on naming and interfaces.
- **Stack-Agnostic Generation**: Dynamically implements logic for Spring Boot, FastAPI, Django, Express, React, Vue, etc.
- **Real-Time Progress Tracking**: Granular visibility into the agentic reasoning and file generation process.

## 🏗️ Architecture (The Assembly Line)

DevScaffold uses a multi-phased pipeline to minimize entropy and maximize code quality:

1.  **Stage 1: Spec Builder**: Parses natural language into a structured `Intent Spec`.
2.  **Stage 2: Prompt Expander**: Research-driven expansion of the domain to guide implementation details.
3.  **Stage 3: Contract Builder**: Acts as the Architect, locking down file structures and API schemas.
4.  **Stage 4: Generation Engine**: 
    - **Backend**: Implements business logic and data persistence.
    - **Frontend**: Implements the UI and API integration.
    - **Infrastructure**: Generates READMEs, Dockerfiles, and environment configs.
5.  **Stage 5: Assembler**: Validates, packages, and zips the final repository.

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Django 5.x, PostgreSQL.
- **Frontend**: React 18, Vite, Tailwind CSS (Mobile Responsive, Dark Mode Only).
- **AI Engine**: Google Gemini (Direct Prototyping & Generation).

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
