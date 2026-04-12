"""Supabase PostgREST client for Lion's Feed.

Uses the Supabase REST API over HTTPS instead of direct PostgreSQL,
avoiding IPv6 connectivity issues on networks without IPv6 support.
"""

from __future__ import annotations

import httpx

from config import settings

_BASE_URL = f"{settings.supabase_url}/rest/v1"
_HEADERS = {
    "apikey": settings.supabase_key,
    "Authorization": f"Bearer {settings.supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _client() -> httpx.Client:
    return httpx.Client(base_url=_BASE_URL, headers=_HEADERS, timeout=10.0)


def init_db() -> None:
    """Verify connectivity — tables are created via Supabase migration."""
    with _client() as c:
        resp = c.get("/articles", params={"select": "article_id", "limit": "1"})
        resp.raise_for_status()


def select(
    table: str,
    columns: str = "*",
    filters: dict[str, str] | None = None,
    order: str | None = None,
) -> list[dict]:
    params: dict[str, str] = {"select": columns}
    if filters:
        params.update(filters)
    if order:
        params["order"] = order
    with _client() as c:
        resp = c.get(f"/{table}", params=params)
        resp.raise_for_status()
        return resp.json()


def select_one(
    table: str,
    columns: str = "*",
    filters: dict[str, str] | None = None,
) -> dict | None:
    rows = select(table, columns, filters)
    return rows[0] if rows else None


def insert(table: str, data: dict, returning: str | None = None) -> dict | None:
    headers = dict(_HEADERS)
    params = {}
    if returning:
        params["select"] = returning
    with _client() as c:
        resp = c.post(f"/{table}", json=data, params=params, headers=headers)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None


def insert_many(table: str, data: list[dict]) -> None:
    with _client() as c:
        resp = c.post(f"/{table}", json=data)
        resp.raise_for_status()


def upsert(table: str, data: dict) -> None:
    headers = {**_HEADERS, "Prefer": "resolution=merge-duplicates"}
    with _client() as c:
        resp = c.post(f"/{table}", json=data, headers=headers)
        resp.raise_for_status()


def delete(table: str, filters: dict[str, str]) -> None:
    headers = {**_HEADERS}
    headers.pop("Prefer", None)
    with _client() as c:
        resp = c.delete(f"/{table}", params=filters, headers=headers)
        resp.raise_for_status()
