# Autonomous Energy Grid Balancer (AEGB)

An intelligent multi-agent system designed to optimize electrical grid stability by predicting load demand and dynamically rebalancing energy distribution.

## Architecture
This project utilizes the **Supervisor Pattern** orchestrated via LangGraph:
- **Supervisor Agent**: Monitors grid telemetry and delegates tasks.
- **Forecaster Agent**: Retrieves historical load data (RAG) to predict demand.
- **Optimizer Agent**: Applies control logic to adjust node power output.

## Tech Stack
- **Orchestration**: LangGraph, LangChain
- **Data**: Vector-based RAG for historical load patterns
- **Control Logic**: Rule-based optimization heuristics

## Setup
1. Clone the repo: `git clone [your-repo-link]`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the simulation: `python main.py`
