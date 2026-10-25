#!/usr/bin/env python3
"""Run the deterministic loading/execution illustration, without an LLM call.

Records real file bytes and subprocess results. The context payloads illustrate
what this host would send; they are not real model usage or token measurements.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def encoded(value: str) -> bytes:
    return value.encode("utf-8")


def identity(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "utf8Bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    frontmatter = re.fullmatch(r"---\n(.*?)\n---\n(.*)", text, flags=re.S)
    if not frontmatter:
        raise ValueError(f"Missing SKILL.md frontmatter: {path}")
    fields = {}
    for line in frontmatter[1].splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError("This tiny demo only parses simple single-line YAML fields")
        fields[key] = value.strip()
    name, description = fields["name"], fields["description"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("Invalid skill name")
    if not description or len(description) > 1024:
        raise ValueError("Invalid skill description")
    return {"name": name, "description": description}


def write_json(path: Path, value: dict | list) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    selected = ROOT / "skills/api-compat-review/SKILL.md"
    unrelated = ROOT / "skills/release-notes/SKILL.md"
    reference = ROOT / "skills/api-compat-review/references/request-fields.md"
    script = ROOT / "skills/api-compat-review/scripts/check_fields.py"
    skill_files = [selected, unrelated]

    # A real host can read files while indexing. Only the extracted metadata is
    # included in this demo's discovery payload; file I/O is not model context.
    catalog = [metadata(path) for path in skill_files]
    write_json(out / "catalog.json", catalog)
    discovery_payload = (out / "catalog.json").read_text(encoding="utf-8")
    activated_payload = selected.read_text(encoding="utf-8")
    reference_payload = reference.read_text(encoding="utf-8")
    events = [
        {"phase": "discover", "hostReadFiles": [identity(path) for path in skill_files], "contextPayload": "outputs/catalog.json", "visibleContent": "name and description only"},
        {"phase": "activate", "choice": "explicit host selection in this deterministic demonstration; not measured model routing", "skill": "api-compat-review", "readIntoContext": identity(selected)},
        {"phase": "read-reference", "readIntoContext": identity(reference)},
    ]
    commands = {}
    for branch, fixture, result_name in [
        ("optional-control", "after-optional.json", "review-optional.json"),
        ("required-main", "after-required.json", "review.json"),
    ]:
        command = [sys.executable, script.relative_to(ROOT).as_posix(), "--before", "fixtures/before.json", "--after", "fixtures/" + fixture, "--client-request", "fixtures/old-client-request.json"]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
        result = json.loads(completed.stdout)
        (out / result_name).write_text(completed.stdout, encoding="utf-8")
        commands[branch] = result
        events.append({"phase": "tool-execution", "branch": branch, "argv": command, "exitCode": completed.returncode, "stderr": completed.stderr, "scriptIdentity": identity(script), "scriptSourceReadIntoContext": False, "businessServiceCalled": False, "result": identity(out / result_name)})
    assert commands["optional-control"]["newRequiredFields"] == []
    assert commands["optional-control"]["oldClientValidation"]["after"].startswith("accepted_")
    assert commands["required-main"]["newRequiredFields"] == ["channel"]
    assert commands["required-main"]["oldClientValidation"]["missingRequiredFields"] == ["channel"]

    tool_result = (out / "review.json").read_text(encoding="utf-8")
    stages = [
        {"stage": "discovery", "content": "two candidates' name/description", "addedUtf8Bytes": len(encoded(discovery_payload))},
        {"stage": "activation", "content": "selected SKILL.md", "addedUtf8Bytes": len(encoded(activated_payload))},
        {"stage": "reference", "content": "selected compatibility rule", "addedUtf8Bytes": len(encoded(reference_payload))},
        {"stage": "tool-result", "content": "required-field check result; not script source", "addedUtf8Bytes": len(encoded(tool_result))},
    ]
    cumulative = 0
    for stage in stages:
        cumulative += stage["addedUtf8Bytes"]
        stage["cumulativeAddedUtf8Bytes"] = cumulative
    always_on_material = "\n\n".join(path.read_text(encoding="utf-8") for path in [selected, reference, unrelated])
    (out / "always-on-methods.txt").write_text(always_on_material, encoding="utf-8")
    trace = {
        "example": True,
        "executionMode": "deterministic local loader and Python subprocesses; no LLM request",
        "task": "审查创建订单接口把新增 channel 设为必填后，既有客户端请求是否还能通过必填字段校验。",
        "meaning": "Actual file I/O, byte sizes and check results. Context stages are illustrative host payloads, not measured model inputs or automatic activation.",
        "events": events,
        "contextPayloadStages": stages,
        "unselectedBodyNotAddedToContext": unrelated.relative_to(ROOT).as_posix(),
        "scriptSourceNotAddedToContext": script.relative_to(ROOT).as_posix(),
        "alwaysOnComparison": {
            "profile": "one deliberately always-on method bundle: both skills and the compatibility reference",
            "file": identity(out / "always-on-methods.txt"),
            "initialMethodUtf8Bytes": len(encoded(always_on_material)),
            "afterSameMainToolResultUtf8Bytes": len(encoded(always_on_material)) + len(encoded(tool_result)),
            "progressiveCumulativeAddedUtf8Bytes": cumulative,
            "progressiveMinusAlwaysOnAfterSameResultUtf8Bytes": cumulative - len(encoded(always_on_material)) - len(encoded(tool_result)),
            "notClaimed": "not a token count, price comparison, performance gain, or proof that all prompts are always-on; progressive loading need not minimize total bytes",
        },
        "retention": "No claim that loaded instructions disappear after a task. Actual context retention and compaction depend on the host.",
    }
    write_json(out / "trace.json", trace)
    print(json.dumps({"optional": commands["optional-control"]["verdict"], "required": commands["required-main"]["verdict"], "discoveryPayloadUtf8Bytes": stages[0]["addedUtf8Bytes"], "alwaysOnMethodBundleUtf8Bytes": len(encoded(always_on_material)), "llmRequests": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
