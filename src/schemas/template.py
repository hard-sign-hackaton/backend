from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from schemas.template_widget import TemplateWidgetOut



class TemplateBase(BaseModel):
    title: str
    theme: str = "light"
    grid_columns: int = 4
    background_url: Optional[str] = None
    layout: Dict[str, Any] = Field(default_factory=dict)


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    theme: Optional[str] = None
    grid_columns: Optional[int] = None
    background_url: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None


class TemplateOut(TemplateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    widgets: List[TemplateWidgetOut] = []

    class Config:
        from_attributes = True
