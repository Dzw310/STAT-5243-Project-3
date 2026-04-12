import csv
import io
import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

import database as db
from dependencies import require_export_key

router = APIRouter()

_USERS_COLS = ["user_id", "group", "assigned_at", "user_agent"]
_EVENTS_COLS = ["event_id", "user_id", "event_type", "article_id", "article_position", "value", "timestamp"]
_ARTICLES_COLS = ["article_id", "headline", "teaser", "full_summary", "author", "date", "category", "image_url", "source_url"]


def _rows_to_csv(rows: list[dict], fieldnames: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k) for k in fieldnames})
    return buf.getvalue()


@router.get("/results")
def export_results(_key: str = Depends(require_export_key)) -> StreamingResponse:
    zip_buf = io.BytesIO()

    users = db.select("users", columns=",".join(_USERS_COLS))
    events = db.select("events", columns=",".join(_EVENTS_COLS))
    articles = db.select("articles", columns=",".join(_ARTICLES_COLS), order="article_id")

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("users.csv", _rows_to_csv(users, _USERS_COLS))
        zf.writestr("events.csv", _rows_to_csv(events, _EVENTS_COLS))
        zf.writestr("articles.csv", _rows_to_csv(articles, _ARTICLES_COLS))

    zip_buf.seek(0)
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=lions_feed_data.zip"},
    )
