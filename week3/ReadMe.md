# Week 3: Advanced Agent Development (MCP, LangChain, & LangGraph)

## Overview
This week focused on transitioning from static RAG pipelines to autonomous, stateful agents. The curriculum covered:
*   **Model Context Protocol (MCP):** Establishing standardized tool-call boundaries.
*   **LangChain:** Orchestrating complex agentic workflows.
*   **LangGraph:** Designing stateful, iterative agent behavior.

---

## Status: Work-in-Progress (Technical Hurdles)
Development of these notebooks is currently in progress. While the theoretical architecture has been mapped, the implementation is currently blocked by several technical dependencies and framework structural changes:

*   **Library Import Refactoring:** Recent updates to the `langchain` ecosystem moved core modules like `AgentExecutor` and `create_react_agent` to `langchain-classic`, and `hub` to `langchainhub`. The code currently requires refactoring to align with these new package structures.
*   **Security & Prompt Hub:** Encountered security warnings regarding the pulling of public prompts from the LangChain Hub; shifting toward manual prompt definitions for better local control.
*   **Authentication Bottlenecks:** Integration with the Gmail MCP server on Google Colab is currently stalled due to OAuth authentication requirements and environment configuration limitations.

---

## Future Roadmap
To complete this module, the following steps are prioritized:
1.  **Environment Migration:** Refactor imports to utilize the latest `langchain` and `langchain-community` package structures.
2.  **Authentication Implementation:** Configure a local development environment (rather than Colab) to securely handle OAuth tokens for MCP servers.
3.  **Stateful Agent Implementation:** Finalize the LangGraph workflow to manage multi-turn task delegation and error resolution.
