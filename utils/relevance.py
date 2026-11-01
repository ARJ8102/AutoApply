import re
from bs4 import BeautifulSoup


SKILL_WEIGHTS = {
    # High priority
    "machine learning": 10,
    "deep learning": 10,
    "artificial intelligence": 10,
    "llm": 10,
    "rag": 10,
    "pytorch": 10,
    "tensorflow": 10,
    "generative ai": 10,

    # Medium-high priority
    "python": 8,
    "automation": 8,
    "fastapi": 8,
    "flask": 8,
    "api development": 8,
    "data science": 8,
    "computer vision": 8,
    "nlp": 8,

    # Medium priority
    "java": 6,
    "javascript": 6,
    "react": 6,
    "sql": 6,
    "backend": 6,
    "web development": 6,
    "data analysis": 6,
    "aws": 6,

    # Lower priority
    "testing": 3,
    "debugging": 3,
    "technical writing": 3,
    "data entry": 2,
}


def clean_text(text):
    text = BeautifulSoup(
        str(text or ""), "html.parser"
    ).get_text(" ", strip=True)

    return text.lower()


def score_gig(gig):
    """
    Calculate a heuristic relevance score from 0 to 100.
    """

    title = clean_text(gig.get("title", ""))
    skills = clean_text(gig.get("skills", ""))
    description = clean_text(gig.get("description", ""))

    score = 0
    matched_skills = []

    for skill, weight in SKILL_WEIGHTS.items():

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        title_match = re.search(pattern, title)
        skills_match = re.search(pattern, skills)
        description_match = re.search(pattern, description)

        if title_match:
            score += weight * 2

        elif skills_match:
            score += weight * 1.5

        elif description_match:
            score += weight * 0.5

        if title_match or skills_match or description_match:
            matched_skills.append(skill)

    score = min(round(score), 100)

    return score, ", ".join(matched_skills)