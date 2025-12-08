"""
Database Setup for Mailroom Management Application.

This file orchestrates the database initialization process:
1. Creates all tables from  schema.py
2. Seeds all data from seed.py

Run this file to initialize a fresh database.
"""

import os
from database.connection import get_db_path
from database.schema import create_tables
from database.seed import seed_all


def initialize_database(fresh_start: bool = True):
    """
    Initialize the database.
    
    Args:
        fresh_start: If True, deletes existing database before creating new one.
    """
    print("\n" + "=" * 60)
    print("    MAILROOM DATABASE INITIALIZATION")
    print("=" * 60 + "\n")

    db_path = get_db_path()

    # Remove existing database for fresh start
    if fresh_start and os.path.exists(db_path):
        os.remove(db_path)
        print("[OK] Removed existing database for fresh start.")

    # Create tables
    create_tables()

    # Seed data
    seed_all()

    print("\n" + "=" * 60)
    print("[OK] DATABASE INITIALIZATION COMPLETE!")
    print(f"Database location: {db_path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    initialize_database()
