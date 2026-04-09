from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class Group(str, Enum):
    A = "A"
    B = "B"


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    ARTICLE_TIME = "article_time"
    SESSION_END = "session_end"


# --- Requests ---

class EventIn(BaseModel):
    event_type: EventType
    article_id: Optional[str] = None
    article_position: Optional[int] = None
    value: Optional[float] = None

    @field_validator("article_id")
    @classmethod
    def click_requires_article(cls, v, info):
        et = info.data.get("event_type")
        if et in (EventType.CLICK, EventType.ARTICLE_TIME) and not v:
            raise ValueError(f"{et} events require article_id")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v, info):
        et = info.data.get("event_type")
        if et == EventType.SCROLL and v is not None and not (0 <= v <= 100):
            raise ValueError("scroll depth must be between 0 and 100")
        if et in (EventType.ARTICLE_TIME, EventType.SESSION_END) and v is not None and v < 0:
            raise ValueError("duration must be non-negative")
        return v


# --- Responses ---

class AssignResponse(BaseModel):
    user_id: str
    group: Group
    is_new: bool


class ArticleCard(BaseModel):
    article_id: str
    headline: str
    teaser: str
    full_summary: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    article_position: int


class ArticlesResponse(BaseModel):
    articles: list[ArticleCard]


class ArticleDetail(BaseModel):
    article_id: str
    headline: str
    full_content: str
    author: str
    date: str
    category: str
    image_url: Optional[str] = None
    source_url: Optional[str] = None


class EventCreated(BaseModel):
    event_id: int
    status: str = "ok"
