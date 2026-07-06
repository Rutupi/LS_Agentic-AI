from langgraph.graph import StateGraph
from grid_balancer.state import AgentState
from grid_balancer.agents.supervisor import supervisor_agent
from grid_balancer.agents.forecaster import forecaster_agent
from grid_balancer.agents.optimizer import optimizer_agent

def create_grid_balancer_graph():
    """
    Creates and compiles the LangGraph StateGraph representing the
    multi-agent supervisor orchestration workflow.
    """
    # 1. Initialize StateGraph with our custom AgentState
    workflow = StateGraph(AgentState)
    
    # 2. Add our agent nodes to the graph
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("forecaster", forecaster_agent)
    workflow.add_node("optimizer", optimizer_agent)
    
    # 3. Define control flow: Supervisor is the central coordinator
    workflow.set_entry_point("supervisor")
    
    # Forecaster and Optimizer always report back to the Supervisor
    workflow.add_edge("forecaster", "supervisor")
    workflow.add_edge("optimizer", "supervisor")
    
    # 4. Supervisor routes control dynamically based on current state
    def supervisor_router(state: AgentState):
        return state.get("next_agent", "__end__")
        
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "forecaster": "forecaster",
            "optimizer": "optimizer",
            "__end__": "__end__"
        }
    )
    
    # 5. Compile and return the compiled graph
    return workflow.compile()
