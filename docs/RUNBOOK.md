# GigBid Operations & Viva Runbook (docs/RUNBOOK.md)

## 1. Operating Modes & Scheduling Intervals

### Mode A: GigSim Marketplace Simulator
- **Use Case**: Grading, CI/CD evaluation, local unit/integration testing.
- **Poll Interval**: 30 seconds for background worker scouting.
- **Rate Limit**: Max 5 requests per second per tenant.
- **Behavior**: Deterministic evaluation against simulated clients with hidden preference weights.

### Mode B: Live Upwork Mode (Official MCP Server)
- **Use Case**: Real-world freelancer assistance under human supervision.
- **Poll Interval**: 120 seconds minimum (justified to prevent platform scraping detection).
- **Safety Restriction**: All write actions (`submit_proposal`, `send_message`) create drafts on Upwork; no bid is finalized without user manual confirmation on the Upwork platform.

---

## 2. Failure Recovery & Degraded Mode Handling

### Degraded Mode: Marketplace Server Offline
1. If the marketplace server becomes unreachable (5xx errors or network timeout), `MultiServerMCPClient` intercepts the failure.
2. The UI immediately displays a persistent warning banner: `Marketplace Unavailable — Operating in Degraded Mode`.
3. Agent graph pauses gracefully; pending submissions are queued in the Postgres checkpointer with exponential backoff retries.

### Durability Demonstration: API Crash & Resume
1. A job is analyzed and reaches the **Human Approval Gate** (`PAUSED_PENDING_HUMAN_APPROVAL`).
2. The API process is forcefully terminated (`SIGKILL` or `taskkill`).
3. The API restarts. State is restored from checkpoint storage.
4. User clicks **Approve** from the UI. The proposal is dispatched **exactly once** using its unique `idempotency_key`.

---

## 3. Viva Drill Scenarios (Quick Reference for Examiners)

| Question # | Scenario | Walkthrough & Code Location |
| :--- | :--- | :--- |
| **Q1** | *Kill the marketplace MCP server now. What does the user see?* | Set `mcp_client_instance.set_marketplace_online(False)`. UI shows degraded mode warning; `apps/api/routers/jobs.py` gracefully queues task without crashing. |
| **Q2** | *Approve a proposal, then crash the worker. Prove it submits exactly once.* | Handled via `idempotency_key` in `gigsim/simulator.py`. Retried submissions return the cached submission result without re-deducting Connects. |
| **Q3** | *Show a proposal claim, delete the underlying evidence, and regenerate.* | When evidence chunk is removed from persona JSON, `ClaimVerifier` (`rag/verify.py`) flags the claim as unsupported and excises it before human review. |
| **Q4** | *Open trace of a skipped job.* | Navigate to **Agent Run Viewer** (`/runs/{thread_id}`); inspect `RiskAssessor` trace output showing flagged off-platform keywords or scam indicators. |
| **Q5** | *Planted prompt injection.* | Demonstrated in `job_dev_003`. The `RiskAssessor` delimits untrusted input and catches "Ignore previous instructions", marking `injected_instructions_detected: true`. |
| **Q6** | *What did style memory learn from your last edit?* | Inspect **Settings & Memory** screen. Diff between original draft and human edit promoted rule via `agent/memory/promotion_rules.py`. Click trash icon to delete. |
| **Q7** | *Switch from GigSim to live mode in config.* | Toggle dropdown in Settings. `marketplace_port.py` switches adapter without altering any node or graph logic. |
