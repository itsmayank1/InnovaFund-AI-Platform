"""
One-time migration script: add the remaining missing columns to the
shared users table so it fully matches the newer branch lineage's User
model (Mayank -> kanishka -> Kesiya-Sunny).

After the earlier password_hash and organization_id fixes, comparison
against the live table showed two columns still missing:
  - is_active (Boolean, default True)
  - updated_at (Timestamp, defaults to now(), should update on row change)

Safe to run multiple times - checks current state first and only adds
what's actually missing.

Usage:
    python migrate_add_is_active_updated_at.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://innovafund_user:innovafund_pass@localhost:5433/innovafund_db"
)

engine = create_engine(DATABASE_URL)


def column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(text("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = :table AND column_name = :column
    """), {"table": table, "column": column})
    return result.first() is not None


def main():
    with engine.connect() as conn:
        added_any = False

        if not column_exists(conn, "users", "is_active"):
            print("Adding users.is_active (boolean, default true)...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """))
            added_any = True
        else:
            print("users.is_active already exists, skipping.")

        if not column_exists(conn, "users", "updated_at"):
            print("Adding users.updated_at (timestamptz, default now())...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now()
            """))
            added_any = True
        else:
            print("users.updated_at already exists, skipping.")

        if added_any:
            conn.commit()
            print("Done.")
        else:
            print("Nothing to do - both columns already present.")

        print("Verifying final users table schema...")
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users' ORDER BY ordinal_position
        """))
        print([row[0] for row in result])


if __name__ == "__main__":
    main()