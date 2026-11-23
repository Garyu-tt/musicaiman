"""Optional accounts and personal music library routes."""
from typing import Literal
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from accounts import register, login, current_user, logout, now
from storage import connect

router = APIRouter(prefix="/api/v1")

class Credentials(BaseModel):
    nickname: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=10, max_length=256)

class Melody(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    notation: str = Field(default="", max_length=20000)
    source_url: str = Field(default="", max_length=1000)

class Progress(BaseModel):
    status: Literal["new", "in_progress", "completed"]

def user(authorization: str | None = Header(default=None)):
    return current_user(authorization)

@router.post("/auth/register", status_code=201)
def create_account(body: Credentials):
    return register(body.nickname, body.password)

@router.post("/auth/login")
def sign_in(body: Credentials):
    return login(body.nickname, body.password)

@router.get("/auth/me")
def me(account=Depends(user)):
    return account

@router.post("/auth/logout")
def sign_out(authorization: str | None = Header(default=None), account=Depends(user)):
    logout(authorization[7:])
    return {"ok": True}

@router.get("/me/melodies")
def melodies(account=Depends(user)):
    with connect() as db:
        return {"melodies": [dict(row) for row in db.execute(
            "SELECT id,title,notation,source_url,created_at FROM saved_melodies WHERE user_id=? ORDER BY id DESC",
            (account["id"],))]}

@router.post("/me/melodies", status_code=201)
def save_melody(body: Melody, account=Depends(user)):
    with connect() as db:
        count = db.execute("SELECT COUNT(*) FROM saved_melodies WHERE user_id=?", (account["id"],)).fetchone()[0]
        if count >= 1000:
            raise HTTPException(409, "Melody quota reached")
        cur = db.execute(
            "INSERT INTO saved_melodies(user_id,title,notation,source_url,created_at) VALUES(?,?,?,?,?)",
            (account["id"], body.title, body.notation, body.source_url, now().isoformat()))
        return {"id": cur.lastrowid}

@router.delete("/me/melodies/{melody_id}")
def delete_melody(melody_id: int, account=Depends(user)):
    with connect() as db:
        cur = db.execute("DELETE FROM saved_melodies WHERE id=? AND user_id=?", (melody_id, account["id"]))
        if cur.rowcount == 0:
            raise HTTPException(404, "Melody not found")
        return {"ok": True}

@router.get("/me/progress")
def get_progress(account=Depends(user)):
    with connect() as db:
        return {"progress": [dict(row) for row in db.execute(
            "SELECT lesson_id,status,updated_at FROM lesson_progress WHERE user_id=? ORDER BY lesson_id",
            (account["id"],))]}

@router.put("/me/progress/{lesson_id}")
def put_progress(lesson_id: str, body: Progress, account=Depends(user)):
    if not (1 <= len(lesson_id) <= 100):
        raise HTTPException(422, "Invalid lesson id")
    with connect() as db:
        db.execute("""INSERT INTO lesson_progress(user_id,lesson_id,status,updated_at)
                      VALUES(?,?,?,?) ON CONFLICT(user_id,lesson_id)
                      DO UPDATE SET status=excluded.status,updated_at=excluded.updated_at""",
                   (account["id"], lesson_id, body.status, now().isoformat()))
    return {"ok": True}
