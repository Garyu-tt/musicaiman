# Legacy music work inventory

Source: user-directed retrieval of prior conversations, 2026-08-29. This is an architecture recovery, **not** a claim that old source files were imported.

## Confirmed prior discussion

- INFINI LOOP (`davidegat/infiniloop`): continuous generated backing music, segments queued and crossfaded.
- Proposed Android phone controller/player, while MusicGen or another generator runs on a PC/server.
- Guitar-practice controls: genre (including metal), key, BPM, drums, bass, rhythm guitar.
- Desired flow: prompt -> generate next segment -> check loop/transition -> queue -> crossfade.
- Offline/local-first playback and Bluetooth control are desirable.

## Proposed Musicaiman integration

`BackingTrackRequest` is a provider-neutral, declarative specification, not a request to immediately run a costly model.

`GET /api/v1/backing/providers`: list supported generation modes and honest availability.
`POST /api/v1/backing/spec`: validate/normalize a backing-track specification without generating audio.

Future modules:
- `providers/musicgen.py`: optional server-side model worker with strict budget and cancellation.
- `providers/user_device.py`: WebGPU/WebAssembly local inference capability check, never silently download a large model.
- `player/`: client-side audio queue, prefetch, crossfade, Bluetooth media controls.
- `library/`: save a spec, seed, licensing metadata and generated audio artifact only when requested.
- Dante/Mojum adapter: share tempo/key/structure with school exercises and accept observed performance data.

## Constraints

No evidence yet of an existing private-server checkout or files. Do not mark them migrated. Verify license and model weights before incorporating third-party source. Avoid storing raw audio by default. An endless generation service needs quotas and cancellation to prevent runaway compute.
