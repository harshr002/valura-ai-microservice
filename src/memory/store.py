from collections import defaultdict
from typing import Dict, List


class InMemorySessionStore:
    """
    Simple in-memory session store for demo purposes.

    Stores conversation turns by session_id so agents/classifier can see
    prior turns from the same conversation.
    """

    def __init__(self):
        self.sessions: Dict[str, List[dict]] = defaultdict(list)

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        self.sessions[session_id].append(
            {
                "role": role,
                "content": content,
            }
        )

    def get_history(self, session_id: str) -> List[dict]:
        return self.sessions.get(session_id, [])