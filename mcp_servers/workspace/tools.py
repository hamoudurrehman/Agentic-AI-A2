"""Workspace MCP Server Tools.
Provides calendar availability, tentative holds, and email drafts.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

_holds: List[Dict[str, Any]] = []
_drafts: List[Dict[str, Any]] = []

def get_free_calendar_slots(days_ahead: int = 3) -> List[str]:
    """Return available 45-minute interview slots over the next N days."""
    now = datetime.now()
    slots = []
    for day in range(1, days_ahead + 1):
        target_date = now + timedelta(days=day)
        date_str = target_date.strftime("%Y-%m-%d")
        slots.append(f"{date_str} 10:00 AM - 10:45 AM PKT")
        slots.append(f"{date_str} 02:00 PM - 02:45 PM PKT")
        slots.append(f"{date_str} 04:30 PM - 05:15 PM PKT")
    return slots

def create_tentative_interview_hold(slot: str, client_name: str, job_id: str) -> Dict[str, Any]:
    """Hold a calendar slot tentatively pending client confirmation."""
    hold_record = {
        "hold_id": f"hold_{len(_holds) + 1}",
        "slot": slot,
        "client_name": client_name,
        "job_id": job_id,
        "status": "tentative_hold",
        "created_at": datetime.now().isoformat()
    }
    _holds.append(hold_record)
    return hold_record

def create_email_draft(recipient: str, subject: str, body: str) -> Dict[str, Any]:
    """Draft an interview follow-up or scheduling email."""
    draft = {
        "draft_id": f"draft_{len(_drafts) + 1}",
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "status": "draft_pending_human_review",
        "created_at": datetime.now().isoformat()
    }
    _drafts.append(draft)
    return draft
