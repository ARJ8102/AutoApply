from platforms.jobs.remoteok import fetch_jobs


def fetch_gigs():
    jobs = fetch_jobs()
    gigs = []

    for job in jobs:
        category = str(job.get("category") or "").lower()
        title = str(job.get("title") or "").lower()

        if not any(
            word in f"{title} {category}"
            for word in ("contract", "freelance", "contractor")
        ):
            continue

        gigs.append({
            "id": str(job.get("id", "")),
            "title": job.get("title", ""),
            "description": job.get("description", ""),
            "skills": category,
            "budget_min": None,
            "budget_max": None,
            "currency": "",
            "url": job.get("url", ""),
            "source": "Remote OK",
        })

    return gigs