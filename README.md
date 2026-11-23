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
