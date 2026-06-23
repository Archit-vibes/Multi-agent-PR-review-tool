from app.worker.celery_app import celery_app
import time

@celery_app.task(name="process_github_webhook")
def process_github_webhook(event_type: str, payload: dict):
    """
    Process the GitHub webhook event asynchronously.
    """
    print(f"Received GitHub event: {event_type}")
    
    if event_type == "pull_request":
        action = payload.get("action")
        pr_number = payload.get("pull_request", {}).get("number")
        repo_name = payload.get("repository", {}).get("full_name")
        print(f"Processing PR #{pr_number} in {repo_name} (Action: {action})")
        
        # Simulate some processing time
        time.sleep(2)
        print(f"Finished processing PR #{pr_number}")
        return {"status": "success", "repo": repo_name, "pr": pr_number}
    
    return {"status": "ignored", "event": event_type}
