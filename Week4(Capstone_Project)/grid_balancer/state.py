from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # Current grid telemetry (load, generation, frequency, status, nodes)
    telemetry: Dict[str, Any]
    
    # Historical grid conditions retrieved from the RAG store
    historical_cases: List[Dict[str, Any]]
    
    # Load and generation forecast for the next step (predicted by Forecaster)
    forecast: Dict[str, Any]
    
    # Power generation/storage adjustment recommendations (computed by Optimizer)
    recommendations: Dict[str, Any]
    
    # Chat message log containing conversation/logs between agents
    messages: List[BaseMessage]
    
    # Next node to execute: "forecaster", "optimizer", or "__end__" (decided by Supervisor)
    next_agent: str
