import requests


def fetch_jobs():
    response = requests.get(
        "https://remoteok.com/api",
        headers={
            "User-Agent": "AutoApplyPersonalProject/1.0"
        },
        timeout=25
    )
    response.raise_for_status()

    data = response.json()
    results = []

    for job in data:
        if not isinstance(job, dict) or not job.get("position"):
            continue

        results.append({
            "id": str(job.get("id", "")),
            "title": job.get("position", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "category": ", ".join(job.get("tags") or []),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": "Remote OK",
        })

    return results