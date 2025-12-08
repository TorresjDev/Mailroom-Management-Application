"""
Streamlit Frontend for Mailroom Management Application (V2).

Includes:
- Staff & Resident Portals
- Card-based Dashboard
- Interactive Pickup Flow
- Unknown Package Resolution
- Staff Creation
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
API_URL = "http://127.0.0.1:8000"
st.set_page_config(
    page_title="BuffTeks Mailroom",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLES (Custom CSS for Cards)
# ============================================================
st.markdown("""
<style>
    .pkg-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .pkg-card.pickedup { border-left-color: #00cc66; }
    .pkg-card.pending { border-left-color: #ffaa00; }
    .pkg-card.unknown { border-left-color: #ff4b4b; }
    
    .card-title { font-weight: bold; font-size: 1.1em; }
    .card-meta { font-size: 0.9em; color: #666; }
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        color: white;
    }
    .badge-pending { background-color: #ffaa00; }
    .badge-pickedup { background-color: #00cc66; }
    .badge-unknown { background-color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE MANAGEMENT
# ============================================================
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None  # None, 'staff', 'resident'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'selected_package' not in st.session_state:
    st.session_state.selected_package = None


# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def navigate_to(page, pkg=None):
    st.session_state.page = page
    st.session_state.selected_package = pkg
    st.rerun()

def logout():
    st.session_state.auth_status = None
    st.session_state.user_info = {}
    st.session_state.page = "dashboard"
    st.rerun()

# ============================================================
# AUTHENTICATION FLOWS (UI Only currently)
# ============================================================
def login_page():
    st.title("📦 BuffTeks Mailroom Portal")
    
    tab_staff, tab_resident = st.tabs(["🔒 Staff Login", "🏠 Resident Portal"])
    
    # STAFF LOGIN
    with tab_staff:
        with st.form("staff_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login as Staff"):
                try:
                    r = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
                    if r.status_code == 200 and r.json()["success"]:
                        st.session_state.auth_status = 'staff'
                        st.session_state.user_info = {"name": username}
                        st.rerun()
                    else:
                        st.error("Invalid Credentials")
                except:
                    st.error("Backend offline")

    # RESIDENT LOGIN (Placeholder logic until backend is ready)
    with tab_resident:
        st.info("Enter your details to view your package history.")
        with st.form("res_login"):
            full_name = st.text_input("Full Name")
            unit = st.number_input("Unit Number", min_value=100, step=1)
            email = st.text_input("Email")
            
            if st.form_submit_button("Access My Mail"):
                # TODO: Implement Backend Verification
                # For now, we simulate success if fields are filled
                if full_name and unit and email:
                    st.session_state.auth_status = 'resident'
                    st.session_state.user_info = {"name": full_name, "unit": unit, "email": email}
                    st.rerun()
                else:
                    st.warning("Please fill all fields exactly as registered.")

# ============================================================
# STAFF DASHBOARD COMPONENTS
# ============================================================
def render_package_card(pkg, is_staff=True):
    """Renders a single package card."""
    status_color = "pending"
    if pkg['status'] == 'PickedUp': status_color = "pickedup"
    
    # Card Container
    with st.container():
        cols = st.columns([4, 1])
        
        # Details
        with cols[0]:
            st.markdown(f"""
            <div class="pkg-card {status_color}">
                <div class="card-title">{pkg['full_name']} (Unit {pkg['unit_number']})</div>
                <div class="card-meta">
                    <b>Carrier:</b> {pkg['carrier']} | <b>Arrived:</b> {pkg['delivery_date']}<br>
                    <span class="status-badge badge-{status_color}">{pkg['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Actions
        with cols[1]:
            if is_staff and pkg['status'] == 'Pending':
                if st.button("Pickup", key=f"btn_{pkg['package_id']}"):
                    navigate_to("confirm_pickup", pkg)
            elif is_staff:
                st.button("Details", key=f"det_{pkg['package_id']}", on_click=navigate_to, args=("package_detail", pkg))

def staff_dashboard():
    # Sidebar Navigation
    with st.sidebar:
        st.header(f"Admin: {st.session_state.user_info.get('name')}")
        if st.button("📦 Dashboard"): navigate_to("dashboard")
        if st.button("➕ Log Package"): navigate_to("log_package")
        if st.button("❓ Unknown Pkgs"): navigate_to("unknown_dashboard")
        if st.button("👤 Create Staff"): navigate_to("create_staff")
        st.divider()
        if st.button("Logout"): logout()

    # Page Routing
    if st.session_state.page == "dashboard":
        st.title("📦 Package Dashboard")
        
        # Filter Bar
        col1, col2 = st.columns([3, 1])
        search = col1.text_input("🔍 Search Packages", placeholder="Name or Unit...")
        filter_status = col2.selectbox("Status", ["All", "Pending", "PickedUp"])
        
        # Fetch Data
        try:
            params = {"name": search} if search else {}
            r = requests.get(f"{API_URL}/history", params=params)
            if r.status_code == 200:
                packages = r.json()["packages"]
                
                # Client-Side Filter
                if filter_status != "All":
                    packages = [p for p in packages if p['status'] == filter_status]
                
                # Render Grid
                if not packages:
                    st.info("No packages found.")
                else:
                    for pkg in packages:
                        render_package_card(pkg)
        except Exception as e:
            st.error(f"Connection Error: {e}")

    elif st.session_state.page == "log_package":
        st.title("➕ Log New Package")
        if st.button("← Back"): navigate_to("dashboard")
        
        # Log Form (Existing Logic)
        try:
            res = requests.get(f"{API_URL}/residents")
            if res.status_code == 200:
                residents = res.json()["residents"]
                res_opts = {f"{r['full_name']} (Unit {r['unit_number']})": r['id'] for r in residents}
                
                with st.form("log_pkg"):
                    sel_res = st.selectbox("Resident", options=list(res_opts.keys()))
                    carrier = st.selectbox("Carrier", ["USPS", "UPS", "FedEx", "Amazon", "DHL"])
                    if st.form_submit_button("Log & Notify"):
                        # Just mockup for now since we are frontend focused
                        # Real call: requests.post(...)
                        r = requests.post(f"{API_URL}/packages", json={"resident_id": res_opts[sel_res], "carrier": carrier}) 
                        if r.status_code == 200:
                            st.success("Package Logged!")
                        else:
                            st.error("Failed")
        except:
            st.error("API Error")

    elif st.session_state.page == "confirm_pickup":
        pkg = st.session_state.selected_package
        st.title("✅ Confirm Pickup")
        st.info("Please verify the resident's identity before releasing.")
        
        with st.container(border=True):
            st.markdown(f"**Resident:** {pkg['full_name']}")
            st.markdown(f"**Unit:** {pkg['unit_number']}")
            st.markdown(f"**Package ID:** #{pkg['package_id']}")
            st.markdown(f"**Carrier:** {pkg['carrier']}")
        
        col1, col2 = st.columns(2)
        if col1.button("✅ Confirm Release & Sign"):
            r = requests.post(f"{API_URL}/packages/{pkg['package_id']}/pickup")
            if r.status_code == 200:
                st.success("Released!")
                navigate_to("dashboard")
            else:
                st.error("Error")
        
        if col2.button("❌ Cancel"):
            navigate_to("dashboard")

    elif st.session_state.page == "unknown_dashboard":
        st.title("❓ Unknown Packages")
        if st.button("← Back"): navigate_to("dashboard")
        
        # 1. Log New Unknown
        with st.expander("➕ Log New Unknown Package"):
            with st.form("new_unknown"):
                label = st.text_input("Name on Label")
                carrier = st.selectbox("Carrier", ["USPS", "UPS", "FedEx"])
                if st.form_submit_button("Log Unknown"):
                    requests.post(f"{API_URL}/unknown", json={"name_on_label": label, "carrier": carrier})
                    st.rerun()

        # 2. List & Resolve
        r = requests.get(f"{API_URL}/unknown")
        if r.status_code == 200:
            unknowns = r.json()["unknown_packages"]
            for u in unknowns:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"**ID:** {u['unknown_id']} | **Label:** `{u['name_on_label']}`")
                    if c2.button("Resolve", key=f"res_{u['unknown_id']}"):
                        navigate_to("resolve_unknown", u)
        
    elif st.session_state.page == "resolve_unknown":
        u = st.session_state.selected_package
        st.title("🕵️ Resolve Unknown Package")
        st.write(f"Package for: **{u['name_on_label']}** (ID: {u['unknown_id']})")
        
        # Fetch residents
        res = requests.get(f"{API_URL}/residents")
        if res.status_code == 200:
            residents = res.json()["residents"]
            res_opts = {f"{r['full_name']} (Unit {r['unit_number']})": r['id'] for r in residents}
            
            with st.form("assign"):
                target = st.selectbox("Assign to Resident:", list(res_opts.keys()))
                if st.form_submit_button("Assign"):
                    requests.post(f"{API_URL}/unknown/assign", json={"unknown_id": u['unknown_id'], "resident_id": res_opts[target]})
                    st.success("Assigned!")
                    navigate_to("unknown_dashboard")

    elif st.session_state.page == "create_staff":
        st.title("👤 Create Staff Account")
        if st.button("← Back"): navigate_to("dashboard")
        
        with st.form("new_staff"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            if st.form_submit_button("Create Account"):
                # TODO: Needs backend endpoint
                st.info("Backend endpoint for staff creation pending.")


# ============================================================
# RESIDENT DASHBOARD
# ============================================================
def resident_dashboard():
    user = st.session_state.user_info
    st.sidebar.header(f"Resident: {user.get('name')}")
    st.sidebar.write(f"Unit: {user.get('unit')}")
    if st.sidebar.button("Logout"): logout()
    
    st.title(f"👋 Welcome, {user.get('name')}")
    st.write("Here are your packages:")
    
    # Needs Backend Query Implementation
    st.warning("Feature pending: View Personal Packages (Backend endpoint needed)")
    
    # Mockup of what it WILL look like
    st.markdown("### 📦 My Packages")
    st.info("No packages found.")


# ============================================================
# MAIN ROUTER
# ============================================================
if st.session_state.auth_status == 'staff':
    staff_dashboard()
elif st.session_state.auth_status == 'resident':
    resident_dashboard()
else:
    login_page()
