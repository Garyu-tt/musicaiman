import os
import re
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from storage import seed_concepts, list_videos
from limits import enforce_chat_limit
from exercises import list_exercises, get_exercise
from evaluation import evaluate_eighth_notes

app = FastAPI(title="Musicaiman API", version="0.1.0")
origins = [s.strip() for s in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

CONCEPTS = [
    {"id": "posture", "title": "Посадка и постановка рук", "prerequisites": [], "keywords": ["посадка", "кисть", "руки", "осанка"], "explanation": "Держи плечи расслабленными, избегай чрезмерного изгиба запястий. Проверяй удобство движений, а не копируй одну фиксированную позу."},
    {"id": "power-chords", "title": "Квинты / power chords", "prerequisites": ["posture"], "keywords": ["квинта", "аккорд", "power chord"], "explanation": "Квинта обычно состоит из основного тона и квинты. Сначала зажимай две струны, затем глуши лишние."},
    {"id": "alternate-picking", "title": "Переменный штрих", "prerequisites": ["posture"], "keywords": ["штрих", "медиатор", "alternate picking"], "explanation": "Чередуй движения медиатора вниз и вверх. Начинай медленно под метроном и следи за равномерностью атак."},
    {"id": "palm-mute", "title": "Palm mute", "prerequisites": ["power-chords"], "keywords": ["palm mute", "палм мьют", "глушение", "бридж"], "explanation": "Слегка касайся ребром ладони струн возле бриджа. Меняй положение по миллиметру, пока атака остаётся читаемой."},
    {"id": "downpicking", "title": "Даунпикинг", "prerequisites": ["alternate-picking"], "keywords": ["даунпикинг", "downpicking", "удары вниз"], "explanation": "Играй все атаки вниз с расслабленной кистью. Скорость повышай только после устойчивого ритма."},
    {"id": "gallop", "title": "Галоп и металкор-ритмы", "prerequisites": ["alternate-picking", "palm-mute"], "keywords": ["галоп", "металкор", "ритм", "gallop"], "explanation": "Отрабатывай рисунок длинная-короткая-короткая под метроном, затем соединяй с palm mute."},
]
# Curated video links live in SQLite, never in unreviewed generated content.
seed_concepts(CONCEPTS)

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[Message] = Field(default_factory=list, max_length=8)


def retrieve(query: str):
    q = query.casefold()
    tokens = set(re.findall(r"[\\w-]+", q))
    ranked = []
    for c in CONCEPTS:
        terms = [c["title"], *c["keywords"]]
        score = sum(3 if term.casefold() in q else len(tokens & set(re.findall(r"[\\w-]+", term.casefold()))) for term in terms)
        if score:
            ranked.append((score, c))
    return [c for _, c in sorted(ranked, key=lambda x: -x[0])[:3]]


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/v1/graph")
def graph():
    return {"concepts": CONCEPTS, "edges": [{"source": p, "target": c["id"], "type": "prerequisite"} for c in CONCEPTS for p in c["prerequisites"]], "videos": list_videos()}


@app.get("/api/v1/concepts/{concept_id}")
def concept(concept_id: str):
    item = next((c for c in CONCEPTS if c["id"] == concept_id), None)
    if item is None:
        raise HTTPException(404, "Concept not found")
    return {**item, "videos": list_videos(concept_id)}


@app.post("/api/v1/chat", dependencies=[Depends(enforce_chat_limit)])
async def chat(request: ChatRequest):
    matches = retrieve(request.message)
    context = "\n".join(f'{c["title"]}: {c["explanation"]}' for c in matches)
    answer = "\n".join(f'{c["title"]}: {c["explanation"]}' for c in matches) if matches else "Уточни, какой приём или рифф интересует. Например: palm mute, квинты или переменный штрих."
    base = os.getenv("LLM_BASE_URL", "").rstrip("/")
    model = os.getenv("LLM_MODEL", "")
    if base and model:
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                response = await client.post(base + "/chat/completions", headers={"Authorization": "Bearer " + os.getenv("LLM_API_KEY", "local")}, json={"model": model, "messages": [{"role": "system", "content": "Ты терпеливый преподаватель электрогитары. Отвечай на русском, коротко и с упражнениями. Используй учебный контекст, не выдумывай ссылки или результаты анализа аудио/видео. Контекст:\n" + context}, *[m.model_dump() for m in request.history], {"role": "user", "content": request.message}], "temperature": 0.4, "max_tokens": 500})
                response.raise_for_status()
                answer = response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
            pass
    return {"answer": answer, "concepts": matches, "videos": [v for c in matches for v in list_videos(c["id"])]}


@app.get("/api/v1/exercises")
def exercises():
    return {"exercises": list_exercises()}


@app.get("/api/v1/exercises/{exercise_id}")
def exercise(exercise_id: str):
    item = get_exercise(exercise_id)
    if item is None:
        raise HTTPException(404, "Exercise not found")
    return item


class RhythmAttempt(BaseModel):
    onsets_seconds: list[float] = Field(min_length=1, max_length=1536)


@app.post("/api/v1/exercises/{exercise_id}/evaluate")
def evaluate_exercise(exercise_id: str, attempt: RhythmAttempt):
    item = get_exercise(exercise_id)
    if item is None:
        raise HTTPException(404, "Exercise not found")
    if exercise_id not in {"steady-eighths", "muted-eighths"}:
        raise HTTPException(422, "Timing evaluator not available for this pattern")
    try:
        return {"exercise_id": exercise_id, **evaluate_eighth_notes(attempt.onsets_seconds, item["bpm"], item["bars"], item["beats_per_bar"])}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
