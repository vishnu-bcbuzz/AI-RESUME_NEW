"""Database repository layer for FUTRSEC cybersecurity roles and requirements.

All queries use parameterized SQL against Neon PostgreSQL.
No queries use raw string concatenation or expose credentials.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import psycopg
from app.database.connection import db_manager

logger = logging.getLogger("futrsec.repository")


class RoleRepository:
    """Repository for querying cybersecurity roles, skills, requirements, and criteria."""

    def __init__(self, manager=db_manager):
        self.db = manager
        self._profile_cache: Dict[int, Dict[str, Any]] = {}

    def _execute_query(self, query: str, params: tuple = (), fetch_one: bool = False) -> Any:
        """Executes a parameterized SQL query with automatic single retry on stale connection."""
        for attempt in range(2):
            try:
                with self.db.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, params)
                        if fetch_one:
                            row = cur.fetchone()
                            return dict(row) if row else None
                        return [dict(row) for row in cur.fetchall()]
            except (psycopg.OperationalError, psycopg.DatabaseError) as exc:
                err_msg = str(exc).lower()
                is_stale = any(kw in err_msg for kw in ("closed", "terminated", "broken", "connection", "server closed"))
                if attempt == 0 and is_stale:
                    logger.warning("Stale database connection encountered (%s). Retrying query with fresh connection...", exc)
                    time.sleep(0.15)
                    continue
                logger.error("Database query failed: %s", exc)
                raise

    def list_roles(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all cybersecurity job roles, optionally filtered by name search."""
        query = """
            SELECT
                role_id,
                role_name,
                role_description,
                created_at
            FROM public.job_roles
        """
        params: list[Any] = []
        if search:
            query += " WHERE role_name ILIKE %s"
            params.append(f"%{search.strip()}%")

        query += " ORDER BY role_name ASC;"
        return self._execute_query(query, tuple(params))

    def get_role_by_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single role by its primary ID."""
        query = """
            SELECT
                role_id,
                role_name,
                role_description,
                created_at
            FROM public.job_roles
            WHERE role_id = %s;
        """
        return self._execute_query(query, (role_id,), fetch_one=True)

    def get_role_skills(self, role_id: int) -> List[Dict[str, Any]]:
        """Retrieves all skills configured for a cybersecurity role."""
        query = """
            SELECT
                skill_id,
                role_id,
                skill_name,
                importance
            FROM public.role_skills
            WHERE role_id = %s
            ORDER BY
                CASE importance
                    WHEN 'core' THEN 1
                    WHEN 'preferred' THEN 2
                    WHEN 'additional' THEN 3
                    ELSE 4
                END,
                skill_name ASC;
        """
        return self._execute_query(query, (role_id,))

    def get_role_requirements(self, role_id: int) -> List[Dict[str, Any]]:
        """Retrieves formal requirements (education, etc.) for a role."""
        query = """
            SELECT
                requirement_id,
                role_id,
                requirement_type,
                requirement_description,
                importance
            FROM public.role_requirements
            WHERE role_id = %s
            ORDER BY requirement_type ASC, requirement_id ASC;
        """
        return self._execute_query(query, (role_id,))

    def get_scoring_criteria(self, role_id: int) -> List[Dict[str, Any]]:
        """Retrieves ATS scoring criteria weights for a role."""
        query = """
            SELECT
                criteria_id,
                role_id,
                category,
                weight
            FROM public.scoring_criteria
            WHERE role_id = %s
            ORDER BY category ASC;
        """
        rows = self._execute_query(query, (role_id,))
        # Convert Decimal weights to float for JSON compatibility
        return [
            {
                "criteria_id": r["criteria_id"],
                "role_id": r["role_id"],
                "category": r["category"],
                "weight": float(r["weight"]),
            }
            for r in rows
        ]

    def get_role_full_profile(self, role_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves complete role profile including skills, requirements, and criteria."""
        try:
            role = self.get_role_by_id(role_id)
            if not role:
                return self._profile_cache.get(role_id)

            skills = self.get_role_skills(role_id)
            requirements = self.get_role_requirements(role_id)
            scoring_criteria = self.get_scoring_criteria(role_id)

            profile = {
                **role,
                "skills": skills,
                "requirements": requirements,
                "scoring_criteria": scoring_criteria,
                "skill_counts": {
                    "total": len(skills),
                    "core": sum(1 for s in skills if s.get("importance", "").lower() == "core"),
                    "preferred": sum(1 for s in skills if s.get("importance", "").lower() == "preferred"),
                    "additional": sum(1 for s in skills if s.get("importance", "").lower() == "additional"),
                },
            }
            # Cache successfully retrieved profile
            self._profile_cache[role_id] = profile
            return profile
        except Exception as exc:
            if role_id in self._profile_cache:
                logger.warning("Database query failed (%s); serving role %s from profile cache.", exc, role_id)
                return self._profile_cache[role_id]
            logger.error("Failed to load role profile %s: %s", role_id, exc)
            raise


role_repository = RoleRepository()
