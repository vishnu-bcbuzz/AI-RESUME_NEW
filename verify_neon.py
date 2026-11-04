import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

tables = [
    "job_roles",
    "role_skills",
    "role_requirements",
    "scoring_criteria",
    "role_import_staging",
    "role_skills_staging",
    "role_requirements_staging",
]

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        print("\nFUTRSEC NEON DATABASE VERIFICATION")
        print("-" * 45)

        for table in tables:
            cur.execute(
                f'SELECT COUNT(*) FROM public."{table}"'
            )
            count = cur.fetchone()[0]
            print(f"{table}: {count} records")

print("\nVerification completed.")