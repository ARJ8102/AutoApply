import requests


def fetch_jobs():
    url = "https://himalayas.app/jobs/api"

    results = []
    cursor = None

    # Fetch up to 5 pages (100 jobs)
    for _ in range(5):
        params = {"limit": 20}

        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            url,
            params=params,
            timeout=25
        )
        response.raise_for_status()

        data = response.json()

        for job in data.get("jobs", []):
            locations = job.get("locationRestrictions") or []

            results.append({
                "id": str(job.get("guid", "")),
                "title": job.get("title", ""),
                "company": job.get("companyName", ""),
                "location": (
                    ", ".join(map(str, locations))
                    if locations else "Worldwide"
                ),
                "category": ", ".join(
                    job.get("categories") or []
                ),
                "description": job.get("description", ""),
                "url": job.get("applicationLink", ""),
                "source": "Himalayas",
            })

        cursor = data.get("nextCursor")

        if not cursor:
            break

    return results