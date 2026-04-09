from fastapi import APIRouter, Depends, Request

from database import db_session
from dependencies import get_current_user
from models import EventCreated, EventIn

router = APIRouter()


@router.post("/events", response_model=EventCreated)
def log_event(
    event: EventIn,
    request: Request,
    user: dict = Depends(get_current_user),
) -> EventCreated:
    with db_session() as conn:
        cursor = conn.execute(
            "INSERT INTO events (user_id, event_type, article_id, article_position, value) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                user["user_id"],
                event.event_type.value,
                event.article_id,
                event.article_position,
                event.value,
            ),
        )
        event_id = cursor.lastrowid

    return EventCreated(event_id=event_id)
