from models.session import Session

_sessions: dict[str, Session] = {}


def save(session: Session) -> Session:
    _sessions[session.id] = session
    return session


def get(session_id: str) -> Session | None:
    return _sessions.get(session_id)
