import random
import uuid

from fastapi import APIRouter, Request, Response

from config import settings
from database import db_session
from dependencies import read_user_id_from_cookie, sign_user_id
from models import AssignResponse, Group

router = APIRouter()


@router.get("/assign", response_model=AssignResponse)
def assign_user(request: Request, response: Response) -> AssignResponse:
    existing_uid = read_user_id_from_cookie(request)

    if existing_uid:
        with db_session() as conn:
            row = conn.execute(
                'SELECT user_id, "group" FROM users WHERE user_id = ?',
                (existing_uid,),
            ).fetchone()
        if row:
            return AssignResponse(
                user_id=row["user_id"],
                group=row["group"],
                is_new=False,
            )

    user_id = str(uuid.uuid4())
    group = random.choice([Group.A, Group.B])
    user_agent = request.headers.get("user-agent", "")

    with db_session() as conn:
        conn.execute(
            'INSERT INTO users (user_id, "group", user_agent) VALUES (?, ?, ?)',
            (user_id, group.value, user_agent),
        )

    signed = sign_user_id(user_id)
    response.set_cookie(
        key=settings.cookie_name,
        value=signed,
        max_age=settings.cookie_max_age,
        httponly=True,
        samesite="lax",
    )

    return AssignResponse(user_id=user_id, group=group, is_new=True)
