import os
import psycopg2

db_config = {
    "dbname": os.getenv("DB_NAME", "funding_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),  # Pulls from environment variable DB_PASSWORD
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Query 1: Fetch all funding sources and their opportunity counts
    print("\n--- Funding Sources Summary ---")
    cursor.execute("""
        SELECT s.name, s.category, COUNT(o.id) AS total_opportunities
        FROM funding_sources s
        LEFT JOIN funding_opportunities o ON s.id = o.source_id
        GROUP BY s.id, s.name, s.category;
    """)
    for row in cursor.fetchall():
        print(f"Source: {row[0]} | Category: {row[1]} | Active Grants: {row[2]}")

    # Query 2: Fetch top funding opportunities sorted by max amount
    print("\n--- Top Funding Opportunities ---")
    cursor.execute("""
        SELECT title, amount_min, amount_max, deadline, eligibility_summary
        FROM funding_opportunities
        ORDER BY amount_max DESC;
    """)
    for row in cursor.fetchall():
        print(f"Grant: {row[0]} | Range: ${row[1]:,.2f} - ${row[2]:,.2f} | Deadline: {row[3]}")

except Exception as e:
    print("Error querying database:", e)
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()