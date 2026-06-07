from __future__ import annotations

import logging
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.display_repository import (
    create_display as repo_create_display,
    get_display as repo_get_display,
    list_displays as repo_list_displays,
    update_display as repo_update_display,
    delete_display as repo_delete_display,
)

logger = logging.getLogger(__name__)


class DisplayNotFoundError(Exception):
    pass


class DisplayService:
    async def create_display(self, db: AsyncSession, payload) -> dict:
        display = await repo_create_display(
            db,
            title=payload.title,
            location=payload.location,
            pairing_code=payload.pairing_code,
            ujin_complex_id=payload.ujin_complex_id,
            ujin_building_id=payload.ujin_building_id,
        )
        return self._serialize_display(display)

    async def list_displays(self, db: AsyncSession, limit: int = 100, offset: int = 0) -> List[dict]:
        displays = await repo_list_displays(db, limit=limit, offset=offset)
        return [self._serialize_display(d) for d in displays]

    async def get_display(self, db: AsyncSession, display_id: UUID) -> dict | None:
        d = await repo_get_display(db, display_id)
        if d is None:
            return None
        return self._serialize_display(d)

    async def update_display(self, db: AsyncSession, display_id: UUID, updates) -> dict:
        data = updates.dict(exclude_unset=True) if hasattr(updates, "dict") else dict(updates)
        d = await repo_update_display(db, display_id, data)
        if d is None:
            raise DisplayNotFoundError()
        return self._serialize_display(d)

    async def delete_display(self, db: AsyncSession, display_id: UUID) -> None:
        ok = await repo_delete_display(db, display_id)
        if not ok:
            raise DisplayNotFoundError()

    def _serialize_display(self, display) -> dict:
        return {
            "id": str(display.id),
            "title": display.title,
            "location": display.location,
            "status": display.status,
            "pairing_code": display.pairing_code,
            "ujin_complex_id": display.ujin_complex_id,
            "ujin_building_id": display.ujin_building_id,
            "last_seen_at": display.last_seen_at.isoformat() if getattr(display, "last_seen_at", None) is not None else None,
        }


display_service = DisplayService()
