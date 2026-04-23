import sys
import os
import random

# Add project root to python path to allow importing src module
sys.path.insert(0, '/home/saurabh/Documents/Frontend')
from src.modules.module_36.database import get_db

db = get_db()

genders = ["Male", "Female"]
blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
addresses = ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Bhopal", "Chandigarh", "Patna", "Ranchi", "Guwahati", "Indore", "Nagpur", "Surat"]
lifestyles = ["smoker,sedentary", "non-smoker,active", "smoker,moderate", "non-smoker,sedentary", "smoker,active", "non-smoker,moderate"]

treatments = [
    "Chemotherapy + Radiation", "Medication + Lifestyle Change", "Surgery + Follow-up",
    "Palliative Care", "Observation Only", "Chemotherapy", "Hormone Therapy",
    "Physical Therapy", "Combined Therapy", "Surgery + Chemo", "Immunotherapy",
    "Radiation Therapy", "Targeted Therapy", "Monitoring", "Medication Adjustment"
]

prognosis_data_options = [
    "Stage II - recovery expected", "Early stage - good outlook", "Stage I - high success rate",
    "Stage IV - management focus", "Benign condition - monitoring", "Stage III - aggressive treatment",
    "Chronic - stable management", "Pre-clinical - watch and wait"
]

patients = []
cases = []
prognoses = []

# Fetch the max ID currently in the DB to avoid primary key collisions
max_patient = db.patient_profiles.find_one(sort=[("patient_id", -1)])
start_id = (max_patient["patient_id"] + 1) if max_patient else 1
end_id = start_id + 500

print(f"Generating 500 dummy records starting from ID {start_id}...")

for pid in range(start_id, end_id):
    patients.append({
        "patient_id": pid,
        "age": random.randint(18, 90),
        "gender": random.choice(genders),
        "blood_group": random.choice(blood_groups),
        "address": random.choice(addresses),
        "lifestyle_data": random.choice(lifestyles)
    })
    
    # Random symptom vector of 5 integers (1-10)
    sv = ",".join(str(random.randint(1, 10)) for _ in range(5))
    cases.append({
        "case_id": pid,  # keeping 1:1 mapping logic
        "patient_id": pid,
        "symptom_vector": sv,
        "severity_level": random.randint(1, 10)
    })
    
    prognoses.append({
        "prognosis_id": pid,
        "patient_id": pid,
        "treatment": random.choice(treatments),
        "prognosis_data": random.choice(prognosis_data_options),
        "survival_rate": round(random.uniform(30.0, 99.0), 1)
    })

db.patient_profiles.insert_many(patients)
db.clinical_cases.insert_many(cases)
db.prognosis.insert_many(prognoses)

print(f"Finished seeding 500 dummy records! Database now has {db.patient_profiles.count_documents({})} total patients.")
