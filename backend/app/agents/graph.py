from langgraph.graph import StateGraph, START, END
from app.agents.state import ReviewState
from app.agents.nodes import orchestrator, security_agent, bug_agent, quality_agent, aggregator

def create_review_graph():
    workflow = StateGraph(ReviewState)
    
    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("security_agent", security_agent)
    workflow.add_node("bug_agent", bug_agent)
    workflow.add_node("quality_agent", quality_agent)
    workflow.add_node("aggregator", aggregator)
    
    workflow.add_edge(START, "orchestrator")
    
    # Conditional branching
    def route_agents(state: ReviewState):
        next_agents = state.get("next_agents", [])
        if not next_agents:
             # If no specific agents needed, go straight to aggregator
             return ["aggregator"]
        return next_agents
    
    workflow.add_conditional_edges(
        "orchestrator",
        route_agents,
        {
            "security_agent": "security_agent",
            "bug_agent": "bug_agent",
            "quality_agent": "quality_agent",
            "aggregator": "aggregator"
        }
    )
    
    # All agent nodes feed into aggregator
    workflow.add_edge("security_agent", "aggregator")
    workflow.add_edge("bug_agent", "aggregator")
    workflow.add_edge("quality_agent", "aggregator")
    
    workflow.add_edge("aggregator", END)
    
    return workflow.compile()

review_graph = create_review_graph()
