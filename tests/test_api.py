from fastapi.testclient import TestClient
from app import app, CONCEPTS

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"ok": True}

def test_graph_integrity():
    response = client.get("/api/v1/graph")
    assert response.status_code == 200
    graph = response.json()
    ids = {concept["id"] for concept in graph["concepts"]}
    assert len(ids) == len(CONCEPTS)
    assert all(edge["source"] in ids and edge["target"] in ids for edge in graph["edges"])
    assert all(edge["source"] != edge["target"] for edge in graph["edges"])

def test_concept_not_found():
    assert client.get("/api/v1/concepts/nonexistent").status_code == 404

def test_palm_mute_chat():
    response = client.post("/api/v1/chat", json={"message": "Объясни palm mute"})
    assert response.status_code == 200
    result = response.json()
    assert any(c["id"] == "palm-mute" for c in result["concepts"])
    assert result["answer"]

def test_chat_limits():
    assert client.post("/api/v1/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/v1/chat", json={"message": "a" * 2001}).status_code == 422
    assert client.post("/api/v1/chat", json={"message": "test", "history": [{"role": "user", "content": "x"}] * 9}).status_code == 422
