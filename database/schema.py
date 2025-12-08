"""
Database Schema Module for Mailroom Management Application.

This module contains the CREATE TABLE statements for all database tables.
It defines the structure/architecture of the database.
"""

from database.connection import get_connection


def create_tables():
    """
    Create all required tables in the database.
    Tables:
        - Residents: Stores resident information (id, name, email, unit).
        - StaffLogin: Stores staff credentials (username, password).
        - Packages: Stores package delivery information.
        - UnknownPackages: Stores packages with no identified resident.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ============================================================
    # RESIDENTS TABLE
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Residents (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            unit_number INTEGER NOT NULL
        )
    """)

    # ============================================================
    # STAFF LOGIN TABLE
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS StaffLogin (
            staff_username TEXT PRIMARY KEY,
            staff_password TEXT NOT NULL
        )
    """)

    # ============================================================
    # PACKAGES TABLE
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Packages (
            package_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id INTEGER NOT NULL,
            carrier TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (resident_id) REFERENCES Residents(id)
        )
    """)

    # ============================================================
    # UNKNOWN PACKAGES TABLE
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UnknownPackages (
            unknown_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_on_label TEXT NOT NULL,
            carrier TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            assigned_resident_id INTEGER
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] All tables created successfully!")


if __name__ == "__main__":
    create_tables()
