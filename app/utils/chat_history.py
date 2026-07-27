import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import defaultdict


class ChatMessage:
    __slots__ = ("role", "content", "timestamp", "metadata")

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.role = role  # "user" | "assistant" | "system"
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class ChatHistoryStore:
    """
    In-memory session history store.

    In production this should be backed by:
      - Databricks Delta Lake table  (batch / offline analytics)
      - Redis / Cosmos DB            (low-latency serving)
      - Databricks Online Tables     (managed option)

    The session_id is always provided by the caller because different
    integrations (web widget, WhatsApp, Teams, email) have their own
    session lifecycle rules.
    """

    def __init__(self, max_history_per_session: int = 50):
        self._sessions: Dict[str, List[ChatMessage]] = defaultdict(list)
        self._session_meta: Dict[str, Dict[str, Any]] = {}
        self._max_history = max_history_per_session

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        msg = ChatMessage(role=role, content=content, metadata=metadata)
        history = self._sessions[session_id]
        history.append(msg)

        # Trim oldest messages if over limit
        if len(history) > self._max_history:
            self._sessions[session_id] = history[-self._max_history :]

        # Track session-level metadata
        if session_id not in self._session_meta:
            self._session_meta[session_id] = {
                "created_at": msg.timestamp,
                "message_count": 0,
            }
        self._session_meta[session_id]["last_activity"] = msg.timestamp
        self._session_meta[session_id]["message_count"] = len(
            self._sessions[session_id]
        )

        return msg

    def get_history(
        self, session_id: str, last_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        history = self._sessions.get(session_id, [])
        if last_n is not None:
            history = history[-last_n:]
        return [m.to_dict() for m in history]

    def get_session_meta(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._session_meta.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [
            {"session_id": sid, **meta}
            for sid, meta in self._session_meta.items()
        ]

    def clear_session(self, session_id: str) -> bool:
        removed = session_id in self._sessions
        self._sessions.pop(session_id, None)
        self._session_meta.pop(session_id, None)
        return removed

    def record_turn(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        turn_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.add_message(session_id, "user", user_message)
        self.add_message(
            session_id, "assistant", agent_response, metadata=turn_metadata
        )

    def get_context_summary(self, session_id: str, last_n: int = 6) -> str:
        history = self.get_history(session_id, last_n=last_n)
        if not history:
            return ""
        lines = []
        for msg in history:
            prefix = "Customer" if msg["role"] == "user" else "Agent"
            lines.append(f"{prefix}: {msg['content']}")
        return "\n".join(lines)

# Global singleton
chat_history = ChatHistoryStore()
