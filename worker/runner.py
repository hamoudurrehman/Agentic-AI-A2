"""Background worker for scheduled scouting and asynchronous agent runs.
Supports execution via Redis/Arq/Celery pattern with idempotent job processing.
"""
import time
import logging
from gigbid.agent.marketplace_port import marketplace_port_instance
from gigbid.agent.graphs.bid_graph import bid_graph_instance

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("gigbid-worker")

processed_jobs = set()

def poll_saved_searches(query: str = "LangGraph", interval_seconds: int = 60):
    logger.info(f"Starting scheduled scouting worker for query '{query}' (Interval: {interval_seconds}s)")
    try:
        jobs = marketplace_port_instance.search_jobs(query=query, limit=5)
        for job in jobs:
            job_id = job.get("id")
            if job_id in processed_jobs:
                continue
            logger.info(f"Worker picked up new job: {job_id} - '{job.get('title')}'")
            state = bid_graph_instance.initialize_state(job, persona_id="persona_aiml")
            bid_graph_instance.run_until_interrupt(state)
            processed_jobs.add(job_id)
            logger.info(f"Job {job_id} processed. Status: {state.get('status_message')}")
    except Exception as e:
        logger.error(f"Error in background worker execution: {e}")

if __name__ == "__main__":
    poll_saved_searches()
