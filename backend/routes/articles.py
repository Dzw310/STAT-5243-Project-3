from fastapi import APIRouter, Depends, HTTPException

from database import db_session
from dependencies import get_current_user
from models import ArticleCard, ArticleDetail, ArticlesResponse, Group

router = APIRouter()


@router.get("/articles", response_model=ArticlesResponse)
def list_articles(user: dict = Depends(get_current_user)) -> ArticlesResponse:
    group = user["group"]

    with db_session() as conn:
        rows = conn.execute(
            "SELECT article_id, headline, teaser, full_summary, author, date, "
            "category, image_url, source_url FROM articles ORDER BY rowid"
        ).fetchall()

    cards = []
    for i, row in enumerate(rows, start=1):
        card = ArticleCard(
            article_id=row["article_id"],
            headline=row["headline"],
            teaser=row["teaser"],
            image_url=row["image_url"],
            source_url=row["source_url"],
            article_position=i,
        )
        if group == Group.A:
            card.full_summary = row["full_summary"]
            card.author = row["author"]
            card.date = row["date"]
            card.category = row["category"]

        cards.append(card)

    return ArticlesResponse(articles=cards)


@router.get("/articles/{article_id}", response_model=ArticleDetail)
def get_article(
    article_id: str,
    _user: dict = Depends(get_current_user),
) -> ArticleDetail:
    with db_session() as conn:
        row = conn.execute(
            "SELECT article_id, headline, full_content, author, date, "
            "category, image_url, source_url FROM articles WHERE article_id = ?",
            (article_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleDetail(**dict(row))
