"""
Streamlit Frontend for Mailroom Management Application 
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
# STYLES (Custom CSS for Status Badges)
# ============================================================
st.markdown("""
<style>
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
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


def format_time_ampm(date_string):
    """Convert datetime string from 24h to 12h AM/PM format.
    
    Examples:
        '2025-12-08 21:18:29' -> '2025-12-08 9:18:29 PM'
        '2025-12-08 09:30:00' -> '2025-12-08 9:30:00 AM'
    """
    if not date_string:
        return date_string
    try:
        # Parse the datetime string
        dt = datetime.strptime(str(date_string), "%Y-%m-%d %H:%M:%S")
        # Format with AM/PM (%-I for hour without leading zero on Unix, %#I on Windows)
        return dt.strftime("%Y-%m-%d %I:%M:%S %p").lstrip("0").replace(" 0", " ")
    except ValueError:
        # If parsing fails, return original
        return date_string

# ============================================================
# AUTHENTICATION FLOWS (UI Only currently)
# ============================================================

def login_page():
    st.title("📦 BuffTeks Mailroom Portal")

    tab_staff, tab_resident = st.tabs(["🔒 Staff Login", "🏠 Resident Portal"])

    # STAFF LOGIN
    with tab_staff:
        with st.form("staff_login"):
            username = st.text_input(
                "Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login as Staff")

        # Handle login OUTSIDE the form to avoid race condition
        if submitted:
            try:
                r = requests.post(
                    f"{API_URL}/login", json={"username": username, "password": password})
                if r.status_code == 200:
                    data = r.json()
                    if data.get("success"):
                        st.session_state.auth_status = 'staff'
                        st.session_state.user_info = {"name": username}
                        st.rerun()
                    else:
                        st.error(data.get("message", "Invalid Credentials"))
                else:
                    st.error("Invalid Credentials")
            except Exception as e:
                st.error(f"Backend offline: {e}")

    # RESIDENT LOGIN
    with tab_resident:
        st.info("Enter your details to view your package history.")
        with st.form("res_login"):
            full_name = st.text_input("Full Name")
            unit = st.number_input("Unit Number", min_value=100, step=1)
            email = st.text_input("Email")
            submitted = st.form_submit_button("Access My Mail")

        # Handle login OUTSIDE the form to avoid race condition
        if submitted:
            if full_name and unit and email:
                try:
                    r = requests.post(f"{API_URL}/resident/login", json={
                        "full_name": full_name,
                        "email": email,
                        "unit_number": int(unit)
                    })
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("success"):
                            # Store resident info including ID for package queries
                            resident_data = data.get("resident", {})
                            st.session_state.auth_status = 'resident'
                            st.session_state.user_info = {
                                "id": resident_data.get("id"),
                                "name": resident_data.get("full_name", full_name),
                                "unit": resident_data.get("unit_number", unit),
                                "email": resident_data.get("email", email)
                            }
                            st.rerun()
                        else:
                            st.error(
                                data.get("message", "Invalid credentials. Verify your name, email, and unit number are correct."))
                    else:
                        st.error(
                            "Invalid credentials. Verify your name, email, and unit number are correct.")
                except Exception as e:
                    st.error(f"Backend offline: {e}")
            else:
                st.warning("Please fill all fields exactly as registered.")

# ============================================================
# STAFF DASHBOARD COMPONENTS
# ============================================================

def render_package_card(pkg, is_staff=True, is_unknown=False):
    """Renders a single package card with action button inside."""
    status_color = "pending"
    if is_unknown:
        status_color = "unknown"
    elif pkg.get('status') == 'PickedUp':
        status_color = "pickedup"

    if is_unknown:
        btn_text = "🔴 Resolve"
        btn_key = f"res_{pkg['unknown_id']}"
    elif pkg.get('status') == 'Pending':
        btn_text = "🟡 Pickup"
        btn_key = f"btn_{pkg['package_id']}"
    else:
        btn_text = "🟢 Details"
        btn_key = f"det_{pkg['package_id']}"

    # Card with button inside - full width
    # The CSS uses :has() selector to style buttons based on the badge class in the same container
    with st.container(border=True):
        col_info, col_btn = st.columns([5, 1])

        with col_info:
            if is_unknown:
                st.markdown(f"**{pkg['name_on_label']}** (Unknown Resident)")
                st.caption(
                    f"**Package Delivery Carrier:** {pkg['carrier']} | **Package Arrived At:** {format_time_ampm(pkg['delivery_date'])}")
                st.markdown(
                    f'<span class="status-badge badge-unknown">Unknown</span>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f"**{pkg['full_name']}** (Unit {pkg['unit_number']})")
                st.caption(
                    f"**Package Delivery Carrier:** {pkg['carrier']} | **Package Arrived At:** {format_time_ampm(pkg['delivery_date'])}")
                st.markdown(
                    f'<span class="status-badge badge-{status_color}">{pkg["status"]}</span>', unsafe_allow_html=True)

        with col_btn:
            if is_staff:
                if is_unknown:
                    if st.button(btn_text, key=btn_key, use_container_width=True):
                        navigate_to("resolve_unknown", pkg)
                elif pkg.get('status') == 'Pending':
                    if st.button(btn_text, key=btn_key, use_container_width=True):
                        navigate_to("confirm_pickup", pkg)
                else:
                    if st.button(btn_text, key=btn_key, use_container_width=True):
                        navigate_to("package_detail", pkg)


def staff_dashboard():
    # Sidebar Navigation
    with st.sidebar:
        st.header(f"Admin: {st.session_state.user_info.get('name')}")
        if st.button("📦 Dashboard"):
            navigate_to("dashboard")
        if st.button("➕ Log Package"):
            navigate_to("log_package")
        if st.button("✅ Confirm Pickups"):
            st.session_state.selected_package = None  # Clear any pre-selection
            navigate_to("confirm_pickup")
        st.divider()
        st.caption("Management")
        if st.button("👤 Create Staff"):
            navigate_to("create_staff")
        if st.button("🏠 Create Resident"):
            navigate_to("create_resident")
        st.divider()
        if st.button("Logout"):
            logout()

    # Page Routing
    if st.session_state.page == "dashboard":
        st.title("📦 Package Dashboard")

        # Search Bar
        search = st.text_input(
            "🔍 Search Packages",
            placeholder="Search by name, carrier, date, unit, status...",
            key="pkg_search"
        )

        # Filter & Sort Row
        col1, col2, col3 = st.columns([1, 1, 1])
        filter_status = col1.selectbox(
            "Filter by Status", ["All", "Pending", "PickedUp", "Unknown"])
        sort_by = col2.selectbox("Sort By", ["Date", "Name", "Status"])
        sort_order = col3.selectbox("Order", ["Descending", "Ascending"])

        # Fetch Data
        try:
            # Fetch regular packages (get all, filter client-side for dynamic search)
            r = requests.get(f"{API_URL}/history")
            packages = []
            if r.status_code == 200:
                packages = r.json()["packages"]

            # Fetch unknown packages
            r_unknown = requests.get(f"{API_URL}/unknown")
            unknown_packages = []
            if r_unknown.status_code == 200:
                unknown_packages = r_unknown.json().get("unknown_packages", [])

            # Normalize unknown packages to have consistent fields for unified display
            normalized_unknown = []
            for u in unknown_packages:
                normalized_unknown.append({
                    **u,
                    'full_name': u['name_on_label'],
                    'unit_number': 'N/A',
                    'status': 'Unknown',
                    '_is_unknown': True
                })

            # Add marker for regular packages
            for p in packages:
                p['_is_unknown'] = False

            # Combine all packages into one unified list
            all_packages = normalized_unknown + packages

            # Client-Side Filter by Status
            if filter_status != "All":
                all_packages = [
                    p for p in all_packages if p['status'] == filter_status]

            # Dynamic Search Filter (searches across ALL fields - works with single characters!)
            if search:
                search_lower = search.lower()
                filtered = []
                for p in all_packages:
                    # Search across ALL fields including unit number
                    name = p.get('full_name', p.get(
                        'name_on_label', '')).lower()
                    carrier = p.get('carrier', '').lower()
                    date = p.get('delivery_date', '').lower()
                    status = p.get('status', '').lower()
                    unit = str(p.get('unit_number', '')).lower()
                    # Package ID for regular packages
                    pkg_id = str(
                        p.get('package_id', p.get('unknown_id', ''))).lower()

                    if (search_lower in name or
                        search_lower in carrier or
                        search_lower in date or
                        search_lower in status or
                        search_lower in unit or
                            search_lower in pkg_id):
                        filtered.append(p)
                all_packages = filtered

            # Apply Sorting based on user selection
            is_descending = (sort_order == "Descending")

            if sort_by == "Date":
                all_packages.sort(key=lambda x: x.get(
                    'delivery_date', ''), reverse=is_descending)
            elif sort_by == "Name":
                all_packages.sort(key=lambda x: x.get('full_name', x.get(
                    'name_on_label', '')).lower(), reverse=is_descending)
            elif sort_by == "Status":
                # Custom order: Unknown first, then Pending, then PickedUp (or reverse)
                status_order = {"Unknown": 0, "Pending": 1, "PickedUp": 2}
                all_packages.sort(key=lambda x: status_order.get(
                    x.get('status', ''), 3), reverse=is_descending)

            # Render unified package list
            if not all_packages:
                st.info("No packages found matching your criteria.")
            else:
                st.caption(f"Showing {len(all_packages)} package(s)")
                for pkg in all_packages:
                    render_package_card(
                        pkg, is_staff=True, is_unknown=pkg.get('_is_unknown', False))

        except Exception as e:
            st.error(f"Connection Error: {e}")

    elif st.session_state.page == "log_package":
        st.title("➕ Log Package")
        if st.button("← Back"):
            navigate_to("dashboard")

        # Tabbed interface for Known vs Unknown packages
        tab_known, tab_unknown = st.tabs(["📋 Log Known Package", "❓ Log Unknown Package"])

        # ==================== TAB 1: Known Package ====================
        with tab_known:
            st.subheader("Log Package for Existing Resident")
            st.info("Select a resident and carrier to log a new package arrival.")

            try:
                res = requests.get(f"{API_URL}/residents")
                if res.status_code == 200:
                    residents = res.json()["residents"]
                    if not residents:
                        st.warning("No residents found. Create a resident first.")
                    else:
                        res_opts = {
                            f"{r['full_name']} (Unit {r['unit_number']})": r['id'] for r in residents}

                        with st.form("log_known_pkg", clear_on_submit=True):
                            sel_res = st.selectbox(
                                "Resident", options=list(res_opts.keys()),
                                placeholder="Select a resident...")
                            carrier = st.selectbox(
                                "Carrier", ["Amazon", "DHL", "FedEx", "Walmart", "USPS", "UPS"])
                            known_submitted = st.form_submit_button("📦 Log & Notify", use_container_width=True)

                        # Handle submission OUTSIDE form (Streamlit best practice)
                        if known_submitted:
                            if sel_res:
                                with st.spinner("Logging package and sending notification..."):
                                    r = requests.post(
                                        f"{API_URL}/packages", 
                                        json={"resident_id": res_opts[sel_res], "carrier": carrier})
                                    if r.status_code == 200:
                                        st.toast("Package logged successfully!", icon="📦")
                                        st.success(f"Package logged for {sel_res}! Notification sent.")
                                        st.balloons()
                                        import time
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        st.error("Failed to log package. Please try again.")
                            else:
                                st.warning("Please select a resident.")
                else:
                    st.error("Failed to load residents.")
            except Exception as e:
                st.error(f"API Error: {e}")

        # ==================== TAB 2: Unknown Package ====================
        with tab_unknown:
            st.subheader("Log Package with Unknown Recipient")
            st.info("Use this when the name on the package label doesn't match any resident.")

            with st.form("log_unknown_pkg", clear_on_submit=True):
                label_name = st.text_input(
                    "Name on Label", 
                    placeholder="Enter exactly as shown on package...")
                unknown_carrier = st.selectbox(
                    "Carrier", 
                    ["Amazon", "DHL", "FedEx", "Walmart", "USPS", "UPS"],
                    key="unknown_carrier")
                unknown_submitted = st.form_submit_button("❓ Log Unknown Package", use_container_width=True)

            # Handle submission OUTSIDE form (Streamlit best practice)
            if unknown_submitted:
                if label_name and label_name.strip():
                    with st.spinner("Logging unknown package..."):
                        r = requests.post(
                            f"{API_URL}/unknown", 
                            json={"name_on_label": label_name.strip(), "carrier": unknown_carrier})
                        if r.status_code == 200:
                            st.toast("Unknown package logged!", icon="❓")
                            st.success(f"Unknown package '{label_name}' logged. You can resolve it from the dashboard.")
                            st.balloons()
                            import time
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Failed to log unknown package. Please try again.")
                else:
                    st.warning("Please enter the name on the label.")

    elif st.session_state.page == "confirm_pickup":
        st.title("✅ Confirm Pickup")
        st.info("Select a pending package to confirm pickup.")

        if st.button("← Back to Dashboard"):
            navigate_to("dashboard")

        # Fetch all pending packages
        try:
            r = requests.get(f"{API_URL}/packages/pending")
            if r.status_code == 200:
                pending_packages = r.json()["packages"]

                if not pending_packages:
                    st.warning("No pending packages to pick up.")
                else:
                    # Fetch resident emails
                    res = requests.get(f"{API_URL}/residents")
                    residents_map = {}
                    if res.status_code == 200:
                        for resident in res.json()["residents"]:
                            residents_map[resident['id']] = resident['email']

                    # Create dropdown options
                    pkg_options = {
                        f"{p['full_name']} (Unit {p['unit_number']}) - {p['carrier']} - #{p['package_id']}": p
                        for p in pending_packages
                    }

                    # Determine default selection
                    # If came from dashboard with a selected package, find it in the list
                    pre_selected = st.session_state.selected_package
                    default_index = None

                    if pre_selected:
                        # Find the matching option
                        target_key = f"{pre_selected['full_name']} (Unit {pre_selected['unit_number']}) - {pre_selected['carrier']} - #{pre_selected['package_id']}"
                        options_list = list(pkg_options.keys())
                        if target_key in options_list:
                            default_index = options_list.index(target_key)

                    # Show dropdown - no default if came from sidebar, pre-selected if came from dashboard
                    selected = st.selectbox(
                        "Select Pending Package",
                        options=list(pkg_options.keys()),
                        index=default_index,
                        placeholder="Choose a package to confirm pickup..."
                    )

                    # Only show details if a package is selected
                    if selected:
                        pkg = pkg_options[selected]
                        resident_email = residents_map.get(
                            pkg['resident_id'], 'N/A')

                        st.divider()
                        st.subheader("📦 Package Details")

                        with st.container(border=True):
                            st.markdown(f"**Resident:** {pkg['full_name']}")
                            st.markdown(f"**Email:** {resident_email}")
                            st.markdown(f"**Unit:** {pkg['unit_number']}")
                            st.markdown(f"**Package ID:** #{pkg['package_id']}")
                            st.markdown(f"**Carrier:** {pkg['carrier']}")
                            st.markdown(f"**Arrived:** {format_time_ampm(pkg['delivery_date'])}")

                        col1, col2 = st.columns(2)
                        if col1.button("✅ Confirm Release & Sign", use_container_width=True):
                            with st.spinner("Processing pickup and sending notification..."):
                                r = requests.post(
                                    f"{API_URL}/packages/{pkg['package_id']}/pickup")
                                if r.status_code == 200:
                                    st.toast(
                                        "📧 Email notification sent to resident!", icon="✅")
                                    st.success(
                                        f"Pickup confirmed! Notification sent to {resident_email}")
                                    st.balloons()
                                    import time
                                    time.sleep(2)
                                    # return to dashboard
                                    navigate_to("dashboard")
                                else:
                                    st.error("Error processing pickup")

                        if col2.button("❌ Cancel", use_container_width=True):
                            st.session_state.selected_package = None
                            navigate_to("dashboard")
            else:
                st.error("Failed to fetch pending packages")
        except Exception as e:
            st.error(f"Connection Error: {e}")

    elif st.session_state.page == "unknown_dashboard":
        st.title("❓ Unknown Packages")
        if st.button("← Back"):
            navigate_to("dashboard")

        # 1. Log New Unknown
        with st.expander("➕ Log New Unknown Package"):
            with st.form("new_unknown"):
                label = st.text_input("Name on Label")
                carrier = st.selectbox("Carrier", ["Amazon", "DHL", "FedEx", "Walmart", "USPS", "UPS"])
                if st.form_submit_button("Log Unknown"):
                    requests.post(
                        f"{API_URL}/unknown", json={"name_on_label": label, "carrier": carrier})
                    st.rerun()

        # 2. List & Resolve
        r = requests.get(f"{API_URL}/unknown")
        if r.status_code == 200:
            unknowns = r.json()["unknown_packages"]
            for u in unknowns:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(
                        f"**ID:** {u['unknown_id']} | **Label:** `{u['name_on_label']}`")
                    if c2.button("Resolve", key=f"res_{u['unknown_id']}"):
                        navigate_to("resolve_unknown", u)

    elif st.session_state.page == "resolve_unknown":
        u = st.session_state.selected_package
        st.title("🕵️ Resolve Unknown Package")

        if st.button("← Back to Dashboard"):
            navigate_to("dashboard")

        # Package info
        with st.container(border=True):
            st.markdown(f"**Name on Label:** {u['name_on_label']}")
            st.markdown(f"**Carrier:** {u['carrier']}")
            st.markdown(f"**Arrived:** {format_time_ampm(u['delivery_date'])}")
            st.markdown(f"**Unknown ID:** #{u['unknown_id']}")

        st.divider()

        # Two options: Select existing resident OR create new
        tab1, tab2 = st.tabs(
            ["📋 Select Existing Resident", "➕ Create New Resident"])

        with tab1:
            st.subheader("Assign to Existing Resident")
            # Fetch residents
            try:
                res = requests.get(f"{API_URL}/residents")
                if res.status_code == 200:
                    residents = res.json()["residents"]
                    if not residents:
                        st.warning(
                            "No residents found. Create a new resident first.")
                    else:
                        res_opts = {
                            f"{r['full_name']} (Unit {r['unit_number']}) - {r['email']}": r['id']
                            for r in residents
                        }

                        selected_resident = st.selectbox(
                            "Select Resident:",
                            options=list(res_opts.keys()),
                            placeholder="Choose a resident to assign this package..."
                        )

                        if selected_resident:
                            col1, col2 = st.columns(2)
                            if col1.button("✅ Assign Package", use_container_width=True, key="assign_existing"):
                                with st.spinner("Assigning package..."):
                                    r = requests.post(f"{API_URL}/unknown/assign", json={
                                        "unknown_id": u['unknown_id'],
                                        "resident_id": res_opts[selected_resident]
                                    })
                                    if r.status_code == 200:
                                        st.toast(
                                            "Package assigned successfully!", icon="✅")
                                        st.success(
                                            "Package assigned and notification sent!")
                                        st.balloons()
                                        import time
                                        time.sleep(2)
                                        navigate_to("dashboard")
                                    else:
                                        st.error("Failed to assign package")

                            if col2.button("❌ Cancel", use_container_width=True, key="cancel_assign"):
                                navigate_to("dashboard")
            except Exception as e:
                st.error(f"Error loading residents: {e}")

        with tab2:
            st.subheader("Create New Resident & Assign")
            st.info(
                "Create a new resident and automatically assign this package to them.")

            with st.form("create_and_assign"):
                new_name = st.text_input(
                    "Full Name", value=u['name_on_label'], placeholder="Enter resident's full name")
                new_email = st.text_input(
                    "Email", placeholder="Enter email address")
                new_unit = st.number_input(
                    "Unit Number", min_value=100, max_value=999, step=1)

                if st.form_submit_button("✅ Create Resident & Assign Package"):
                    if new_name and new_email and new_unit:
                        with st.spinner("Creating resident and assigning package..."):
                            # Step 1: Create the resident
                            r1 = requests.post(f"{API_URL}/residents/create", json={
                                "full_name": new_name,
                                "email": new_email,
                                "unit_number": int(new_unit)
                            })

                            if r1.status_code == 200 and r1.json().get("success"):
                                resident_id = r1.json().get("resident_id")

                                # Step 2: Assign the package
                                r2 = requests.post(f"{API_URL}/unknown/assign", json={
                                    "unknown_id": u['unknown_id'],
                                    "resident_id": resident_id
                                })

                                if r2.status_code == 200:
                                    st.toast(
                                        "Resident created and package assigned!", icon="✅")
                                    st.success(
                                        f"Created resident '{new_name}' and assigned package!")
                                    st.balloons()
                                    import time
                                    time.sleep(2)
                                    navigate_to("dashboard")
                                else:
                                    st.error(
                                        "Resident created but failed to assign package")
                            else:
                                st.error(r1.json().get(
                                    "message", "Failed to create resident"))
                    else:
                        st.warning("Please fill in all fields")

    elif st.session_state.page == "package_detail":
        pkg = st.session_state.selected_package
        st.title("📦 Package Details")

        if st.button("← Back to Dashboard"):
            navigate_to("dashboard")

        # Fetch resident email
        resident_email = "N/A"
        try:
            res = requests.get(f"{API_URL}/residents")
            if res.status_code == 200:
                for r in res.json()["residents"]:
                    if r['id'] == pkg.get('resident_id'):
                        resident_email = r['email']
                        break
        except:
            pass

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Resident:** {pkg['full_name']}")
                st.markdown(f"**Email:** {resident_email}")
                st.markdown(f"**Unit:** {pkg['unit_number']}")
            with col2:
                st.markdown(f"**Package ID:** #{pkg['package_id']}")
                st.markdown(f"**Carrier:** {pkg['carrier']}")
                st.markdown(f"**Arrived:** {format_time_ampm(pkg['delivery_date'])}")

        # Status display
        if pkg['status'] == 'PickedUp':
            st.success("✅ This package has been picked up.")
        else:
            st.warning("⏳ This package is still pending pickup.")

    elif st.session_state.page == "create_resident":
        st.title("🏠 Create New Resident")

        if st.button("← Back to Dashboard"):
            navigate_to("dashboard")

        st.info("Add a new resident to the system.")

        with st.form("create_resident_form"):
            full_name = st.text_input(
                "Full Name", placeholder="Enter resident's full name")
            email = st.text_input("Email", placeholder="Enter email address")
            unit_number = st.number_input(
                "Unit Number", min_value=100, max_value=999, step=1)

            submitted = st.form_submit_button("✅ Create Resident")

        if submitted:
            if full_name and email and unit_number:
                with st.spinner("Creating resident..."):
                    try:
                        r = requests.post(f"{API_URL}/residents/create", json={
                            "full_name": full_name,
                            "email": email,
                            "unit_number": int(unit_number)
                        })
                        if r.status_code == 200:
                            data = r.json()
                            if data.get("success"):
                                st.toast(
                                    "Resident created successfully!", icon="✅")
                                st.success(
                                    f"Resident '{full_name}' created successfully!")
                                st.balloons()
                            else:
                                st.error(
                                    data.get("message", "Failed to create resident"))
                        else:
                            st.error("Failed to create resident")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please fill in all fields")

    elif st.session_state.page == "create_staff":
        st.title("👤 Create Staff Account")
        if st.button("← Back"):
            navigate_to("dashboard")

        with st.form("new_staff"):
            new_user = st.text_input(
                "New Username", placeholder="Enter username")
            new_pass = st.text_input(
                "New Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Create Account")

        if submitted:
            if new_user and new_pass:
                try:
                    r = requests.post(f"{API_URL}/staff/register", json={
                        "username": new_user,
                        "password": new_pass
                    })
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("success"):
                            st.balloons()
                            st.success(
                                f"Staff account '{new_user}' created successfully!")
                        else:
                            st.error(
                                data.get("message", "Failed to create account."))
                    else:
                        st.error("Failed to create account.")
                except Exception as e:
                    st.error(f"Backend error: {e}")
            else:
                st.warning("Please fill in both username and password.")


# ============================================================
# RESIDENT DASHBOARD
# ============================================================
def resident_dashboard():
    user = st.session_state.user_info
    st.sidebar.header(f"Resident: {user.get('name')}")
    st.sidebar.write(f"Unit: {user.get('unit')}")
    if st.sidebar.button("Logout"):
        logout()

    st.title(f"👋 Welcome, {user.get('name')}")
    st.write("Here are your packages:")

    st.markdown("### 📦 My Packages")

    # Fetch packages for this resident
    resident_id = user.get('id')
    if not resident_id:
        st.error("Session error: Please log in again.")
        return

    try:
        r = requests.get(f"{API_URL}/packages/resident/{resident_id}")
        if r.status_code == 200:
            packages = r.json().get("packages", [])

            if not packages:
                st.info("No packages found.")
            else:
                # Separate pending and picked up packages
                pending = [p for p in packages if p['status'] == 'Pending']
                picked_up = [p for p in packages if p['status'] == 'PickedUp']

                if pending:
                    st.markdown("#### 📬 Pending Pickup")
                    for pkg in pending:
                        with st.container(border=True):
                            st.markdown(f"**Carrier:** {pkg['carrier']}")
                            st.markdown(f"**Arrived:** {format_time_ampm(pkg['delivery_date'])}")
                            st.markdown(f"🟡 **Status:** Pending")

                if picked_up:
                    st.markdown("#### ✅ Picked Up")
                    for pkg in picked_up:
                        with st.container(border=True):
                            st.markdown(f"**Carrier:** {pkg['carrier']}")
                            st.markdown(f"**Arrived:** {format_time_ampm(pkg['delivery_date'])}")
                            st.markdown(f"🟢 **Status:** Picked Up")
        else:
            st.error("Failed to fetch packages.")
    except Exception as e:
        st.error(f"Connection Error: {e}")


# ============================================================
# MAIN ROUTER
# ============================================================
if st.session_state.auth_status == 'staff':
    staff_dashboard()
elif st.session_state.auth_status == 'resident':
    resident_dashboard()
else:
    login_page()
