
import os
import psycopg
from dotenv import load_dotenv
from getpass import getpass

load_dotenv()

NEON_URL = os.getenv("DATABASE_URL")

LOCAL_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "futrsec_resume",
    "user": "postgres",
    "password": getpass("Enter your local PostgreSQL password:"),
}

if not NEON_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

# Read requirements from the local database.
with psycopg.connect(**LOCAL_CONFIG) as local_conn:
    with local_conn.cursor() as cur:
        cur.execute("""
            SELECT
                jr.role_name,
                rr.requirement_type,
                rr.requirement_description,
                rr.importance
            FROM public.role_requirements AS rr
            JOIN public.job_roles AS jr
                ON jr.role_id = rr.role_id
            ORDER BY jr.role_name, rr.requirement_type;
        """)
        requirements = cur.fetchall()

print(f"Local requirements found: {len(requirements)}")

# Insert requirements into Neon without duplicating existing records.
with psycopg.connect(NEON_URL) as neon_conn:
    with neon_conn.cursor() as cur:
        # Map local role names to Neon role IDs.
        cur.execute("""
            SELECT role_id, role_name
            FROM public.job_roles;
        """)
        neon_roles = {
            name.strip(): role_id
            for role_id, name in cur.fetchall()
        }

        inserted = 0
        unmatched_roles = set()

        for role_name, req_type, description, importance in requirements:
            role_id = neon_roles.get(role_name.strip())

            if role_id is None:
                unmatched_roles.add(role_name)
                continue

            cur.execute("""
                INSERT INTO public.role_requirements (
                    role_id,
                    requirement_type,
                    requirement_description,
                    importance
                )
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM public.role_requirements
                    WHERE role_id = %s
                      AND requirement_type = %s
                      AND requirement_description = %s
                );
            """, (
                role_id,
                req_type,
                description,
                importance,
                role_id,
                req_type,
                description,
            ))

            inserted += cur.rowcount

    neon_conn.commit()

# Verify the Neon requirements count.
with psycopg.connect(NEON_URL) as neon_conn:
    with neon_conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT role_id)
            FROM public.role_requirements;
        """)
        total, roles_covered = cur.fetchone()

print(f"New requirements inserted: {inserted}")
print(f"Unmatched roles: {len(unmatched_roles)}")

if unmatched_roles:
    print("Unmatched role names:")
    for name in sorted(unmatched_roles):
        print("-", name)

print(f"Neon requirements total: {total}")
print(f"Roles covered in Neon: {roles_covered}")
print("Requirements synchronization finished.")

