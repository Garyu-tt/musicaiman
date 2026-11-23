# Storage and low-cost inference architecture

## Previous music projects
Consolidation target: Musicaiman. Source repositories/files for earlier music-service experiments have not yet been positively identified; do not claim they were migrated. Inventory source modules and licenses before importing them. Keep Frontear as the shared UI layer.

## Minimal storage
SQLite contains nicknames, salted scrypt password hashes, hashed bearer sessions, saved melody text/tab/links and per-lesson status. No audio recordings or model weights are stored in the account database. Text-only melody records are capped at 20,000 characters and 1,000 records/account. Browser-local progress remains available without an account; sync is optional.

Illustrative sizing: 1,000 short melody entries at 2 KB each are about 2 MB of text before SQLite indexes and overhead. Actual size depends on notation length, number of users, journaling, and backups. Large audio files belong in optional object storage or on the user's device, not SQLite.

## CPU-first and browser-first inference
1. Deterministic browser DSP: Web Audio for onsets, tempo and basic pitch detection. This requires no server-side model.
2. Browser vision: MediaPipe Hands (Frontear live-vision prototype), with camera data staying local by default. Requires calibration to the guitar.
3. Lightweight browser ASR or local on-device model when hardware supports it. Feature-detect and provide a non-ML fallback.
4. Server fallback: a small quantized local model on CPU for explanation, with retrieval over the curriculum and hard per-user/inference quotas. Cache repeated explanations; avoid running an LLM for deterministic scoring.
5. Optional user-supplied provider endpoint or BYOK only with explicit opt-in and clear disclosure. Never transmit raw camera/audio to an external provider silently, and never store provider keys in public shared storage.

Do not ship a model or claim GPU/CPU speed until benchmarked on target devices.

## Auth and deployment caveats
Current accounts are an MVP, not production-hardened identity. Before public deployment: TLS, ingress-level shared rate limiting for login/register and chat, trusted reverse-proxy configuration, password reset/account deletion, safe token storage (prefer secure HttpOnly cookie with CSRF protection for web clients), session cleanup, backups, and a privacy policy. Do not expose the MVP publicly before these controls.

## Dante / Mojum
The curriculum and rhythm evaluator are shared. Dante's private memory and simulation state should remain in Noosphere/Mojum; export only opt-in lesson IDs, scores with provenance, and capability descriptors. Human camera feedback and virtual actuator telemetry are different evidence sources.
