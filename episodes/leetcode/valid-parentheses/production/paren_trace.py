from __future__ import annotations

from typing import Any

PAIRS = {")": "(", "]": "[", "}": "{"}


def validate_with_trace(s: str) -> tuple[bool, list[dict[str, Any]]]:
    stack: list[str] = []
    events: list[dict[str, Any]] = []
    for index, ch in enumerate(s):
        if ch in PAIRS:
            if not stack:
                events.append({"kind": "empty", "index": index, "char": ch, "stack": []})
                return False, events
            top = stack[-1]
            if top != PAIRS[ch]:
                events.append({"kind": "mismatch", "index": index, "char": ch, "top": top, "stack": stack[:]})
                return False, events
            stack.pop()
            events.append({"kind": "pop", "index": index, "char": ch, "top": top, "stack": stack[:]})
        else:
            stack.append(ch)
            events.append({"kind": "push", "index": index, "char": ch, "stack": stack[:]})
    if stack:
        events.append({"kind": "leftover", "index": len(s), "stack": stack[:]})
        return False, events
    events.append({"kind": "finish", "index": len(s), "stack": []})
    return True, events
