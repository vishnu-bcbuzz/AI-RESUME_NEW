import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

try:
    with psycopg.connect(DATABASE_URL, connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    current_database(),
                    current_user,
                    version();
            """)

            database, user, version = cur.fetchone()

            print("Database connection successful!")
            print("Database:", database)
            print("Connected user:", user)
            print("PostgreSQL:", version.split(",")[0])

except Exception as error:
    print("Database connection failed.")
    print("Error:", error)
    