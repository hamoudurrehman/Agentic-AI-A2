# ADR 002: Human-in-the-Loop Interrupt Discipline

## Status
Accepted

## Context
Upwork terms of service, marketplace integrity guidelines, and professional ethics prohibit unmonitored automated proposal spamming and unauthorized financial token expenditures (Connects). Proposals must be verified and approved by a human freelancer before leaving the system.

## Decision
We implement a non-negotiable **Human Approval Gate** using LangGraph's `interrupt()` pattern:
1. The graph halts execution before any proposal or message dispatch.
2. The approval payload packages the proposal draft, claim-to-evidence citations, risk report, and dry-run cost preview.
3. Resumption occurs only upon explicit human action: `approve`, `reject` (with reason), or `edit`.
4. User edits are diffed, promoted into persistent Style Memory, and re-validated by the Compliance Guard before dispatch.

## Consequences
- Guaranteed zero autonomous transmissions without human review.
- Proposals can survive API and worker restarts while paused at the gate.
