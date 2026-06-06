import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import (
    Display,
    DisplayGroupMember,
    DisplayTemplateAssignment,
    EmergencyEvent,
    EmergencyTarget,
    StaticContent,
    Template,
    TemplateWidget,
)


async def get_display_state(db: AsyncSession, display_id: uuid.UUID) -> dict | None:
    display = await db.get(Display, display_id)
    if display is None:
        return None

    template = await _get_template_state(db, display_id)
    emergency = await _get_active_emergency_state(db, display_id)

    return {
        "type": "display_state",
        "display": _serialize_display(display),
        "template": template,
        "emergency": emergency,
    }


async def _get_template_state(db: AsyncSession, display_id: uuid.UUID) -> dict | None:
    assignment_result = await db.execute(
        select(DisplayTemplateAssignment).where(
            DisplayTemplateAssignment.display_id == display_id,
        )
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment is None:
        return None

    template = await db.get(Template, assignment.template_id)
    if template is None:
        return None

    widgets_result = await db.execute(
        select(TemplateWidget, StaticContent)
        .outerjoin(StaticContent, TemplateWidget.static_content_id == StaticContent.id)
        .where(TemplateWidget.template_id == template.id)
        .order_by(TemplateWidget.sort_order, TemplateWidget.y, TemplateWidget.x)
    )

    widgets = [
        _serialize_widget(widget, static_content)
        for widget, static_content in widgets_result.all()
    ]

    return {
        "id": str(template.id),
        "title": template.title,
        "theme": template.theme,
        "grid_columns": template.grid_columns,
        "background_url": template.background_url,
        "layout": template.layout,
        "assigned_at": _to_iso(assignment.assigned_at),
        "widgets": widgets,
    }


async def _get_active_emergency_state(db: AsyncSession, display_id: uuid.UUID) -> dict | None:
    now = datetime.now(timezone.utc)
    display_group_ids = select(DisplayGroupMember.display_group_id).where(
        DisplayGroupMember.display_id == display_id,
    )

    result = await db.execute(
        select(EmergencyEvent)
        .join(EmergencyTarget, EmergencyTarget.emergency_event_id == EmergencyEvent.id)
        .where(
            EmergencyEvent.status == "active",
            EmergencyEvent.starts_at <= now,
            or_(EmergencyEvent.ends_at.is_(None), EmergencyEvent.ends_at > now),
            or_(
                EmergencyTarget.target_type == "all",
                EmergencyTarget.display_id == display_id,
                and_(
                    EmergencyTarget.target_type == "group",
                    EmergencyTarget.display_group_id.in_(display_group_ids),
                ),
            ),
        )
        .order_by(EmergencyEvent.priority.desc(), EmergencyEvent.created_at.desc())
        .limit(1)
    )
    emergency = result.scalar_one_or_none()
    if emergency is None:
        return None

    return {
        "id": str(emergency.id),
        "message": emergency.message,
        "priority": emergency.priority,
        "status": emergency.status,
        "starts_at": _to_iso(emergency.starts_at),
        "ends_at": _to_iso(emergency.ends_at),
        "created_at": _to_iso(emergency.created_at),
        "reset_at": _to_iso(emergency.reset_at),
    }


def _serialize_display(display: Display) -> dict:
    return {
        "id": str(display.id),
        "title": display.title,
        "location": display.location,
        "status": display.status,
        "ujin_complex_id": display.ujin_complex_id,
        "ujin_building_id": display.ujin_building_id,
        "last_seen_at": _to_iso(display.last_seen_at),
    }


def _serialize_widget(widget: TemplateWidget, static_content: StaticContent | None) -> dict:
    return {
        "id": str(widget.id),
        "type": widget.type,
        "settings": widget.settings,
        "position": {
            "x": widget.x,
            "y": widget.y,
            "w": widget.w,
            "h": widget.h,
        },
        "sort_order": widget.sort_order,
        "static_content": _serialize_static_content(static_content),
    }


def _serialize_static_content(static_content: StaticContent | None) -> dict | None:
    if static_content is None:
        return None

    return {
        "id": str(static_content.id),
        "title": static_content.title,
        "content_type": static_content.content_type,
        "body": static_content.body,
        "media_url": static_content.media_url,
        "valid_from": _to_iso(static_content.valid_from),
        "valid_to": _to_iso(static_content.valid_to),
    }


def _to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
