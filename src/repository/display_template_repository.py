import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Display, Template, DisplayTemplateAssignment

logger = logging.getLogger(__name__)


async def get_display(db: AsyncSession, display_id: uuid.UUID) -> Optional[Display]:
    return await db.get(Display, display_id)


async def assign_template_to_display(db: AsyncSession, display_id: uuid.UUID, layout: dict) -> Template:
    template = Template(layout=layout)
    db.add(template)
    await db.flush()

    result = await db.execute(select(DisplayTemplateAssignment).where(DisplayTemplateAssignment.display_id == display_id))
    assignment = result.scalar_one_or_none()
    if assignment:
        assignment.template_id = template.id
        assignment.assigned_at = datetime.now(timezone.utc)
    else:
        assignment = DisplayTemplateAssignment(display_id=display_id, template_id=template.id)
        db.add(assignment)

    await db.commit()
    await db.refresh(template)
    logger.info("Темплейт привязан %s к %s", template.id, display_id)
    return template


async def get_assigned_template(db: AsyncSession, display_id: uuid.UUID) -> Optional[Template]:
    result = await db.execute(select(DisplayTemplateAssignment).where(DisplayTemplateAssignment.display_id == display_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        return None
    return await db.get(Template, assignment.template_id)


async def update_assigned_template(db: AsyncSession, display_id: uuid.UUID, layout: dict) -> Optional[Template]:
    result = await db.execute(select(DisplayTemplateAssignment).where(DisplayTemplateAssignment.display_id == display_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        return None

    template = await db.get(Template, assignment.template_id)
    if template is None:
        return None

    template.layout = layout
    db.add(template)
    await db.commit()
    await db.refresh(template)
    logger.info("Темплей изменен %s для %s", template.id, display_id)
    return template
