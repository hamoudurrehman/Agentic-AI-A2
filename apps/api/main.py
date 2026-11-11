"""GigBid FastAPI Backend Application.
Provides REST and SSE endpoints for all multi-agent operations and serves the full web interface.
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Add base directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from apps.api.routers import auth, jobs, proposals, approvals, messages, runs, analytics, settings
from gigbid.agent.mcp_client import mcp_client_instance

app = FastAPI(
    title="GigBid — Multi-Agent Freelancer Copilot API",
    version="1.0.0",
    description="Backend API powering the GigBid copilot system with LangGraph orchestration, Advanced RAG, and MCP adapters."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(proposals.router)
app.include_router(approvals.router)
app.include_router(messages.router)
app.include_router(runs.router)
app.include_router(analytics.router)
app.include_router(settings.router)

# Mount Static Assets & Dashboard
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "GigBid API Running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "marketplace_online": mcp_client_instance.marketplace_online,
        "active_mode": settings.SYSTEM_SETTINGS["marketplace_mode"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
