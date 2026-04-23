"""Tool for fetching and parsing job descriptions from URLs."""

import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool

from app.tools.models import JobFetcherInput, JobData


@tool(args_schema=JobFetcherInput)
def fetch_job_description(url: str) -> dict:
    """Fetch and parse a job description from a URL.

    Extracts the job title, company, location, description, requirements,
    and preferred qualifications from the job posting page.

    Args:
        url: The URL of the job posting.

    Returns:
        A dictionary containing job details matching JobData model.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    text_content = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]

    description = "\n".join(lines)

    title = _extract_title(soup, lines) or ""
    company = _extract_company(soup, url) or ""
    location = _extract_location(soup, lines) or ""

    requirements = (
        _extract_section(lines, ["requirements", "required", "qualifications"]) or ""
    )
    responsibilities = (
        _extract_section(lines, ["responsibilities", "duties", "what you'll do"]) or ""
    )
    benefits = _extract_section(lines, ["benefits", "perks", "what we offer"]) or ""

    return JobData(
        url=url,
        title=title,
        company=company,
        location=location,
        description=description,
        requirements=requirements,
        responsibilities=responsibilities,
        benefits=benefits,
    ).model_dump()


def _extract_title(soup: BeautifulSoup, lines: list[str]) -> str | None:
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text and len(text) < 200:
            return text

    for line in lines[:10]:
        if any(
            keyword in line.lower() for keyword in ["hiring", "job", "position", "role"]
        ):
            return line

    return None


def _extract_company(soup: BeautifulSoup, url: str) -> str | None:
    company_keywords = ["company", "employer", "organization"]

    for tag in soup.find_all(
        ["span", "div", "p"],
        class_=lambda x: x and any(k in x.lower() for k in company_keywords),
    ):
        text = tag.get_text(strip=True)
        if text and len(text) < 100:
            return text

    domain = url.split("/")[2] if "/" in url else ""
    if "linkedin" in domain:
        return "LinkedIn"
    elif "indeed" in domain:
        return "Indeed"
    elif "glassdoor" in domain:
        return "Glassdoor"

    return None


def _extract_location(soup: BeautifulSoup, lines: list[str]) -> str | None:
    location_keywords = ["location", "location:", "address", "remote"]

    for tag in soup.find_all(
        ["span", "div", "p"],
        class_=lambda x: x and any(k in x.lower() for k in ["location", "address"]),
    ):
        text = tag.get_text(strip=True)
        if text and len(text) < 100:
            return text

    for line in lines[:20]:
        lower = line.lower()
        if any(kw in lower for kw in location_keywords):
            return line.split(":", 1)[-1].strip()

    return None


def _extract_section(lines: list[str], keywords: list[str]) -> str | None:
    start_idx = None

    for i, line in enumerate(lines):
        lower = line.lower()
        if any(kw in lower for kw in keywords):
            start_idx = i
            break

    if start_idx is None:
        return None

    section_lines = []
    for line in lines[start_idx + 1 : start_idx + 50]:
        if line and len(line) > 2:
            if any(
                heading in line.lower()
                for heading in [
                    "responsibilities",
                    "requirements",
                    "qualifications",
                    "benefits",
                    "about",
                    "who",
                ]
            ):
                break
            section_lines.append(line)

    if section_lines:
        return "\n".join(section_lines)
    return None
