from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LocationInfo(BaseModel):
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""

class PersonalInfo(BaseModel):
    full_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    location: LocationInfo = Field(default_factory=LocationInfo)
    linkedin_url: Optional[str] = ""
    github_url: Optional[str] = ""
    portfolio_url: Optional[str] = ""

class Skills(BaseModel):
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    languages_programming: List[str] = Field(default_factory=list)
    languages_spoken: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    institution: Optional[str] = ""
    degree: Optional[str] = ""
    field_of_study: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    gpa: Optional[str] = ""
    location: Optional[str] = ""

class ExperienceItem(BaseModel):
    company: Optional[str] = ""
    title: Optional[str] = ""
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    is_current: bool = False
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)

class CertificationItem(BaseModel):
    name: Optional[str] = ""
    issuing_org: Optional[str] = ""
    issue_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    credential_id: Optional[str] = ""

class ProjectItem(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    tech_stack: List[str] = Field(default_factory=list)
    url: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""

class ResumeData(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: Optional[str] = ""
    education: List[EducationItem] = Field(default_factory=list)
    work_experience: List[ExperienceItem] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: List[CertificationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    total_experience_years: Optional[float] = None
    raw_text: str = ""
