"""Deterministic timing assessment from measured onset timestamps.

The caller must provide externally observed onsets in seconds. This module
does not claim to validate pitch, technique, muting, or camera posture.
"""
from math import isfinite

def evaluate_eighth_notes(onsets, bpm, bars, beats_per_bar=4):
    if not (20 <= bpm <= 300 and 1 <= bars <= 64 and 1 <= beats_per_bar <= 12):
        raise ValueError("Invalid exercise meter or tempo")
    expected = bars * beats_per_bar * 2
    if len(onsets) != expected:
        raise ValueError(f"Expected {expected} onsets, got {len(onsets)}")
    if any(not isfinite(x) or x < 0 for x in onsets):
        raise ValueError("Onsets must be finite nonnegative seconds")
    if any(b <= a for a, b in zip(onsets, onsets[1:])):
        raise ValueError("Onsets must be strictly increasing")
    period = 30.0 / bpm
    # Relative intervals: do not penalize the initial latency of the recording.
    errors = [abs((onsets[i] - onsets[0]) - i * period) * 1000 for i in range(expected)]
    return {
        "expected_onsets": expected,
        "observed_onsets": len(onsets),
        "mean_absolute_timing_error_ms": round(sum(errors) / len(errors), 2),
        "max_timing_error_ms": round(max(errors), 2),
        "evaluation_scope": "timing_only",
        "evidence": "caller_supplied_onsets",
    }
