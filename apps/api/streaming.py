"""Server-Sent Events (SSE) Streaming Bridge for LangGraph Agent Runs."""
import json
import asyncio
from typing import AsyncGenerator, Dict, Any

async def stream_agent_execution(state: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Streams node-by-node execution events to the client via SSE."""
    traces = state.get("execution_trace", [])
    
    yield f"data: {json.dumps({'event': 'start', 'thread_id': state.get('thread_id'), 'trace_id': state.get('trace_id')})}\n\n"
    await asyncio.sleep(0.05)

    for step in traces:
        yield f"data: {json.dumps({'event': 'node_update', 'node': step.get('node'), 'action': step.get('action'), 'tokens': step.get('tokens'), 'cost_usd': step.get('cost_usd')})}\n\n"
        await asyncio.sleep(0.08)

    # Final event
    status = state.get("status_message", "COMPLETED")
    is_interrupt = "PAUSED" in status
    yield f"data: {json.dumps({'event': 'completed', 'status': status, 'interrupted_for_approval': is_interrupt, 'proposal_id': state.get('proposal_draft', {}).proposal_id if state.get('proposal_draft') else None})}\n\n"
