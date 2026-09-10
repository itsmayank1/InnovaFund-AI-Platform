import os
import psycopg2

db_config = {
    "dbname": os.getenv("DB_NAME", "funding_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

sources = [
    (1, "Government Grants", "Govt Grants", "National and local government funding programs.", "https://grants.gov"),
    (2, "Research Councils", "Research Councils", "Council grants for academic research.", "https://researchcouncils.org"),
    (3, "Innovation Funds", "Innovation Funds", "Grants aimed at driving disruptive innovation.", "https://innovationfund.org"),
    (4, "Startup Accelerators", "Startup Accelerators", "Funding and incubation for early-stage startups.", "https://accelerator.io"),
    (5, "Venture Programs", "Venture Programs", "Corporate and institutional venture funding.", "https://ventureprograms.com"),
    (6, "International Agencies", "Int'l Funding Agencies", "Global research and development grants.", "https://globalfunding.org")
]

opportunities = [
    (1, 1, "National AI Advancement Grant", "Funding for cutting-edge AI research.", 50000.00, 200000.00, "2026-12-31", "PhD required, AI focus"),
    (2, 2, "Quantum Computing Breakthrough Fund", "Grants for quantum hardware/software projects.", 100000.00, 500000.00, "2026-11-15", "Academic affiliation"),
    (3, 3, "Green Tech Innovation Seed", "Seed funding for sustainable technologies.", 25000.00, 100000.00, "2026-10-01", "Early-stage prototype"),
    (4, 4, "Biomedical Engineering Initiative", "Support for medical technology applications.", 75000.00, 300000.00, "2026-09-30", "Interdisciplinary team"),
    (5, 5, "Next-Gen Cybersecurity Fellowship", "Research support for network security.", 30000.00, 150000.00, "2026-12-01", "Open to postdocs and faculty"),
    (6, 6, "Global Climate Resilience Grant", "International fund for climate solutions.", 150000.00, 1000000.00, "2027-01-15", "International partnership mandatory")
]

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Clear existing data so script can be re-run safely without duplicate key/record errors
    cursor.execute("TRUNCATE funding_sources, funding_opportunities, eligibility_criteria RESTART IDENTITY CASCADE;")

    for s in sources:
        cursor.execute(
            """
            INSERT INTO funding_sources (id, name, category, description, website_url)
            VALUES (%s, %s, %s, %s, %s);
            """,
            s
        )

    for o in opportunities:
        cursor.execute(
            """
            INSERT INTO funding_opportunities (id, source_id, title, description, amount_min, amount_max, deadline, eligibility_summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            o
        )

    conn.commit()
    print("Database successfully refreshed and seeded with sample data!")

except Exception as e:
    print("Error seeding database:", e)
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()