"""Tool for ATS resume scoring against job descriptions."""

import re
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.tools.models import (
    ExperienceScore,
    EducationScore,
    ATSScore,
)


class ATSInput(BaseModel):
    resume_data: dict = Field(..., description="Parsed resume data")
    job_data: dict = Field(..., description="Job description data")


@tool(args_schema=ATSInput)
def ats_score_resume(resume_data: dict, job_data: dict) -> dict:
    """Score a resume against a job description for ATS compatibility.

    Analyzes keyword matches, skills alignment, experience requirements,
    and provides an overall ATS compatibility score.

    Args:
        resume_data: Parsed resume data from parse_resume tool.
        job_data: Job description data from fetch_job_description tool.

    Returns:
        A dictionary containing the ATS score and detailed analysis.
    """
    if not resume_data or not job_data:
        return {"error": "Missing resume_data or job_data"}

    resume_text = resume_data.get("raw_text", "") or ""
    job_text = job_data.get("description", "") or ""
    job_requirements = job_data.get("requirements", "") or ""

    if not resume_text or not job_text:
        return {"error": "Empty resume or job data"}

    keywords = _extract_keywords(job_text.lower())
    resume_keywords = _extract_keywords(resume_text.lower())

    keyword_matches = [kw for kw in keywords if kw in resume_text.lower()]
    keyword_gaps = [kw for kw in keywords if kw not in resume_text.lower()]

    resume_skills = [s.lower() for s in (resume_data.get("skills") or []) if s]
    required_skills = _extract_skills(job_requirements.lower())

    skill_matches = [
        s for s in required_skills if any(s.lower() in rs for rs in resume_skills)
    ]
    skill_gaps = [
        s for s in required_skills if not any(s.lower() in rs for rs in resume_skills)
    ]

    experience_match = _analyze_experience(
        resume_data.get("experience") or [], job_requirements.lower()
    )

    education_match = _analyze_education(
        resume_data.get("education") or [], job_text.lower()
    )

    keyword_score = (
        min(len(keyword_matches) / len(keywords) * 40, 40) if keywords else 0
    )
    skill_score = (
        min(len(skill_matches) / len(required_skills) * 30, 30)
        if required_skills
        else 0
    )
    experience_score = min(experience_match["score"] * 20 / 100, 20)
    education_score = min(education_match["score"] * 10 / 100, 10)

    overall_score = min(
        keyword_score + skill_score + experience_score + education_score, 100
    )

    return ATSScore(
        overall_score=round(overall_score, 1),
        keyword_score=round(keyword_score, 1),
        keyword_matches=keyword_matches[:15],
        keyword_gaps=keyword_gaps[:15],
        skill_score=round(skill_score, 1),
        skill_matches=skill_matches[:10],
        skill_gaps=skill_gaps[:10],
        experience=ExperienceScore(**experience_match),
        education=EducationScore(**education_match),
        recommendations=_generate_recommendations(
            keyword_gaps, skill_gaps, experience_match, overall_score
        ),
    ).model_dump()


def _extract_keywords(text: str) -> list[str]:
    common_words = {
        "the",
        "and",
        "a",
        "an",
        "in",
        "to",
        "of",
        "for",
        "is",
        "on",
        "at",
        "by",
        "with",
        "as",
        "be",
        "or",
        "are",
        "was",
        "will",
        "from",
        "that",
        "this",
        "we",
        "you",
        "your",
        "they",
        "their",
        "our",
        "us",
        "can",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "but",
        "not",
        "all",
        "any",
        "one",
        "when",
        "what",
        "who",
        "how",
        "why",
        "where",
        "which",
        "also",
        "more",
        "most",
        "some",
        "other",
        "into",
        "out",
        "over",
        "under",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "now",
        "here",
        "there",
        "then",
        "if",
        "about",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "need",
        "position",
        "job",
        "work",
        "role",
        "team",
        "company",
        "year",
        "years",
        "experience",
        "required",
        "preferred",
        "qualifications",
    }

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+-]{3,}", text)

    keywords = [
        w
        for w in words
        if w.lower() not in common_words and len(w) > 2 and not w.isdigit()
    ]

    keyword_freq = {}
    for kw in keywords:
        keyword_freq[kw.lower()] = keyword_freq.get(kw.lower(), 0) + 1

    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)

    return [kw[0] for kw in sorted_keywords[:50]]


def _extract_skills(text: str) -> list[str]:
    skill_patterns = [
        r"\b(Python|Java|JavaScript|TypeScript|C\+\+|Go|Rust|Ruby|SQL|NoSQL)\b",
        r"\b(React|Angular|Vue|Node\.js|Express|Django|Flask|FastAPI)\b",
        r"\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|CI/CD|Git)\b",
        r"\b(ML|Machine Learning|AI|Deep Learning|NLP|Data Science)\b",
        r"\b(Agile|Scrum|Kanban|TDD|BDD|JIRA)\b",
        r"\b(REST API|GraphQL|gRPC|Microservices)\b",
        r"\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b",
        r"\b(Leadership|Management|Communication|Teamwork)\b",
    ]

    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)

    return list(set(skills))


def _analyze_experience(resume_experience: list[dict], job_requirements: str) -> dict:
    if not resume_experience:
        return {
            "score": 0,
            "level": "not_found",
            "details": "No experience found in resume",
            "years": 0,
            "required": 0,
        }

    years_match = re.search(
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience", job_requirements
    )
    required_years = int(years_match.group(1)) if years_match else 0

    total_years = 0
    for exp in resume_experience:
        exp_text = str(exp).lower()
        year_match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)", exp_text)
        if year_match:
            total_years += int(year_match.group(1))
        else:
            total_years += 1

    score = (
        1.0 if total_years >= required_years else total_years / max(required_years, 1)
    )
    score = min(score, 1.0)

    level = "senior" if total_years >= 5 else "mid" if total_years >= 2 else "junior"

    return {
        "score": round(score * 100, 1),
        "level": level,
        "years": total_years,
        "required": required_years,
    }


def _analyze_education(resume_education: list[dict], job_text: str) -> dict:
    education_keywords = {
        "phd": 4,
        "doctoral": 4,
        "masters": 3,
        "master's": 3,
        "ms": 3,
        "m.s.": 3,
        "bachelor": 2,
        "bachelor's": 2,
        "bs": 2,
        "b.s.": 2,
        "associate": 1,
        "high school": 0,
    }

    required_education = 0
    for level, points in education_keywords.items():
        if level in job_text:
            required_education = max(required_education, points)

    resume_education_text = " ".join([str(edu).lower() for edu in resume_education])

    resume_level = 0
    for level, points in education_keywords.items():
        if level in resume_education_text:
            resume_level = max(resume_level, points)

    score = (
        1.0
        if resume_level >= required_education
        else resume_level / max(required_education, 1)
    )
    score = min(score, 1.0)

    return {
        "score": round(score * 100, 1),
        "required_level": required_education,
        "resume_level": resume_level,
    }


def _generate_recommendations(
    keyword_gaps: list[str],
    skill_gaps: list[str],
    experience_match: dict,
    overall_score: float,
) -> list[str]:
    recommendations = []

    if overall_score < 70:
        recommendations.append(
            f"Overall ATS score is {overall_score:.0f}%. Target 70%+ for best results."
        )

    if keyword_gaps:
        top_gaps = keyword_gaps[:5]
        recommendations.append(
            f"Add these keywords to your resume: {', '.join(top_gaps)}"
        )

    if skill_gaps:
        recommendations.append(
            f"Highlight these missing skills: {', '.join(skill_gaps[:3])}"
        )

    if experience_match.get("required", 0) > 0:
        if experience_match.get("years", 0) < experience_match.get("required", 0):
            recommendations.append(
                f"Job requires {experience_match.get('required')} years of experience. "
                f"You have {experience_match.get('years')} years."
            )

    if not recommendations:
        recommendations.append("Resume is well-optimized for this position!")

    return recommendations
