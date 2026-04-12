"""
process_data.py — Clean and merge raw Lion's Feed A/B test data.

Reads the ZIP export from /api/results, computes per-user metrics,
filters bot traffic, and outputs analysis/clean_data.csv.
"""

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent
BOT_PATTERNS = [
    "bot", "crawl", "spider", "headless", "phantom", "selenium", "puppeteer",
]


def load_zip(zip_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    with zipfile.ZipFile(zip_path) as zf:
        users = pd.read_csv(io.BytesIO(zf.read("users.csv")))
        events = pd.read_csv(io.BytesIO(zf.read("events.csv")))
        articles = pd.read_csv(io.BytesIO(zf.read("articles.csv")))
    return users, events, articles


def filter_bots(users: pd.DataFrame) -> pd.DataFrame:
    pattern = "|".join(BOT_PATTERNS)
    is_bot = users["user_agent"].str.lower().str.contains(pattern, na=False)
    removed = is_bot.sum()
    if removed > 0:
        print(f"Filtered {removed} bot/crawler sessions")
    return users[~is_bot].copy()


def compute_user_metrics(
    users: pd.DataFrame, events: pd.DataFrame, articles: pd.DataFrame
) -> pd.DataFrame:
    merged = events.merge(users[["user_id", "group"]], on="user_id", how="inner")

    clicks = (
        merged[merged["event_type"] == "click"]
        .groupby("user_id")
        .size()
        .rename("total_clicks")
    )

    article_views = (
        merged[merged["event_type"] == "page_view"]
        .groupby("user_id")
        .size()
        .rename("page_views")
    )

    scroll_depth = (
        merged[merged["event_type"] == "scroll"]
        .groupby("user_id")["value"]
        .max()
        .rename("max_scroll_depth")
    )

    article_time = (
        merged[merged["event_type"] == "article_time"]
        .groupby("user_id")["value"]
        .mean()
        .rename("avg_article_time")
    )

    session_time = (
        merged[merged["event_type"] == "session_end"]
        .groupby("user_id")["value"]
        .max()
        .rename("session_duration")
    )

    card_impressions = (
        merged[merged["event_type"] == "card_impression"]
        .groupby("user_id")
        .size()
        .rename("card_impressions")
    )

    hover_time = (
        merged[merged["event_type"] == "card_hover"]
        .groupby("user_id")["value"]
        .mean()
        .rename("avg_hover_time")
    )

    metrics = users[["user_id", "group", "assigned_at"]].set_index("user_id")
    for col in [clicks, article_views, scroll_depth, article_time,
                session_time, card_impressions, hover_time]:
        metrics = metrics.join(col, how="left")

    metrics = metrics.fillna({
        "total_clicks": 0,
        "page_views": 0,
        "max_scroll_depth": 0,
        "card_impressions": 0,
    })

    # Total articles shown (from articles table, not just clicked ones)
    n_articles = max(len(articles), 1)

    metrics["ctr"] = metrics["total_clicks"] / n_articles

    # Impression-to-click rate: of cards seen, what fraction were clicked
    metrics["impression_ctr"] = metrics["total_clicks"] / metrics["card_impressions"].replace(0, pd.NA)

    return metrics.reset_index()


def compute_click_level(
    users: pd.DataFrame, events: pd.DataFrame, articles: pd.DataFrame
) -> pd.DataFrame:
    """Create article-level click data for mixed-effects logistic regression."""
    click_events = events[events["event_type"] == "click"][
        ["user_id", "article_id"]
    ].drop_duplicates(subset=["user_id", "article_id"])

    # Assign position from article order (consistent for all users)
    articles_with_pos = articles[["article_id", "category"]].copy()
    articles_with_pos["article_position"] = range(1, len(articles_with_pos) + 1)

    all_combos = (
        users[["user_id", "group"]]
        .merge(articles_with_pos, how="cross")
    )

    click_level = all_combos.merge(
        click_events.assign(clicked=1),
        on=["user_id", "article_id"],
        how="left",
    )
    click_level["clicked"] = click_level["clicked"].fillna(0).astype(int)

    return click_level


def main() -> None:
    zip_path = sys.argv[1] if len(sys.argv) > 1 else str(DATA_DIR / "lions_feed_data.zip")
    print(f"Loading data from {zip_path}")

    users, events, articles = load_zip(zip_path)
    print(f"Raw: {len(users)} users, {len(events)} events, {len(articles)} articles")

    users = filter_bots(users)
    print(f"After bot filter: {len(users)} users")

    # Drop events from filtered users
    events = events[events["user_id"].isin(users["user_id"])]

    # Per-user summary
    user_metrics = compute_user_metrics(users, events, articles)
    user_metrics.to_csv(DATA_DIR / "clean_data.csv", index=False)
    print(f"Wrote clean_data.csv ({len(user_metrics)} rows)")

    # Article-level click data for mixed-effects model
    click_level = compute_click_level(users, events, articles)
    click_level.to_csv(DATA_DIR / "click_level.csv", index=False)
    print(f"Wrote click_level.csv ({len(click_level)} rows)")

    # Summary stats
    for g in ["A", "B"]:
        subset = user_metrics[user_metrics["group"] == g]
        print(f"\nGroup {g} (n={len(subset)}):")
        print(f"  Mean CTR: {subset['ctr'].mean():.3f}")
        print(f"  Mean clicks: {subset['total_clicks'].mean():.1f}")
        print(f"  Mean scroll depth: {subset['max_scroll_depth'].mean():.0f}%")
        print(f"  Mean card impressions: {subset['card_impressions'].mean():.1f}")
        print(f"  Mean hover time: {subset['avg_hover_time'].mean():.2f}s")
        print(f"  Mean session duration: {subset['session_duration'].mean():.1f}s")


if __name__ == "__main__":
    main()
