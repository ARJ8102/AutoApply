import requests


def fetch_jobs():
    response = requests.get(
        "https://www.arbeitnow.com/api/job-board-api",
        timeout=25
    )
    response.raise_for_status()

    jobs = response.json().get("data", [])

    results = []

    for job in jobs:
        results.append({
            "id": str(job.get("slug", "")),
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": job.get("location", ""),
            "category": ", ".join(job.get("tags") or []),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": "Arbeitnow",
            "remote": job.get("remote", False),
        })

    return results