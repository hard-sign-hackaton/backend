from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Display


async def create_display(
    db: AsyncSession,
    *,
    title: str,
    location: str | None,
    pairing_code: str,
    ujin_complex_id: int,
    ujin_building_id: int,
) -> Display:
    display = Display(
        title=title,
        location=location,
        pairing_code=pairing_code,
        ujin_complex_id=ujin_complex_id,
        ujin_building_id=ujin_building_id,
    )
    db.add(display)
    await db.commit()
    await db.refresh(display)
    return display


async def get_display(db: AsyncSession, display_id: UUID) -> Display | None:
    return await db.get(Display, display_id)


async def list_displays(db: AsyncSession, limit: int = 100, offset: int = 0) -> List[Display]:
    result = await db.execute(
        select(Display).order_by(Display.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all()


async def update_display(db: AsyncSession, display_id: UUID, updates: dict) -> Display | None:
    display = await db.get(Display, display_id)
    if display is None:
        return None
    for key, value in updates.items():
        if hasattr(display, key):
            setattr(display, key, value)
    await db.commit()
    await db.refresh(display)
    return display


async def delete_display(db: AsyncSession, display_id: UUID) -> bool:
    display = await db.get(Display, display_id)
    if display is None:
        return False
    await db.delete(display)
    await db.commit()
    return True
