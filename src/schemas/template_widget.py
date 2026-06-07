import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TemplateWidgetBase(BaseModel):
    type: str
    settings: Dict[str, Any] = Field(default_factory=dict)
    x: int = 0
    y: int = 0
    w: int = 1
    h: int = 1
    sort_order: int = 0
    static_content_id: Optional[uuid.UUID] = None


class TemplateWidgetCreate(TemplateWidgetBase):
    pass


class TemplateWidgetUpdate(BaseModel):
    type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    x: Optional[int] = None
    y: Optional[int] = None
    w: Optional[int] = None
    h: Optional[int] = None
    sort_order: Optional[int] = None
    static_content_id: Optional[uuid.UUID] = None


class TemplateWidgetOut(TemplateWidgetBase):
    id: uuid.UUID
    template_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True