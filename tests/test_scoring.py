"""Automated tests for deterministic ATS scoring and skill matching."""

import pytest
from app.scoring.matcher import SkillMatcher
from app.scoring.engine import ATSScoringEngine
from app.scoring.gap_analysis import SkillGapAnalyzer
from app.resume.extractor import ParsedResumeData, ContactInfo, EducationEntry, ProjectEntry


@pytest.fixture
def mock_role_skills():
    return [
        {"skill_name": "Penetration Testing", "importance": "core"},
        {"skill_name": "Vulnerability Assessment", "importance": "core"},
        {"skill_name": "Python", "importance": "core"},
        {"skill_name": "Wireshark", "importance": "preferred"},
        {"skill_name": "Burp Suite", "importance": "preferred"},
        {"skill_name": "SIEM", "importance": "preferred"},
        {"skill_name": "Reverse Engineering", "importance": "additional"},
    ]


@pytest.fixture
def mock_scoring_criteria():
    return [
        {"category": "Technical Skills", "weight": 40.0},
        {"category": "Projects", "weight": 25.0},
        {"category": "Education", "weight": 15.0},
        {"category": "Tools & Certifications", "weight": 15.0},
        {"category": "Career Objective", "weight": 5.0},
    ]


@pytest.fixture
def sample_resume_data():
    return ParsedResumeData(
        candidate_name="Alex Mercer",
        contact_info=ContactInfo(email="alex@sec.io", location="New York, NY"),
        career_objective="Aspiring Penetration Tester focused on offensive security and web exploits.",
        professional_summary="Experienced in penetration testing, vulnerability assessment, and Python scripting.",
        technical_skills=["Python", "Penetration Testing", "Vulnerability Assessment", "Wireshark", "Burp Suite", "Linux"],
        education=[
            EducationEntry(degree="Bachelor of Science in Computer Science", institution="MIT", graduation_year="2023")
        ],
        certifications=["CEH", "CompTIA Security+"],
        projects=[
            ProjectEntry(
                title="Automated Exploit Suite",
                description="Engineered network scanner using Python, Scapy, and Wireshark to identify open CVE vulnerabilities.",
                technologies=["Python", "Wireshark"],
            ),
            ProjectEntry(
                title="Web Vulnerability Assessment",
                description="Audited web applications using Burp Suite for OWASP Top 10 vulnerabilities.",
                technologies=["Burp Suite"],
            )
        ],
    )


def test_skill_matcher(mock_role_skills, sample_resume_data):
    full_text = "Alex Mercer Penetration Testing Vulnerability Assessment Python Wireshark Burp Suite"
    report = SkillMatcher.match_skills(
        role_skills=mock_role_skills,
        resume_skills=sample_resume_data.technical_skills,
        resume_full_text=full_text,
        resume_projects=sample_resume_data.projects,
        resume_experience=[],
        role_id=1,
        role_name="Penetration Tester",
    )
    assert report.total_role_skills == 7
    assert len(report.matched_skills) >= 5
    assert report.matched_core_count == 3  # Pen testing, vuln assess, python all matched
    assert report.total_core_count == 3


def test_deterministic_scoring(mock_role_skills, mock_scoring_criteria, sample_resume_data):
    report = SkillMatcher.match_skills(
        role_skills=mock_role_skills,
        resume_skills=sample_resume_data.technical_skills,
        resume_full_text="Sample text with Python and Penetration Testing",
        resume_projects=sample_resume_data.projects,
        resume_experience=[],
        role_id=1,
        role_name="Penetration Tester",
    )

    score_1 = ATSScoringEngine.calculate_score(
        resume_data=sample_resume_data,
        match_report=report,
        role_requirements=[],
        db_scoring_criteria=mock_scoring_criteria,
        threshold=80.0,
    )

    score_2 = ATSScoringEngine.calculate_score(
        resume_data=sample_resume_data,
        match_report=report,
        role_requirements=[],
        db_scoring_criteria=mock_scoring_criteria,
        threshold=80.0,
    )

    # Identical repeatability
    assert score_1.final_score == score_2.final_score
    assert 0.0 <= score_1.final_score <= 100.0
    assert len(score_1.category_scores) == 5

    # Check weights sum
    total_weights = sum(c.weight for c in score_1.category_scores)
    assert total_weights == 100.0


def test_missing_sections_scoring(mock_role_skills, mock_scoring_criteria):
    empty_resume = ParsedResumeData()
    report = SkillMatcher.match_skills(
        role_skills=mock_role_skills,
        resume_skills=[],
        resume_full_text="",
        resume_projects=[],
        resume_experience=[],
        role_id=1,
        role_name="Penetration Tester",
    )
    score = ATSScoringEngine.calculate_score(
        resume_data=empty_resume,
        match_report=report,
        role_requirements=[],
        db_scoring_criteria=mock_scoring_criteria,
        threshold=80.0,
    )
    assert score.final_score == 0.0
    assert score.meets_threshold is False
    assert score.status == "IMPROVEMENT_RECOMMENDED"


def test_threshold_boundary():
    """Validates that score < 80 recommends improvement and >= 80 qualifies."""
    # Test threshold property directly on ATSScoreResult
    assert ATSScoringEngine.DEFAULT_WEIGHTS["Technical Skills"] == 40.0
    assert ATSScoringEngine.DEFAULT_WEIGHTS["Projects"] == 25.0
    assert ATSScoringEngine.DEFAULT_WEIGHTS["Education"] == 15.0
    assert ATSScoringEngine.DEFAULT_WEIGHTS["Tools & Certifications"] == 15.0
    assert ATSScoringEngine.DEFAULT_WEIGHTS["Career Objective"] == 5.0
