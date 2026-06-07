import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Keep a single JSONB column `layout` that carries all frontend-provided template data.
    layout: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    widgets: Mapped[list["TemplateWidget"]] = relationship(back_populates="template")
    display_assignments: Mapped[list["DisplayTemplateAssignment"]] = relationship(
        back_populates="template",
    )

    # Provide convenient accessors for legacy fields by reading from `layout`.
    @property
    def title(self) -> str | None:
        if isinstance(self.layout, dict):
            return self.layout.get("title")
        return None

    @property
    def theme(self) -> str:
        if isinstance(self.layout, dict):
            return self.layout.get("theme") or "light"
        return "light"

    @property
    def grid_columns(self) -> int:
        if isinstance(self.layout, dict):
            try:
                gc = self.layout.get("grid_columns")
                if gc is None:
                    return 4
                return int(gc)
            except Exception:
                return 4
        return 4

    @property
    def background_url(self) -> str | None:
        if isinstance(self.layout, dict):
            return self.layout.get("background_url")
        return None
