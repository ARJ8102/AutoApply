import re


INDIA_TERMS = [
    "india", "indian", "bangalore", "bengaluru",
    "hyderabad", "pune", "mumbai", "delhi",
    "chennai", "kolkata", "noida", "gurgaon",
    "gurugram"
]

WORLDWIDE_TERMS = [
    "worldwide", "anywhere in the world",
    "work from anywhere", "globally remote",
    "global remote", "remote globally"
]

RESTRICTED_TERMS = [
    r"\bus only\b",
    r"\busa only\b",
    r"\bus residents only\b",
    r"\bmust be based in the us\b",
    r"\bmust reside in the united states\b",
    r"\bremote within the us\b",
    r"\bremote - us\b",
    r"\bremote \(us\)\b",
    r"\beu only\b",
    r"\buk only\b",
    r"\bcanada only\b",
    r"\bus work authorization required\b",
    r"\bmust be authorized to work in the us\b",
]


def check_eligibility(job):
    """
    Returns:
        Eligible
        Ineligible
        Needs Review
    """

    location = str(job.get("location") or "").lower()
    description = str(job.get("description") or "").lower()

    text = f"{location} {description}"

    remote = bool(
        re.search(r"\bremote\b", location)
        or re.search(r"\bremote\b", description[:500])
    )

    india_location = any(
        term in location for term in INDIA_TERMS
    )

    worldwide_location = any(
        term in location for term in WORLDWIDE_TERMS
    )

    restricted = any(
        re.search(pattern, text)
        for pattern in RESTRICTED_TERMS
    )

    if restricted:
        return "Ineligible"

    if india_location:
        return "Eligible"

    if remote and worldwide_location:
        return "Eligible"

    if remote:
        return "Needs Review"

    return "Needs Review"