from app.agents.state import ReviewState
from app.agents.llm import get_llm
from langchain_core.messages import HumanMessage
import json

def orchestrator(state: ReviewState):
    llm = get_llm()
    diff = state.get("diff", "")
    
    prompt = f"""You are an Orchestrator Agent. Your job is to read a PR diff and decide which review agents should run.
The available agents are: security_agent, bug_agent, quality_agent.
If there are potential security concerns (auth, secrets, database queries), include security_agent.
If there are complex logic changes, include bug_agent.
If there are code style, naming, or readability issues, include quality_agent.

Return ONLY a JSON array of agent names. Do not include markdown formatting or explanation.
Example: ["security_agent", "quality_agent"]

Diff:
{diff[:3000]} # Limit diff size for orchestrator
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        next_agents = json.loads(content)
        if not isinstance(next_agents, list):
            next_agents = ["security_agent", "bug_agent", "quality_agent"]
    except Exception as e:
        print(f"Orchestrator parsing failed: {e}")
        # Default to all agents if parsing fails
        next_agents = ["security_agent", "bug_agent", "quality_agent"]
        
    return {"next_agents": next_agents}

def security_agent(state: ReviewState):
    llm = get_llm()
    diff = state.get("diff", "")
    
    prompt = f"""You are a Security Review Agent. Review the following PR diff for security vulnerabilities.
Return your findings as a JSON array of strings. If none, return [].
Do not include markdown block ticks around JSON.

Diff:
{diff}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        findings = json.loads(content)
    except:
        findings = ["Failed to parse security findings."]
    
    return {"security_findings": findings}

def bug_agent(state: ReviewState):
    llm = get_llm()
    diff = state.get("diff", "")
    
    prompt = f"""You are a Bug Review Agent. Review the following PR diff for logic errors or bugs.
Return your findings as a JSON array of strings. If none, return [].
Do not include markdown block ticks around JSON.

Diff:
{diff}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        findings = json.loads(content)
    except:
        findings = ["Failed to parse bug findings."]
        
    return {"bug_findings": findings}

def quality_agent(state: ReviewState):
    llm = get_llm()
    diff = state.get("diff", "")
    
    prompt = f"""You are a Code Quality Review Agent. Review the following PR diff for style, readability, and maintainability.
Return your findings as a JSON array of strings. If none, return [].
Do not include markdown block ticks around JSON.

Diff:
{diff}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        findings = json.loads(content)
    except:
        findings = ["Failed to parse quality findings."]
        
    return {"quality_findings": findings}

def aggregator(state: ReviewState):
    llm = get_llm()
    
    sec = state.get("security_findings", [])
    bug = state.get("bug_findings", [])
    qual = state.get("quality_findings", [])
    
    prompt = f"""You are an Aggregator Agent. Compile the following findings into a final, professional GitHub PR review comment in Markdown.

Security Findings:
{sec}

Bug Findings:
{bug}

Quality Findings:
{qual}

Combine overlapping points, ignore parser errors, and structure it cleanly. If there are no findings, state that the code looks good.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_review": response.content}
