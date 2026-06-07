import logging
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Template
from src.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)


async def create_template(db: AsyncSession, payload: TemplateCreate) -> Template:
    template = Template(
        title=payload.title,
        theme=payload.theme,
        grid_columns=payload.grid_columns,
        background_url=payload.background_url,
        layout=payload.layout or {},
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_template(db: AsyncSession, template_id: uuid.UUID) -> Optional[Template]:
    return await db.get(Template, template_id)


async def list_templates(db: AsyncSession) -> List[Template]:
    result = await db.execute(select(Template).order_by(Template.created_at.desc()))
    return result.scalars().all()


async def update_template(db: AsyncSession, template_id: uuid.UUID, payload: TemplateUpdate) -> Optional[Template]:
    template = await db.get(Template, template_id)
    if template is None:
        return None
    try:
        data = payload.model_dump(exclude_unset=True)
    except Exception:
        data = {k: v for k, v in payload.__dict__.items() if v is not None}
    for key, value in data.items():
        setattr(template, key, value)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template_id: uuid.UUID) -> bool:
    template = await db.get(Template, template_id)
    if template is None:
        return False
    await db.delete(template)
    await db.commit()
    return True

