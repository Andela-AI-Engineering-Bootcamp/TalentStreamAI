"""Pydantic models for tool inputs and outputs."""

from typing import Optional

from pydantic import BaseModel, Field


class JobFetcherInput(BaseModel):
    url: str = Field(..., description="URL of the job posting")


class JobData(BaseModel):
    url: str
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    requirements: str = ""
    responsibilities: str = ""
    benefits: str = ""


class ResumeParserInput(BaseModel):
    file_content: str = Field(..., description="Base64 encoded file content")
    file_extension: str = Field(..., description="File extension (.pdf or .docx)")


class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    name: Optional[str] = None


class ExperienceEntry(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None


class EducationEntry(BaseModel):
    school: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None


class ResumeData(BaseModel):
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    raw_text: Optional[str] = None


class ATSInput(BaseModel):
    resume_data: ResumeData
    job_data: JobData


class ExperienceScore(BaseModel):
    score: float
    level: str
    years: int
    required: int


class EducationScore(BaseModel):
    score: float
    required_level: int
    resume_level: int


class ATSScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    keyword_score: float
    keyword_matches: list[str] = Field(default_factory=list)
    keyword_gaps: list[str] = Field(default_factory=list)
    skill_score: float
    skill_matches: list[str] = Field(default_factory=list)
    skill_gaps: list[str] = Field(default_factory=list)
    experience: ExperienceScore
    education: EducationScore
    recommendations: list[str] = Field(default_factory=list)


class GapAnalysis(BaseModel):
    keyword_gaps: list[str] = Field(default_factory=list)
    skill_gaps: list[str] = Field(default_factory=list)
    experience_gap: dict = Field(default_factory=dict)
    education_gap: dict = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    resume_skills: list[str] = Field(default_factory=list)
    resume_experience: list[dict] = Field(default_factory=list)
