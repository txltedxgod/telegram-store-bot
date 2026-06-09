"""Declarative base for all ORM models."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class shared by every model in the project."""

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__} id={pk}>"
