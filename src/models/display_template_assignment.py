import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class DisplayTemplateAssignment(Base):
    __tablename__ = "display_template_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("displays.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    display: Mapped["Display"] = relationship(back_populates="template_assignment")
    template: Mapped["Template"] = relationship(back_populates="display_assignments")
