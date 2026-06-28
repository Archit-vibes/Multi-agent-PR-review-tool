from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from contextlib import asynccontextmanager
from app.core.security import verify_github_signature
from app.services.github_service import process_github_webhook
from app.db.session import engine
from app.models.base import Base
from app.models.pr import Repository, PullRequest, WebhookEvent
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Clean up connections
    await engine.dispose()

app = FastAPI(title="AI PR Reviewer API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Pull Request Review Assistant is running"}

@app.post("/api/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint to receive GitHub webhooks.
    """
    # Verify the signature
    await verify_github_signature(request)
    
    event_type = request.headers.get("x-github-event", "unknown")
    
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON payload"}

    # Dispatch to background tasks
    background_tasks.add_task(process_github_webhook, event_type, payload)
    
    return {"status": "accepted", "message": "Webhook received and queued for processing"}

@app.get("/api/prs")
async def get_prs():
    async with AsyncSessionLocal() as session:
        # Join with repository to get the repo name, or just return PRs. Let's just return PRs for now.
        result = await session.execute(select(PullRequest).order_by(PullRequest.id.desc()))
        prs = result.scalars().all()
        return prs

@app.get("/api/prs/{pr_id}")
async def get_pr(pr_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PullRequest).filter(PullRequest.id == pr_id))
        pr = result.scalars().first()
        if not pr:
            raise HTTPException(status_code=404, detail="PR not found")
        return pr
