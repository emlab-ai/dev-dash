
from contextvars import ContextVar
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.model.user import User

context_session: ContextVar[Session | None] = ContextVar("session")
context_async_session: ContextVar[AsyncSession | None] = ContextVar("async_session")
context_trace_id: ContextVar[str] = ContextVar("trace_id")
context_user: ContextVar[User] = ContextVar("user")
