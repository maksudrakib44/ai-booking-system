"""
Memory module for storing conversation sessions.
Currently uses an in-memory dictionary. Replace with Redis for production.
"""

from typing import Dict, Optional
from app.ai.agents.state import AgentState

# Simple in-memory session store
sessions: Dict[str, AgentState] = {}

def get_session(session_id: str) -> Optional[AgentState]:
    return sessions.get(session_id)

def save_session(session_id: str, state: AgentState):
    sessions[session_id] = state

def delete_session(session_id: str):
    sessions.pop(session_id, None)