<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>

<h3 align="center">Agentic AI GitHub PR Review Assistant</h3>

<p align="center">
An AI-powered multi-agent GitHub Pull Request reviewer that automatically analyzes code, detects security vulnerabilities, identifies bugs, reviews code quality, and generates GitHub Suggested Changes developers can apply with a single click.
<br />
<br />
<a href="https://youtu.be/WN5023Hkznw">View Demo</a>
&middot;
<a href="https://github.com/Archit-vibes/Multi-agent-PR-review-tool/issues">Report Bug</a>
&middot;
<a href="https://github.com/Archit-vibes/Multi-agent-PR-review-tool/issues">Request Feature</a>
</p>

---

# Table of Contents

<details>
<summary>Table of Contents</summary>

<ol>
<li>
<a href="#about-the-project">About The Project</a>
<ul>
<li><a href="#built-with">Built With</a></li>
</ul>
</li>
<li>
<a href="#architecture">Architecture</a>
</li>
<li>
<a href="#getting-started">Getting Started</a>
<ul>
<li><a href="#prerequisites">Prerequisites</a></li>
<li><a href="#installation">Installation</a></li>
</ul>
</li>
<li><a href="#usage">Usage</a></li>
<li><a href="#future-improvements">Future Improvements</a></li>
<li><a href="#license">License</a></li>
<li><a href="#contact">Contact</a></li>

</ol>

</details>

---

# About The Project

Modern pull requests often require multiple reviewers to check for:

- Security vulnerabilities
- Logic bugs
- Code quality
- Maintainability
- Best practices

Instead of relying on a single LLM prompt, this project uses **multiple specialized AI agents** orchestrated using **LangGraph** to review every Pull Request independently before combining their findings into a professional GitHub review.

Whenever a Pull Request is opened or updated:

- GitHub sends a webhook
- FastAPI verifies the webhook signature
- GitHub App authentication is performed using JWT
- The PR diff is fetched
- LangGraph launches multiple AI reviewers
- Findings are aggregated
- GitHub review comments are posted automatically
- AI Suggested Changes allow developers to apply fixes directly inside GitHub

---

## Architecture Highlights

- 🤖 Multi-agent orchestration using LangGraph with conditional routing.
- 🔄 Automatic LLM failover using LiteLLM (Groq → Gemini) for higher availability.
- 📊 LangSmith tracing for end-to-end observability, debugging, and prompt evaluation.
- ⚡ Fully asynchronous FastAPI backend with background webhook processing.
- 🔐 Secure GitHub App authentication using JWT and Installation Access Tokens.
- 💬 AI-generated GitHub Suggested Changes that developers can apply directly from Pull Requests.

## Key Features

### Multi-Agent Code Review

- Orchestrator Agent dynamically decides which reviewers should execute.
- Security Agent detects vulnerabilities.
- Bug Agent identifies logical issues.
- Code Quality Agent reviews maintainability.
- Aggregator Agent combines every finding into a professional review.

---

### AI Suggested Changes

Instead of only telling developers what is wrong, the reviewer generates actual replacement code.

GitHub displays:

> **Apply Suggestion**

allowing developers to accept AI fixes with a single click.

---

### Secure GitHub Integration

- GitHub App Authentication
- JWT-based authentication
- Installation Access Tokens
- HMAC SHA-256 Webhook Verification

---

### Real-Time Dashboard

A React dashboard continuously polls the backend to display

- Incoming Pull Requests
- AI Review Status
- Security Findings
- Bug Findings
- Quality Analysis
- Final Aggregated Review

---

### Async Processing

Heavy operations like

- GitHub API calls
- LLM inference
- Database operations

run asynchronously using FastAPI Background Tasks.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# Built With

## Backend

- Python
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- HTTPX
- PyJWT

## AI

- LangGraph
- LangChain
- LiteLLM
- Groq
- Gemini

## LLM Reliability & Observability

- Automatic LLM fallback using LiteLLM (Groq → Gemini) to ensure uninterrupted reviews even if the primary provider fails.
- End-to-end tracing and execution monitoring with LangSmith for debugging prompts, inspecting agent execution, and evaluating workflow performance.

## Frontend

- React
- Vite
- React Markdown
- Framer Motion
- Lucide React

## APIs

- GitHub Webhooks
- GitHub Apps API
- GitHub Pull Request Reviews API

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# Architecture

```text
Developer Opens PR
        │
        ▼
GitHub Webhook
        │
        ▼
FastAPI Backend
        │
        ├── Verify HMAC Signature
        ├── Save Event
        ├── Authenticate GitHub App
        └── Fetch PR Diff
                │
                ▼
          LangGraph Workflow
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
 Security     Bug      Quality
   Agent      Agent      Agent
      └─────────┼─────────┘
                ▼
        Aggregator Agent
                │
                ▼
     GitHub Review Comments
                │
                ▼
    GitHub Suggested Changes
                │
                ▼
 React Dashboard + PostgreSQL
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# Getting Started

Follow the steps below to run the project locally.

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- GitHub App
- Groq API Key or Gemini API Key

---

## Installation

### Clone Repository

```sh
git clone https://github.com/Archit-vibes/Multi-agent-PR-review-tool.git

cd Multi-agent-PR-review-tool
```

### Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### Configure Environment

Create a `.env`

```env
GITHUB_APP_ID=

GITHUB_WEBHOOK_SECRET=

GITHUB_PRIVATE_KEY=

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pr_reviewer

GROQ_API_KEY=

GEMINI_API_KEY=

LANGCHAIN_API_KEY=

LANGCHAIN_PROJECT=pr_reviewer
```

### Run Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```
http://localhost:8000
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:5173
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# Usage

1. Install the GitHub App on a repository.

2. Configure GitHub Webhooks.

3. Open or update a Pull Request.

4. The backend automatically

- verifies the webhook
- authenticates with GitHub
- downloads the PR diff
- launches the LangGraph workflow

5. AI agents independently review the code.

6. Findings are merged into a final review.

7. GitHub receives:

- Review Summary
- Inline Comments
- AI Suggested Changes

8. Developers can accept generated fixes directly from GitHub.

---

# Future Improvements

- Test Generation Agent
- Performance Review Agent
- Documentation Review Agent
- Architecture Review Agent
- PR Chat Assistant
- Auto Merge after approval
- Repository-wide Memory using RAG
- Historical Review Analytics
- CI/CD Integration
- Slack & Discord Notifications

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# Contact

**Archit Sharma**

GitHub: https://github.com/Archit-vibes

LinkedIn: https://www.linkedin.com/in/archit-sharma2006/

Project Link:

https://github.com/Archit-vibes/Multi-agent-PR-review-tool

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Project Link:

https://github.com/Archit-vibes/agentic-ai-pr-reviewer

<p align="right">(<a href="#readme-top">back to top</a>)</p>
