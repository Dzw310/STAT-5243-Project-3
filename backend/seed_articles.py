"""Seed the articles table with Columbia campus news.

Uses Tavily API if TAVILY_API_KEY is set; otherwise falls back to
hardcoded sample articles for development and testing.

Tavily pipeline: search (find URLs + images) → extract (clean article text).
"""

import hashlib
import json
import re
import sys

import httpx

from config import settings
from database import db_session, init_db

FALLBACK_ARTICLES = [
    {
        "headline": "Columbia Opens New Interdisciplinary Science Building on Manhattanville Campus",
        "teaser": "The state-of-the-art facility will house research labs spanning neuroscience, climate science, and data analytics.",
        "full_summary": "Columbia University has officially opened the doors to its newest academic building on the Manhattanville campus, a 450,000-square-foot facility designed to foster cross-disciplinary collaboration. The building features open-plan laboratories, shared equipment floors, and seminar spaces that bring together researchers from the sciences, engineering, and public health. University President Minouche Shafik called it a milestone in Columbia's commitment to tackling complex global challenges through integrated research.",
        "full_content": "Columbia University has officially opened the doors to its newest academic building on the Manhattanville campus, a 450,000-square-foot facility designed to foster cross-disciplinary collaboration.\n\nThe building features open-plan laboratories, shared equipment floors, and seminar spaces that bring together researchers from the sciences, engineering, and public health. University President Minouche Shafik called it \"a milestone in Columbia's commitment to tackling complex global challenges through integrated research.\"\n\nThe facility includes dedicated floors for neuroscience, climate modeling, and data analytics, with shared cores for microscopy, genomics, and high-performance computing. Architects from Renzo Piano Building Workshop designed the structure to maximize natural light and encourage informal interaction between research groups.\n\nGraduate students have already begun moving into the new spaces. \"Having climate scientists down the hall from data engineers changes the kinds of questions we can ask,\" said doctoral candidate Maria Torres.\n\nThe building is the latest addition to Columbia's Manhattanville expansion, which has transformed a stretch of upper Manhattan into a modern academic hub while preserving the neighborhood's historic character.",
        "author": "Sarah Chen",
        "date": "April 7, 2026",
        "category": "Campus Life",
        "image_url": "https://images.unsplash.com/photo-1562774053-701939374585?w=800&h=400&fit=crop",
        "source_url": "https://news.columbia.edu",
    },
    {
        "headline": "Student-Led Climate Initiative Wins National Sustainability Award",
        "teaser": "EcoLion, a Columbia student group, was recognized for reducing campus food waste by 40 percent.",
        "full_summary": "EcoLion, a student-run sustainability organization at Columbia University, has won the 2026 National Campus Sustainability Award for its innovative food waste reduction program. Over the past academic year, the group partnered with Columbia Dining to implement a composting and redistribution system that diverted over 200 tons of food waste from landfills. The initiative also includes a mobile app that alerts students to surplus meals available for free pickup across campus dining halls.",
        "full_content": "EcoLion, a student-run sustainability organization at Columbia University, has won the 2026 National Campus Sustainability Award for its innovative food waste reduction program.\n\nOver the past academic year, the group partnered with Columbia Dining to implement a composting and redistribution system that diverted over 200 tons of food waste from landfills. The initiative also includes a mobile app that alerts students to surplus meals available for free pickup across campus dining halls.\n\n\"We started with just five volunteers and a spreadsheet,\" said EcoLion president Jordan Kimura, a junior in the School of Engineering. \"Now we have 80 active members and real infrastructure.\"\n\nThe composting system processes organic waste from John Jay Dining Hall and Ferris Booth Commons, converting it into soil amendment used in the campus community garden. The redistribution app, built by CS students, has logged over 15,000 meal pickups since its September launch.\n\nColumbia's Office of Sustainability provided seed funding and helped navigate city composting regulations. The award committee cited EcoLion's replicable model as a key factor in its selection.",
        "author": "David Park",
        "date": "April 5, 2026",
        "category": "Academics",
        "image_url": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=800&h=400&fit=crop",
        "source_url": "https://news.columbia.edu",
    },
    {
        "headline": "Lions Baseball Clinches Ivy League Series Win Against Penn",
        "teaser": "Columbia won two of three games in Philadelphia to take the early conference lead.",
        "full_summary": "The Columbia Lions baseball team secured a crucial Ivy League series victory over the University of Pennsylvania this weekend, winning two of three games in Philadelphia. Junior pitcher Alex Morales threw seven strong innings in the opener, and the offense produced 14 runs across the final two games. The wins put Columbia atop the Ivy League standings with a 5-1 conference record heading into a home series against Dartmouth next weekend.",
        "full_content": "The Columbia Lions baseball team secured a crucial Ivy League series victory over the University of Pennsylvania this weekend, winning two of three games in Philadelphia.\n\nJunior pitcher Alex Morales threw seven strong innings in the opener, striking out nine and allowing just two earned runs in a 5-2 Columbia victory. \"Alex was in total command,\" said head coach Brett Boretti. \"He set the tone for the whole weekend.\"\n\nAfter dropping the second game 4-3 in extra innings, the Lions bounced back with a convincing 9-4 win in the finale. Sophomore outfielder James Washington led the offense with three hits including a two-run homer in the seventh inning.\n\nThe series win puts Columbia atop the Ivy League standings with a 5-1 conference record. The Lions return home to Robertson Field at Satow Stadium next weekend for a three-game set against Dartmouth.\n\n\"The guys showed real resilience after that tough loss in game two,\" Boretti said. \"That's the kind of character you need for a championship run.\"",
        "author": "Mike Reynolds",
        "date": "April 6, 2026",
        "category": "Sports",
        "image_url": "https://images.unsplash.com/photo-1508344928928-7165b67de128?w=800&h=400&fit=crop",
        "source_url": "https://gocolumbialions.com",
    },
    {
        "headline": "Columbia to Host International Forum on AI Ethics and Governance",
        "teaser": "The three-day conference will bring policymakers and researchers to campus in May.",
        "full_summary": "Columbia University will host a major international conference on artificial intelligence ethics and governance from May 15-17, organized by the Data Science Institute and the School of International and Public Affairs. The forum will convene over 200 researchers, policymakers, and industry leaders to discuss AI regulation, algorithmic fairness, and the societal impact of generative AI systems. Keynote speakers include former EU Digital Commissioner Margrethe Vestager and Turing Award winner Yoshua Bengio.",
        "full_content": "Columbia University will host a major international conference on artificial intelligence ethics and governance from May 15-17, organized jointly by the Data Science Institute and the School of International and Public Affairs.\n\nThe forum will convene over 200 researchers, policymakers, and industry leaders to discuss AI regulation, algorithmic fairness, and the societal impact of generative AI systems.\n\nKeynote speakers include former EU Digital Commissioner Margrethe Vestager and Turing Award winner Yoshua Bengio. Panel topics range from regulatory frameworks for foundation models to the use of AI in criminal justice and healthcare.\n\n\"We designed this conference to bridge the gap between technical AI research and public policy,\" said Professor Jeannette Wing, director of the Data Science Institute. \"Columbia is uniquely positioned at the intersection of these fields.\"\n\nThe conference will also feature a student poster session showcasing AI ethics research from across the university. Registration is open to Columbia affiliates at no cost, with limited seats available for external attendees.\n\nThe event follows Columbia's recent expansion of its AI curriculum, which now includes a cross-school minor in AI and Society available to undergraduates in all four schools.",
        "author": "Lisa Hernandez",
        "date": "April 3, 2026",
        "category": "Events",
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&h=400&fit=crop",
        "source_url": "https://datascience.columbia.edu",
    },
    {
        "headline": "Opinion: Why Columbia Should Expand Pass/Fail Options for Core Curriculum",
        "teaser": "A student argues that rigid grading in the Core discourages intellectual risk-taking.",
        "full_summary": "The Core Curriculum is supposed to be Columbia's great intellectual adventure — the shared experience that exposes every student to foundational texts, scientific reasoning, and artistic traditions. In practice, it has become another source of GPA anxiety.\n\nI've watched classmates sit silently through Literature Humanities discussions, not because they had nothing to say, but because they were afraid of saying something wrong.",
        "full_content": "The Core Curriculum is supposed to be Columbia's great intellectual adventure — the shared experience that exposes every student to foundational texts, scientific reasoning, and artistic traditions. In practice, it has become another source of GPA anxiety.\n\nI've watched classmates sit silently through Literature Humanities discussions, not because they had nothing to say, but because they were afraid of saying something wrong. I've seen friends choose their University Writing sections based on rumored grading curves rather than topic interest.\n\nThis is backwards. The Core should be the one place where students feel free to take intellectual risks.\n\nMy proposal is simple: allow students to designate one Core course per academic year as pass/fail, with the option exercised after the add/drop deadline but before midterms. This preserves academic rigor — you still need to pass — while removing the GPA penalty for genuine exploration.\n\nA survey I conducted with the Columbia College Student Council found that 62 percent of undergraduates have avoided participating in Core discussions specifically because of grading concerns. That's a failure of the system, not the students.\n\nOther elite universities have recognized this. MIT has a pass/no-record first semester. Stanford experimented with expanded pass/fail during the pandemic and kept elements of it.\n\nColumbia's Core is too important to let grading anxiety hollow it out.\n\nEmma Zhang is a senior in Columbia College majoring in Political Science and East Asian Studies.",
        "author": "Emma Zhang",
        "date": "April 4, 2026",
        "category": "Opinion",
        "image_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=400&fit=crop",
        "source_url": "https://www.columbiaspectator.com",
    },
    {
        "headline": "New Mental Health Center Opens Adjacent to Morningside Campus",
        "teaser": "The facility doubles Columbia's counseling capacity and offers walk-in appointments.",
        "full_summary": "Columbia University has opened a dedicated mental health and wellness center on Broadway near 114th Street, directly adjacent to the Morningside Heights campus. The new facility doubles the university's counseling capacity, adding 20 therapy rooms, group session spaces, and a crisis intervention suite. For the first time, students can access same-day walk-in appointments without a prior referral, addressing long-standing complaints about wait times at Counseling and Psychological Services.",
        "full_content": "Columbia University has opened a dedicated mental health and wellness center on Broadway near 114th Street, directly adjacent to the Morningside Heights campus.\n\nThe new facility doubles the university's counseling capacity, adding 20 therapy rooms, group session spaces, and a crisis intervention suite. For the first time, students can access same-day walk-in appointments without a prior referral.\n\n\"We heard students loud and clear,\" said Dr. Richard Eichler, vice president for student health. \"The number one complaint was wait times. This facility is our answer.\"\n\nThe center addresses long-standing complaints about Counseling and Psychological Services (CPS), where students previously reported waiting three to four weeks for an initial appointment. The new model offers walk-in hours every weekday from 9 AM to 5 PM, with evening hours on Tuesdays and Thursdays.\n\nIn addition to individual therapy, the center offers group programs for anxiety, grief, identity exploration, and academic stress. A meditation room and peer counseling lounge are open to all students without an appointment.\n\nThe Columbia College Student Council, which had advocated for expanded mental health resources for several years, praised the opening. \"This has been a top priority for student government since 2023,\" said council president Aiden Brooks.\n\nThe facility was funded through a combination of university capital funds and a $10 million gift from an anonymous alumnus.",
        "author": "Rachel Kim",
        "date": "April 8, 2026",
        "category": "Campus Life",
        "image_url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&h=400&fit=crop",
        "source_url": "https://news.columbia.edu",
    },
]


FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1562774053-701939374585?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1523050854058-8df90110c8f1?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=400&fit=crop",
]


def _article_id(headline: str) -> str:
    return hashlib.sha256(headline.encode()).hexdigest()[:12]


def _is_index_page(url: str, title: str) -> bool:
    """Filter out index/listing pages that aren't real articles."""
    skip_url_patterns = ["/tag/", "/category/", "/author/", "/page/", "/archive/", "/content/"]
    if any(p in url.lower() for p in skip_url_patterns):
        return True
    path = url.rstrip("/").split("//", 1)[-1]
    if path.count("/") <= 1:
        return True
    skip_titles = ["home", "search results", "archives", "all articles",
                   "columbia news", "campus & community", "campus and community"]
    if title.lower().strip() in skip_titles:
        return True
    return False


def _clean_content(raw: str, headline: str = "") -> str:
    """Strip web scraping noise from Tavily raw content."""
    text = raw

    # Remove markdown images: [![alt](src)](href) or ![alt](src)
    text = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # Remove markdown links but keep the display text: [text](url) → text
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)

    # Remove markdown bold/italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)

    # Remove markdown heading markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip accessibility / nav lines
        if "skip to main content" in stripped.lower():
            continue
        if "submit keywords" in stripped.lower():
            continue
        # Skip image captions
        if re.match(r"^Image \d+:?\s", stripped):
            continue
        # Skip social share artifacts
        if re.match(r"^(Share|Share to\s)", stripped):
            continue
        if "FacebookShare" in stripped or "TwitterInstagram" in stripped:
            continue
        # Skip standalone dates
        if re.match(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\s*$", stripped):
            continue
        # Skip nav-style headings
        if any(kw in stripped.lower() for kw in [
            "more stories", "contact us", "follow us", "related stories",
            "more campus", "read more", "sign up for", "subscribe",
        ]):
            continue
        # Skip lines that are just URLs or email addresses
        if re.match(r"^https?://\S+$", stripped) or re.match(r"^\S+@\S+\.\S+$", stripped):
            continue
        # Skip very short fragments (likely leftover nav text)
        if len(stripped) < 15 and not stripped.endswith("."):
            continue
        cleaned.append(stripped)

    text = "\n\n".join(cleaned)

    # Remove the headline if it appears at the start (extract API repeats it)
    if headline:
        for variant in [headline, headline.split("|")[0].strip()]:
            if text.startswith(variant):
                text = text[len(variant):].strip()

    # Remove " | Columbia News" or " | Office of..." suffixes from start
    text = re.sub(r"^\|\s*[^\n]+\n*", "", text)

    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _extract_teaser_from_raw(raw: str) -> str | None:
    match = re.search(r'"subheadlines"\s*:\s*\{\s*"basic"\s*:\s*"((?:\\"|[^"])*)"', raw)
    if not match:
        return None
    return match.group(1).replace('\\"', '"').strip()
    
def _extract_byline(content: str) -> tuple[str, str, str]:
    """Pull author and date from common byline patterns."""
    author = "Staff Reporter"
    date = "April 2026"
    # Pattern: "By Author Name • March 12, 2026 at 5:24 AM"
    byline = re.match(
        r"^By\s+(.+?)\s*[•·]\s*(\w+ \d{1,2},\s*\d{4})(?:\s+at\s+\d{1,2}:\d{2}\s*[AP]M)?",
        content,
    )
    if byline:
        author = byline.group(1).replace(",and ", ", ").replace(",", ", ").strip()
        date = byline.group(2).strip()
        content = content[byline.end():].strip()
    # Clean leftover time fragments at the start
    content = re.sub(r"^at\s+\d{1,2}:\d{2}\s*[AP]M\s*", "", content)
    # Clean "Updated ..." lines
    content = re.sub(r"^Updated\s+\w+\s+\d{1,2}\s+at\s+[\d:]+\s*[ap]\.?m\.?\s*", "", content)
    return author, date, content.strip()


def _is_low_quality(content: str) -> bool:
    """Reject content that's mostly navigation, lists, or too short."""
    lines = content.split("\n")
    if len(content) < 200:
        return True
    # If many lines are just article titles/dates (short, no periods), it's nav
    short_lines = sum(1 for l in lines if len(l.strip()) < 60 and "." not in l)
    if len(lines) > 3 and short_lines / len(lines) > 0.5:
        return True
    return False



def _make_teaser(content: str) -> str:
    """Extract a clean 1-2 sentence teaser from article content."""
    # Split on sentence boundaries (period + space + capital letter)
    sentences = re.split(r"(?<=\.)\s+(?=[A-Z])", content.replace("\n", " "))
    # Skip very short fragments (likely leftover noise)
    good = [s for s in sentences if len(s) > 30]
    if good:
        return good[0] if len(good[0]) < 200 else good[0][:197] + "..."
    return content[:150] + "..."


def _make_summary(content: str) -> str:
    """Build a 3-4 sentence summary from the article body."""
    sentences = re.split(r"(?<=\.)\s+(?=[A-Z])", content.replace("\n", " "))
    good = [s for s in sentences if len(s) > 30]
    summary = " ".join(good[:4])
    if len(summary) > 600:
        summary = summary[:597] + "..."
    return summary


def _seed_from_tavily() -> list[dict]:
    """Search Tavily for Columbia campus articles with images."""
    api_key = settings.tavily_api_key
    articles: list[dict] = []

    search_resp = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": "Columbia University campus news 2026",
            "max_results": 10,
            "search_depth": "advanced",
            "include_images": True,
            "include_domains": [
                "news.columbia.edu",
                "columbiaspectator.com",
                "bwog.com",
                "gocolumbialions.com",
            ],
        },
        timeout=30.0,
    )
    search_resp.raise_for_status()
    data = search_resp.json()
    results = data.get("results", [])
    top_images = data.get("images", [])

    for idx, item in enumerate(results):
        url = item.get("url", "")
        title = item.get("title", "Untitled")
        raw = httpx.get(url, timeout=30.0).text
        raw_teaser = _extract_teaser_from_raw(raw)
        '''
        raw = item.get("content", "")
        raw_teaser = _extract_teaser_from_raw(raw)'''

        if _is_index_page(url, title):
            continue

        content = _clean_content(raw, headline=title)
        if len(content) < 100:
            continue

        author, date, content = _extract_byline(content)
        if _is_low_quality(content):
            continue

        image_url = item.get("image_url", "") or ""
        if not image_url and idx < len(top_images):
            image_url = top_images[idx]
        if not image_url:
            image_url = FALLBACK_IMAGES[len(articles) % len(FALLBACK_IMAGES)]

        articles.append({
            "article_id": _article_id(title),
            "headline": title,
            "teaser": raw_teaser if raw_teaser else _make_teaser(content),
            "full_summary": _make_summary(content),
            "full_content": content,
            "author": author,
            "date": date,
            "category": "Campus News",
            "image_url": image_url,
            "source_url": url,
        })

        if len(articles) >= 6:
            break

    return articles


def _seed_from_fallback() -> list[dict]:
    """Use hardcoded sample articles."""
    return [
        {**a, "article_id": _article_id(a["headline"])}
        for a in FALLBACK_ARTICLES
    ]


def seed() -> None:
    init_db()

    if settings.tavily_api_key:
        print("Fetching articles from Tavily...")
        try:
            articles = _seed_from_tavily()
        except Exception as e:
            print(f"Tavily failed ({e}), using fallback articles")
            articles = _seed_from_fallback()
    else:
        print("No TAVILY_API_KEY set, using fallback articles")
        articles = _seed_from_fallback()

    if not articles:
        print("No articles found, using fallback")
        articles = _seed_from_fallback()
    elif len(articles) < 6:
        existing_ids = {a["article_id"] for a in articles}
        for fb in _seed_from_fallback():
            if fb["article_id"] not in existing_ids:
                articles.append(fb)
            if len(articles) >= 6:
                break
        print(f"  Padded with fallback articles to reach {len(articles)}")

    with db_session() as conn:
        conn.execute("DELETE FROM articles")
        for a in articles:
            conn.execute(
                "INSERT INTO articles "
                "(article_id, headline, teaser, full_summary, full_content, author, date, category, image_url, source_url) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(article_id) DO UPDATE SET "
                "headline=excluded.headline, teaser=excluded.teaser, "
                "full_summary=excluded.full_summary, full_content=excluded.full_content",
                (
                    a["article_id"], a["headline"], a["teaser"], a["full_summary"],
                    a["full_content"], a["author"], a["date"], a["category"],
                    a["image_url"], a["source_url"],
                ),
            )

    print(f"Seeded {len(articles)} articles")


if __name__ == "__main__":
    seed()
