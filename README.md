## 🚀 Live Demo & API
- **Frontend App (Streamlit):** 👉 [https://dbms-m36.streamlit.app/](https://dbms-m36.streamlit.app/)
- **Backend API (Render):** 👉 [https://dbms-m36.onrender.com/](https://dbms-m36.onrender.com/) *(Requires `x-api-key` header)*

              MediCare: Patient Similarity Retrieval System
A DBMS group project designed to help doctors find similar patient cases using SQL-based similarity logic.

  Key Features
Similarity Search: Uses Euclidean Distance in SQL to find matching patient profiles.

Role Dashboards: Separate portals for Patients, Doctors, and Admins.

Optimized Navigation: Smooth integration between Streamlit and FastAPI.

Tech Stack
Database: MariaDB / SQL

Backend: Python (FastAPI)

Frontend: Streamlit

## 📡 API Usage Guide

Other modules can search the database for similar patients by sending a GET request to the Render API endpoint. You must include the `x-api-key` header for authentication.

### Using cURL (Terminal)
```bash
curl -X GET "https://dbms-m36.onrender.com/api/module_36/similarity/1" \
     -H "x-api-key: m36_super_secret_api_key_2026"
```

### Using Python (Requests)
```python
import requests

url = "https://dbms-m36.onrender.com/api/module_36/similarity/1" # Replace 1 with any patient_id
headers = {
    "x-api-key": "m36_super_secret_api_key_2026"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.text}")
```
