import pytest
import sys
import os
from fastapi.testclient import TestClient

# Ensure the backend/src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

from main import app  # Import the FastAPI app from backend/src/main.py

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}  # Adjust based on your endpoint
