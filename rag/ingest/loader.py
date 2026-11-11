"""Portfolio data ingestion and chunking module.
Extracts chunks with rich metadata across CV, case studies, GitHub repos, reviews, and past proposals.
"""
import os
import json
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "personas")

class Chunk:
    def __init__(self, chunk_id: str, text: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.text = text
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata
        }

def load_persona_chunks(persona_id: str = "persona_aiml") -> List[Chunk]:
    file_path = os.path.join(DATA_DIR, f"{persona_id}.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks: List[Chunk] = []

    # 1. CV / Bio chunk
    chunks.append(Chunk(
        chunk_id=f"{persona_id}_cv",
        text=f"{data.get('name')} - {data.get('title')}. {data.get('bio')} Skills: {', '.join(data.get('skills', []))}",
        metadata={
            "persona": persona_id,
            "type": "cv",
            "project": "profile",
            "skills": data.get("skills", []),
            "date": "2026",
            "client_industry": "All",
            "outcome": "verified"
        }
    ))

    # 2. Case studies
    for cs in data.get("case_studies", []):
        chunks.append(Chunk(
            chunk_id=cs["id"],
            text=f"Case Study: {cs['title']}. Client Industry: {cs['client_industry']}. Deliverables: {cs['deliverables']} Metrics: {cs['metrics']} Details: {cs['full_text']}",
            metadata={
                "persona": persona_id,
                "type": "case_study",
                "project": cs["id"],
                "skills": cs.get("skills", []),
                "date": "2025-2026",
                "client_industry": cs.get("client_industry"),
                "outcome": "delivered_successfully",
                "metrics": cs.get("metrics")
            }
        ))

    # 3. GitHub Repos
    for repo in data.get("repos", []):
        chunks.append(Chunk(
            chunk_id=f"repo_{repo['name']}",
            text=f"GitHub Repository: {repo['name']}. {repo['description']} README: {repo['readme']} Sample Code: {repo.get('code_snippets', '')}",
            metadata={
                "persona": persona_id,
                "type": "repo",
                "project": repo["name"],
                "skills": data.get("skills", []),
                "date": "2026",
                "client_industry": "OpenSource",
                "outcome": "active_open_source"
            }
        ))

    # 4. Past Proposals
    for prop in data.get("past_proposals", []):
        chunks.append(Chunk(
            chunk_id=prop["id"],
            text=f"Past Proposal for '{prop['job_title']}': {prop['proposal_text']} Outcome: {prop.get('outcome')}",
            metadata={
                "persona": persona_id,
                "type": "past_proposal",
                "project": prop["id"],
                "skills": [],
                "date": "2026",
                "client_industry": "Freelance",
                "outcome": prop.get("outcome")
            }
        ))

    return chunks
