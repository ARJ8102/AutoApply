import requests


def fetch_jobs():
    response = requests.get(
        "https://remotive.com/api/remote-jobs",
        timeout=25
    )
    response.raise_for_status()

    jobs = response.json().get("jobs", [])

    return [
        {
            "id": str(job.get("id", "")),
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": job.get("candidate_required_location", ""),
            "category": job.get("category", ""),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": "Remotive",
        }
        for job in jobs
    ]