import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.display_template_repository import (
    get_display,
    assign_template_to_display,
    get_assigned_template,
    update_assigned_template,
)
from src.services.display_push import display_push_service

logger = logging.getLogger(__name__)


class DisplayNotFoundError(Exception):
    pass


class NoAssignedTemplateError(Exception):
    pass


class DisplayTemplateService:
    async def accept_template(self, db: AsyncSession, display_id: uuid.UUID, layout: dict):
        display = await get_display(db, display_id)
        if display is None:
            raise DisplayNotFoundError()

        template = await assign_template_to_display(db, display_id, layout)
        return template

    async def update_template(self, db: AsyncSession, display_id: uuid.UUID, layout: dict):
        template = await update_assigned_template(db, display_id, layout)
        if template is None:
            raise NoAssignedTemplateError()
        return template

    async def send_template(self, db: AsyncSession, display_id: uuid.UUID) -> bool:
        template = await get_assigned_template(db, display_id)
        if template is None:
            raise NoAssignedTemplateError()
        delivered = await display_push_service.push_display_state(db, display_id)
        return delivered


display_template_service = DisplayTemplateService()
