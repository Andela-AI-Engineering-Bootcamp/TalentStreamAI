"""Tool for parsing resumes from PDF and DOCX files."""

import base64
import io
import re
from pathlib import Path
from typing import Optional

from docx import Document as DocxDocument
from langchain_core.tools import tool
from pypdf import PdfReader
from pydantic import BaseModel

from app.tools.models import (
    ContactInfo,
    EducationEntry,
    ExperienceEntry,
    ResumeData,
)


class ResumeParserInput(BaseModel):
    file_content: str
    file_extension: str


@tool(args_schema=ResumeParserInput)
def parse_resume(file_content: str, file_extension: str) -> dict:
    """Parse a resume from PDF or DOCX file content.

    Extracts contact info, summary, experience, education, and skills.

    Args:
        file_content: Base64 encoded file content.
        file_extension: The file extension (.pdf or .docx).

    Returns:
        A dictionary containing parsed resume data matching ResumeData model.
    """
    try:
        file_bytes = base64.b64decode(file_content)
    except Exception as e:
        return {"error": f"Failed to decode file: {str(e)}"}

    ext = file_extension.lower().strip().lstrip(".")

    if ext == "pdf":
        return _parse_pdf(file_bytes)
    elif ext in ["docx", "doc"]:
        return _parse_docx(file_bytes)
    else:
        return {"error": f"Unsupported file format: {file_extension}"}


def _parse_pdf(file_bytes: bytes) -> dict:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        return {"error": f"Failed to parse PDF: {str(e)}"}

    return _extract_sections(text)


def _parse_docx(file_bytes: bytes) -> dict:
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return {"error": f"Failed to parse DOCX: {str(e)}"}

    return _extract_sections(text)


def _extract_sections(text: str) -> dict:
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    contact_info = _extract_contact_info(lines)
    summary = _extract_summary(text)
    experience = _extract_experience(lines)
    education = _extract_education(lines)
    skills = _extract_skills(lines)

    return ResumeData(
        contact_info=contact_info,
        summary=summary,
        experience=experience,
        education=education,
        skills=skills,
        raw_text=text,
    ).model_dump()


def _extract_contact_info(lines: list[str]) -> ContactInfo:
    contact = {}

    for line in lines[:15]:
        line = line.strip()

        if "@" in line and "." in line:
            contact["email"] = line
        elif any(x in line for x in ["linkedin.com/in/", "github.com/", "portfolio"]):
            contact["linkedin"] = line

        phone_match = re.search(
            r"(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", line
        )
        if phone_match:
            contact["phone"] = phone_match.group(1)

    return ContactInfo(**contact)


def _extract_summary(text: str) -> str | None:
    lines = [line.strip() for line in text.split("\n")]

    summary_keywords = ["summary", "profile", "objective", "about"]

    for i, line in enumerate(lines):
        lower = line.lower().strip()

        if any(kw in lower for kw in summary_keywords):
            summary_lines = []
            for next_line in lines[i + 1 : i + 6]:
                if not next_line or len(next_line) < 3:
                    break
                if any(
                    kw in next_line.lower()
                    for kw in [
                        "experience",
                        "education",
                        "skills",
                        "work",
                        "employment",
                    ]
                ):
                    break
                summary_lines.append(next_line)

            if summary_lines:
                return " ".join(summary_lines)

    return None


def _extract_experience(lines: list[str]) -> list[ExperienceEntry]:
    experience = []

    exp_keywords = ["experience", "employment", "work history", "professional"]

    for i, line in enumerate(lines):
        lower = line.lower().strip()

        if any(kw in lower for kw in exp_keywords) and len(line) < 50:
            exp_section_lines = lines[i + 1 : i + 40]

            current_entry = {}
            for j, exp_line in enumerate(exp_section_lines):
                if not exp_line or len(exp_line) < 3:
                    if current_entry:
                        experience.append(ExperienceEntry(**current_entry))
                        current_entry = {}
                    continue

                if any(
                    kw in exp_line.lower()
                    for kw in ["experience", "employment", "education", "skills"]
                ):
                    if current_entry:
                        experience.append(ExperienceEntry(**current_entry))
                    break

                colon_idx = exp_line.find(":")
                if colon_idx > 0:
                    key = exp_line[:colon_idx].strip()
                    value = exp_line[colon_idx + 1 :].strip()
                    current_entry[key.lower()] = value
                elif not current_entry and exp_line and len(exp_line) > 10:
                    current_entry["title"] = exp_line

    return experience


def _extract_education(lines: list[str]) -> list[EducationEntry]:
    education = []

    edu_keywords = ["education", "academic", "degree", "university", "college"]

    for i, line in enumerate(lines):
        lower = line.lower().strip()

        if any(kw in lower for kw in edu_keywords) and len(line) < 50:
            edu_section_lines = lines[i + 1 : i + 25]

            current_entry = {}
            for edu_line in edu_section_lines:
                if not edu_line or len(edu_line) < 3:
                    if current_entry:
                        education.append(EducationEntry(**current_entry))
                        current_entry = {}
                    continue

                if any(
                    kw in edu_line.lower() for kw in ["experience", "skills", "work"]
                ):
                    if current_entry:
                        education.append(EducationEntry(**current_entry))
                    break

                colon_idx = edu_line.find(":")
                if colon_idx > 0:
                    key = edu_line[:colon_idx].strip()
                    value = edu_line[colon_idx + 1 :].strip()
                    current_entry[key.lower()] = value
                elif not current_entry and edu_line and len(edu_line) > 5:
                    current_entry["school"] = edu_line

    return education


def _extract_skills(lines: list[str]) -> list[str]:
    skills = []

    skills_keywords = ["skills", "technical", "competencies", "tools"]

    for i, line in enumerate(lines):
        lower = line.lower().strip()

        if any(kw in lower for kw in skills_keywords) and len(line) < 30:
            skills_section = lines[i + 1 : i + 15]

            all_skills_text = " ".join(skills_section)

            skill_patterns = [
                r"([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
                r"([A-Z]{2,})",
            ]

            for pattern in skill_patterns:
                matches = re.findall(pattern, all_skills_text)
                skills.extend([s for s in matches if len(s) > 1 and len(s) < 30])

            if skills:
                break

    return list(set(skills))[:20]
