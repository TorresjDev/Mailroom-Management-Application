"""
Pydantic Models for Mailroom Management Application.

These models define the data structures for API request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, List


# ============================================================
# AUTHENTICATION MODELS
# ============================================================

class LoginRequest(BaseModel):
    """Request model for staff login."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login."""
    success: bool
    message: str
    username: Optional[str] = None


# ============================================================
# RESIDENT MODELS
# ============================================================

class Resident(BaseModel):
    """Model representing a resident."""
    id: int
    full_name: str
    email: str
    unit_number: int


class ResidentList(BaseModel):
    """Response model for list of residents."""
    residents: List[Resident]


# ============================================================
# PACKAGE MODELS
# ============================================================

class PackageCreate(BaseModel):
    """Request model for creating a new package."""
    resident_id: int
    carrier: str


class Package(BaseModel):
    """Model representing a package."""
    package_id: int
    resident_id: int
    carrier: str
    delivery_date: str
    status: str
    full_name: Optional[str] = None
    unit_number: Optional[int] = None


class PackageList(BaseModel):
    """Response model for list of packages."""
    packages: List[Package]


class PickupResponse(BaseModel):
    """Response model for package pickup."""
    success: bool
    message: str


# ============================================================
# UNKNOWN PACKAGE MODELS
# ============================================================

class UnknownPackageCreate(BaseModel):
    """Request model for logging an unknown package."""
    name_on_label: str
    carrier: str


class UnknownPackage(BaseModel):
    """Model representing an unknown package."""
    unknown_id: int
    name_on_label: str
    carrier: str
    delivery_date: str
    assigned_resident_id: Optional[int] = None


class UnknownPackageList(BaseModel):
    """Response model for list of unknown packages."""
    unknown_packages: List[UnknownPackage]


class AssignUnknownRequest(BaseModel):
    """Request model for assigning unknown package to resident."""
    unknown_id: int
    resident_id: int


# ============================================================
# HISTORY/SEARCH MODELS
# ============================================================

class HistorySearchRequest(BaseModel):
    """Request model for history search."""
    name: Optional[str] = None
    unit: Optional[int] = None


# ============================================================
# NEW: RESIDENT PORTAL MODELS
# ============================================================

class ResidentLoginRequest(BaseModel):
    """Request model for resident login (3-factor match)."""
    full_name: str
    email: str
    unit_number: int


class ResidentLoginResponse(BaseModel):
    """Response for resident login."""
    success: bool
    message: str
    resident: Optional[Resident] = None


class StaffRegisterRequest(BaseModel):
    """Request model for creating new staff."""
    username: str
    password: str


class ResidentCreateRequest(BaseModel):
    """Request model for creating a new resident."""
    full_name: str
    email: str
    unit_number: int
