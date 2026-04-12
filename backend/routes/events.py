from fastapi import APIRouter, Depends, Request

import database as db
from dependencies import get_current_user
from models import EventCreated, EventIn

router = APIRouter()


@router.post("/events", response_model=EventCreated)
def log_event(
    event: EventIn,
    request: Request,
    user: dict = Depends(get_current_user),
) -> EventCreated:
    result = db.insert(
        "events",
        {
            "user_id": user["user_id"],
            "event_type": event.event_type.value,
            "article_id": event.article_id,
            "article_position": event.article_position,
            "value": event.value,
        },
        returning="event_id",
    )

    return EventCreated(event_id=result["event_id"])
