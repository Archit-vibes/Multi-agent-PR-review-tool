from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph

class ReviewState(TypedDict, total=False):
    pr_number: int
    repo_name: str
    diff: str
    files: List[Dict[str, Any]]
    
    # Orchestrator output
    next_agents: List[str]
    
    # Specific agent outputs
    security_findings: List[str]
    bug_findings: List[str]
    quality_findings: List[str]
    
    # Aggregator output
    final_review: str
