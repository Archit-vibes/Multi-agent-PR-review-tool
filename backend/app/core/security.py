import hmac
import hashlib
from fastapi import Request, HTTPException
from app.core.config import settings

async def verify_github_signature(request: Request):
    """
    Verify that the webhook payload was sent from GitHub using the configured secret.
    """
    if not settings.GITHUB_WEBHOOK_SECRET:
        print("WARNING: GITHUB_WEBHOOK_SECRET is not set. Skipping signature verification.")
        return True

    signature_header = request.headers.get("x-hub-signature-256")
    if not signature_header:
        raise HTTPException(status_code=401, detail="x-hub-signature-256 header is missing!")
    
    try:
        body = await request.body()
        secret = settings.GITHUB_WEBHOOK_SECRET.encode("utf-8")
        
        # Calculate expected signature
        hash_object = hmac.new(secret, msg=body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature_header):
            raise HTTPException(status_code=401, detail="Invalid GitHub signature!")
            
        return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Error verifying signature.")
