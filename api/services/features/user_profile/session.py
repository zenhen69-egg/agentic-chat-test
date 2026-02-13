import uuid
from api.schemas.profile import UserProfileUpdate

SESSION_MEMORY: dict[str, dict[str, object]] = {}


def ensure_session_id(session_id: str | None) -> str:
    if session_id:
        return session_id
    return str(uuid.uuid4())


def get_session_state(session_id: str) -> dict[str, object]:
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = {
            "history": [],
            "profile": UserProfileUpdate(),
            "awaiting_confirmation": False,
        }
    return SESSION_MEMORY[session_id]
