# Musicaiman

Open, anonymous AI guitar tutor backend. Frontear is the separate reusable frontend.

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Endpoints: `GET /health`, `GET /api/v1/graph`, `GET /api/v1/concepts/{id}`, `POST /api/v1/chat`.

Chat uses concept retrieval and verified teaching links. Optional OpenAI-compatible local LLM configured by `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`. Without a model it uses deterministic grounded answers. No login or registration. Public deployment must enforce network rate limits and model quotas.

Video URLs are seed candidates and should be curated and verified before public launch. Never treat video content as reviewed unless actually reviewed.

## Anonymous chat limits

`CHAT_REQUESTS_PER_MINUTE=12` (default) limits requests to `/api/v1/chat` per direct peer IP. HTTP 429 includes `Retry-After`. This in-memory limiter is per process only: for production behind a reverse proxy or multiple workers, configure trusted proxy handling at the ingress and enforce a shared gateway/Redis quota. Do not rely on this mechanism alone for paid inference. Set `LLM_BASE_URL` only to a trusted service; never expose model credentials to the frontend.

## Local checks

```bash
pip install -r requirements-dev.txt
pytest -q
```
