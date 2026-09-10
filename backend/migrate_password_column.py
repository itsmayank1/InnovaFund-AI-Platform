"""
One-time migration script: reconcile the users table's password column name.

Background: two branch lineages diverged on what to call this column.
- Milestone 1 (original saumyaa-dev model, which actually created the live
  shared innovafund_db) used: hashed_password
- Mayank's branch (and everything built on top of it: kanishka, Kesiya-Sunny)
  uses: password_hash

This script renames the live column from hashed_password to password_hash,
so the shared DB matches the newer, more widely-adopted lineage. Safe to
run multiple times — it checks the current column name first and does
nothing if the rename has already happened.

Usage:
    python migrate_password_column.py
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
        has_old = column_exists(conn, "users", "hashed_password")
        has_new = column_exists(conn, "users", "password_hash")

        if has_new and not has_old:
            print("Already migrated — 'password_hash' exists, 'hashed_password' does not. Nothing to do.")
            return

        if not has_old:
            print("ERROR: 'hashed_password' column not found on users table. "
                  "Check DATABASE_URL and confirm you're connected to the right database.")
            return

        if has_old and has_new:
            print("ERROR: both 'hashed_password' and 'password_hash' exist on users table. "
                  "This needs manual review — refusing to guess which is correct.")
            return

        print("Renaming users.hashed_password -> users.password_hash ...")
        conn.execute(text("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash"))
        conn.commit()
        print("Done. Verifying...")

        if column_exists(conn, "users", "password_hash") and not column_exists(conn, "users", "hashed_password"):
            print("Verified: migration successful.")
        else:
            print("WARNING: post-migration check failed — please inspect the users table manually.")


if __name__ == "__main__":
    main()