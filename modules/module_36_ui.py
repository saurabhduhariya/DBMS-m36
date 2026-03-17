# modules/module_36_ui.py
# Streamlit UI for Module 36: Similar Patient Case Retrieval System
import streamlit as st
import matplotlib.pyplot as plt
from src.module_36.service import (
    init_db, get_all_patients, get_patient_detail,
    find_similar_patients, save_matches, submit_feedback,
    get_dashboard_view, get_statistics, get_collection_data
)


def module_36_page():
    """Main entry point for Module 36 UI — called from dashboard."""
    cat_key = st.session_state.get("selected_category", "F")
    
    # Breadcrumb
    st.markdown(f"Category {cat_key.split('-')[0].strip()} > **Similar Patient Case Retrieval System**")
    st.markdown("# 🧬 Similar Patient Case Retrieval System")
    st.markdown("*Module 36 — Pure DBMS-based patient similarity matching*")

    # Initialize DB button (one-time setup)
    if "m36_initialized" not in st.session_state:
        st.session_state.m36_initialized = False

    if not st.session_state.m36_initialized:
        st.warning("⚠️ Database not initialized. Click below to create collections and seed data.")
        if st.button("🔄 Initialize Database", key="m36_init_btn"):
            with st.spinner("Creating MongoDB collections and seeding data..."):
                try:
                    init_db()
                    st.session_state.m36_initialized = True
                    st.success("✅ Database initialized successfully! 20 patients seeded.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.info("Make sure MongoDB is running on localhost:27017")
        return

    # Tabs
    tab = st.radio(
        "", 
        ["🏠 Home", "🔗 ER Diagram", "📋 Tables", "🔍 Similarity Query", "⚡ Triggers & Views", "📊 Output"],
        horizontal=True,
        key="m36_tab"
    )
    st.divider()

    if tab == "🏠 Home":
        render_home_tab()
    elif tab == "🔗 ER Diagram":
        render_er_diagram_tab()
    elif tab == "📋 Tables":
        render_tables_tab()
    elif tab == "🔍 Similarity Query":
        render_query_tab()
    elif tab == "⚡ Triggers & Views":
        render_triggers_tab()
    elif tab == "📊 Output":
        render_output_tab()

    st.divider()
    col_back, col_reset = st.columns([1, 1])
    with col_back:
        if st.button("⬅ Back to Modules"):
            st.session_state.view = "category"
            st.rerun()
    with col_reset:
        if st.button("🔄 Reset Database"):
            init_db()
            st.success("Database reset!")
            st.rerun()


# ─────────────────────── TAB 1: HOME ───────────────────────

def render_home_tab():
    if st.session_state.get("role") == "Patient":
        st.info(
            "**Similar Patient Case Retrieval System** helps you find anonymized patient records "
            "with similar clinical profiles so you can understand typical treatments and outcomes."
        )
    else:
        st.info(
            "**Similar Patient Case Retrieval System** finds patients with similar clinical "
            "profiles using Weighted Euclidean Distance computed entirely within MongoDB "
            "Aggregation Pipelines — no machine learning libraries used."
        )

    # Statistics
    try:
        stats = get_statistics()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("👥 Patients", stats["total_patients"])
        c2.metric("📋 Cases", stats["total_cases"])
        c3.metric("🔗 Matches", stats["total_matches"])
        c4.metric("💬 Feedback", stats["total_feedback"])
        c5.metric("💚 Avg Survival", f"{stats['avg_survival_rate']}%")
    except Exception:
        st.caption("Stats will appear after first similarity search.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📥 Input Entities")
        st.success("1️⃣ **PatientProfile** — Demographics, lifestyle")
        st.success("2️⃣ **ClinicalCase** — Symptoms, severity")
        st.success("3️⃣ **SimilarityAlgorithm** — Algorithm parameters")
    with col2:
        st.markdown("### 📤 Output Entities")
        st.success("1️⃣ **SimilarityMatch** — Matched patients + scores")
        st.success("2️⃣ **Prognosis** — Treatment & survival data")
        st.success("3️⃣ **Feedback** — Doctor validation")

    if st.session_state.get("role") != "Patient":
        st.divider()
        st.markdown("### 🏗️ System Architecture")
        st.markdown("""
        ```
        Doctor → Dashboard UI → Input Validation → MongoDB Aggregation Pipeline
                                                        ↓
                                ┌──────────────────────────────────────┐
                                │  $lookup (JOIN PatientProfile)       │
                                │  $lookup (JOIN ClinicalCase)         │
                                │  $addFields (Normalize Age/Severity) │
                                │  $addFields (Euclidean Distance)     │
                                │  $sort (by Similarity Score)         │
                                │  $limit (Top 10)                     │
                                │  $lookup (JOIN Prognosis)            │
                                └──────────────────────────────────────┘
                                                        ↓
                                Results → Save Matches → Feedback → Trigger Update
        ```
        """)

        st.divider()
        st.markdown("### 📚 DBMS Concepts Used")
        concepts = {
            "Concept": [
                "Collection Schema + Indexes", "$lookup (JOIN)",
                "Aggregation Pipeline", "$group (Aggregate Functions)",
                "Post-Insert Trigger", "Math Operators",
                "CRUD Operations", "MIN-MAX Normalization"
            ],
            "MongoDB Feature": [
                "create_index(), unique constraints", "$lookup stage",
                "$match, $addFields, $sort, $limit, $project", "$avg, $sum, $min, $max",
                "After insert_one → update_one", "$sqrt, $pow, $subtract, $divide",
                "find, insert_one, update_one, delete_one", "$group for MIN/MAX + $addFields"
            ],
            "Used In": [
                "collections.py", "service.py (find_similar)",
                "Core similarity engine", "Feedback + Statistics",
                "submit_feedback()", "Distance calculation",
                "All service functions", "Aggregation pipeline"
            ]
        }
        st.table(concepts)


# ─────────────────────── TAB 2: ER DIAGRAM ───────────────────────

def render_er_diagram_tab():
    st.markdown("### 📐 Entity Relationship Diagram")
    st.markdown("*Based on the handwritten ER diagram for Module 36*")

    # Display ER diagram as text since we can't embed the handwritten image
    st.markdown("""
    ```
    ┌──────────────────────┐         ┌──────────────────────┐
    │    PatientProfile    │────1:1──│      Prognosis       │
    │──────────────────────│  (has)  │──────────────────────│
    │ Patient_ID (PK)      │         │ Prognosis_ID (PK)    │
    │ Age                  │         │ Patient_ID (FK)      │
    │ Gender               │         │ Treatment            │
    │ Blood_Group          │         │ Prognosis_Data       │
    │ Address              │         │ Survival_Rate        │
    │ Lifestyle_Data       │         └──────────┬───────────┘
    └──────────┬───────────┘                    │
               │ 1:N (exhibits)                 │ 1:N (predicts)
               ▼                                ▼
    ┌──────────────────────┐         ┌──────────────────────┐
    │    ClinicalCase      │──1:N─── │   SimilarityMatch    │
    │──────────────────────│(analyzed│──────────────────────│
    │ Case_ID (PK)         │  via)   │ Match_ID (PK)        │
    │ Patient_ID (FK)      │         │ Source_Patient_ID(FK)│
    │ Symptom_Vector       │         │ Matched_Patient_ID   │
    │ Severity_Level       │         │ Similarity_Score     │
    └──────────────────────┘         │ Confidence_Score     │
                                     │ Algo_ID (FK)         │
    ┌──────────────────────┐         └──────────┬───────────┘
    │ SimilarityAlgorithm  │──N:1───┘           │
    │──────────────────────│(computes)          │ 1:N
    │ Algo_ID (PK)         │                    │ (validated by)
    │ Algo_Name            │                    ▼
    └──────────────────────┘         ┌──────────────────────┐
                                     │      Feedback        │
                                     │──────────────────────│
                                     │ Feedback_ID (PK)     │
                                     │ Match_ID (FK)        │
                                     │ Is_Useful            │
                                     │ Survival_Rate        │
                                     │ Doctor_Comments      │
                                     └──────────────────────┘
    ```
    """)

    st.divider()
    st.markdown("### 🔗 Relationships")
    relationships = {
        "Relationship": [
            "PatientProfile → ClinicalCase",
            "PatientProfile → Prognosis",
            "ClinicalCase → SimilarityMatch",
            "Prognosis → SimilarityMatch",
            "SimilarityAlgorithm → SimilarityMatch",
            "SimilarityMatch → Feedback"
        ],
        "Cardinality": ["1:N", "1:1", "N:N (via match)", "1:N", "1:N", "1:N"],
        "Name": ["Exhibits", "Has", "Analyzed Via", "Predicts", "Computes", "Validated By"],
        "FK Location": [
            "ClinicalCase.Patient_ID",
            "Prognosis.Patient_ID",
            "SimilarityMatch.Source/Matched",
            "SimilarityMatch.Matched_Patient_ID",
            "SimilarityMatch.Algo_ID",
            "Feedback.Match_ID"
        ]
    }
    st.table(relationships)


# ─────────────────────── TAB 3: TABLES ───────────────────────

def render_tables_tab():
    st.markdown("### 📋 MongoDB Collections (Live Data)")

    collections = [
        ("patient_profiles", "👤 PatientProfile"),
        ("clinical_cases", "🏥 ClinicalCase"),
        ("prognosis", "📊 Prognosis"),
        ("similarity_algorithms", "⚙️ SimilarityAlgorithm"),
        ("similarity_matches", "🔗 SimilarityMatch"),
        ("feedback", "💬 Feedback"),
    ]

    selected_coll = st.selectbox(
        "Select Collection",
        [name for _, name in collections],
        key="m36_coll_select"
    )

    # Map display name to collection name
    coll_map = {name: key for key, name in collections}
    coll_key = coll_map[selected_coll]

    try:
        data = get_collection_data(coll_key)
        if data:
            st.dataframe(data, use_container_width=True)
            st.caption(f"📊 {len(data)} documents in `{coll_key}`")
        else:
            st.info(f"No data in `{coll_key}` yet. Run a similarity search first!")
    except Exception as e:
        st.error(f"Error reading collection: {e}")


# ─────────────────────── TAB 4: SIMILARITY QUERY ───────────────────────

def render_query_tab():
    st.markdown("### 🔍 Find Similar Patients")
    if st.session_state.get("role") == "Patient":
        st.markdown("*Adjust the weights below to see similar patient cases based on different health factors.*")
    else:
        st.markdown("*Adjust the weights below to tune the similarity search — this changes the SQL-equivalent aggregation pipeline parameters.*")

    # Patient selector
    try:
        patients = get_all_patients()
    except Exception as e:
        st.error(f"Error loading patients: {e}")
        return

    patient_options = {f"Patient {p['patient_id']} — Age: {p['age']}, {p['gender']}, {p['blood_group']}": p['patient_id'] for p in patients}
    selected = st.selectbox("🎯 Select Source Patient", list(patient_options.keys()), key="m36_source")
    source_pid = patient_options[selected]

    # Show source patient details
    detail = get_patient_detail(source_pid)
    if detail:
        with st.expander("📋 Source Patient Details", expanded=True):
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Age", detail["age"])
            d2.metric("Gender", detail["gender"])
            d3.metric("Blood Group", detail["blood_group"])
            d4.metric("Address", detail.get("address", "N/A"))
            if detail.get("clinical_cases"):
                cc = detail["clinical_cases"][0]
                st.caption(f"🏥 Severity: {cc['severity_level']}/10 | Symptoms: {cc['symptom_vector']}")

    st.divider()

    # Weight sliders — Adjust based on role
    if st.session_state.get("role") == "Patient":
        st.markdown("### ⚖️ Similarity Weights")
        st.caption("Adjust these factors to see how they impact your matched patient results.")
    else:
        st.markdown("### ⚖️ Similarity Weights (Doctor's Intuition)")
        st.caption("Adjust these to prioritize different factors in the matching algorithm")
    
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    with w_col1:
        w_age = st.slider("🎂 Age Weight", 0.0, 1.0, 0.3, 0.05, key="m36_w_age")
    with w_col2:
        w_sev = st.slider("🩺 Severity Weight", 0.0, 1.0, 0.3, 0.05, key="m36_w_sev")
    with w_col3:
        w_gen = st.slider("👤 Gender Weight", 0.0, 1.0, 0.2, 0.05, key="m36_w_gen")
    with w_col4:
        w_bld = st.slider("🩸 Blood Group Weight", 0.0, 1.0, 0.2, 0.05, key="m36_w_bld")

    st.divider()

    # Show the aggregation pipeline code
    with st.expander("🔧 MongoDB Aggregation Pipeline (View Code)"):
        st.code(f"""
# MongoDB Aggregation Pipeline — Weighted Euclidean Distance
# Source Patient: {source_pid}
# Weights: age={w_age}, severity={w_sev}, gender={w_gen}, blood={w_bld}

pipeline = [
    # STEP 1: JOIN patient_profiles with clinical_cases
    {{"$lookup": {{
        "from": "clinical_cases",
        "localField": "patient_id",
        "foreignField": "patient_id",
        "as": "clinical"
    }}}},
    {{"$unwind": "$clinical"}},
    
    # STEP 2: Exclude source patient
    {{"$match": {{"patient_id": {{"$ne": {source_pid}}}}}}},
    
    # STEP 3: Normalize + Compute Distance
    {{"$addFields": {{
        "age_norm": {{"$divide": [{{"$subtract": ["$age", MIN_AGE]}}, AGE_RANGE]}},
        "severity_norm": {{"$divide": [{{"$subtract": ["$clinical.severity_level", 1]}}, 9]}},
        "gender_diff": {{"$cond": [{{"$eq": ["$gender", SOURCE_GENDER]}}, 0, 1]}},
        "blood_diff": {{"$cond": [{{"$eq": ["$blood_group", SOURCE_BLOOD]}}, 0, 1]}}
    }}}},
    
    # STEP 4: Weighted Euclidean Distance
    {{"$addFields": {{
        "distance": {{"$sqrt": {{"$add": [
            {{"$multiply": [{w_age}, {{"$pow": [{{"$subtract": ["$src_age_norm", "$age_norm"]}}, 2]}}]}},
            {{"$multiply": [{w_sev}, {{"$pow": [{{"$subtract": ["$src_sev_norm", "$severity_norm"]}}, 2]}}]}},
            {{"$multiply": [{w_gen}, {{"$pow": ["$gender_diff", 2]}}]}},
            {{"$multiply": [{w_bld}, {{"$pow": ["$blood_diff", 2]}}]}}
        ]}}}}
    }}}},
    
    # STEP 5: Convert to Similarity Score
    {{"$addFields": {{"similarity_score": {{"$divide": [1, {{"$add": [1, "$distance"]}}]}}}}}},
    
    # STEP 6: Sort by score descending, limit to 10
    {{"$sort": {{"similarity_score": -1}}}},
    {{"$limit": 10}},
    
    # STEP 7: JOIN with prognosis
    {{"$lookup": {{"from": "prognosis", "localField": "patient_id",
                   "foreignField": "patient_id", "as": "prog"}}}}
]
""", language="python")

    # Execute search
    if st.button("🚀 Find Similar Patients", type="primary", use_container_width=True, key="m36_search"):
        with st.spinner("Executing MongoDB Aggregation Pipeline..."):
            try:
                results = find_similar_patients(source_pid, w_age, w_sev, w_gen, w_bld)
                st.session_state.m36_results = results
                st.session_state.m36_source_pid = source_pid

                if results:
                    # Save matches to DB
                    count = save_matches(source_pid, results)
                    st.success(f"✅ Found {len(results)} similar patients! ({count} matches saved to DB)")
                else:
                    st.warning("No similar patients found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display results
    if "m36_results" in st.session_state and st.session_state.m36_results:
        results = st.session_state.m36_results
        st.markdown("### 📊 Top Similar Patients")

        # Results table
        display_data = []
        for i, r in enumerate(results):
            display_data.append({
                "Rank": i + 1,
                "Patient ID": r["patient_id"],
                "Age": r["age"],
                "Gender": r["gender"],
                "Blood Group": r["blood_group"],
                "Severity": r.get("severity_level", "N/A"),
                "Similarity": f"{r['similarity_score']:.4f}",
                "Treatment": r.get("treatment", "N/A"),
                "Survival %": r.get("survival_rate", "N/A"),
            })
        st.dataframe(display_data, use_container_width=True)

        # Feedback form - restrict to non-patients
        st.divider()
        if st.session_state.get("role") == "Patient":
            st.info("💡 **Note:** Clinical feedback and validation forms are restricted to Medical Professionals.")
        else:
            st.markdown("### 💬 Doctor Feedback (Clinical Validation)")
            
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                fb_match = st.number_input("Match ID", min_value=1, value=1, key="m36_fb_match")
                fb_useful = st.radio("Was this match clinically useful?", ["Yes", "No"], key="m36_fb_useful", horizontal=True)
            with fb_col2:
                fb_comments = st.text_area("Clinical Notes", key="m36_fb_comments", placeholder="Enter your clinical feedback...")

            if st.button("📝 Submit Feedback", key="m36_fb_submit"):
                try:
                    submit_feedback(fb_match, fb_useful == "Yes", fb_comments)
                    st.success("✅ Feedback submitted! Confidence score updated (trigger fired).")
                except Exception as e:
                    st.error(f"Error: {e}")


# ─────────────────────── TAB 5: TRIGGERS & VIEWS ───────────────────────

def render_triggers_tab():
    st.markdown("### ⚡ Triggers & Views (DBMS Concepts)")

    st.markdown("#### 1. Trigger: Auto-Update Confidence on Feedback")
    st.markdown("*In SQL, this would be `CREATE TRIGGER`. In MongoDB, we implement it as a post-insert hook.*")
    st.code("""
# TRIGGER EQUIVALENT: After INSERT on Feedback
# Automatically update SimilarityMatch.confidence_score

def submit_feedback(match_id, is_useful, doctor_comments):
    db = get_db()
    
    # 1. INSERT into feedback collection
    db.feedback.insert_one({
        "match_id": match_id,
        "is_useful": is_useful,
        "doctor_comments": doctor_comments,
        "created_at": datetime.utcnow()
    })
    
    # 2. TRIGGER: Auto-compute AVG(is_useful) and update confidence
    avg_result = db.feedback.aggregate([
        {"$match": {"match_id": match_id}},
        {"$group": {
            "_id": None,
            "avg_useful": {"$avg": {"$cond": ["$is_useful", 1, 0]}}
        }}
    ]).next()
    
    db.similarity_matches.update_one(
        {"match_id": match_id},
        {"$set": {"confidence_score": avg_result["avg_useful"]}}
    )

# SQL Equivalent:
# CREATE TRIGGER trg_after_feedback
# AFTER INSERT ON Feedback
# FOR EACH ROW
# BEGIN
#     UPDATE SimilarityMatch
#     SET Confidence_Score = (
#         SELECT AVG(Is_Useful) FROM Feedback
#         WHERE Match_ID = NEW.Match_ID
#     )
#     WHERE Match_ID = NEW.Match_ID;
# END;
""", language="python")

    st.divider()

    st.markdown("#### 2. View: Patient Similarity Dashboard")
    st.markdown("*In SQL, this would be `CREATE VIEW`. In MongoDB, we use a multi-$lookup aggregation pipeline.*")
    st.code("""
# VIEW EQUIVALENT: patient_similarity_dashboard
# Joins 4 collections: SimilarityMatch + PatientProfile (x2) + Prognosis + Feedback

pipeline = [
    # JOIN source patient
    {"$lookup": {
        "from": "patient_profiles",
        "localField": "source_patient_id",
        "foreignField": "patient_id",
        "as": "source"
    }},
    {"$unwind": "$source"},
    
    # JOIN matched patient  
    {"$lookup": {
        "from": "patient_profiles",
        "localField": "matched_patient_id",
        "foreignField": "patient_id",
        "as": "matched"
    }},
    {"$unwind": "$matched"},
    
    # JOIN prognosis
    {"$lookup": {
        "from": "prognosis",
        "localField": "matched_patient_id",
        "foreignField": "patient_id",
        "as": "prog"
    }},
    
    # JOIN feedback
    {"$lookup": {
        "from": "feedback",
        "localField": "match_id",
        "foreignField": "match_id",
        "as": "fb"
    }},
    
    # Sort + Project final columns
    {"$sort": {"similarity_score": -1}},
    {"$project": {
        "source_id": "$source.patient_id",
        "matched_id": "$matched.patient_id",
        "similarity_score": 1,
        "treatment": "$prog.treatment",
        "survival_rate": "$prog.survival_rate",
        "feedback_count": {"$size": "$fb"}
    }}
]

# SQL Equivalent:
# CREATE VIEW patient_similarity_dashboard AS
# SELECT pp1.Patient_ID AS Source, pp2.Patient_ID AS Match,
#        sm.Similarity_Score, pr.Treatment, pr.Survival_Rate,
#        COUNT(f.Feedback_ID) AS Feedback_Count
# FROM SimilarityMatch sm
# JOIN PatientProfile pp1 ON sm.Source_Patient_ID = pp1.Patient_ID
# JOIN PatientProfile pp2 ON sm.Matched_Patient_ID = pp2.Patient_ID
# LEFT JOIN Prognosis pr ON pp2.Patient_ID = pr.Patient_ID
# LEFT JOIN Feedback f ON sm.Match_ID = f.Match_ID
# GROUP BY pp1.Patient_ID, pp2.Patient_ID
# ORDER BY sm.Similarity_Score DESC;
""", language="python")

    st.divider()

    st.markdown("#### 3. Indexes (Performance Optimization)")
    st.code("""
# MongoDB Indexes — equivalent to CREATE INDEX in SQL

db.patient_profiles.create_index("patient_id", unique=True)
db.clinical_cases.create_index("patient_id")
db.prognosis.create_index("patient_id", unique=True)
db.similarity_matches.create_index([("similarity_score", -1)])
db.similarity_matches.create_index("source_patient_id")
db.feedback.create_index("match_id")

# SQL Equivalent:
# CREATE UNIQUE INDEX idx_patient_id ON PatientProfile(Patient_ID);
# CREATE INDEX idx_clinical_patient ON ClinicalCase(Patient_ID);
# CREATE UNIQUE INDEX idx_prognosis_patient ON Prognosis(Patient_ID);
# CREATE INDEX idx_match_score ON SimilarityMatch(Similarity_Score DESC);
# CREATE INDEX idx_match_source ON SimilarityMatch(Source_Patient_ID);
# CREATE INDEX idx_feedback_match ON Feedback(Match_ID);
""", language="python")


# ─────────────────────── TAB 6: OUTPUT ───────────────────────

def render_output_tab():
    st.markdown("### 📊 Results & Analytics")

    # Try to load dashboard view
    try:
        view_data = get_dashboard_view()
    except Exception:
        view_data = []

    if not view_data:
        st.info("No match results yet. Go to the **Similarity Query** tab and run a search first!")
        
        # Show sample output format
        st.markdown("#### 📋 Expected Output Format")
        st.code("""
Source_Patient: 1   (Age: 45, Male, O+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rank 1: Patient_ID: 6  | Similarity: 0.9823 | Confidence: 0.98
        Age: 47 | Gender: Male | Blood: O+
        Treatment: Chemotherapy
        Prognosis: Stage II - moderate response
        Survival Rate: 78%

Rank 2: Patient_ID: 14 | Similarity: 0.9156 | Confidence: 0.92
        Age: 44 | Gender: Male | Blood: A+
        Treatment: Targeted Therapy
        Prognosis: Stage II - good response
        Survival Rate: 80%
        """)
        return

    # Dashboard view table
    st.markdown("#### 🔗 Similarity Dashboard View (Multi-Collection JOIN)")
    st.dataframe(view_data, use_container_width=True)

    st.divider()

    # Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 📊 Similarity Score Distribution")
        scores = [d.get("similarity_score", 0) for d in view_data]
        match_ids = [f"P{d.get('matched_id', '?')}" for d in view_data]

        if scores:
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(match_ids[:10], scores[:10], color='#5B47D8')
            ax.set_ylabel("Similarity Score")
            ax.set_xlabel("Matched Patient")
            ax.set_title("Top Matches by Similarity Score")
            ax.set_ylim(0, 1.1)
            for bar, score in zip(bars, scores[:10]):
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                       f'{score:.2f}', ha='center', va='bottom', fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with chart_col2:
        st.markdown("#### 💊 Treatment Distribution")
        treatments = [d.get("treatment", "Unknown") for d in view_data if d.get("treatment")]
        if treatments:
            from collections import Counter
            treat_counts = Counter(treatments)
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            wedges, texts, autotexts = ax2.pie(
                treat_counts.values(),
                labels=treat_counts.keys(),
                autopct='%1.0f%%',
                startangle=90
            )
            for text in texts:
                text.set_fontsize(7)
            ax2.set_title("Treatment Types of Similar Patients")
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()

    st.divider()

    # Survival rate chart
    st.markdown("#### 💚 Survival Rates of Matched Patients")
    survival_rates = [d.get("survival_rate", 0) for d in view_data if d.get("survival_rate")]
    matched_ids = [f"P{d.get('matched_id', '?')}" for d in view_data if d.get("survival_rate")]
    if survival_rates:
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        colors = ['#4CAF50' if s >= 70 else '#FFC107' if s >= 50 else '#F44336' for s in survival_rates[:10]]
        bars = ax3.barh(matched_ids[:10], survival_rates[:10], color=colors)
        ax3.set_xlabel("Survival Rate (%)")
        ax3.set_title("Survival Rates of Similar Patients")
        ax3.set_xlim(0, 110)
        for bar, rate in zip(bars, survival_rates[:10]):
            ax3.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2.,
                    f'{rate:.0f}%', ha='left', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
