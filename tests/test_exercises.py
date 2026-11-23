from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_exercises_have_known_concepts():
    concepts = {c["id"] for c in client.get("/api/v1/graph").json()["concepts"]}
    response = client.get("/api/v1/exercises")
    assert response.status_code == 200
    items = response.json()["exercises"]
    assert len(items) >= 3
    assert len({item["id"] for item in items}) == len(items)
    for item in items:
        assert set(item["concept_ids"]) <= concepts
        assert item["bpm"] > 0 and item["bars"] > 0
        assert item["evaluation"]
        assert client.get(f'/api/v1/exercises/{item["id"]}').json() == item

def test_missing_exercise():
    assert client.get("/api/v1/exercises/not-real").status_code == 404
