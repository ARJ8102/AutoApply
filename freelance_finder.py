from concurrent.futures import ThreadPoolExecutor, as_completed






from platforms.freelance import (
    freelancer,
    remoteok,
    weworkremotely,
    freelancehunt,
)

from utils.relevance import score_gig


SOURCES = {
    "Freelancer": freelancer.fetch_gigs,
    "Remote OK": remoteok.fetch_gigs,
    "We Work Remotely": weworkremotely.fetch_gigs,
    "Freelancehunt": freelancehunt.fetch_gigs,
}


def fetch_gigs(keyword="", pages=3):

    all_gigs = []
    errors = {}
    source_counts = {}

    with ThreadPoolExecutor(max_workers=4) as executor:

        futures = {}

        for name, function in SOURCES.items():

            if name == "Freelancer":
                future = executor.submit(
                    function,
                    keyword=keyword,
                    pages=pages,
                    per_page=50
                )

            elif name == "Freelancehunt":
                future = executor.submit(function, pages=pages)
            else:
                future = executor.submit(function)





            futures[future] = name

        for future in as_completed(futures):

            source = futures[future]

            try:
                gigs = future.result()
                source_counts[source] = len(gigs)
                all_gigs.extend(gigs)

            except Exception as error:
                source_counts[source] = 0
                errors[source] = str(error)

    unique = []
    seen = set()

    for gig in all_gigs:

        key = (
            gig.get("source", ""),
            str(gig.get("id") or gig.get("url") or "")
        )

        if key in seen:
            continue

        seen.add(key)

        score, matched_skills = score_gig(gig)

        gig["relevance_score"] = score
        gig["matched_skills"] = matched_skills

        unique.append(gig)

    if keyword.strip():

        keyword_lower = keyword.strip().lower()

        unique = [
            gig for gig in unique
            if keyword_lower in (
                str(gig.get("title") or "") + " " +
                str(gig.get("description") or "") + " " +
                str(gig.get("skills") or "")
            ).lower()
        ]

    unique.sort(
        key=lambda gig: gig["relevance_score"],
        reverse=True
    )

    return unique, source_counts, errors