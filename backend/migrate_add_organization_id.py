"""
One-time migration script: add the missing organization_id column to the
shared users table.

Background: the newer branch lineage (Mayank -> kanishka -> Kesiya-Sunny)
added an `organizations` table and a `users.organization_id` foreign key
to it. The original Milestone 1 users table (which built the live shared
innovafund_db) predates this and doesn't have the column.

The `organizations` table itself was already auto-created by SQLAlchemy's
create_all() when a newer-lineage app first connected, so this script only
needs to add the missing column to the existing users table.

Safe to run multiple times - checks the current state first and does
nothing if the column already exists.

Usage:
    python migrate_add_organization_id.py
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


def table_exists(conn, table: str) -> bool:
    result = conn.execute(text("""
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = :table
    """), {"table": table})
    return result.first() is not None


def main():
    with engine.connect() as conn:
        if not table_exists(conn, "organizations"):
            print("ERROR: 'organizations' table not found. Expected it to already exist "
                  "(created by an app's SQLAlchemy create_all()). Check DATABASE_URL.")
            return

        if column_exists(conn, "users", "organization_id"):
            print("Already migrated - users.organization_id exists. Nothing to do.")
            return

        print("Adding users.organization_id column (nullable, FK to organizations.id)...")
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN organization_id INTEGER
            REFERENCES organizations(id) ON DELETE SET NULL
        """))
        conn.commit()
        print("Done. Verifying...")

        if column_exists(conn, "users", "organization_id"):
            print("Verified: migration successful.")
        else:
            print("WARNING: post-migration check failed - please inspect the users table manually.")


if __name__ == "__main__":
    main()