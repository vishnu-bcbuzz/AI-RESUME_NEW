
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

try:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)

            tables = cur.fetchall()

            print("\nConnected to Neon successfully!")
            print("Tables found in the database:")

            if tables:
                for table in tables:
                    print("-", table[0])
            else:
                print("No tables found yet.")

except Exception as error:
    print("Database check failed:", error)
