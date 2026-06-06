import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class DisplayGroupMember(Base):
    __tablename__ = "display_group_members"
    __table_args__ = (
        UniqueConstraint("display_group_id", "display_id", name="uq_display_group_member"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("display_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    display_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("displays.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    display_group: Mapped["DisplayGroup"] = relationship(back_populates="members")
    display: Mapped["Display"] = relationship(back_populates="group_members")
