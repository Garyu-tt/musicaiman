import sqlite3
import storage
from app import CONCEPTS

def test_seed_is_idempotent_and_relationships_persist(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "graph.sqlite3"))
    storage.seed_concepts(CONCEPTS)
    storage.seed_concepts(CONCEPTS)
    with storage.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM concepts").fetchone()[0] == len(CONCEPTS)
        assert db.execute("SELECT COUNT(*) FROM prerequisites").fetchone()[0] == sum(len(c["prerequisites"]) for c in CONCEPTS)
        db.execute("INSERT INTO videos(id,title,url,source,verified_at) VALUES(?,?,?,?,?)", ("v1", "Test lesson", "https://www.youtube.com/watch?v=test", "youtube", "2026-11-23"))
        db.execute("INSERT INTO concept_videos(concept_id,video_id,start_seconds,end_seconds) VALUES(?,?,?,?)", ("palm-mute", "v1", 10, 40))
    rows = storage.list_videos("palm-mute")
    assert len(rows) == 1 and rows[0]["start_seconds"] == 10
    assert storage.list_videos("downpicking") == []

def test_invalid_timestamps_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "graph.sqlite3"))
    storage.seed_concepts(CONCEPTS)
    with storage.connect() as db:
        db.execute("INSERT INTO videos(id,title,url,source,verified_at) VALUES(?,?,?,?,?)", ("v1", "Test", "https://example.com", "test", "2026-11-23"))
        try:
            db.execute("INSERT INTO concept_videos(concept_id,video_id,start_seconds,end_seconds) VALUES(?,?,?,?)", ("palm-mute", "v1", 40, 10))
            assert False, "Invalid timestamps accepted"
        except sqlite3.IntegrityError:
            pass
