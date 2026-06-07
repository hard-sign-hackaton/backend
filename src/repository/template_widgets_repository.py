import logging
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import TemplateWidget
from src.schemas.template import (
    TemplateWidgetCreate,
    TemplateWidgetUpdate,
)

logger = logging.getLogger(__name__)

async def create_widget(db: AsyncSession, template_id: uuid.UUID, payload: TemplateWidgetCreate) -> TemplateWidget:
    widget = TemplateWidget(
        template_id=template_id,
        type=payload.type,
        settings=payload.settings,
        x=payload.x,
        y=payload.y,
        w=payload.w,
        h=payload.h,
        sort_order=payload.sort_order,
        static_content_id=payload.static_content_id,
    )
    db.add(widget)
    await db.commit()
    await db.refresh(widget)
    return widget


async def list_widgets(db: AsyncSession, template_id: uuid.UUID) -> List[TemplateWidget]:
    result = await db.execute(
        select(TemplateWidget)
        .where(TemplateWidget.template_id == template_id)
        .order_by(TemplateWidget.sort_order, TemplateWidget.y, TemplateWidget.x)
    )
    return result.scalars().all()


async def get_widget(db: AsyncSession, widget_id: uuid.UUID) -> Optional[TemplateWidget]:
    return await db.get(TemplateWidget, widget_id)


async def update_widget(db: AsyncSession, widget_id: uuid.UUID, payload: TemplateWidgetUpdate) -> Optional[TemplateWidget]:
    widget = await db.get(TemplateWidget, widget_id)
    if widget is None:
        return None
    try:
        data = payload.model_dump(exclude_unset=True)
    except Exception:
        data = {k: v for k, v in payload.__dict__.items() if v is not None}
    for key, value in data.items():
        setattr(widget, key, value)
    db.add(widget)
    await db.commit()
    await db.refresh(widget)
    return widget


async def delete_widget(db: AsyncSession, widget_id: uuid.UUID) -> bool:
    widget = await db.get(TemplateWidget, widget_id)
    if widget is None:
        return False
    await db.delete(widget)
    await db.commit()
    return True
