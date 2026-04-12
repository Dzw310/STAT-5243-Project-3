from __future__ import annotations

from fastapi import Header, HTTPException, Request

from itsdangerous import URLSafeSerializer, BadSignature

from config import settings
import database as db

_signer = URLSafeSerializer(settings.secret_key, salt="lions-feed-uid")


def sign_user_id(user_id: str) -> str:
    return _signer.dumps(user_id)


def unsign_user_id(token: str) -> str | None:
    try:
        return _signer.loads(token)
    except BadSignature:
        return None


def read_user_id_from_cookie(request: Request) -> str | None:
    token = request.cookies.get(settings.cookie_name)
    if not token:
        return None
    return unsign_user_id(token)


def get_current_user(request: Request) -> dict:
    user_id = read_user_id_from_cookie(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="No valid session cookie")
    row = db.select_one(
        "users",
        columns="user_id,group",
        filters={"user_id": f"eq.{user_id}"},
    )
    if not row:
        raise HTTPException(status_code=401, detail="Unknown user")
    return {"user_id": row["user_id"], "group": row["group"]}


def require_export_key(x_export_key: str = Header(...)) -> str:
    if x_export_key != settings.export_key:
        raise HTTPException(status_code=403, detail="Invalid export key")
    return x_export_key
