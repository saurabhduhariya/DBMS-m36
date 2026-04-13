import streamlit as st
from auth.login import login_page
from auth.signup import signup_page
from dashboards.patient_dashboard import patient_dashboard
from dashboards.doctor_dashboard import doctor_dashboard
from dashboards.admin_dashboard import admin_dashboard

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
# Setting up the browser tab title and wide layout for better UI
st.set_page_config(
    page_title="MediCare - Patient Retrieval System", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
# Ensuring all required session variables exist to prevent KeyErrors
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "role" not in st.session_state:
    st.session_state["role"] = None

# ==========================================
# 3. REDIRECT LOGIC (Post-Login)
# ==========================================
# If user is authenticated, route them to their specific dashboard
if st.session_state.logged_in:
    role = st.session_state.role
    
    try:
        if role == "Patient":
            patient_dashboard()
        elif role == "Doctor":
            doctor_dashboard()
        elif role == "Admin":
            admin_dashboard()
        
        # Stop further execution of app.py to focus on the dashboard
        st.stop()
        
    except Exception as e:
        st.error(f"Error loading {role} dashboard. Please contact admin.")
        st.session_state.logged_in = False  # Reset on critical failure

# ==========================================
# 4. AUTHENTICATION ROUTING
# ==========================================
# Navigation between Login and Signup pages
def main_navigation():
    try:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "signup":
            signup_page()
            
    except Exception as navigation_error:
        st.warning("Could not load the requested page. Retrying...")
        st.session_state.page = "login"

if __name__ == "__main__":
    main_navigation()
