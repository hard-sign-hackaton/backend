from __future__ import annotations

from typing import Optional
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DisplayBase(BaseModel):
    title: str
    location: Optional[str] = None
    pairing_code: str
    ujin_complex_id: int
    ujin_building_id: int


class DisplayCreate(DisplayBase):
    pass


class DisplayUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    pairing_code: Optional[str] = None
    ujin_complex_id: Optional[int] = None
    ujin_building_id: Optional[int] = None
    last_seen_at: Optional[datetime] = None


class DisplayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    location: Optional[str] = None
    status: str
    pairing_code: str
    ujin_complex_id: int
    ujin_building_id: int
    last_seen_at: Optional[datetime] = None
