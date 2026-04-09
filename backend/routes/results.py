import csv
import io
import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from database import db_session
from dependencies import require_export_key

router = APIRouter()

_USERS_COLS = ["user_id", "group", "assigned_at", "user_agent"]
_EVENTS_COLS = ["event_id", "user_id", "event_type", "article_id", "article_position", "value", "timestamp"]
_ARTICLES_COLS = ["article_id", "headline", "teaser", "full_summary", "author", "date", "category", "image_url", "source_url"]


def _query_to_csv(conn, sql: str, fieldnames: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in conn.execute(sql).fetchall():
        writer.writerow({k: row[k] for k in fieldnames})
    return buf.getvalue()


@router.get("/results")
def export_results(_key: str = Depends(require_export_key)) -> StreamingResponse:
    zip_buf = io.BytesIO()

    with db_session() as conn, zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "users.csv",
            _query_to_csv(
                conn,
                'SELECT user_id, "group" AS "group", assigned_at, user_agent FROM users',
                _USERS_COLS,
            ),
        )
        zf.writestr(
            "events.csv",
            _query_to_csv(
                conn,
                "SELECT event_id, user_id, event_type, article_id, article_position, value, timestamp FROM events",
                _EVENTS_COLS,
            ),
        )
        zf.writestr(
            "articles.csv",
            _query_to_csv(
                conn,
                "SELECT article_id, headline, teaser, full_summary, author, date, category, image_url, source_url FROM articles",
                _ARTICLES_COLS,
            ),
        )

    zip_buf.seek(0)
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=lions_feed_data.zip"},
    )
