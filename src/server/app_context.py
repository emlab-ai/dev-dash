
from contextvars import ContextVar
from sqlalchemy.orm import Session
from db.model.user import User

context_session: ContextVar[Session] = ContextVar("session")
context_trace_id: ContextVar[str] = ContextVar("trace_id")
context_user: ContextVar[User] = ContextVar("user")
