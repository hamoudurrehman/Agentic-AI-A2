# ADR 004: Durable Checkpoint Persistence & Crash Recovery

## Status
Accepted

## Context
Long-running agent workflows that pause for human approval cannot rely exclusively on transient in-memory state. In production, web servers and worker processes cycle, restart, or scale dynamically.

## Decision
Graph threads persist state checkpoints before and after every major stage:
- Checkpoints record state, execution traces, handoff Pydantic models, and approval status.
- When an API or worker restarts, the thread can be resumed immediately from the checkpoint store without re-running prior nodes.
- Every external write tool includes a deterministic `idempotency_key`, guaranteeing that retries or duplicate approval submissions never trigger duplicate marketplace submissions or double Connects charges.

## Consequences
- 100% resilience against transient crashes.
- Complete thread audit history accessible via `/runs/{thread_id}`.
