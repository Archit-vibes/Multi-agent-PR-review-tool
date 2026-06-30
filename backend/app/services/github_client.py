import time
import jwt
import httpx
from app.core.config import settings

class GitHubClient:
    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self.app_id = settings.GITHUB_APP_ID
        self.private_key = settings.GITHUB_PRIVATE_KEY
        self.token = None

    def _generate_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": self.app_id
        }
        encoded_jwt = jwt.encode(payload, self.private_key, algorithm="RS256")
        return encoded_jwt

    async def authenticate(self):
        jwt_token = self._generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/app/installations/{self.installation_id}/access_tokens",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["token"]

    async def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        if not self.token:
            await self.authenticate()

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
                headers=headers,
                follow_redirects=True
            )
            response.raise_for_status()
            return response.text

    async def get_pr_files(self, repo_full_name: str, pr_number: int) -> list:
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str) -> dict:
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
                headers=headers,
                json={"body": body}
            )
            response.raise_for_status()
            return response.json()

    async def post_pr_review(self, repo_full_name: str, pr_number: int, body: str, commit_id: str, comments: list) -> dict:
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "body": body,
            "event": "COMMENT",
            "commit_id": commit_id,
            "comments": comments
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/reviews",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def post_pr_inline_comment(self, repo_full_name: str, pr_number: int, commit_id: str, path: str, line: int, body: str) -> dict:
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line,
            "side": "RIGHT"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/comments",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

