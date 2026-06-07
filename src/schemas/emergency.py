import uuid

from pydantic import BaseModel, Field


class CreateEmergencyRequest(BaseModel):
    message: str
    duration_seconds: int
    display_id: uuid.UUID | None = None
    display_group_id: uuid.UUID | None = None
