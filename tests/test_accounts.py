import pytest
from fastapi.testclient import TestClient
import storage
import accounts
from app import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "accounts.sqlite3"))
    return TestClient(app)

def test_register_login_and_private_library(client):
    assert client.post("/api/v1/auth/register", json={"nickname":"guitar_1","password":"long-password-123"}).status_code == 201
    assert client.post("/api/v1/auth/register", json={"nickname":"GUITAR_1","password":"long-password-123"}).status_code == 409
    assert client.post("/api/v1/auth/login", json={"nickname":"guitar_1","password":"wrong-password"}).status_code == 401
    login = client.post("/api/v1/auth/login", json={"nickname":"guitar_1","password":"long-password-123"})
    assert login.status_code == 200
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    assert client.get("/api/v1/auth/me", headers=headers).json()["nickname"] == "guitar_1"
    assert client.get("/api/v1/me/melodies").status_code == 401
    result = client.post("/api/v1/me/melodies", json={"title":"My riff","notation":"E|--0-3--|"}, headers=headers)
    assert result.status_code == 201
    melody_id = result.json()["id"]
    assert client.get("/api/v1/me/melodies", headers=headers).json()["melodies"][0]["title"] == "My riff"
    assert client.put("/api/v1/me/progress/steady-eighths", json={"status":"in_progress"}, headers=headers).status_code == 200
    assert client.get("/api/v1/me/progress", headers=headers).json()["progress"][0]["status"] == "in_progress"
    assert client.delete(f"/api/v1/me/melodies/{melody_id}", headers=headers).status_code == 200
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401

def test_user_isolation(client):
    headers = []
    for name in ("alpha", "bravo"):
        client.post("/api/v1/auth/register", json={"nickname":name,"password":"long-password-123"})
        token = client.post("/api/v1/auth/login", json={"nickname":name,"password":"long-password-123"}).json()["access_token"]
        headers.append({"Authorization":"Bearer "+token})
    melody = client.post("/api/v1/me/melodies", json={"title":"Private"}, headers=headers[0]).json()["id"]
    assert client.get("/api/v1/me/melodies", headers=headers[1]).json()["melodies"] == []
    assert client.delete(f"/api/v1/me/melodies/{melody}", headers=headers[1]).status_code == 404
