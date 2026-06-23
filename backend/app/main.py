from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.security import verify_github_signature
from app.worker.tasks import process_github_webhook
import json

app = FastAPI(title="AI PR Reviewer API")

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
async def github_webhook(request: Request):
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

    # Dispatch to celery worker
    process_github_webhook.delay(event_type, payload)
    
    return {"status": "accepted", "message": "Webhook received and queued for processing"}
