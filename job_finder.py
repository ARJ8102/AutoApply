import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from platforms.jobs import (
    remotive,
    remoteok,
    arbeitnow,
    himalayas,
    freehire,
)

from utils.eligibility import check_eligibility


def normalize_url(url):
    if not url:
        return ""

    parts = urlsplit(str(url).strip())

    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/").lower()

    return urlunsplit((
        parts.scheme.lower(),
        host,
        path,
        "",
        ""
    ))


def job_key(job):
    """
    Generate a unique identifier for each job.
    Used to remove duplicate listings across platforms.
    """

    url = normalize_url(job.get("url"))

    if url:
        return ("url", url)

    return (
        "fallback",
        re.sub(
            r"\W+",
            "",
            str(job.get("company") or "").lower()
        ),
        re.sub(
            r"\W+",
            "",
            str(job.get("title") or "").lower()
        ),
        re.sub(
            r"\W+",
            "",
            str(job.get("location") or "").lower()
        )
    )


def text_matches(job, keyword):
    """
    Check whether a job matches the search keyword.
    """

    if not keyword.strip():
        return True

    raw = " ".join(
        str(job.get(k) or "")
        for k in (
            "title",
            "company",
            "location",
            "category",
            "description"
        )
    )

    text = BeautifulSoup(
        raw,
        "html.parser"
    ).get_text(" ", strip=True)

    return keyword.casefold() in text.casefold()


def fetch_jobs(
    keyword="",
    pages=2,
    remote_only=False,
    junior_only=False,
    yc_only=False
):
    """
    Fetch jobs from multiple platforms.

    Returns:
        jobs
        source_counts
        errors
    """

    # --------------------------------------------------
    # 1. Job sources
    # --------------------------------------------------

    sources = {
        "Remotive": remotive.fetch_jobs,

        "Remote OK": remoteok.fetch_jobs,

        "Arbeitnow": arbeitnow.fetch_jobs,

        "Himalayas": himalayas.fetch_jobs,

        "freehire": lambda: freehire.fetch_jobs(
            keyword,
            pages,
            remote_only,
            junior_only,
            yc_only
        ),
    }

    # Greenhouse, Lever, and Ashby are temporarily disabled.

    source_counts = {
        name: 0
        for name in sources
    }

    errors = {}
    all_jobs = []

    # --------------------------------------------------
    # 2. Fetch jobs concurrently
    # --------------------------------------------------

    with ThreadPoolExecutor(max_workers=5) as pool:

        futures = {
            pool.submit(fn): name
            for name, fn in sources.items()
        }

        for future in as_completed(futures):

            name = futures[future]

            try:
                jobs = future.result()

                source_counts[name] = len(jobs)

                all_jobs.extend(jobs)

            except Exception as exc:

                errors[name] = str(exc)

    # --------------------------------------------------
    # 3. Remove duplicate jobs
    # --------------------------------------------------

    unique = []
    seen = set()

    for job in all_jobs:

        key = job_key(job)

        if key in seen:
            continue

        seen.add(key)
        unique.append(job)

    # --------------------------------------------------
    # 4. Keyword filtering
    # --------------------------------------------------

    unique = [
        job
        for job in unique
        if text_matches(job, keyword)
    ]

    # --------------------------------------------------
    # 5. Geographic eligibility classification
    # --------------------------------------------------

    for job in unique:

        try:
            job["eligibility"] = check_eligibility(job)

        except Exception:
            job["eligibility"] = "Needs Review"

    # --------------------------------------------------
    # 6. Sort results
    # --------------------------------------------------

    unique.sort(
        key=lambda job: (
            str(job.get("source") or ""),
            str(job.get("title") or "")
        )
    )

    # --------------------------------------------------
    # 7. Return results
    # --------------------------------------------------

    return unique, source_counts, errors