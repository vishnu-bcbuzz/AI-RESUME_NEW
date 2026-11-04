"""Automated tests for Neon database connection and repository queries."""

import pytest
from app.database.connection import db_manager
from app.database.repositories import role_repository


def test_database_health():
    """Verifies that Neon PostgreSQL connection is alive and healthy."""
    health = db_manager.check_health()
    assert health["status"] == "healthy"
    assert "latency_ms" in health
    assert health["latency_ms"] >= 0


def test_role_listing():
    """Verifies that all 74 cybersecurity roles are retrieved from Neon."""
    roles = role_repository.list_roles()
    assert len(roles) >= 74
    role_names = [r["role_name"] for r in roles]
    assert "Ethical Hacker" in role_names
    assert "Junior Penetration Tester" in role_names


def test_role_skills_retrieval():
    """Verifies skill retrieval with importance classification for Role 1."""
    skills = role_repository.get_role_skills(1)
    assert len(skills) > 0
    importances = {s["importance"].lower() for s in skills}
    assert "core" in importances or "preferred" in importances


def test_role_requirements_retrieval():
    """Verifies role requirements retrieval from Neon."""
    reqs = role_repository.get_role_requirements(1)
    assert len(reqs) > 0
    assert any("education" in r["requirement_type"].lower() for r in reqs)


def test_scoring_criteria_retrieval():
    """Verifies that scoring criteria sum to 100%."""
    criteria = role_repository.get_scoring_criteria(1)
    assert len(criteria) == 5
    total_weight = sum(c["weight"] for c in criteria)
    assert abs(total_weight - 100.0) < 0.01


def test_full_role_profile():
    """Verifies full profile packaging."""
    profile = role_repository.get_role_full_profile(1)
    assert profile is not None
    assert profile["role_name"] == "Ethical Hacker"
    assert "skill_counts" in profile
    assert profile["skill_counts"]["total"] == len(profile["skills"])
