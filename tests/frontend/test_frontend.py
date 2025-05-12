import sys
import os
import pytest 

# Add the frontend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend')))

from frontend import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    # Check for actual content in the HTML page
    assert b"Liver Disease Prediction System" in response.data
