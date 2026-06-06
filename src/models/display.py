import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Display(Base):
    __tablename__ = "displays"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="offline", index=True)
    pairing_code: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    ujin_complex_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ujin_building_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    group_members: Mapped[list["DisplayGroupMember"]] = relationship(back_populates="display")
    template_assignment: Mapped["DisplayTemplateAssignment | None"] = relationship(
        back_populates="display",
        uselist=False,
    )
    emergency_targets: Mapped[list["EmergencyTarget"]] = relationship(back_populates="display")
