import pytest
from fastapi import HTTPException
from starlette.requests import Request
import limits

def request(ip="127.0.0.1"):
    return Request({"type": "http", "method": "POST", "path": "/api/v1/chat", "headers": [], "client": (ip, 4000), "server": ("localhost", 8000), "scheme": "http"})

def test_limit_and_retry(monkeypatch):
    monkeypatch.setenv("CHAT_REQUESTS_PER_MINUTE", "2")
    monkeypatch.setattr(limits, "_hits", {})
    monkeypatch.setattr(limits, "_last_sweep", 0.0)
    limits.enforce_chat_limit(request("10.0.0.1"))
    limits.enforce_chat_limit(request("10.0.0.1"))
    with pytest.raises(HTTPException) as exc:
        limits.enforce_chat_limit(request("10.0.0.1"))
    assert exc.value.status_code == 429
    assert int(exc.value.headers["Retry-After"]) >= 1
    limits.enforce_chat_limit(request("10.0.0.2"))

def test_ignores_untrusted_forwarded_header(monkeypatch):
    monkeypatch.setenv("CHAT_REQUESTS_PER_MINUTE", "1")
    monkeypatch.setattr(limits, "_hits", {})
    monkeypatch.setattr(limits, "_last_sweep", 0.0)
    first = request("192.0.2.1")
    limits.enforce_chat_limit(first)
    spoofed = Request({"type": "http", "method": "POST", "path": "/api/v1/chat", "headers": [(b"x-forwarded-for", b"198.51.100.8")], "client": ("192.0.2.1", 4001), "server": ("localhost", 8000), "scheme": "http"})
    with pytest.raises(HTTPException) as exc:
        limits.enforce_chat_limit(spoofed)
    assert exc.value.status_code == 429
