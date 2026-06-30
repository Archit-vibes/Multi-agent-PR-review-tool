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
    security_findings: List[Dict[str, Any]]
    bug_findings: List[Dict[str, Any]]
    quality_findings: List[Dict[str, Any]]
    
    # Aggregator output
    final_review: str
    suggestions: List[Dict[str, Any]]
