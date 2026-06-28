from app.services.github_client import GitHubClient
from app.db.session import AsyncSessionLocal
from app.models.pr import Repository, PullRequest, WebhookEvent
from sqlalchemy.future import select

async def process_github_webhook(event_type: str, payload: dict):
    """
    Process the GitHub webhook event asynchronously using FastAPI BackgroundTasks.
    """
    print(f"Received GitHub event: {event_type}")
    
    # Save the raw event
    try:
        async with AsyncSessionLocal() as session:
            action = payload.get("action")
            event = WebhookEvent(event_type=event_type, action=action, payload=payload)
            session.add(event)
            await session.commit()
    except Exception as e:
        print(f"Failed to save webhook event to database: {e}")

    if event_type == "pull_request":
        pr_number = payload.get("pull_request", {}).get("number")
        repo_name = payload.get("repository", {}).get("full_name")
        installation_id = payload.get("installation", {}).get("id")
        
        if not installation_id:
            print("No installation ID found in payload.")
            return {"status": "error", "message": "No installation ID"}

        print(f"Processing PR #{pr_number} in {repo_name} (Action: {action})")
        
        # Save or update Repo and PR
        try:
            async with AsyncSessionLocal() as session:
                # 1. Repository
                result = await session.execute(select(Repository).filter(Repository.full_name == repo_name))
                repo = result.scalars().first()
                if not repo:
                    repo = Repository(full_name=repo_name)
                    session.add(repo)
                    await session.commit()
                    await session.refresh(repo)
                
                # 2. Pull Request
                result = await session.execute(
                    select(PullRequest).filter(
                        PullRequest.repo_id == repo.id,
                        PullRequest.number == pr_number
                    )
                )
                pr = result.scalars().first()
                if not pr:
                    pr = PullRequest(
                        number=pr_number,
                        repo_id=repo.id,
                        state=payload["pull_request"]["state"],
                        title=payload["pull_request"]["title"],
                        body=payload["pull_request"].get("body", "")
                    )
                    session.add(pr)
                else:
                    pr.state = payload["pull_request"]["state"]
                    pr.title = payload["pull_request"]["title"]
                    pr.body = payload["pull_request"].get("body", "")
                
                await session.commit()
        except Exception as e:
             print(f"Failed to save PR to database: {e}")

        # Fetch PR diff and files
        client = GitHubClient(installation_id)
        
        try:
            files = await client.get_pr_files(repo_name, pr_number)
            print(f"Fetched {len(files)} files for PR #{pr_number}")
            
            diff = await client.get_pr_diff(repo_name, pr_number)
            print(f"Fetched diff for PR #{pr_number} (length: {len(diff)})")
            
            # Invoke LangGraph pipeline
            from app.agents.graph import review_graph
            print("Triggering LangGraph review pipeline...")
            
            initial_state = {
                "pr_number": pr_number,
                "repo_name": repo_name,
                "diff": diff,
                "files": files
            }
            
            # Run the graph synchronously in the async context
            # (In a real high-throughput scenario we'd use ainvoke or run in executor)
            final_state = await review_graph.ainvoke(initial_state)
            final_review = final_state.get("final_review", "Review failed to generate.")
            
            agent_reviews = {
                "security": final_state.get("security_findings", []),
                "bug": final_state.get("bug_findings", []),
                "quality": final_state.get("quality_findings", [])
            }
            
            print("Successfully completed PR review!")
            
            # Save the final review back to the database
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(PullRequest).filter(
                        PullRequest.repo_id == repo.id,
                        PullRequest.number == pr_number
                    )
                )
                pr_record = result.scalars().first()
                if pr_record:
                    pr_record.final_review = final_review
                    pr_record.agent_reviews = agent_reviews
                    await session.commit()
                    print(f"Saved review to DB for PR #{pr_number}")
            
            # Post the final review to GitHub PR
            try:
                await client.post_pr_comment(repo_name, pr_number, final_review)
                print(f"Successfully posted review comment to GitHub PR #{pr_number}")
            except Exception as e:
                print(f"Failed to post comment to GitHub: {e}")

        except Exception as e:
            print(f"Failed to fetch PR details from GitHub: {e}")
            
        print(f"Finished processing PR #{pr_number}")
        return {"status": "success", "repo": repo_name, "pr": pr_number}
    
    return {"status": "ignored", "event": event_type}
