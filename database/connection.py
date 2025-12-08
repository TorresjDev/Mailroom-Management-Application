"""
Database Connection Module for Mailroom Management Application.

This module provides a centralized way to manage database connections.
Used by schema, seed, repository, and any other module needing DB access.
"""

import sqlite3
import os

# ============================================================
# CONFIGURATION
# ============================================================
# Database file location (relative to project root)
DB_PATH = os.path.join(os.path.dirname(__file__), "mailroom.db")


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def get_db_path() -> str:
    """
    Returns the absolute path to the database file.
    
    Returns:
        str: The path to the mailroom.db file.
    """
    return DB_PATH
