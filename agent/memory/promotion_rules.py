"""Explicit Promotion Rules for Long-Term Memory.
Governs the transformation of user edits and marketplace outcomes into promoted memories.
"""
import difflib
from typing import Optional, Dict, Any
from .store import memory_store_instance

def evaluate_style_promotion(original_draft: str, user_edited_draft: str) -> Optional[Dict[str, Any]]:
    """Compare user's manual edit against the original agent draft.
    Promotes persistent style preference if significant repeated pattern detected.
    """
    orig_words = original_draft.split()
    edit_words = user_edited_draft.split()

    matcher = difflib.SequenceMatcher(None, orig_words, edit_words)
    deleted_phrases = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "delete":
            deleted_text = " ".join(orig_words[i1:i2])
            if len(deleted_text) > 4:
                deleted_phrases.append(deleted_text)

    # Detect common editorial patterns
    promoted_rule = None
    if original_draft.lower().startswith("hi there") and not user_edited_draft.lower().startswith("hi there"):
        promoted_rule = "Cut informal conversational openers; begin directly with technical alignment."
    elif any("passionate" in p.lower() for p in deleted_phrases):
        promoted_rule = "Never use the word 'passionate' or emotional adjectives."
    elif any("guarantee" in p.lower() for p in deleted_phrases):
        promoted_rule = "Remove all guarantee claims or unconditional promises."
    elif deleted_phrases:
        promoted_rule = f"User preference: trimmed verbose phrasing: '{deleted_phrases[0][:50]}...'"

    if promoted_rule:
        return memory_store_instance.add_style_rule(promoted_rule, source="human_draft_edit")
    return None

def evaluate_outcome_promotion(job_category: str, proposal_text: str, outcome: str) -> Optional[Dict[str, Any]]:
    """Promotes winning proposal framing into Outcome Memory."""
    if outcome in ["won", "replied", "interview", "hired"]:
        # Extract opening sentence as the effective hook
        first_sentence = proposal_text.split(".")[0] if "." in proposal_text else proposal_text[:80]
        memory_store_instance.record_outcome(
            job_category=job_category,
            framing=first_sentence.strip(),
            outcome=outcome
        )
        return {"promoted": True, "category": job_category, "framing": first_sentence.strip()}
    return None
