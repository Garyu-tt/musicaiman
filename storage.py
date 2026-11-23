"""SQLite persistence for curated music teaching resources."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.getenv("MUSICAIMAN_DB", "data/musicaiman.sqlite3")

@contextmanager
def connect():
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA foreign_keys=ON")
        yield db
        db.commit()
    finally:
        db.close()

def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS concepts (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, explanation TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS prerequisites (
          concept_id TEXT NOT NULL REFERENCES concepts(id),
          prerequisite_id TEXT NOT NULL REFERENCES concepts(id),
          PRIMARY KEY(concept_id, prerequisite_id),
          CHECK(concept_id != prerequisite_id)
        );
        CREATE TABLE IF NOT EXISTS videos (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL,
          source TEXT NOT NULL, verified_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS concept_videos (
          concept_id TEXT NOT NULL REFERENCES concepts(id),
          video_id TEXT NOT NULL REFERENCES videos(id),
          start_seconds INTEGER NOT NULL DEFAULT 0 CHECK(start_seconds >= 0),
          end_seconds INTEGER CHECK(end_seconds IS NULL OR end_seconds > start_seconds),
          notes TEXT NOT NULL DEFAULT '',
          PRIMARY KEY(concept_id, video_id, start_seconds)
        );
        CREATE INDEX IF NOT EXISTS idx_concept_videos_video ON concept_videos(video_id);
        """)

def seed_concepts(concepts):
    initialize()
    with connect() as db:
        for c in concepts:
            db.execute("INSERT OR IGNORE INTO concepts(id,title,explanation) VALUES(?,?,?)",
                       (c["id"], c["title"], c["explanation"]))
        for c in concepts:
            for parent in c["prerequisites"]:
                db.execute("INSERT OR IGNORE INTO prerequisites(concept_id,prerequisite_id) VALUES(?,?)",
                           (c["id"], parent))

def list_videos(concept_id=None):
    initialize()
    with connect() as db:
        query = """SELECT v.id,v.title,v.url,v.source,v.verified_at,
                          cv.concept_id,cv.start_seconds,cv.end_seconds,cv.notes
                   FROM videos v JOIN concept_videos cv ON cv.video_id=v.id"""
        args = ()
        if concept_id is not None:
            query += " WHERE cv.concept_id=?"
            args = (concept_id,)
        query += " ORDER BY v.id,cv.start_seconds"
        return [dict(row) for row in db.execute(query, args)]
