# Musicaiman as Dante's music school

Musicaiman is both a public human guitar tutor and an optional curriculum provider for Dante/Mojum. The public service must not assume a human body, a camera, or even a physical guitar is present.

## Contract

- A student (human or agent) requests `GET /api/v1/exercises` and selects an exercise ID.
- The exercise returns concept IDs, tempo, meter, bar count, a symbolic pattern, instructions and evaluation guidance.
- A simulator or external runtime supplies *observations* (e.g. MIDI onset events, synthesized audio, microphone analysis, or calibrated vision) with explicit provenance. An agent's claimed performance is not treated as measured evidence.
- A separate evaluator can calculate timing accuracy, coverage and confidence; no performance scores are fabricated by the curriculum API.
- Progress belongs to the student runtime or a future opt-in progress service. Do not persist identifiable student activity on the anonymous public API by default.

## Integration

Dante's school runtime may consume the same lessons as humans through a thin adapter. Later add a versioned `attempt` schema, metronome/audio feature extractor and optional calibrated posture signals. Keep teaching content separate from embodiment, simulation time and personal memory.

## Safety and scope

The current exercises are guitar-focused. A future curriculum can add listening, pitch recognition, rhythm, composition, voice and instruments beyond guitar. Do not treat a virtual student as a human player or assume physical pain feedback.
