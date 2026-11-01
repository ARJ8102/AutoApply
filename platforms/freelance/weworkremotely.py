import requests
import feedparser
from bs4 import BeautifulSoup


FEED_URL = (
    "https://weworkremotely.com/"
    "categories/remote-programming-jobs.rss"
)


def fetch_gigs():
    response = requests.get(
        FEED_URL,
        headers={"User-Agent": "AutoApply/1.0"},
        timeout=25
    )
    response.raise_for_status()

    feed = feedparser.parse(response.content)

    gigs = []

    for entry in feed.entries:
        title = entry.get("title", "")
        description = BeautifulSoup(
            entry.get("summary", ""),
            "html.parser"
        ).get_text(" ", strip=True)

        # Only include explicitly labeled contract opportunities.
        text = f"{title} {description}".lower()

        if not any(
            term in text
            for term in (
                "contract position",
                "contract role",
                "contractor",
                "freelance",
                "contract-based",
            )
        ):
            continue

        gigs.append({
            "id": entry.get("id", entry.get("link", "")),
            "title": title,
            "description": description,
            "skills": "",
            "budget_min": None,
            "budget_max": None,
            "currency": "",
            "url": entry.get("link", ""),
            "source": "We Work Remotely",
        })

    return gigs