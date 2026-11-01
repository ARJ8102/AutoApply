import requests
import time


API_URL = "https://www.freelancer.com/api/projects/0.1/projects/active/"


def fetch_gigs(keyword="", pages=3, per_page=50):
    """
    Search active Freelancer projects with pagination.
    """

    results = []
    seen_ids = set()

    for page in range(pages):

        params = {
            "limit": per_page,
            "offset": page * per_page,
            "full_description": "true",
            "job_details": "true",
        }

        if keyword.strip():
            params["query"] = keyword.strip()

        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            raise ValueError("Freelancer API returned an error.")

        projects = data.get("result", {}).get("projects", [])

        if not projects:
            break

        for project in projects:

            project_id = str(project.get("id", ""))

            if project_id in seen_ids:
                continue

            seen_ids.add(project_id)

            currency = project.get("currency") or {}
            budget = project.get("budget") or {}

            skills = project.get("jobs") or []

            skill_names = [
                skill.get("name", "")
                for skill in skills
                if isinstance(skill, dict)
            ]

            seo_url = project.get("seo_url", "")

            project_url = (
                f"https://www.freelancer.com/projects/{seo_url}"
                if seo_url
                else f"https://www.freelancer.com/projects/{project_id}"
            )

            results.append({
                "id": project_id,
                "title": project.get("title", ""),
                "description": (
                    project.get("description")
                    or project.get("preview_description")
                    or ""
                ),
                "skills": ", ".join(skill_names),
                "budget_min": budget.get("minimum"),
                "budget_max": budget.get("maximum"),
                "currency": currency.get("code", ""),
                "url": project_url,
                "source": "Freelancer",
            })

        if len(projects) < per_page:
            break

        # Avoid sending requests too quickly.
        time.sleep(0.5)

    return results