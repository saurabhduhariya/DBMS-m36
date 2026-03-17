# src/module_36/database.py
# MongoDB connection helper for Module 36 — Uses MongoDB Atlas
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env file from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

_client = None
_db = None

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "medicare_module36")

def get_client():
    """Get or create a MongoClient singleton."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client

def get_db():
    """Get the Module 36 database instance."""
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
    return _db

def close_connection():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
