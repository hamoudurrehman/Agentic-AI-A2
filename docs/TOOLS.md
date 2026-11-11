# GigBid MCP Tool Registry (docs/TOOLS.md)

All agents interact with external environments strictly through the Model Context Protocol (MCP). Agents never make direct HTTP or database calls.

| Tool Name | MCP Server | Type | Annotations | Auth / Permissions | Trust Rationale & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `search_evidence` | Portfolio | Read | `readOnlyHint=True`, `idempotentHint=True` | Internal Local | Fetches verified case studies, repos, and metrics from freelancer portfolio. |
| `get_case_study` | Portfolio | Read | `readOnlyHint=True`, `idempotentHint=True` | Internal Local | Loads full case study text and deliverables by unique ID. |
| `list_skills` | Portfolio | Read | `readOnlyHint=True`, `idempotentHint=True` | Internal Local | Returns verified technical skills list for active persona. |
| `search_jobs` | Marketplace | Read | `readOnlyHint=True`, `idempotentHint=True` | Bearer Token | Reads open job postings from GigSim simulator or Upwork live port. |
| `get_job` | Marketplace | Read | `readOnlyHint=True`, `idempotentHint=True` | Bearer Token | Fetches complete job details and client history metrics. |
| `get_client_history` | Marketplace | Read | `readOnlyHint=True`, `idempotentHint=True` | Bearer Token | Reads verified client spend, hire rate, and reviews. |
| `get_connects_balance` | Marketplace | Read | `readOnlyHint=True`, `idempotentHint=True` | Bearer Token | Checks available Connects tokens to prevent overspending. |
| `list_messages` | Marketplace | Read | `readOnlyHint=True`, `idempotentHint=True` | Bearer Token | Retrieves message threads and inquiries for client liaison. |
| `create_proposal_draft`| Marketplace | Write | `readOnlyHint=False`, `idempotentHint=True` | Bearer Token | Dry-run proposal creation; verifies cost without spending Connects. |
| `submit_proposal` | Marketplace | Write | `destructiveHint=True`, `idempotentHint=True` | Bearer Token | Submits approved proposal; spends Connects idempotently. |
| `send_message` | Marketplace | Write | `readOnlyHint=False`, `idempotentHint=True` | Bearer Token | Dispatches approved reply or interview schedule to client. |
| `get_free_calendar_slots` | Workspace | Read | `readOnlyHint=True`, `idempotentHint=True` | Local / Google Cal | Returns available 45-minute interview windows over next 3 days. |
| `create_tentative_interview_hold` | Workspace | Write | `readOnlyHint=False`, `idempotentHint=True`| Local / Google Cal | Temporarily reserves a calendar slot during client negotiation. |
| `create_email_draft` | Workspace | Write | `readOnlyHint=False`, `idempotentHint=True`| Local / Gmail API | Creates interview follow-up email drafts for human review. |
| `get_repo_contents` | GitHub (3rd Party) | Read | `readOnlyHint=True`, `idempotentHint=True` | GitHub Personal Token | Third-Party: Reads public repository code and READMEs for automated portfolio ingestion. |
| `upwork_mcp_client` | Upwork (Official) | Read/Write | Streamable HTTP OAuth 2.1 | Upwork OAuth 2.1 | Third-Party: Official Upwork MCP server for live mode draft preparation. |

## Third-Party Trust Rationales
1. **Official Upwork MCP Server (`mcp.upwork.com/mcp`)**: Trusted vendor-operated MCP server using scoped OAuth 2.1 tokens. Runs in draft-only mode; never submits finalized bids without user confirmation.
2. **GitHub Official MCP Server**: Read-only ingestion of verified public source repositories to back portfolio claims with tangible code evidence.
