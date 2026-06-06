import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class EmergencyTarget(Base):
    __tablename__ = "emergency_targets"
    __table_args__ = (
        UniqueConstraint(
            "emergency_event_id",
            "display_id",
            "display_group_id",
            "target_type",
            name="uq_emergency_target",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    emergency_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergency_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    display_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("displays.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    display_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("display_groups.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    emergency_event: Mapped["EmergencyEvent"] = relationship(back_populates="targets")
    display: Mapped["Display | None"] = relationship(back_populates="emergency_targets")
    display_group: Mapped["DisplayGroup | None"] = relationship(back_populates="emergency_targets")
