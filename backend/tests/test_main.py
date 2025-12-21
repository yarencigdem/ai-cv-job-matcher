import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_match_similar_texts_high_score():
    payload = {
        "cv_text": "I know Python, FastAPI and Docker. I worked with AWS for deployments.",
        "job_text": "We are looking for a backend developer experienced in Python, FastAPI, Docker and AWS."
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "similarity_score" in data
    assert data["similarity_score"] > 60  


def test_match_different_texts_low_score():
    payload = {
        "cv_text": "I am a graphic designer with experience in Photoshop and Illustrator.",
        "job_text": "We are looking for a backend developer with Python and FastAPI experience."
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "similarity_score" in data
    assert data["similarity_score"] <= 100


def test_validation_short_text_error():
    payload = {
        "cv_text": "too short",
        "job_text": "also short"
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

