"""
Database Repository Module for Mailroom Management Application.

This module implements the Repository Pattern (Data Access Layer).
The application uses this module to interact with the database,
abstracting away raw SQL from the business logic layer.
"""

from typing import List, Optional
import sqlite3
from database.connection import get_connection


# ============================================================
# STAFF LOGIN REPOSITORY
# ============================================================

def get_staff_by_username(username: str) -> Optional[sqlite3.Row]:
    """
    Fetch a staff member by username.
    
    Args:
        username: The staff username to look up.
    
    Returns:
        sqlite3.Row with staff data or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StaffLogin WHERE staff_username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result


# ============================================================
# RESIDENTS REPOSITORY
# ============================================================

def get_resident_by_id(resident_id: int) -> Optional[sqlite3.Row]:
    """
    Fetch a resident by ID.
    
    Args:
        resident_id: The resident ID to look up.
    
    Returns:
        sqlite3.Row with resident data or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Residents WHERE id = ?", (resident_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_residents() -> List[sqlite3.Row]:
    """
    Fetch all residents.
    
    Returns:
        List of sqlite3.Row with all resident data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Residents ORDER BY full_name")
    results = cursor.fetchall()
    conn.close()
    return results


def search_residents(query: str) -> List[sqlite3.Row]:
    """
    Search residents by name (fuzzy match).
    
    Args:
        query: The search string.
    
    Returns:
        List of matching residents.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Residents WHERE full_name LIKE ? ORDER BY full_name",
        (f"%{query}%",)
    )
    results = cursor.fetchall()
    conn.close()
    return results


# ============================================================
# PACKAGES REPOSITORY
# ============================================================

def create_package(resident_id: int, carrier: str, delivery_date: str) -> int:
    """
    Create a new package record.
    
    Args:
        resident_id: The resident ID to associate with the package.
        carrier: The carrier name (UPS, FedEx, etc.).
        delivery_date: The delivery date string.
    
    Returns:
        The package_id of the newly created package.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Packages (resident_id, carrier, delivery_date, status)
        VALUES (?, ?, ?, 'Pending')
        """,
        (resident_id, carrier, delivery_date)
    )
    package_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return package_id


def get_pending_packages() -> List[sqlite3.Row]:
    """
    Fetch all packages with 'Pending' status, joined with resident info.
    
    Returns:
        List of pending packages with resident name and unit.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.*, r.full_name, r.unit_number
        FROM Packages p
        JOIN Residents r ON p.resident_id = r.id
        WHERE p.status = 'Pending'
        ORDER BY p.delivery_date DESC
        """
    )
    results = cursor.fetchall()
    conn.close()
    return results


def mark_package_picked_up(package_id: int) -> bool:
    """
    Update a package status to 'PickedUp'.
    
    Args:
        package_id: The package ID to update.
    
    Returns:
        True if update was successful, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Packages SET status = 'PickedUp' WHERE package_id = ?",
        (package_id,)
    )
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_package_by_id(package_id: int) -> Optional[sqlite3.Row]:
    """
    Fetch a package by ID.
    
    Args:
        package_id: The package ID to look up.
    
    Returns:
        sqlite3.Row with package data or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Packages WHERE package_id = ?", (package_id,))
    result = cursor.fetchone()
    conn.close()
    return result


# ============================================================
# UNKNOWN PACKAGES REPOSITORY
# ============================================================

def log_unknown_package(name_on_label: str, carrier: str, delivery_date: str) -> int:
    """
    Log a package with no identified resident.
    
    Args:
        name_on_label: The name written on the package label.
        carrier: The carrier name.
        delivery_date: The delivery date string.
    
    Returns:
        The unknown_id of the newly created record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO UnknownPackages (name_on_label, carrier, delivery_date)
        VALUES (?, ?, ?)
        """,
        (name_on_label, carrier, delivery_date)
    )
    unknown_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return unknown_id


def get_unknown_packages() -> List[sqlite3.Row]:
    """
    Fetch all unassigned unknown packages.
    
    Returns:
        List of unknown packages that haven't been assigned to a resident.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM UnknownPackages WHERE assigned_resident_id IS NULL ORDER BY delivery_date DESC"
    )
    results = cursor.fetchall()
    conn.close()
    return results


def assign_unknown_to_resident(unknown_id: int, resident_id: int) -> bool:
    """
    Assign an unknown package to a resident.
    This:
    1. Updates the UnknownPackages record with the assigned_resident_id.
    2. Creates a new Package record for the resident.
    
    Args:
        unknown_id: The unknown package ID.
        resident_id: The resident ID to assign to.
    
    Returns:
        True if successful, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get the unknown package info
    cursor.execute("SELECT * FROM UnknownPackages WHERE unknown_id = ?", (unknown_id,))
    unknown_pkg = cursor.fetchone()

    if not unknown_pkg:
        conn.close()
        return False

    # Update the unknown package record
    cursor.execute(
        "UPDATE UnknownPackages SET assigned_resident_id = ? WHERE unknown_id = ?",
        (resident_id, unknown_id)
    )

    # Create a new official package
    cursor.execute(
        """
        INSERT INTO Packages (resident_id, carrier, delivery_date, status)
        VALUES (?, ?, ?, 'Pending')
        """,
        (resident_id, unknown_pkg['carrier'], unknown_pkg['delivery_date'])
    )

    conn.commit()
    conn.close()
    return True


# ============================================================
# HISTORY / SEARCH REPOSITORY
# ============================================================

def search_history(name_query: str = None, unit_query: int = None) -> List[sqlite3.Row]:
    """
    Search package history by resident name or unit number.
    
    Args:
        name_query: Optional name to search for (fuzzy match).
        unit_query: Optional unit number to filter by.
    
    Returns:
        List of packages matching the criteria.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT p.*, r.full_name, r.unit_number
        FROM Packages p
        JOIN Residents r ON p.resident_id = r.id
        WHERE 1=1
    """
    params = []

    if name_query:
        query += " AND r.full_name LIKE ?"
        params.append(f"%{name_query}%")

    if unit_query:
        query += " AND r.unit_number = ?"
        params.append(unit_query)

    query += " ORDER BY p.delivery_date DESC"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()
    return results
