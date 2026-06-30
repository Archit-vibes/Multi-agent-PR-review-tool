from app.services.github_client import GitHubClient
from app.db.session import AsyncSessionLocal
from app.models.pr import Repository, PullRequest, WebhookEvent
from sqlalchemy.future import select

async def process_github_webhook(event_type: str, payload: dict):
    """
    Process the GitHub webhook event asynchronously using FastAPI BackgroundTasks.
    """
    print("=" * 30)
    print(f"Received GitHub event: {event_type}")
    print("=" * 30)
    
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
            print("=" * 30)
            print("Triggering LangGraph review pipeline...")
            print("=" * 30)
            
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
            
            print("=" * 30)
            print("Successfully completed PR review!")
            print("=" * 30)
            
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
                suggestions = final_state.get("suggestions", [])
                commit_id = payload.get("pull_request", {}).get("head", {}).get("sha")

                print("=" * 30)
                print(f"DEBUG: Total suggestions to post: {len(suggestions)}")
                print(f"DEBUG: commit_id = {commit_id}")
                print("=" * 30)
                
                if suggestions and commit_id:
                    for i, s in enumerate(suggestions):
                        print(f"DEBUG: Posting suggestion {i+1}/{len(suggestions)} -> {s.get('file')}:{s.get('line')}")
                        body = f"**{s.get('issue', 'Issue')}**\n{s.get('reason', '')}"
                        if s.get("replacement"):
                            replacement_text = str(s['replacement']).strip()
                            # If the AI accidentally wrapped the code in markdown backticks, strip them to prevent breaking the suggestion block
                            if replacement_text.startswith("```"):
                                lines = replacement_text.split("\n")
                                if len(lines) > 1 and lines[0].startswith("```"):
                                    lines = lines[1:]
                                if len(lines) > 0 and lines[-1].strip().startswith("```"):
                                    lines = lines[:-1]
                                replacement_text = "\n".join(lines).strip()
                            
                            body += f"\n\n```suggestion\n{replacement_text}\n```"
                        
                        comment = {
                            "path": s.get("file"),
                            "line": int(s.get("line")),
                            "side": "RIGHT",
                            "body": body
                        }
                        
                        try:
                            # We must post it as a Review, otherwise GitHub disables the 'Apply suggestion' button for standalone comments!
                            await client.post_pr_review(repo_name, pr_number, "", commit_id, [comment])
                            print(f"  [OK] Inline review posted: {s.get('file')}:{s.get('line')}")
                        except Exception as e:
                            resp_text = getattr(getattr(e, "response", None), "text", "N/A")
                            print(f"  [FAIL] Inline review failed: {s.get('file')}:{s.get('line')} -> {e}")
                            print(f"  [FAIL] GitHub said: {resp_text}")
                elif not commit_id:
                    print("DEBUG: No commit_id found — falling back to plain summary comment!")
                    await client.post_pr_comment(repo_name, pr_number, final_review)
                    print(f"[OK] Fallback summary comment posted to GitHub PR #{pr_number}")
                else:
                    print("DEBUG: No suggestions — posting plain summary comment as fallback!")
                    await client.post_pr_comment(repo_name, pr_number, final_review)
                    print(f"[OK] Summary comment posted to GitHub PR #{pr_number}")
                    
                print("=" * 30)
                print("[DONE] GitHub posting complete.")
                print("=" * 30)
            except Exception as e:
                print(f"[FAIL] Failed to post comment to GitHub: {e}")

        except Exception as e:
            print("=" * 30)
            print(f"Failed to fetch PR details from GitHub: {e}")
            print("=" * 30)
            
        print("=" * 30)
        print(f"Finished processing PR #{pr_number}")
        print("=" * 30)
        return {"status": "success", "repo": repo_name, "pr": pr_number}
    
    return {"status": "ignored", "event": event_type}
