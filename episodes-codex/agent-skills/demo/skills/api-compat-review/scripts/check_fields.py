#!/usr/bin/env python3
"""Read-only, narrow required-field comparison for this synthetic lesson.

This is not an OpenAPI validator and does not call an HTTP service.
Exit 0 means the check ran successfully, including when it finds a break.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def required_fields(contract: dict) -> set[str]:
    request = contract["request"]
    if request.get("type") != "object":
        raise ValueError("Only object request contracts are supported")
    properties = request["properties"]
    required = request["required"]
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise ValueError("properties must be an object and required an array")
    if not all(isinstance(name, str) for name in required):
        raise ValueError("required names must be strings")
    if len(required) != len(set(required)) or not set(required) <= properties.keys():
        raise ValueError("required names must be unique declared properties")
    return set(required)


def review(before: dict, after: dict, client_request: dict) -> dict:
    if not isinstance(client_request, dict):
        raise ValueError("The example client request must be a JSON object")
    if (before["method"], before["path"]) != (after["method"], after["path"]):
        raise ValueError("This example compares the same method and path only")
    old_required, new_required = required_fields(before), required_fields(after)
    old_missing = sorted(old_required - client_request.keys())
    if old_missing:
        raise ValueError("The supplied old client request already lacks old required fields: " + ", ".join(old_missing))
    added_required = sorted(new_required - old_required)
    missing_after = sorted(new_required - client_request.keys())
    return {
        "example": True,
        "endpoint": {"method": before["method"], "path": before["path"]},
        "checkedRule": "R2: newly required request fields can break old clients",
        "newRequiredFields": added_required,
        "oldClientValidation": {
            "before": "accepted_by_example_required_field_validator",
            "after": "rejected_by_example_required_field_validator" if missing_after else "accepted_by_example_required_field_validator",
            "missingRequiredFields": missing_after,
        },
        "verdict": "breaking_required_field_change" if added_required else "passes_checked_required_field_rules",
        "scope": "Synthetic JSON object required-field check only; no HTTP call, full OpenAPI analysis, or universal compatibility claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--client-request", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = review(load_json(args.before), load_json(args.after), load_json(args.client_request))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"Input/check error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
