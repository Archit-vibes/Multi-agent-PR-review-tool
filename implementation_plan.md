# AI-Powered Pull Request Review Assistant

This document outlines the proposed architecture, tech stack, and step-by-step implementation plan for the AI-Powered Pull Request Review Assistant.

## User Review Required

> [!IMPORTANT]
> Please review the architecture, directory structure, and the phased implementation plan below. Since this is a large system, we will build it iteratively. Your approval on the initial foundation (Phase 1) and overall direction is needed before we proceed.

## Open Questions

> [!WARNING]
> - Do you have a preference for package management in Python? (e.g., `poetry`, `uv`, or standard `pip` + `requirements.txt`/`pyproject.toml`)?
> - For the frontend, do you envision a web dashboard (e.g., Next.js or Vite) to manage repositories and view review logs, or should we focus strictly on the backend webhook and GitHub integration first?
> - Do you have an existing GitHub App configured, or should part of the setup include instructions on generating the webhook secret and private key?

## Proposed Changes

We will use a modular backend architecture to cleanly separate concerns (API, background jobs, database, and AI logic).

### Backend Directory Structure

#### [NEW] `backend/app/api/`
- Webhook receiver endpoints for GitHub events.

#### [NEW] `backend/app/core/`
- App configuration, security, GitHub signature verification.

#### [NEW] `backend/app/models/` & `backend/app/schemas/`
- SQLAlchemy models (PostgreSQL) and Pydantic validation schemas.

#### [NEW] `backend/app/services/`
- GitHub client logic (fetching diffs, posting comments) and generic business logic.

#### [NEW] `backend/app/worker/`
- Celery task definitions for asynchronous queue processing.

#### [NEW] `backend/app/agents/`
- LangGraph orchestration and individual review agents (Security, Bug, Quality, Aggregator) via LiteLLM.

#### [NEW] `backend/docker-compose.yml`
- Infrastructure orchestration (PostgreSQL, Redis, FastAPI web server, Celery worker).

---

## Phased Implementation Plan

### Phase 1: Foundation & Webhook Integration
1. Set up project dependencies (`FastAPI`, `Celery`, `Redis`, `SQLAlchemy`, etc.).
2. Initialize `docker-compose.yml` for local development.
3. Create the FastAPI webhook receiver endpoint.
4. Implement GitHub webhook payload verification (using HMAC).
5. Set up Celery and Redis to receive webhook events asynchronously.

### Phase 2: GitHub Context Retrieval
1. Develop GitHub API integration service.
2. Implement logic to fetch PR metadata, file lists, and raw diffs upon receiving a webhook task.
3. Store basic PR and event data in PostgreSQL.

### Phase 3: AI Pipeline Integration (LangGraph + LiteLLM)
1. Set up LiteLLM routing and basic prompt structures.
2. Develop the LangGraph workflow orchestrator.
3. Implement the first review agent (e.g., Code Quality Agent).
4. Implement the Aggregator node to format output.

### Phase 4: Feedback Loop
1. Implement the service to post aggregated review comments back to GitHub via the PR review API.
2. Finalize multi-agent orchestration (adding Security and Bug Detection agents).

## Verification Plan

### Automated Tests
- Unit tests for GitHub signature verification.
- Mock tests for the Celery task queue and GitHub API client.
- Tests for LangGraph agent output formats.

### Manual Verification
- Run `docker-compose up` to start all services locally.
- Use a tool like `ngrok` or `localtunnel` to expose the local webhook endpoint.
- Configure a test GitHub App and trigger PR events to verify the end-to-end flow.
