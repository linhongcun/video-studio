from __future__ import annotations

from typing import Any


def _copy_intervals(intervals: list[list[int]]) -> list[list[int]]:
    return [interval[:] for interval in intervals]


def merge_with_trace(
    intervals: list[list[int]],
) -> tuple[list[list[int]], list[dict[str, Any]]]:
    ordered = sorted(
        ((index, interval[0], interval[1]) for index, interval in enumerate(intervals)),
        key=lambda item: (item[1], item[0]),
    )
    order = [index for index, _, _ in ordered]

    if not ordered:
        return [], [{
            "kind": "empty",
            "order": [],
            "processedIds": [],
            "completed": [],
            "current": None,
        }]

    completed: list[list[int]] = []
    first_id, first_start, first_end = ordered[0]
    current = [first_start, first_end]
    processed_ids = [first_id]
    events: list[dict[str, Any]] = [{
        "kind": "begin",
        "order": order,
        "processedIds": processed_ids[:],
        "completed": [],
        "current": current[:],
    }]

    for source_id, start, end in ordered[1:]:
        before = current[:]
        incoming = [start, end]
        processed_ids.append(source_id)

        if start <= current[1]:
            if start == current[1]:
                relation = "touching"
            elif end <= current[1]:
                relation = "nested"
            else:
                relation = "overlap"
            current[1] = max(current[1], end)
            events.append({
                "kind": "merge",
                "id": source_id,
                "relation": relation,
                "before": before,
                "incoming": incoming,
                "completed": _copy_intervals(completed),
                "current": current[:],
                "processedIds": processed_ids[:],
            })
        else:
            completed.append(current[:])
            current = incoming[:]
            events.append({
                "kind": "separate",
                "id": source_id,
                "before": before,
                "incoming": incoming,
                "completed": _copy_intervals(completed),
                "current": current[:],
                "processedIds": processed_ids[:],
            })

    result = _copy_intervals(completed + [current])
    events.append({
        "kind": "finish",
        "completed": _copy_intervals(result),
        "current": None,
        "processedIds": processed_ids[:],
    })
    return result, events
