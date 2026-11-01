import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.freelancehunt.com/v2/projects"


def fetch_gigs(pages=3):
    token = os.getenv("FREELANCEHUNT_API_TOKEN")

    if not token:
        raise ValueError("FREELANCEHUNT_API_TOKEN is missing")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
    }

    gigs = []
    url = API_URL

    for _ in range(pages):
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        for project in data.get("data", []):
            attributes = project.get("attributes") or {}
            links = project.get("links") or {}
            budget = attributes.get("budget") or {}
            skills = attributes.get("skills") or []

            status = attributes.get("status") or {}
            if status.get("id") != 11:
                continue

            gigs.append({
                "id": str(project.get("id", "")),
                "title": attributes.get("name", ""),
                "description": attributes.get("description", ""),
                "skills": ", ".join(
                    skill.get("name", "")
                    for skill in skills
                    if isinstance(skill, dict)
                ),
                "budget_min": budget.get("amount"),
                "budget_max": budget.get("amount"),
                "currency": budget.get("currency", ""),
                "url": (links.get("self") or {}).get("web", ""),
                "source": "Freelancehunt",
            })

        url = data.get("links", {}).get("next")
        if not url:
            break

    return gigs