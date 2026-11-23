"""Small single-process rate limiter for anonymous inference endpoints.

For multi-worker deployments use a shared Redis limiter or an ingress gateway.
"""
import os
import threading
import time
from collections import deque

from fastapi import HTTPException, Request

_lock = threading.Lock()
_hits = {}
_last_sweep = 0.0

def enforce_chat_limit(request: Request):
    global _last_sweep
    limit = max(1, int(os.getenv("CHAT_REQUESTS_PER_MINUTE", "12")))
    window = 60.0
    now = time.monotonic()
    # Only the direct peer address is trusted. Do not accept client-controlled X-Forwarded-For.
    client = request.client.host if request.client else "unknown"
    with _lock:
        if now - _last_sweep > window:
            for key, times in list(_hits.items()):
                while times and now - times[0] >= window:
                    times.popleft()
                if not times:
                    del _hits[key]
            _last_sweep = now
        times = _hits.setdefault(client, deque())
        while times and now - times[0] >= window:
            times.popleft()
        if len(times) >= limit:
            retry = max(1, int(window - (now - times[0])) + 1)
            raise HTTPException(status_code=429, detail="Chat request limit exceeded", headers={"Retry-After": str(retry)})
        times.append(now)
