import re
import os
from typing import List, Set, Dict, Any, Optional
from pypdf import PdfReader
from app.schemas.resume import (
    ResumeData,
    PersonalInfo,
    LocationInfo,
    Skills,
    ExperienceItem,
    EducationItem,
    CertificationItem,
    ProjectItem
)

# Standard UUID regex pattern
UUID_PATTERN = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')

# Regex patterns for resume data points
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
LINKEDIN_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)/?', re.IGNORECASE)
GITHUB_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/?', re.IGNORECASE)
PORTFOLIO_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?(?:[a-zA-Z0-9-]+\.)+(?:io|dev|me|tech|com|app)(?:/[^\s]*)?', re.IGNORECASE)

PROGRAMMING_LANGUAGES = {
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "golang", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "html", "css", "sql"
}

TOOLS = {
    "docker", "kubernetes", "git", "github", "gitlab", "jira", "aws", "azure", "gcp",
    "linux", "postman", "jenkins", "terraform", "ansible", "figma"
}

TECHNICAL_SKILLS = {
    "react", "node.js", "nodejs", "fastapi", "django", "flask", "postgresql", "mysql",
    "mongodb", "redis", "graphql", "rest api", "ci/cd", "pandas", "numpy", "pytorch",
    "tensorflow", "scikit-learn", "tailwind", "next.js", "express", "microservices"
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "time management", "adaptability", "collaboration", "agile", "scrum"
}

SPOKEN_LANGUAGES = {
    "english", "spanish", "french", "german", "mandarin", "chinese", "hindi",
    "arabic", "japanese", "portuguese", "russian", "korean", "italian"
}

DEGREE_PATTERNS = [
    r"(?:Bachelor|B\.?S\.?|B\.?A\.?|B\.?E\.?|B\.?Tech)\b.*",
    r"(?:Master|M\.?S\.?|M\.?A\.?|M\.?E\.?|M\.?Tech|MBA)\b.*",
    r"(?:Ph\.?D|Doctorate)\b.*",
    r"(?:Associate|Diploma)\b.*"
]

def extract_uuids_from_text(text: str) -> List[str]:
    """
    Extracts all unique UUIDs from the given text string.
    """
    if not text:
        return []
    matches: Set[str] = {match.lower() for match in UUID_PATTERN.findall(text)}
    return sorted(list(matches))

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file using pypdf.
    """
    text_content = []
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return "\n".join(text_content)

def extract_text_from_file(file_path: str, content_type: str = "") -> str:
    """
    Determines file type and extracts text accordingly.
    """
    if not os.path.exists(file_path):
        return ""
        
    ext = os.path.splitext(file_path)[1].lower()
    
    # PDF processing
    if ext == '.pdf' or 'pdf' in content_type.lower():
        return extract_text_from_pdf(file_path)
        
    # Text file processing
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""

def split_into_sections(text: str) -> Dict[str, str]:
    """
    Segments resume text into logical sections based on common headings.
    """
    section_headers = [
        "experience", "work experience", "employment history", "work history",
        "education", "academic background",
        "skills", "technical skills", "skills & tools", "core competencies",
        "projects", "personal projects", "key projects",
        "certifications", "certificates", "licenses",
        "summary", "professional summary", "profile", "about me",
        "publications", "papers", "awards", "honors", "achievements"
    ]
    
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"
    
    for line in lines:
        stripped = line.strip()
        cleaned_header = re.sub(r'[^a-zA-Z\s]', '', stripped).lower()
        if cleaned_header in section_headers and len(stripped) < 40:
            if "experience" in cleaned_header or "employment" in cleaned_header or "work" in cleaned_header:
                current_section = "experience"
            elif "education" in cleaned_header or "academic" in cleaned_header:
                current_section = "education"
            elif "skill" in cleaned_header or "competencies" in cleaned_header:
                current_section = "skills"
            elif "project" in cleaned_header:
                current_section = "projects"
            elif "cert" in cleaned_header or "license" in cleaned_header:
                current_section = "certifications"
            elif "summary" in cleaned_header or "profile" in cleaned_header or "about" in cleaned_header:
                current_section = "summary"
            elif "publication" in cleaned_header or "paper" in cleaned_header:
                current_section = "publications"
            elif "award" in cleaned_header or "honor" in cleaned_header or "achievement" in cleaned_header:
                current_section = "awards"
            else:
                current_section = cleaned_header
            sections[current_section] = []
        else:
            sections[current_section].append(line)
            
    return {k: "\n".join(v).strip() for k, v in sections.items()}

def extract_resume_data(text: str) -> ResumeData:
    """
    Parses resume text into a structured ResumeData object matching the full schema.
    """
    if not text:
        return ResumeData()

    sections = split_into_sections(text)
    
    # 1. Personal Info
    emails = EMAIL_PATTERN.findall(text)
    phones = [p.strip() for p in PHONE_PATTERN.findall(text)]
    linkedin_matches = LINKEDIN_PATTERN.findall(text)
    github_matches = GITHUB_PATTERN.findall(text)
    portfolio_matches = PORTFOLIO_PATTERN.findall(text)

    # Clean portfolio matches (exclude linkedin/github)
    portfolios = [
        p for p in portfolio_matches 
        if "linkedin.com" not in p.lower() and "github.com" not in p.lower()
    ]

    # Name heuristic from top header
    full_name = ""
    header_text = sections.get("header", "")
    for line in header_text.splitlines():
        line_clean = line.strip()
        if (line_clean and not re.search(r'[@\d/:]', line_clean) 
            and 2 <= len(line_clean.split()) <= 4 
            and len(line_clean) < 40):
            full_name = line_clean
            break

    personal_info = PersonalInfo(
        full_name=full_name,
        email=emails[0] if emails else "",
        phone=phones[0] if phones else "",
        location=LocationInfo(),
        linkedin_url=f"https://linkedin.com/in/{linkedin_matches[0]}" if linkedin_matches else "",
        github_url=f"https://github.com/{github_matches[0]}" if github_matches else "",
        portfolio_url=portfolios[0] if portfolios else ""
    )

    # 2. Skills
    text_lower = text.lower()
    found_prog_languages = [s for s in PROGRAMMING_LANGUAGES if re.search(rf'\b{re.escape(s)}\b', text_lower)]
    found_tools = [s for s in TOOLS if re.search(rf'\b{re.escape(s)}\b', text_lower)]
    found_tech = [s for s in TECHNICAL_SKILLS if re.search(rf'\b{re.escape(s)}\b', text_lower)]
    found_soft = [s for s in SOFT_SKILLS if re.search(rf'\b{re.escape(s)}\b', text_lower)]
    found_spoken = [s for s in SPOKEN_LANGUAGES if re.search(rf'\b{re.escape(s)}\b', text_lower)]
    
    skills = Skills(
        technical=sorted(list(set(found_tech))),
        soft=sorted(list(set(found_soft))),
        tools=sorted(list(set(found_tools))),
        languages_programming=sorted(list(set(found_prog_languages))),
        languages_spoken=sorted(list(set(found_spoken)))
    )

    # 3. Work Experience
    work_experiences = []
    exp_text = sections.get("experience", "")
    if exp_text:
        exp_lines = [l.strip() for l in exp_text.splitlines() if l.strip()]
        current_exp: Optional[ExperienceItem] = None
        for line in exp_lines:
            if line.startswith(('-', '•', '*', '–')) or (current_exp and len(line) > 50):
                if current_exp:
                    current_exp.responsibilities.append(line.lstrip('-•*– '))
            else:
                if current_exp:
                    work_experiences.append(current_exp)
                
                # Check for is_current
                is_current = bool(re.search(r'\b(present|current|now)\b', line, re.IGNORECASE))
                current_exp = ExperienceItem(
                    title=line,
                    is_current=is_current,
                    responsibilities=[],
                    achievements=[]
                )
        if current_exp:
            work_experiences.append(current_exp)

    # 4. Education
    educations = []
    edu_text = sections.get("education", "")
    if edu_text:
        edu_lines = [l.strip() for l in edu_text.splitlines() if l.strip()]
        for line in edu_lines:
            degree_match = None
            for d_pat in DEGREE_PATTERNS:
                m = re.search(d_pat, line, re.IGNORECASE)
                if m:
                    degree_match = m.group(0)
                    break
            
            # Check for GPA
            gpa_match = re.search(r'\b(?:GPA|CGPA)[:\s]*([0-4]\.\d{1,2}|[0-9]\.\d{1,2}/10|[0-9]{1,2}\.?\d?%?)\b', line, re.IGNORECASE)
            gpa = gpa_match.group(1) if gpa_match else ""

            # Check for year
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', line)
            end_date = year_match.group(0) if year_match else ""

            if degree_match or end_date or len(educations) < 2:
                educations.append(EducationItem(
                    degree=degree_match or line,
                    institution=line if not degree_match else "",
                    end_date=end_date,
                    gpa=gpa
                ))

    # 5. Projects
    projects = []
    proj_text = sections.get("projects", "")
    if proj_text:
        proj_lines = [l.strip() for l in proj_text.splitlines() if l.strip()]
        current_proj: Optional[ProjectItem] = None
        for line in proj_lines:
            if line.startswith(('-', '•', '*', '–')):
                if current_proj:
                    desc = current_proj.description or ""
                    current_proj.description = (desc + " " + line.lstrip('-•*– ')).strip()
            else:
                if current_proj:
                    projects.append(current_proj)
                current_proj = ProjectItem(
                    name=line,
                    tech_stack=[s for s in (TECHNICAL_SKILLS | PROGRAMMING_LANGUAGES | TOOLS) if s in line.lower()]
                )
        if current_proj:
            projects.append(current_proj)

    # 6. Certifications
    certifications = []
    cert_text = sections.get("certifications", "")
    if cert_text:
        cert_lines = [l.strip() for l in cert_text.splitlines() if l.strip() and not l.lower().startswith("certification")]
        for line in cert_lines:
            certifications.append(CertificationItem(
                name=line.lstrip('-•*– ')
            ))

    # 7. Publications & Awards
    pub_text = sections.get("publications", "")
    publications = [
        l.lstrip('-•*– ').strip() 
        for l in pub_text.splitlines() 
        if l.strip() and not l.lower().startswith("publication")
    ]

    award_text = sections.get("awards", "")
    awards = [
        l.lstrip('-•*– ').strip() 
        for l in award_text.splitlines() 
        if l.strip() and not l.lower().startswith("award")
    ]

    # Summary
    summary_text = sections.get("summary", "")

    return ResumeData(
        personal_info=personal_info,
        summary=summary_text,
        education=educations,
        work_experience=work_experiences,
        skills=skills,
        certifications=certifications,
        projects=projects,
        publications=publications,
        awards=awards,
        total_experience_years=None,
        raw_text=text
    )
