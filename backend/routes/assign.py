import random
import uuid

from fastapi import APIRouter, Request, Response

from config import settings
import database as db
from dependencies import read_user_id_from_cookie, sign_user_id
from models import AssignResponse, Group

router = APIRouter()


@router.get("/assign", response_model=AssignResponse)
def assign_user(request: Request, response: Response) -> AssignResponse:
    existing_uid = read_user_id_from_cookie(request)

    if existing_uid:
        row = db.select_one(
            "users",
            columns="user_id,group",
            filters={"user_id": f"eq.{existing_uid}"},
        )
        if row:
            return AssignResponse(
                user_id=row["user_id"],
                group=row["group"],
                is_new=False,
            )

    user_id = str(uuid.uuid4())
    group = random.choice([Group.A, Group.B])
    user_agent = request.headers.get("user-agent", "")

    db.insert("users", {
        "user_id": user_id,
        "group": group.value,
        "user_agent": user_agent,
    })

    signed = sign_user_id(user_id)
    response.set_cookie(
        key=settings.cookie_name,
        value=signed,
        max_age=settings.cookie_max_age,
        httponly=True,
        samesite="lax",
    )

    return AssignResponse(user_id=user_id, group=group, is_new=True)
