# dashboards/patient_dashboard.py
import streamlit as st
from components.sidebar import sidebar
from components.charts import patient_line_chart, appointment_donut_chart
from src.modules.module_36.module_36_ui import module_36_page

# All categories and their modules
CATEGORIES = {
    "A - Patient Clinical Data": {
        "title": "Patient Clinical Data Management",
        "description": "Manage patient records, medical history, diagnoses, and treatment plans",
        "icon": "🏥",
        "stats": {"total": "153,600", "alerts": "12", "modules": "6"},
        "modules": [
            ("A1", "Patient Demographics & Visit History Database", "Patient demographics and admission data", 5, 12500),
            ("A2", "Chronic Disease Patient Record Management", "Past medical records and conditions", 4, 8900),
            ("A3", "Pediatric Patient Clinical Data System", "ICD codes and diagnosis tracking", 3, 15600),
            ("A4", "Geriatric Patient Health Record Database", "Care plans and treatment", 6, 7800),
            ("A5", "Patient Allergy & Immunization Tracking System", "Patient vitals and monitoring", 4, 9200),
            ("A6", "Clinical Alert System for Abnormal Vital Values", "Doctor notes and observations", 5, 11400)
        ]
    },
    "B - Symptom-Disease Diagnosis": {
        "title": "Symptom-Disease Diagnosis Support",
        "description": "AI-powered symptom analysis and disease diagnosis support systems",
        "icon": "🔬",
        "stats": {"total": "89,400", "alerts": "8", "modules": "6"},
        "modules": [
            ("B1", "Symptom-Disease Mapping Database", "Comprehensive symptom database", 8, 25000),
            ("B2", "Fever-Based Differential Diagnosis System", "Fever pattern analysis", 4, 12000),
            ("B3", "Respiratory Symptom Diagnosis Database", "Respiratory condition database", 6, 15400),
            ("B4", "Gastrointestinal Disorder Diagnosis Support", "GI symptom analysis", 5, 10800),
            ("B5", "Neurological Symptom Analysis Database", "Neural condition tracking", 7, 14200),
            ("B6", "Rule-Based Disease Ranking System", "Disease probability system", 3, 12000)
        ]
    },
    "C - Clinical Query Copilot": {
        "title": "Clinical Query Copilot (NL to SQL)",
        "description": "Natural language interface for clinical database queries",
        "icon": "💬",
        "stats": {"total": "45,200", "alerts": "5", "modules": "6"},
        "modules": [
            ("C1", "Natural Language Patient Search System", "Voice and text patient search", 4, 8500),
            ("C2", "Clinical Query Translator for Laboratory Records", "Lab record queries", 5, 9200),
            ("C3", "Voice-Assisted Clinical Query System (Text Simulation)", "Text simulation queries", 3, 6800),
            ("C4", "Doctor-Friendly SQL Query Dashboard", "Visual query builder", 6, 7400),
            ("C5", "Smart Clinical Views using SQL", "Pre-built SQL views", 4, 8100),
            ("C6", "Question-Answering System for Hospital Database", "Hospital database QA", 3, 5200)
        ]
    },
    "D - Drug & Prescription Safety": {
        "title": "Drug & Prescription Safety Systems",
        "description": "Medication safety, interaction alerts, and prescription validation",
        "icon": "💊",
        "stats": {"total": "67,800", "alerts": "15", "modules": "6"},
        "modules": [
            ("D1", "Drug-Drug Interaction Alert Database", "Interaction database", 7, 18500),
            ("D2", "Prescription Validation & Consistency System", "Consistency checks", 5, 12300),
            ("D3", "Allergy-Aware Medication Alert System", "Allergy cross-reference", 4, 9800),
            ("D4", "Polypharmacy Risk Detection Database", "Multiple drug analysis", 6, 11200),
            ("D5", "High-Risk Drug Monitoring System", "Critical medication tracking", 5, 8700),
            ("D6", "Automated Prescription Audit System", "Prescription review system", 4, 7300)
        ]
    },
    "E - ICU & Real-Time Monitoring": {
        "title": "ICU & Real-Time Monitoring Databases",
        "description": "Critical care monitoring and real-time vital sign tracking",
        "icon": "📊",
        "stats": {"total": "34,500", "alerts": "23", "modules": "6"},
        "modules": [
            ("E1", "ICU Vital Signs Monitoring Database", "Real-time vitals tracking", 8, 8900),
            ("E2", "Emergency Room Patient Alert System", "ER alert system", 5, 6200),
            ("E3", "Cardiac ICU Monitoring Database", "Heart monitoring database", 6, 5800),
            ("E4", "Neonatal ICU Monitoring System", "Newborn care tracking", 7, 4100),
            ("E5", "Threshold-Based Clinical Alert Database", "Alert threshold system", 4, 5300),
            ("E6", "Time-Series Patient Health Data System", "Historical health trends", 5, 4200)
        ]
    },
    "F - Case-Based Decision Support": {
        "title": "Case-Based Clinical Decision Support",
        "description": "Historical case analysis and treatment outcome evaluation",
        "icon": "📋",
        "stats": {"total": "52,100", "alerts": "6", "modules": "6"},
        "modules": [
            ("F1", "Historical Case Comparison Database", "Case matching database", 6, 12400),
            ("F2", "Treatment Outcome Analysis System", "Outcome tracking system", 5, 9800),
            ("F3", "Disease Progression Case Repository", "Progression tracking", 7, 8900),
            ("F4", "Readmission Risk Analysis Database", "Readmission prediction", 4, 7600),
            ("F5", "Therapy Effectiveness Evaluation System", "Treatment efficacy", 5, 6700),
            ("F6", "Similar Patient Case Retrieval System", "Patient matching system", 6, 6700)
        ]
    },
    "G - Secure EHR & Access Control": {
        "title": "Secure EHR & Access Control Systems",
        "description": "Electronic health records security and role-based access management",
        "icon": "🔒",
        "stats": {"total": "156,300", "alerts": "3", "modules": "6"},
        "modules": [
            ("G1", "Secure Electronic Health Record (EHR) Database", "Main EHR database", 12, 45000),
            ("G2", "Role-Based Access Control for Hospital Systems", "Permission management", 8, 28900),
            ("G3", "Clinical Audit Trail & Logging System", "Activity logging system", 6, 32100),
            ("G4", "Patient Consent & Data Privacy Database", "Privacy management", 5, 18700),
            ("G5", "Multi-Role Access Control System", "Advanced permissions", 7, 19200),
            ("G6", "Secure Clinical Summary View Generator", "Summary views", 4, 12400)
        ]
    },
    "H - Laboratory Test Interpretation": {
        "title": "Laboratory Test Interpretation Systems",
        "description": "Lab test management, result interpretation, and critical value alerts",
        "icon": "🧪",
        "stats": {"total": "78,900", "alerts": "11", "modules": "6"},
        "modules": [
            ("H1", "Laboratory Test Management Database", "Test ordering system", 9, 22300),
            ("H2", "Automated Lab Result Interpretation System", "AI result analysis", 6, 15800),
            ("H3", "Reference Range Validation Database", "Normal range database", 4, 12400),
            ("H4", "Follow-Up Test Recommendation System", "Test suggestion system", 5, 9100),
            ("H5", "Pathology Report Management Database", "Pathology database", 7, 11200),
            ("H6", "Critical Lab Value Alert System", "Critical value alerts", 3, 8100)
        ]
    },
    "I - Integrated Capstone Projects": {
        "title": "Integrated Capstone-Style Mini Projects",
        "description": "Comprehensive integrated clinical decision support systems",
        "icon": "🎯",
        "stats": {"total": "125,600", "alerts": "9", "modules": "2"},
        "modules": [
            ("I1", "Integrated Clinical Decision Support Database (Patients, Symptoms, Drugs, Labs)", "Full CDSS with patients, symptoms, drugs, labs", 25, 78900),
            ("I2", "AI-Inspired Medical Copilot using DBMS Concept", "AI copilot using DBMS concepts", 18, 46700)
        ]
    }
}

def patient_dashboard():
    st.session_state.setdefault("view", "main")
    st.session_state.setdefault("selected_category", None)
    st.session_state.setdefault("selected_module", None)

    # Sidebar
    selected = sidebar([
        "Dashboard",
        "A - Patient Clinical Data",
        "B - Symptom-Disease Diagnosis",
        "C - Clinical Query Copilot",
        "D - Drug & Prescription Safety",
        "E - ICU & Real-Time Monitoring",
        "F - Case-Based Decision Support",
        "G - Secure EHR & Access Control",
        "H - Laboratory Test Interpretation",
        "I - Integrated Capstone Projects"
    ])

    # Handle sidebar selection
    if selected != "Dashboard" and selected in CATEGORIES:
        if st.session_state.get("sidebar_selected") != selected:
            st.session_state.selected_category = selected
            st.session_state.view = "category"
            st.session_state.selected_module = None
            st.session_state.sidebar_selected = selected
    elif selected == "Dashboard":
        if st.session_state.get("sidebar_selected") != selected:
            st.session_state.view = "main"
            st.session_state.selected_category = None
            st.session_state.selected_module = None
            st.session_state.sidebar_selected = selected

    # ROUTER
    if st.session_state.view == "category":
        show_category_view()
    elif st.session_state.view == "module":
        show_module_detail()
    else:
        show_main_dashboard()

def show_main_dashboard():
    # Top bar with search and user profile
    col1, col2, col3, col4 = st.columns([6, 1, 1, 2])
    with col1:
        st.text_input("🔍", placeholder="Search patients, doctors, reports...", label_visibility="collapsed")
    with col2:
        st.button("🔔")
    with col3:
        st.button("💬")
    with col4:
        st.markdown("**Sarah Johnson**  \n*Patient*")
    
    st.divider()
    
    # Welcome section with health score
    col_welcome, col_score = st.columns([3, 1])
    with col_welcome:
        st.markdown("## Welcome back, Sarah!")
        st.markdown("*Here's an overview of your health dashboard*")
    with col_score:
        st.markdown("**Health Score**")
        st.markdown("### 💚 Good")

    st.divider()

    # Quick action buttons
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button("📅 Book Appointment", use_container_width=True)
    with c2:
        st.button("📄 View Reports", use_container_width=True)
    with c3:
        st.button("💊 My Prescriptions", use_container_width=True)
    with c4:
        st.button("🧪 Lab Results", use_container_width=True)

    st.divider()

    # Main content area
    main_col, side_col = st.columns([2, 1])
    
    with main_col:
        st.subheader("Your Health Categories")
        
        # Clinical Records Card
        with st.container():
            cat_col1, cat_col2 = st.columns([4, 1])
            with cat_col1:
                st.markdown("### 💓 Clinical Records")
                st.caption("View your medical history, diagnoses, and treatment plans")
                st.markdown("**12 Records**")
            with cat_col2:
                if st.button("→", key="clinical", use_container_width=True):
                    st.session_state.selected_category = "A - Patient Clinical Data"
                    st.session_state.view = "category"
                    st.rerun()
        
        st.markdown("---")
        
        # Laboratory Card
        with st.container():
            cat_col1, cat_col2 = st.columns([4, 1])
            with cat_col1:
                st.markdown("### 🧪 Laboratory")
                st.caption("Access your lab test results and reports")
                st.markdown("**5 Pending**")
            with cat_col2:
                if st.button("→", key="laboratory", use_container_width=True):
                    st.session_state.selected_category = "B - Symptom-Disease Diagnosis"
                    st.session_state.view = "category"
                    st.rerun()
        
        st.markdown("---")
        
        # Pharmacy Card
        with st.container():
            cat_col1, cat_col2 = st.columns([4, 1])
            with cat_col1:
                st.markdown("### 💊 Pharmacy")
                st.caption("View prescriptions and medication history")
                st.markdown("**3 Active**")
            with cat_col2:
                if st.button("→", key="pharmacy", use_container_width=True):
                    st.session_state.selected_category = "D - Drug & Prescription Safety"
                    st.session_state.view = "category"
                    st.rerun()
        
        st.markdown("---")
        
        # Billing Card
        with st.container():
            cat_col1, cat_col2 = st.columns([4, 1])
            with cat_col1:
                st.markdown("### 💳 Billing")
                st.caption("View invoices, payments, and insurance claims")
                st.markdown("**2 Pending**")
            with cat_col2:
                if st.button("→", key="billing", use_container_width=True):
                    st.session_state.selected_category = "G - Secure EHR & Access Control"
                    st.session_state.view = "category"
                    st.rerun()
    
    with side_col:
        st.subheader("Upcoming Appointments")
        st.markdown("[View All](#)")
        
        # Appointment 1
        with st.container():
            st.markdown("#### 👨‍⚕️ Dr. Sarah Wilson")
            st.caption("Cardiology")
            st.caption("📅 Jan 10, 2026  🕐 10:30 AM")
        
        st.markdown("---")
        
        # Appointment 2
        with st.container():
            st.markdown("#### 👨‍⚕️ Dr. Michael Chen")
            st.caption("General Medicine")
            st.caption("📅 Jan 15, 2026  🕐 2:00 PM")
        
        st.markdown("---")
        st.button("📅 Book New Appointment", use_container_width=True)
        
        st.divider()
        
        # Recent Activity
        st.subheader("Recent Activity")
        
        st.markdown("🔵 **Lab Result**")
        st.caption("Blood test results available")
        st.caption("2 hours ago")
        st.markdown("---")
        
        st.markdown("🔵 **Prescription**")
        st.caption("New medication prescribed")
        st.caption("1 day ago")
        st.markdown("---")
        
        st.markdown("🔵 **Appointment**")
        st.caption("Appointment confirmed with Dr. Wilson")
        st.caption("2 days ago")

def show_category_view():
    cat_key = st.session_state.selected_category
    category = CATEGORIES[cat_key]
    
    # Header with icon and title
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# {category['icon']} {category['title']}")
        st.markdown(f"*{category['description']}*")
    with col2:
        st.button("📄 Export Data", use_container_width=True)
    
    st.divider()
    
    # Stats cards
    stats = category['stats']
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Total Records", stats['total'])
    c2.metric("⚠️ Active Alerts", stats['alerts'])
    c3.metric("⚡ Modules", stats['modules'])
    
    st.divider()
    st.markdown("## Modules")
    
    # Module cards in grid
    cols = st.columns(3)
    for idx, module in enumerate(category['modules']):
        code, name, desc, tables, records = module
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {code}")
                st.markdown(f"**{name}**")
                st.caption(desc)
                
                mcol1, mcol2 = st.columns(2)
                mcol1.metric("Tables", tables)
                mcol2.metric("Records", f"{records:,}")
                
                if st.button("→", key=f"mod_{code}", use_container_width=True):
                    st.session_state.selected_module = module
                    st.session_state.view = "module"
                    st.rerun()
                st.markdown("---")
    
    st.divider()
    if st.button("⬅ Back to Dashboard"):
        st.session_state.view = "main"
        st.rerun()

def show_module_detail():
    code, name, desc, tables, records = st.session_state.selected_module
    cat_key = st.session_state.selected_category
    
    # ── Module 36 (F6): Use custom implementation ──
    if code == "F6":
        module_36_page()
        return
    
    # ── Generic module detail view for all other modules ──
    # Breadcrumb
    st.markdown(f"Category {cat_key.split('-')[0].strip()} > {name}")
    st.markdown(f"# {name}")
    st.markdown(f"*{desc}*")
    
    # Tabs
    tab = st.radio("", ["🏠 Home", "🔗 ER Diagram", "📋 Tables", "🔍 SQL Query", "⚡ Triggers", "📊 Output"], horizontal=True)
    st.divider()
    
    if tab == "🏠 Home":
        st.info(f"**{name}** - {desc}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Input Entities")
            st.success("1️⃣ Patient Form")
            st.success("2️⃣ Insurance Details")
            st.success("3️⃣ Emergency Contact")
        
        with col2:
            st.markdown("### Output Entities")
            st.success("1️⃣ Patient Record")
            st.success("2️⃣ Admission Summary")
            st.success("3️⃣ Patient ID")
    
    elif tab == "🔗 ER Diagram":
        st.markdown("### Entity Relationship Diagram")
        st.image("https://via.placeholder.com/900x500?text=ER+Diagram+for+" + code)
    
    elif tab == "📋 Tables":
        st.markdown("### Database Tables")
        st.table({
            "Table Name": ["patients", "insurance", "emergency_contacts", "admissions", "visit_history"],
            "Records": [12500, 8900, 6400, 15200, 22100],
            "Status": ["✅ Active", "✅ Active", "✅ Active", "✅ Active", "✅ Active"]
        })
    
    elif tab == "🔍 SQL Query":
        st.markdown("### Sample SQL Queries")
        st.code(f"""
-- Query for {name}
SELECT p.patient_id, p.name, p.age, i.insurance_type
FROM patients p
LEFT JOIN insurance i ON p.id = i.patient_id
WHERE p.status = 'active'
ORDER BY p.admission_date DESC
LIMIT 100;
""", language="sql")
        
        if st.button("▶️ Execute Query"):
            st.success("Query executed successfully! 1,234 rows returned.")
    
    elif tab == "⚡ Triggers":
        st.markdown("### Database Triggers")
        st.code(f"""
-- Trigger for {name}
CREATE TRIGGER after_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
  INSERT INTO audit_logs (entity_type, entity_id, action, timestamp)
  VALUES ('patient', NEW.patient_id, 'INSERT', NOW());
  
  -- Send notification
  INSERT INTO notifications (user_id, message)
  VALUES (NEW.assigned_doctor, CONCAT('New patient registered: ', NEW.name));
END;
""", language="sql")
    
    elif tab == "📊 Output":
        st.markdown("### Module Output")
        st.success("✅ Patient Registered Successfully")
        st.info("📋 Patient ID: PT-2024-001234")
        st.info("📅 Registration Date: January 08, 2026")
        
        st.markdown("#### Generated Records")
        st.json({
            "patient_id": "PT-2024-001234",
            "name": "John Doe",
            "age": 45,
            "admission_date": "2026-01-08",
            "status": "active"
        })
    
    st.divider()
    if st.button("⬅ Back to Modules"):
        st.session_state.view = "category"
        st.rerun()