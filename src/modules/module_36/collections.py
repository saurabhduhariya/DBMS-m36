# src/module_36/collections.py
# MongoDB collection setup: schemas, indexes, and seed data for Module 36
from datetime import datetime
from src.modules.module_36.database import get_db


def create_indexes(db):
    """Create indexes for all collections (performance optimization)."""
    db.patient_profiles.create_index("patient_id", unique=True)
    db.clinical_cases.create_index("patient_id")
    db.clinical_cases.create_index("case_id", unique=True)
    db.prognosis.create_index("patient_id", unique=True)
    db.prognosis.create_index("prognosis_id", unique=True)
    db.similarity_algorithms.create_index("algo_id", unique=True)
    db.similarity_matches.create_index("match_id", unique=True)
    db.similarity_matches.create_index([("similarity_score", -1)])
    db.similarity_matches.create_index("source_patient_id")
    db.feedback.create_index("feedback_id", unique=True)
    db.feedback.create_index("match_id")


def seed_patient_profiles(db):
    """Insert 20 sample patient profiles."""
    patients = [
        {"patient_id": 1,  "age": 45, "gender": "Male",   "blood_group": "O+",  "address": "Delhi",       "lifestyle_data": "smoker,sedentary"},
        {"patient_id": 2,  "age": 52, "gender": "Female", "blood_group": "A+",  "address": "Mumbai",      "lifestyle_data": "non-smoker,active"},
        {"patient_id": 3,  "age": 38, "gender": "Male",   "blood_group": "B+",  "address": "Kolkata",     "lifestyle_data": "smoker,moderate"},
        {"patient_id": 4,  "age": 61, "gender": "Female", "blood_group": "AB+", "address": "Chennai",     "lifestyle_data": "non-smoker,sedentary"},
        {"patient_id": 5,  "age": 29, "gender": "Male",   "blood_group": "O-",  "address": "Bangalore",   "lifestyle_data": "non-smoker,active"},
        {"patient_id": 6,  "age": 47, "gender": "Male",   "blood_group": "O+",  "address": "Hyderabad",   "lifestyle_data": "smoker,sedentary"},
        {"patient_id": 7,  "age": 55, "gender": "Female", "blood_group": "A-",  "address": "Pune",        "lifestyle_data": "non-smoker,moderate"},
        {"patient_id": 8,  "age": 33, "gender": "Male",   "blood_group": "B+",  "address": "Ahmedabad",   "lifestyle_data": "non-smoker,active"},
        {"patient_id": 9,  "age": 68, "gender": "Female", "blood_group": "O+",  "address": "Jaipur",      "lifestyle_data": "non-smoker,sedentary"},
        {"patient_id": 10, "age": 42, "gender": "Male",   "blood_group": "A+",  "address": "Lucknow",     "lifestyle_data": "smoker,moderate"},
        {"patient_id": 11, "age": 50, "gender": "Female", "blood_group": "B-",  "address": "Bhopal",      "lifestyle_data": "non-smoker,active"},
        {"patient_id": 12, "age": 36, "gender": "Male",   "blood_group": "AB-", "address": "Chandigarh",  "lifestyle_data": "smoker,active"},
        {"patient_id": 13, "age": 59, "gender": "Female", "blood_group": "O+",  "address": "Patna",       "lifestyle_data": "non-smoker,sedentary"},
        {"patient_id": 14, "age": 44, "gender": "Male",   "blood_group": "A+",  "address": "Ranchi",      "lifestyle_data": "smoker,moderate"},
        {"patient_id": 15, "age": 27, "gender": "Female", "blood_group": "B+",  "address": "Dehradun",    "lifestyle_data": "non-smoker,active"},
        {"patient_id": 16, "age": 63, "gender": "Male",   "blood_group": "O-",  "address": "Guwahati",    "lifestyle_data": "non-smoker,sedentary"},
        {"patient_id": 17, "age": 41, "gender": "Female", "blood_group": "AB+", "address": "Indore",      "lifestyle_data": "smoker,moderate"},
        {"patient_id": 18, "age": 34, "gender": "Male",   "blood_group": "A-",  "address": "Nagpur",      "lifestyle_data": "non-smoker,active"},
        {"patient_id": 19, "age": 57, "gender": "Female", "blood_group": "O+",  "address": "Varanasi",    "lifestyle_data": "non-smoker,moderate"},
        {"patient_id": 20, "age": 48, "gender": "Male",   "blood_group": "B+",  "address": "Surat",       "lifestyle_data": "smoker,sedentary"},
    ]
    db.patient_profiles.insert_many(patients)


def seed_clinical_cases(db):
    """Insert clinical cases for each patient."""
    cases = [
        {"case_id": 1,  "patient_id": 1,  "symptom_vector": "7,3,8,5,2",  "severity_level": 7},
        {"case_id": 2,  "patient_id": 2,  "symptom_vector": "4,6,3,8,5",  "severity_level": 5},
        {"case_id": 3,  "patient_id": 3,  "symptom_vector": "6,4,7,3,4",  "severity_level": 6},
        {"case_id": 4,  "patient_id": 4,  "symptom_vector": "8,7,9,6,8",  "severity_level": 9},
        {"case_id": 5,  "patient_id": 5,  "symptom_vector": "2,1,3,2,1",  "severity_level": 2},
        {"case_id": 6,  "patient_id": 6,  "symptom_vector": "7,4,8,5,3",  "severity_level": 7},
        {"case_id": 7,  "patient_id": 7,  "symptom_vector": "5,5,4,7,6",  "severity_level": 6},
        {"case_id": 8,  "patient_id": 8,  "symptom_vector": "3,2,4,3,2",  "severity_level": 3},
        {"case_id": 9,  "patient_id": 9,  "symptom_vector": "9,8,8,7,9",  "severity_level": 9},
        {"case_id": 10, "patient_id": 10, "symptom_vector": "6,5,7,4,5",  "severity_level": 6},
        {"case_id": 11, "patient_id": 11, "symptom_vector": "5,4,5,6,4",  "severity_level": 5},
        {"case_id": 12, "patient_id": 12, "symptom_vector": "4,3,5,4,3",  "severity_level": 4},
        {"case_id": 13, "patient_id": 13, "symptom_vector": "8,6,7,8,7",  "severity_level": 8},
        {"case_id": 14, "patient_id": 14, "symptom_vector": "6,4,7,5,3",  "severity_level": 6},
        {"case_id": 15, "patient_id": 15, "symptom_vector": "2,2,3,1,2",  "severity_level": 2},
        {"case_id": 16, "patient_id": 16, "symptom_vector": "7,6,8,7,6",  "severity_level": 8},
        {"case_id": 17, "patient_id": 17, "symptom_vector": "5,5,6,4,5",  "severity_level": 5},
        {"case_id": 18, "patient_id": 18, "symptom_vector": "3,2,4,2,3",  "severity_level": 3},
        {"case_id": 19, "patient_id": 19, "symptom_vector": "7,5,6,6,5",  "severity_level": 7},
        {"case_id": 20, "patient_id": 20, "symptom_vector": "6,5,7,5,4",  "severity_level": 7},
    ]
    db.clinical_cases.insert_many(cases)


def seed_prognosis(db):
    """Insert prognosis data for each patient."""
    prognosis = [
        {"prognosis_id": 1,  "patient_id": 1,  "treatment": "Chemotherapy + Radiation",     "prognosis_data": "Stage II - recovery expected",     "survival_rate": 85.0},
        {"prognosis_id": 2,  "patient_id": 2,  "treatment": "Medication + Lifestyle Change", "prognosis_data": "Early stage - good outlook",       "survival_rate": 92.0},
        {"prognosis_id": 3,  "patient_id": 3,  "treatment": "Surgery + Follow-up",           "prognosis_data": "Stage I - high success rate",      "survival_rate": 90.0},
        {"prognosis_id": 4,  "patient_id": 4,  "treatment": "Palliative Care",               "prognosis_data": "Stage IV - management focus",      "survival_rate": 35.0},
        {"prognosis_id": 5,  "patient_id": 5,  "treatment": "Observation Only",              "prognosis_data": "Benign condition - monitoring",     "survival_rate": 98.0},
        {"prognosis_id": 6,  "patient_id": 6,  "treatment": "Chemotherapy",                  "prognosis_data": "Stage II - moderate response",     "survival_rate": 78.0},
        {"prognosis_id": 7,  "patient_id": 7,  "treatment": "Hormone Therapy",               "prognosis_data": "Stage II - positive response",     "survival_rate": 88.0},
        {"prognosis_id": 8,  "patient_id": 8,  "treatment": "Physical Therapy",              "prognosis_data": "Minor condition - full recovery",   "survival_rate": 96.0},
        {"prognosis_id": 9,  "patient_id": 9,  "treatment": "Combined Therapy",              "prognosis_data": "Stage III - aggressive treatment",  "survival_rate": 45.0},
        {"prognosis_id": 10, "patient_id": 10, "treatment": "Surgery + Chemo",               "prognosis_data": "Stage II - standard protocol",     "survival_rate": 82.0},
        {"prognosis_id": 11, "patient_id": 11, "treatment": "Immunotherapy",                 "prognosis_data": "Stage II - responding well",       "survival_rate": 86.0},
        {"prognosis_id": 12, "patient_id": 12, "treatment": "Radiation Therapy",             "prognosis_data": "Stage I - excellent prognosis",    "survival_rate": 93.0},
        {"prognosis_id": 13, "patient_id": 13, "treatment": "Chemotherapy + Surgery",        "prognosis_data": "Stage III - moderate outlook",     "survival_rate": 55.0},
        {"prognosis_id": 14, "patient_id": 14, "treatment": "Targeted Therapy",              "prognosis_data": "Stage II - good response",         "survival_rate": 80.0},
        {"prognosis_id": 15, "patient_id": 15, "treatment": "Monitoring",                    "prognosis_data": "Pre-clinical - watch and wait",    "survival_rate": 97.0},
        {"prognosis_id": 16, "patient_id": 16, "treatment": "Palliative + Chemo",            "prognosis_data": "Stage III - comfort measures",     "survival_rate": 42.0},
        {"prognosis_id": 17, "patient_id": 17, "treatment": "Medication Adjustment",         "prognosis_data": "Chronic - stable management",      "survival_rate": 84.0},
        {"prognosis_id": 18, "patient_id": 18, "treatment": "Lifestyle + Medication",        "prognosis_data": "Early stage - preventive care",    "survival_rate": 95.0},
        {"prognosis_id": 19, "patient_id": 19, "treatment": "Combination Therapy",           "prognosis_data": "Stage II - steady improvement",    "survival_rate": 76.0},
        {"prognosis_id": 20, "patient_id": 20, "treatment": "Surgery + Radiation",           "prognosis_data": "Stage II - scheduled treatment",   "survival_rate": 81.0},
    ]
    db.prognosis.insert_many(prognosis)


def seed_algorithms(db):
    """Insert the default similarity algorithm."""
    db.similarity_algorithms.insert_one({
        "algo_id": 1,
        "algo_name": "Weighted Euclidean Distance (MongoDB Aggregation)"
    })


def init_collections():
    """Drop and recreate all collections with indexes and seed data."""
    db = get_db()

    # Drop existing collections for clean reset
    for coll_name in ["patient_profiles", "clinical_cases", "prognosis",
                      "similarity_algorithms", "similarity_matches", "feedback"]:
        db.drop_collection(coll_name)

    # Seed data
    seed_patient_profiles(db)
    seed_clinical_cases(db)
    seed_prognosis(db)
    seed_algorithms(db)

    # Create indexes
    create_indexes(db)

    return True
