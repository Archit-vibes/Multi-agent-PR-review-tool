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
If a problem can be fixed, generate the corrected replacement code.

Return JSON only.
Your output MUST be a JSON array of objects with the following schema:
[
  {{
    "file": "...",
    "line": 42,
    "issue": "...",
    "severity": "...",
    "reason": "...",
    "old_code": "...",
    "replacement": "..."
  }}
]
IMPORTANT: The `line` MUST be a line number that was modified or added (i.e. starts with `+`) in the right side of the diff. Do not suggest changes on unchanged lines (context lines), as GitHub will reject them!
If an issue cannot safely be fixed automatically, set replacement to null.
If there are no findings, return [].
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
        findings = [{"issue": "Failed to parse security findings."}]
    
    return {"security_findings": findings}

def bug_agent(state: ReviewState):
    llm = get_llm()
    diff = state.get("diff", "")
    
    prompt = f"""You are a Bug Review Agent. Review the following PR diff for logic errors or bugs.
If a problem can be fixed, generate the corrected replacement code.

Return JSON only.
Your output MUST be a JSON array of objects with the following schema:
[
  {{
    "file": "...",
    "line": 42,
    "issue": "...",
    "severity": "...",
    "reason": "...",
    "old_code": "...",
    "replacement": "..."
  }}
]
IMPORTANT: The `line` MUST be a line number that was modified or added (i.e. starts with `+`) in the right side of the diff. Do not suggest changes on unchanged lines (context lines), as GitHub will reject them!
If an issue cannot safely be fixed automatically, set replacement to null.
If there are no findings, return [].
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
        findings = [{"issue": "Failed to parse bug findings."}]
        
    return {"bug_findings": findings}

def quality_agent(state: ReviewState):
    llm = get_llm()
    diff = state.get("diff", "")
    
    prompt = f"""You are a Code Quality Review Agent. Review the following PR diff for style, readability, and maintainability.
If a problem can be fixed, generate the corrected replacement code.

Return JSON only.
Your output MUST be a JSON array of objects with the following schema:
[
  {{
    "file": "...",
    "line": 42,
    "issue": "...",
    "severity": "...",
    "reason": "...",
    "old_code": "...",
    "replacement": "..."
  }}
]
IMPORTANT: The `line` MUST be a line number that was modified or added (i.e. starts with `+`) in the right side of the diff. Do not suggest changes on unchanged lines (context lines), as GitHub will reject them!
If an issue cannot safely be fixed automatically, set replacement to null.
If there are no findings, return [].
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
        findings = [{"issue": "Failed to parse quality findings."}]
        
    return {"quality_findings": findings}

def aggregator(state: ReviewState):
    sec = state.get("security_findings", [])
    bug = state.get("bug_findings", [])
    qual = state.get("quality_findings", [])

    all_findings = []
    if isinstance(sec, list): all_findings.extend(sec)
    if isinstance(bug, list): all_findings.extend(bug)
    if isinstance(qual, list): all_findings.extend(qual)

    suggestions = []
    for f in all_findings:
        if isinstance(f, dict) and f.get("replacement") and f.get("file") and f.get("line"):
            suggestions.append(f)

    # Severity emoji map
    severity_emoji = {
        "critical": "🔴",
        "high":     "🟠",
        "medium":   "🟡",
        "minor":    "🔵",
        "low":      "🟢",
    }

    def format_finding(f):
        if not isinstance(f, dict):
            return ""
        severity = str(f.get("severity", "minor")).lower()
        emoji = severity_emoji.get(severity, "⚪")
        issue = f.get("issue", "Issue")
        file_path = f.get("file", "unknown file")
        line = f.get("line", "?")
        reason = f.get("reason", "")
        old_code = f.get("old_code", "")
        replacement = f.get("replacement", "")

        # Detect language from file extension for syntax highlighting
        ext = file_path.rsplit(".", 1)[-1] if "." in file_path else ""
        lang_map = {"js": "javascript", "jsx": "javascript", "ts": "typescript", "tsx": "typescript",
                    "py": "python", "css": "css", "html": "html", "json": "json", "md": "markdown"}
        lang = lang_map.get(ext, "")

        lines = []
        lines.append(f"- {emoji} **{severity.capitalize()} Severity:** `{issue}`")
        lines.append(f"  - **File:** `{file_path}`")
        lines.append(f"  - **Line:** {line}")
        if reason:
            lines.append(f"  - **Reason:** {reason}")
        if old_code:
            lines.append(f"  - **Old Code:**")
            lines.append(f"    ```{lang}")
            lines.append(f"    {old_code}")
            lines.append(f"    ```")
        if replacement:
            lines.append(f"  - **Suggested Fix:**")
            lines.append(f"    ```{lang}")
            lines.append(f"    {replacement}")
            lines.append(f"    ```")
        return "\n".join(lines)

    # Group by category
    sections = [
        ("🔒 Security Findings", [f for f in sec if isinstance(f, dict) and f.get("issue")]),
        ("🐛 Bug Findings",      [f for f in bug if isinstance(f, dict) and f.get("issue")]),
        ("✨ Code Quality Findings", [f for f in qual if isinstance(f, dict) and f.get("issue")]),
    ]

    review_parts = ["## 🤖 AI Code Review Summary", ""]

    has_findings = False
    for section_title, findings in sections:
        real_findings = [f for f in findings if isinstance(f, dict) and f.get("issue") and "Failed to parse" not in str(f.get("issue", ""))]
        if not real_findings:
            continue
        has_findings = True
        review_parts.append(f"### {section_title}")
        review_parts.append("")
        for f in real_findings:
            review_parts.append(format_finding(f))
            review_parts.append("")

    if not has_findings:
        review_parts.append("✅ **No issues found.** The code looks good!")

    review_parts.append("---")
    review_parts.append("*Review generated by the Multi-Agent PR Review Tool*")

    final_review = "\n".join(review_parts)
    return {"final_review": final_review, "suggestions": suggestions}

