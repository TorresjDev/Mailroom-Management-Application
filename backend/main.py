"""
FastAPI Backend for Mailroom Management Application.

This is the Business Logic Tier (Tier 2).
It handles all API routes and orchestrates the application logic.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

# Import models
from backend.models import (
    LoginRequest, LoginResponse,
    Resident, ResidentList,
    PackageCreate, Package, PackageList, PickupResponse,
    UnknownPackageCreate, UnknownPackage, UnknownPackageList, AssignUnknownRequest,
)

# Import database repository
from database import repository

# Import email service
from backend.email_service import send_notification

# ============================================================
# APP INITIALIZATION
# ============================================================
app = FastAPI(
    title="Mailroom Management API",
    description="API for managing package deliveries in a university apartment complex.",
    version="1.0.0"
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Authenticate a staff member.
    
    Validates credentials against the StaffLogin table.
    """
    staff = repository.get_staff_by_username(request.username)
    
    if not staff:
        return LoginResponse(success=False, message="Invalid username")
    
    if staff['staff_password'] != request.password:
        return LoginResponse(success=False, message="Invalid password")
    
    return LoginResponse(
        success=True,
        message="Login successful",
        username=request.username
    )


# ============================================================
# RESIDENT ENDPOINTS
# ============================================================

@app.get("/residents", response_model=ResidentList)
def get_residents():
    """
    Get all residents.
    
    Returns a list of all residents for dropdown menus.
    """
    residents = repository.get_all_residents()
    return ResidentList(
        residents=[
            Resident(
                id=r['id'],
                full_name=r['full_name'],
                email=r['email'],
                unit_number=r['unit_number']
            ) for r in residents
        ]
    )


@app.get("/residents/search")
def search_residents(query: str):
    """
    Search residents by name.
    
    Args:
        query: Search string to match against resident names.
    """
    residents = repository.search_residents(query)
    return {
        "residents": [
            {
                "id": r['id'],
                "full_name": r['full_name'],
                "email": r['email'],
                "unit_number": r['unit_number']
            } for r in residents
        ]
    }


# ============================================================
# PACKAGE ENDPOINTS
# ============================================================

@app.post("/packages")
def create_package(request: PackageCreate):
    """
    Log a new package delivery.
    
    Creates a package record and sends email notification to the resident.
    """
    # Get resident info
    resident = repository.get_resident_by_id(request.resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    
    # Create package record
    delivery_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    package_id = repository.create_package(
        resident_id=request.resident_id,
        carrier=request.carrier,
        delivery_date=delivery_date
    )
    
    # CRITICAL: Send email notification
    email_sent = send_notification(resident['email'])
    
    return {
        "success": True,
        "package_id": package_id,
        "message": f"Package logged for {resident['full_name']}",
        "email_sent": email_sent
    }


@app.get("/packages/pending", response_model=PackageList)
def get_pending_packages():
    """
    Get all packages with 'Pending' status.
    
    Returns packages that haven't been picked up yet.
    """
    packages = repository.get_pending_packages()
    return PackageList(
        packages=[
            Package(
                package_id=p['package_id'],
                resident_id=p['resident_id'],
                carrier=p['carrier'],
                delivery_date=p['delivery_date'],
                status=p['status'],
                full_name=p['full_name'],
                unit_number=p['unit_number']
            ) for p in packages
        ]
    )


@app.post("/packages/{package_id}/pickup", response_model=PickupResponse)
def pickup_package(package_id: int):
    """
    Mark a package as picked up.
    
    Updates the package status to 'PickedUp'.
    """
    success = repository.mark_package_picked_up(package_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Package not found")
    
    return PickupResponse(
        success=True,
        message=f"Package {package_id} marked as picked up"
    )


# ============================================================
# UNKNOWN PACKAGE ENDPOINTS
# ============================================================

@app.post("/unknown")
def log_unknown_package(request: UnknownPackageCreate):
    """
    Log a package with no identified resident.
    """
    delivery_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unknown_id = repository.log_unknown_package(
        name_on_label=request.name_on_label,
        carrier=request.carrier,
        delivery_date=delivery_date
    )
    
    return {
        "success": True,
        "unknown_id": unknown_id,
        "message": f"Unknown package logged with name: {request.name_on_label}"
    }


@app.get("/unknown", response_model=UnknownPackageList)
def get_unknown_packages():
    """
    Get all unassigned unknown packages.
    """
    packages = repository.get_unknown_packages()
    return UnknownPackageList(
        unknown_packages=[
            UnknownPackage(
                unknown_id=p['unknown_id'],
                name_on_label=p['name_on_label'],
                carrier=p['carrier'],
                delivery_date=p['delivery_date'],
                assigned_resident_id=p['assigned_resident_id'] if p['assigned_resident_id'] else None
            ) for p in packages
        ]
    )


@app.post("/unknown/assign")
def assign_unknown_package(request: AssignUnknownRequest):
    """
    Assign an unknown package to a resident.
    
    Creates a proper Package record and marks the unknown package as resolved.
    """
    # Get resident info for email
    resident = repository.get_resident_by_id(request.resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    
    success = repository.assign_unknown_to_resident(
        unknown_id=request.unknown_id,
        resident_id=request.resident_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Unknown package not found")
    
    # Send email notification
    email_sent = send_notification(resident['email'])
    
    return {
        "success": True,
        "message": f"Package assigned to {resident['full_name']}",
        "email_sent": email_sent
    }


# ============================================================
# HISTORY ENDPOINT
# ============================================================

@app.get("/history", response_model=PackageList)
def search_history(name: Optional[str] = None, unit: Optional[int] = None):
    """
    Search package history by resident name or unit number.
    """
    packages = repository.search_history(name_query=name, unit_query=unit)
    return PackageList(
        packages=[
            Package(
                package_id=p['package_id'],
                resident_id=p['resident_id'],
                carrier=p['carrier'],
                delivery_date=p['delivery_date'],
                status=p['status'],
                full_name=p['full_name'],
                unit_number=p['unit_number']
            ) for p in packages
        ]
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Mailroom Management API is running"}
