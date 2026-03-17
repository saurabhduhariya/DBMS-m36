# src/module_36/service.py
# Business logic for Module 36 — Similar Patient Case Retrieval System
# All similarity computation uses MongoDB Aggregation Pipelines (pure DBMS, no ML)
from datetime import datetime
import pymongo.errors
from src.module_36.database import get_db
from src.module_36.collections import init_collections


# ─────────────────────── INITIALIZATION ───────────────────────

def init_db():
    """Initialize database: drop, seed, and index all collections."""
    try:
        init_collections()
        return True
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB connection failed during init: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Database initialization error: {e}") from e


# ─────────────────────── BASIC QUERIES ───────────────────────

def get_all_patients():
    """Return all patient profiles."""
    try:
        db = get_db()
        return list(db.patient_profiles.find({}, {"_id": 0}).sort("patient_id", 1))
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Failed to fetch patients: {e}") from e


def get_patient_detail(patient_id):
    """
    Get full patient detail by joining PatientProfile + ClinicalCase + Prognosis.
    Uses MongoDB $lookup (equivalent of SQL JOIN).
    """
    try:
        db = get_db()
        pipeline = [
            {"$match": {"patient_id": patient_id}},
            # JOIN with clinical_cases
            {"$lookup": {
                "from": "clinical_cases",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "clinical_cases"
            }},
            # JOIN with prognosis
            {"$lookup": {
                "from": "prognosis",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "prognosis"
            }},
            {"$project": {"_id": 0}}
        ]
        results = list(db.patient_profiles.aggregate(pipeline))
        return results[0] if results else None
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Failed to fetch patient detail for id={patient_id}: {e}") from e


def get_collection_data(collection_name):
    """Fetch all documents from a given collection (for Tables tab display)."""
    try:
        db = get_db()
        return list(db[collection_name].find({}, {"_id": 0}))
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Failed to read collection '{collection_name}': {e}") from e


# ─────────────────────── CORE SIMILARITY ENGINE ───────────────────────

def find_similar_patients(source_pid, w_age=0.3, w_severity=0.3, w_gender=0.2, w_blood=0.2):
    """
    Find the top 10 most similar patients using Weighted Euclidean Distance.
    
    DBMS CONCEPTS USED:
    - MongoDB Aggregation Pipeline ($lookup, $match, $addFields, $project, $sort, $limit)
    - Mathematical operators ($sqrt, $pow, $subtract, $divide, $multiply)
    - $group for MIN/MAX normalization
    - $lookup for JOIN equivalent
    - $cond for conditional logic
    
    FORMULA:
    Similarity = 1 / (1 + sqrt(w1*(x1-y1)^2 + w2*(x2-y2)^2 + ...))
    Where values are normalized to 0-1 range using MIN-MAX normalization.
    """
    try:
        db = get_db()

        # ─── Step 1: Get global min/max for normalization (Aggregate Function) ───
        stats_cursor = list(db.patient_profiles.aggregate([
            {"$group": {
                "_id": None,
                "min_age": {"$min": "$age"},
                "max_age": {"$max": "$age"}
            }}
        ]))
        if not stats_cursor:
            # Edge case: empty database
            return []
        stats = stats_cursor[0]
        age_range = max(stats["max_age"] - stats["min_age"], 1)

        # ─── Step 2: Get source patient data ───
        source = db.patient_profiles.find_one({"patient_id": source_pid})
        source_case = db.clinical_cases.find_one({"patient_id": source_pid})
        if not source or not source_case:
            # Edge case: patient not found
            return []

        # Pre-compute source normalized values
        source_age_norm = (source["age"] - stats["min_age"]) / age_range
        source_sev_norm = (source_case["severity_level"] - 1) / 9.0

        # ─── Step 3: MongoDB Aggregation Pipeline — THE BRAIN ───
        pipeline = [
            # JOIN: patient_profiles ↔ clinical_cases ($lookup = SQL JOIN)
            {"$lookup": {
                "from": "clinical_cases",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "clinical"
            }},
            {"$unwind": "$clinical"},

            # FILTER: exclude source patient ($match = SQL WHERE)
            {"$match": {"patient_id": {"$ne": source_pid}}},

            # COMPUTE: Normalize + Distance ($addFields = SQL computed columns)
            {"$addFields": {
                # MIN-MAX Normalization for Age
                "age_norm": {"$divide": [
                    {"$subtract": ["$age", stats["min_age"]]},
                    age_range
                ]},
                # MIN-MAX Normalization for Severity (1-10 → 0-1)
                "severity_norm": {"$divide": [
                    {"$subtract": ["$clinical.severity_level", 1]},
                    9.0
                ]},
                # Gender match: 0 if same, 1 if different
                "gender_diff": {"$cond": [
                    {"$eq": ["$gender", source["gender"]]}, 0.0, 1.0
                ]},
                # Blood group match: 0 if same, 1 if different
                "blood_diff": {"$cond": [
                    {"$eq": ["$blood_group", source["blood_group"]]}, 0.0, 1.0
                ]}
            }},

            # COMPUTE: Weighted Euclidean Distance
            {"$addFields": {
                "distance": {"$sqrt": {"$add": [
                    {"$multiply": [w_age,      {"$pow": [{"$subtract": [source_age_norm, "$age_norm"]}, 2]}]},
                    {"$multiply": [w_severity, {"$pow": [{"$subtract": [source_sev_norm, "$severity_norm"]}, 2]}]},
                    {"$multiply": [w_gender,   {"$pow": ["$gender_diff", 2]}]},
                    {"$multiply": [w_blood,    {"$pow": ["$blood_diff", 2]}]}
                ]}}
            }},

            # COMPUTE: Convert distance to similarity score (0-1)
            {"$addFields": {
                "similarity_score": {"$round": [
                    {"$divide": [1.0, {"$add": [1.0, "$distance"]}]},
                    4
                ]}
            }},

            # SORT: Highest similarity first ($sort = SQL ORDER BY)
            {"$sort": {"similarity_score": -1}},

            # LIMIT: Top 10 matches ($limit = SQL LIMIT)
            {"$limit": 10},

            # JOIN: Get prognosis for matched patients ($lookup = SQL LEFT JOIN)
            {"$lookup": {
                "from": "prognosis",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "prog"
            }},
            {"$unwind": {"path": "$prog", "preserveNullAndEmptyArrays": True}},

            # PROJECT: Select final output columns ($project = SQL SELECT)
            {"$project": {
                "_id": 0,
                "patient_id": 1,
                "age": 1,
                "gender": 1,
                "blood_group": 1,
                "address": 1,
                "severity_level": "$clinical.severity_level",
                "symptom_vector": "$clinical.symptom_vector",
                "similarity_score": 1,
                "treatment": "$prog.treatment",
                "survival_rate": "$prog.survival_rate",
                "prognosis_data": "$prog.prognosis_data"
            }}
        ]

        return list(db.patient_profiles.aggregate(pipeline))
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Similarity search failed for patient {source_pid}: {e}") from e


# ─────────────────────── MATCH STORAGE ───────────────────────

def save_matches(source_pid, matches, algo_id=1):
    """
    Save computed similarity matches to the SimilarityMatch collection.
    Uses INSERT (equivalent of SQL INSERT INTO).
    """
    try:
        db = get_db()

        if not matches:
            return 0

        # Get next match_id
        last = db.similarity_matches.find_one(sort=[("match_id", -1)])
        next_id = (last["match_id"] + 1) if last else 1

        docs = []
        for i, match in enumerate(matches):
            docs.append({
                "match_id": next_id + i,
                "source_patient_id": source_pid,
                "matched_patient_id": match["patient_id"],
                "similarity_score": match["similarity_score"],
                "confidence_score": match["similarity_score"],  # Initial confidence = similarity
                "algo_id": algo_id,
                "created_at": datetime.utcnow()
            })

        if docs:
            db.similarity_matches.insert_many(docs)

        return len(docs)
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Failed to save matches for patient {source_pid}: {e}") from e


# ─────────────────────── FEEDBACK (TRIGGER EQUIVALENT) ───────────────────────

def submit_feedback(match_id, is_useful, doctor_comments="", survival_rate=None):
    """
    Submit doctor feedback on a similarity match.

    TRIGGER EQUIVALENT:
    After inserting feedback, automatically update the confidence_score
    of the SimilarityMatch (like an SQL AFTER INSERT trigger).

    Edge case: match_id not found — feedback is still stored but the
    confidence update is silently skipped (no match to update).
    """
    try:
        db = get_db()

        # Edge case: verify the match exists before accepting feedback
        match_doc = db.similarity_matches.find_one({"match_id": match_id})
        if match_doc is None:
            raise ValueError(f"No similarity match found with match_id={match_id}")

        # Get next feedback_id
        last = db.feedback.find_one(sort=[("feedback_id", -1)])
        next_id = (last["feedback_id"] + 1) if last else 1

        # INSERT feedback document
        db.feedback.insert_one({
            "feedback_id": next_id,
            "match_id": match_id,
            "is_useful": is_useful,
            "survival_rate": survival_rate,
            "doctor_comments": doctor_comments,
            "created_at": datetime.utcnow()
        })

        # ─── TRIGGER EQUIVALENT: Auto-update confidence score ───
        # This mirrors: CREATE TRIGGER trg_after_feedback AFTER INSERT ON Feedback
        agg_result = list(db.feedback.aggregate([
            {"$match": {"match_id": match_id}},
            {"$group": {
                "_id": None,
                "avg_useful": {"$avg": {"$cond": ["$is_useful", 1, 0]}}
            }}
        ]))

        if agg_result:
            db.similarity_matches.update_one(
                {"match_id": match_id},
                {"$set": {"confidence_score": round(agg_result[0]["avg_useful"], 4)}}
            )

        return True
    except ValueError:
        raise
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Failed to submit feedback for match_id={match_id}: {e}") from e


# ─────────────────────── DASHBOARD VIEW (SQL VIEW EQUIVALENT) ───────────────────────

def get_dashboard_view():
    """
    Multi-collection aggregation = MongoDB equivalent of SQL VIEW.
    Joins SimilarityMatch with PatientProfile (source + matched), Prognosis, and Feedback.
    """
    try:
        db = get_db()
        pipeline = [
            # JOIN: source patient
            {"$lookup": {
                "from": "patient_profiles",
                "localField": "source_patient_id",
                "foreignField": "patient_id",
                "as": "source"
            }},
            {"$unwind": "$source"},
            # JOIN: matched patient
            {"$lookup": {
                "from": "patient_profiles",
                "localField": "matched_patient_id",
                "foreignField": "patient_id",
                "as": "matched"
            }},
            {"$unwind": "$matched"},
            # JOIN: prognosis of matched patient
            {"$lookup": {
                "from": "prognosis",
                "localField": "matched_patient_id",
                "foreignField": "patient_id",
                "as": "prog"
            }},
            {"$unwind": {"path": "$prog", "preserveNullAndEmptyArrays": True}},
            # JOIN: feedback
            {"$lookup": {
                "from": "feedback",
                "localField": "match_id",
                "foreignField": "match_id",
                "as": "fb"
            }},
            # SORT and PROJECT
            {"$sort": {"similarity_score": -1}},
            {"$project": {
                "_id": 0,
                "match_id": 1,
                "source_id": "$source.patient_id",
                "source_age": "$source.age",
                "source_gender": "$source.gender",
                "matched_id": "$matched.patient_id",
                "matched_age": "$matched.age",
                "matched_gender": "$matched.gender",
                "similarity_score": 1,
                "confidence_score": 1,
                "treatment": "$prog.treatment",
                "survival_rate": "$prog.survival_rate",
                "feedback_count": {"$size": "$fb"}
            }}
        ]
        return list(db.similarity_matches.aggregate(pipeline))
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Dashboard view aggregation failed: {e}") from e


# ─────────────────────── STATISTICS (AGGREGATE FUNCTIONS) ───────────────────────

def get_statistics():
    """Get overall statistics using MongoDB aggregate functions."""
    try:
        db = get_db()
        stats = {
            "total_patients": db.patient_profiles.count_documents({}),
            "total_cases": db.clinical_cases.count_documents({}),
            "total_matches": db.similarity_matches.count_documents({}),
            "total_feedback": db.feedback.count_documents({}),
        }

        # Average survival rate using $group
        avg_result = list(db.prognosis.aggregate([
            {"$group": {
                "_id": None,
                "avg_survival": {"$avg": "$survival_rate"}
            }}
        ]))
        stats["avg_survival_rate"] = round(avg_result[0]["avg_survival"], 1) if avg_result else 0

        return stats
    except pymongo.errors.ConnectionFailure as e:
        raise RuntimeError(f"MongoDB unreachable: {e}") from e
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"Failed to compute statistics: {e}") from e
