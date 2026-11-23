# Knowledge graph schema (v0)

Concept: id, title, explanation, keywords, prerequisites[]
Video: id, url, title, verified_at, source, duration_seconds
ConceptVideo: concept_id, video_id, start_seconds, end_seconds, relevance_notes
Exercise: id, concept_ids[], instructions, bpm, target_pattern
Progress: browser-local by default; no account identifiers

The seed API currently uses in-memory concepts. Production migration should store concepts, videos and concept-video relationships in SQLite, expose provenance and moderation status, and only serve verified YouTube links. Do not conflate an AI-generated suggestion with verified instructional content.
