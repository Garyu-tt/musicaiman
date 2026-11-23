"""Music school exercises shared by humans and autonomous students."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Exercise:
    id: str
    title: str
    concept_ids: tuple[str, ...]
    bpm: int
    beats_per_bar: int
    bars: int
    pattern: str
    instructions: str
    evaluation: str

EXERCISES = (
    Exercise("steady-eighths", "Ровные восьмые", ("alternate-picking",), 70, 4, 4,
             "D U D U D U D U", "Играй ровные восьмые под метроном. Не ускоряйся после паузы.",
             "Compare onset timing with 8 subdivisions per bar; report absolute timing error."),
    Exercise("muted-eighths", "Глушёные восьмые", ("palm-mute",), 80, 4, 4,
             "PM PM PM PM PM PM PM PM", "Слегка глуши струны у бриджа, сохраняя чёткую атаку.",
             "Report timing; muting quality requires audio evidence and cannot be inferred from taps."),
    Exercise("metal-gallop", "Металлический галоп", ("gallop",), 75, 4, 4,
             "D DU D DU", "Играй рисунок длинная-короткая-короткая, начиная медленно.",
             "Report onset timing; evaluate note articulation separately."),
)

def list_exercises():
    return [asdict(item) for item in EXERCISES]

def get_exercise(exercise_id):
    return next((asdict(item) for item in EXERCISES if item.id == exercise_id), None)
