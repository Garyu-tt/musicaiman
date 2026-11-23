from fastapi.testclient import TestClient
from app import app
from evaluation import evaluate_eighth_notes

client = TestClient(app)

def test_perfect_rhythm():
    onsets = [i * (30 / 70) for i in range(32)]
    result = evaluate_eighth_notes(onsets, 70, 4)
    assert result["mean_absolute_timing_error_ms"] == 0
    assert result["evaluation_scope"] == "timing_only"

def test_api_rejects_fabricated_or_malformed_onsets():
    path = "/api/v1/exercises/steady-eighths/evaluate"
    assert client.post(path, json={"onsets_seconds": [0, 0.5]}).status_code == 422
    assert client.post(path, json={"onsets_seconds": [0] * 32}).status_code == 422
    assert client.post("/api/v1/exercises/metal-gallop/evaluate", json={"onsets_seconds": [0]}).status_code == 422

def test_api_evaluates_supplied_onsets():
    onsets = [i * (30 / 70) for i in range(32)]
    response = client.post("/api/v1/exercises/steady-eighths/evaluate", json={"onsets_seconds": onsets})
    assert response.status_code == 200
    assert response.json()["mean_absolute_timing_error_ms"] == 0
