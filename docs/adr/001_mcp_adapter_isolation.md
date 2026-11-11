# ADR 001: MCP Protocol for External Tool Isolation

## Status
Accepted

## Context
Agents in freelancer copilot systems must interact with multiple diverse platforms: job marketplaces (GigSim and live Upwork), local portfolios (case studies and code repos), and productivity workspaces (calendars and email). Calling APIs or databases directly couples agent prompts and logic to changing third-party schemas.

## Decision
All external capabilities are strictly mediated by MCP (Model Context Protocol) servers:
1. `mcp_servers/portfolio`: Read-only access to case studies, code repositories, and skills.
2. `mcp_servers/marketplace`: Unified read/write access to GigSim simulator and Upwork Live.
3. `mcp_servers/workspace`: Calendar holds and follow-up draft generation.

Agents are restricted to granular tool allowlists enforced by `MultiServerMCPClient`.

## Consequences
- Single marketplace port allows switching between testing and live mode without code alterations.
- Strict Pydantic input schemas and idempotency keys prevent double submissions.
- Schema changes are detected immediately in CI via contract snapshot tests.
