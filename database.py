import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "humanitarian.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS field_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_date TEXT NOT NULL,
            district TEXT NOT NULL,
            upazila TEXT NOT NULL,
            affected_population INTEGER NOT NULL,
            children INTEGER NOT NULL,
            women INTEGER NOT NULL,
            persons_with_disabilities INTEGER NOT NULL,
            food_need INTEGER NOT NULL,
            water_need INTEGER NOT NULL,
            health_need INTEGER NOT NULL,
            shelter_need INTEGER NOT NULL,
            education_need INTEGER NOT NULL,
            assistance_delivered INTEGER NOT NULL,
            priority TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def seed_data():
    connection = get_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM field_assessments"
    ).fetchone()[0]

    if count > 0:
        connection.close()
        return

    data = [
        ("2026-01-15", "Cox's Bazar", "Ukhia", 18500, 7200, 6100, 420, 9200, 7800, 4100, 6500, 4800, 11800, "High"),
        ("2026-02-10", "Cox's Bazar", "Teknaf", 14200, 5400, 4700, 310, 7600, 6200, 3500, 5200, 3900, 9100, "High"),
        ("2026-02-18", "Noakhali", "Hatiya", 8700, 3300, 2800, 180, 4100, 3500, 1700, 2900, 2100, 5600, "Medium"),
        ("2026-03-05", "Bhasan Char", "Hatiya", 6200, 2400, 2100, 120, 2800, 2300, 1300, 1900, 1500, 4100, "Medium"),
        ("2026-03-20", "Sunamganj", "Tahirpur", 11300, 4500, 3800, 260, 6100, 5200, 2700, 4300, 3200, 7200, "High"),
        ("2026-04-12", "Sylhet", "Jaintiapur", 7600, 2900, 2500, 150, 3600, 3100, 1600, 2500, 1900, 5200, "Medium"),
        ("2026-05-08", "Khulna", "Koyra", 9400, 3500, 3100, 190, 4700, 3900, 2100, 3300, 2400, 6100, "Medium"),
        ("2026-06-16", "Barguna", "Patharghata", 6800, 2600, 2200, 130, 3200, 2700, 1400, 2300, 1700, 4500, "Low"),
        ("2026-07-04", "Bhola", "Char Fasson", 12500, 4800, 4100, 270, 6700, 5500, 2900, 4500, 3400, 8300, "High"),
        ("2026-07-22", "Barishal", "Mehendiganj", 8100, 3100, 2700, 160, 3900, 3300, 1800, 2700, 2000, 5500, "Medium"),
    ]

    connection.executemany("""
        INSERT INTO field_assessments (
            assessment_date,
            district,
            upazila,
            affected_population,
            children,
            women,
            persons_with_disabilities,
            food_need,
            water_need,
            health_need,
            shelter_need,
            education_need,
            assistance_delivered,
            priority
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    connection.commit()
    connection.close()


def get_assessments():
    connection = get_connection()

    rows = connection.execute("""
        SELECT *
        FROM field_assessments
        ORDER BY assessment_date DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def add_assessment(
    assessment_date,
    district,
    upazila,
    affected_population,
    children,
    women,
    persons_with_disabilities,
    food_need,
    water_need,
    health_need,
    shelter_need,
    education_need,
    assistance_delivered,
    priority
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO field_assessments (
            assessment_date,
            district,
            upazila,
            affected_population,
            children,
            women,
            persons_with_disabilities,
            food_need,
            water_need,
            health_need,
            shelter_need,
            education_need,
            assistance_delivered,
            priority
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        assessment_date,
        district,
        upazila,
        affected_population,
        children,
        women,
        persons_with_disabilities,
        food_need,
        water_need,
        health_need,
        shelter_need,
        education_need,
        assistance_delivered,
        priority
    ))

    connection.commit()
    connection.close()


def delete_assessment(assessment_id):
    connection = get_connection()

    connection.execute(
        "DELETE FROM field_assessments WHERE id = ?",
        (assessment_id,)
    )

    connection.commit()
    connection.close()