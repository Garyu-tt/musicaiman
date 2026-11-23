"""Provider-neutral backing track requests. No model execution or audio storage."""
from typing import Literal
from pydantic import BaseModel, Field

class BackingTrackSpec(BaseModel):
    genre: Literal["metal", "metalcore", "rock", "blues", "jazz", "ambient", "other"] = "metal"
    bpm: int = Field(default=100, ge=40, le=240)
    key: str = Field(default="E", pattern=r"^[A-G](?:#|b)?m?$")
    bars: int = Field(default=8, ge=1, le=64)
    drums: bool = True
    bass: bool = True
    rhythm_guitar: bool = False
    prompt: str = Field(default="", max_length=500)

def providers():
    return {
        "providers": [
            {"id": "spec-only", "available": True, "execution": "none", "description": "Validate a track specification without AI inference"},
            {"id": "server-musicgen", "available": False, "execution": "server", "description": "Optional future budget-limited music generation worker"},
            {"id": "client-local", "available": False, "execution": "device", "description": "Future client capability-gated local inference"},
        ]
    }
