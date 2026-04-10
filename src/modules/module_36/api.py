# src/modules/module_36/api.py
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

from src.modules.module_36.service import find_similar_patients

# Allow this file to be run from anywhere by resolving the correct .env path
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

app = FastAPI(
    title="Module 36 API",
    description="Similar Patient Case Retrieval System API for other modules to access.",
    version="1.0.0"
)

# Fetch the API key from environment variables (fallback for local dev)
API_KEY = os.getenv("MODULE_36_API_KEY", "m36_super_secret_api_key_2026")
API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=401, detail="Could not validate API KEY. Please pass 'x-api-key' in headers."
        )

@app.get("/api/module_36/similarity/{patient_id}")
async def get_similarity(patient_id: int, api_key: str = Depends(get_api_key)):
    """
    Fetch the top 10 similar patients for a given patient_id.
    Requires 'x-api-key' in request headers.
    """
    try:
        matches = find_similar_patients(patient_id)
        if not matches:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found or no matches computed.")
        return {
            "status": "success",
            "source_patient_id": patient_id,
            "similar_cases": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
