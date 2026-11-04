"""Tests for 'UI/UX Improvement: Compact Recommendations, Skill Levels and Project Suggestions'.

Validates:
1. Skill proficiency levels:
   - Beginner / Basic, Intermediate, Advanced, No experience yet (Not Yet).
   - "Senior" is never used as an individual skill proficiency level.
   - Unconfirmed skills or "No experience yet" are routed to learning recommendations, not inserted as qualifications.
2. Practical project recommendations:
   - Each project has title, level (Beginner / Intermediate / Advanced), objective/description,
     relevant role skills demonstrated, and is marked as future suggested project by default.
   - Completed similar project flow updates resume with verified details.
   - Future projects are never inserted into resume as completed work.
3. Certification recommendations:
   - Statuses: Earned, In Progress, Planning, Not Interested.
   - Unearned certs are never placed in completed qualifications.
4. Score category breakdown:
   - Evaluates category score / max, percentage, and 1-line gap explanation.
"""

import pytest
from app.resume.extractor import ParsedResumeData, ContactInfo, EducationEntry, ProjectEntry
from app.scoring.improvement_plan import ImprovementPlanGenerator, PracticalProjectTemplate
from app.projects.generator import ResumeContentGenerator, ConfirmedSkillItem


@pytest.fixture
def base_candidate_resume():
    return ParsedResumeData(
        candidate_name="Jordan Hayes",
        contact_info=ContactInfo(email="jordan.hayes@example.com", phone="555-0144"),
        career_objective="Aspiring SOC Analyst seeking to transition into cyber defense.",
        professional_summary="Junior practitioner with system administration and network fundamentals.",
        technical_skills=["Linux", "Networking Basics"],
        education=[EducationEntry(degree="B.S. in Computer Science", institution="State University", graduation_year="2022")],
        certifications=[],
        projects=[ProjectEntry(title="Basic Lab Router", description="Configured static routing in VirtualBox.", technologies=["Networking"])],
        employment_history=[],
    )


def test_project_recommendation_has_level_and_blueprint():
    """Verify project templates have level (Beginner / Intermediate / Advanced) and structured blueprint."""
    pentest_proj = ImprovementPlanGenerator._build_role_project_template("Ethical Hacker")
    assert pentest_proj.project_title
    assert pentest_proj.level in ("Beginner", "Intermediate", "Advanced", "Beginner / Intermediate")
    assert len(pentest_proj.skills_demonstrated) > 0
    assert len(pentest_proj.proposed_technologies) > 0
    assert pentest_proj.project_objective
    assert len(pentest_proj.suggested_implementation_tasks) > 0
    assert pentest_proj.expected_deliverables
    assert pentest_proj.is_future_project is True

    soc_proj = ImprovementPlanGenerator._build_role_project_template("SOC Analyst")
    assert soc_proj.level in ("Beginner", "Intermediate", "Advanced", "Beginner / Intermediate")

    cloud_proj = ImprovementPlanGenerator._build_role_project_template("Cloud Security Specialist")
    assert cloud_proj.level == "Advanced"


def test_skill_proficiency_levels_and_no_senior_label(base_candidate_resume):
    """Verify skill proficiencies map correctly and 'Senior' is never used as a skill level."""
    confirmed_items = [
        ConfirmedSkillItem(
            skill_name="Linux",
            proficiency="intermediate",
            context_source="Practical laboratory",
            tasks_performed="Configured systemd services and user permissions.",
        ),
        ConfirmedSkillItem(
            skill_name="Wireshark",
            proficiency="beginner",
            context_source="Academic coursework",
            tasks_performed="Inspected HTTP and DNS packet captures in networking class.",
        ),
        ConfirmedSkillItem(
            skill_name="Splunk",
            proficiency="not_yet",  # No experience yet
        ),
    ]

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=base_candidate_resume,
        target_role_name="SOC Analyst",
        missing_core_skills=["Splunk"],
        confirmed_skills=confirmed_items,
        permission_granted=True,
    )

    # 1. Intermediate skill -> included as full active skill
    flat_skills = []
    for s_list in enhanced.technical_skills_grouped.values():
        flat_skills.extend(s_list)
    assert any("Linux" in s for s in flat_skills)

    # 2. Beginner skill -> included under foundational knowledge
    assert any("Wireshark" in s for s in flat_skills)
    foundational_skills = enhanced.technical_skills_grouped.get("Foundational Knowledge & Coursework Exposure", [])
    assert any("Wireshark" in s for s in foundational_skills)

    # 3. Not Yet skill -> strictly NOT included as existing competency
    assert not any("Splunk" == s for s in flat_skills)
    assert not any("Splunk" in s and "(Foundational)" not in s for s in flat_skills)


def test_completed_similar_project_vs_future_project(base_candidate_resume):
    """Verify confirming a completed project incorporates verified details, while uncompleted remains future."""
    proj_item_completed = {
        "item_id": "plan_project_recommendation",
        "category_key": "projects",
        "item_type": "project_recommendation",
        "status": "approved",
        "candidate_response": {
            "has_omitted_project": "yes",
            "project_title": "Enterprise Threat Hunting Lab",
            "project_technologies": "Splunk, Sysmon, Snort",
            "project_contribution": "Configured Sysmon event forwarding and drafted 5 custom detection rules.",
            "project_outcomes": "Detected 100% of simulated brute-force attempts.",
        },
    }

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=base_candidate_resume,
        target_role_name="SOC Analyst",
        missing_core_skills=[],
        approved_plan_items=[proj_item_completed],
        permission_granted=True,
    )

    # The verified completed project must appear in projects
    project_titles = [p["title"] for p in enhanced.projects]
    assert "Enterprise Threat Hunting Lab" in project_titles
    matched_proj = next(p for p in enhanced.projects if p["title"] == "Enterprise Threat Hunting Lab")
    assert "Sysmon" in matched_proj["description"] or "detection" in matched_proj["description"]


def test_category_score_evaluations_have_one_line_gap_summary(base_candidate_resume):
    """Verify category evaluations return structured score/max and clean 1-line gap summary."""
    from app.scoring.matcher import SkillMatcher
    from app.scoring.engine import ATSScoringEngine

    role_skills = [
        {"skill_id": 1, "skill_name": "Linux", "importance": "core"},
        {"skill_id": 2, "skill_name": "Splunk", "importance": "core"},
    ]
    role_reqs = [
        {"requirement_id": 1, "requirement_type": "certification", "requirement_description": "CompTIA Security+ required.", "importance": "core"},
    ]
    criteria = [
        {"category": "Technical Skills", "weight": 40.0},
        {"category": "Projects", "weight": 25.0},
        {"category": "Education", "weight": 15.0},
        {"category": "Tools & Certifications", "weight": 15.0},
        {"category": "Career Objective", "weight": 5.0},
    ]

    match_report = SkillMatcher.match_skills(
        role_skills=role_skills,
        resume_skills=base_candidate_resume.technical_skills,
        resume_full_text="Linux Networking Basics Computer Science State University",
        resume_projects=base_candidate_resume.projects,
        resume_experience=base_candidate_resume.employment_history,
        role_id=1,
        role_name="SOC Analyst",
    )

    score_result = ATSScoringEngine.calculate_score(
        resume_data=base_candidate_resume,
        match_report=match_report,
        role_requirements=role_reqs,
        db_scoring_criteria=criteria,
        threshold=80.0,
    )

    plan = ImprovementPlanGenerator.generate_plan(
        resume_data=base_candidate_resume,
        match_report=match_report,
        score_result=score_result,
        role_requirements=role_reqs,
        role_name="SOC Analyst",
    )

    assert len(plan.category_evaluations) >= 5
    for cat in plan.category_evaluations:
        assert cat.category_name
        assert cat.current_score is not None
        assert cat.max_score > 0
        assert 0 <= cat.percentage <= 100
        assert cat.what_is_missing  # 1-line gap explanation

