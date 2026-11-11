# AI Assistant Usage Record (docs/AI_USAGE.md)

As required by course policy, this document details the AI tools utilized during the architecture, implementation, and evaluation of GigBid.

## 1. Tools and File Scopes

| AI Assistant / Tool | Files / Scope | Tasks Performed |
| :--- | :--- | :--- |
| **Antigravity (Google DeepMind)** | `agent/`, `mcp_servers/`, `rag/`, `apps/` | Codebase architecture, multi-agent LangGraph orchestrator implementation, MCP tool servers, FastAPI REST endpoints, and evaluation runners. |
| **Claude / Cursor** | `docs/`, `agent/prompts/` | Prompt template engineering and documentation review. |

## 2. Issues Caught and Corrected

### Incident Caught:
During the initial implementation of the `submit_proposal` endpoint in the Marketplace MCP server, the initial draft allowed retrying without properly registering previously submitted jobs that were created dynamically during dev evaluations, causing a `ValueError: Job not found` during the integration test suite.

### Resolution:
Inspected the trace log and updated `gigsim/simulator.py` to auto-register incoming job IDs evaluated dynamically by the agent, ensuring that both predefined catalog jobs and dynamically discovered incoming market jobs submit idempotently without exception.
