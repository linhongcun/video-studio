"""Compile and run D03 and audit its exact Java excerpt.

Default is read-only for source, card and saved results. --write-artifacts
explicitly refreshes the card/results, only after compilation and checks pass.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
CARD = HERE.parent / "remotion/src/java-card.json"
SOURCE = HERE / "AdapterDemo.java"
CHECKER = HERE / "VerifyAdapter.java"
EXCERPTS = [("// CARD_CORE_BEGIN", "// CARD_CORE_END", 4),
            ("// CARD_USE_BEGIN", "// CARD_USE_END", 8)]
ROLES = {"业务使用者": "ShipmentReminder", "业务通知约定": "Notifier",
         "转换者": "NotificationAdapter", "已有SDK": "VendorSdk",
         "教学替身": "FakeVendorSdk"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(path.read_bytes())


def make_card():
    source_lines = SOURCE.read_text().splitlines()
    lines, mappings, ranges = [], [], []
    for start_marker, end_marker, indent in EXCERPTS:
        assert sum(line.strip() == start_marker for line in source_lines) == 1
        assert sum(line.strip() == end_marker for line in source_lines) == 1
        begin = next(i for i, line in enumerate(source_lines) if line.strip() == start_marker) + 1
        end = next(i for i, line in enumerate(source_lines) if line.strip() == end_marker)
        assert begin < end
        ranges.append({"from": begin + 1, "to": end, "removeIndent": indent})
        for position in range(begin, end):
            raw = source_lines[position]
            assert raw.startswith(" " * indent)
            shown = raw[indent:]
            lines.append(shown)
            mappings.append({"line": position + 1, "removeIndent": indent})
            assert shown == source_lines[position][indent:]
    assert 18 <= len(lines) <= 22, len(lines)
    return {"title": "Java关键代码 · 节选", "subtitle": "暂停查看", "language": "Java",
            "lines": lines, "sourceFile": "demo-java/AdapterDemo.java",
            "sourceSha256": digest(SOURCE), "excerptRanges": ranges,
            "lineSources": mappings, "lineCount": len(lines),
            "longestLineCharacters": max(map(len, lines)), "roleMapping": ROLES,
            "notice": "教学模拟，不会外发",
            "scope": "Two exact excerpts: the business target and adapter, then main wiring. Not a complete standalone program.",
            "omittedSections": ["enclosing AdapterDemo class and imports",
                                "Submission/Status, SDK DTOs/contracts and exception classes",
                                "input and invalid-receipt validation helper definitions",
                                "ShipmentReminder and FakeVendorSdk class definitions",
                                "main output after the call"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifacts", action="store_true")
    args = parser.parse_args()
    expected = make_card()
    card_text = json.dumps(expected, ensure_ascii=False, indent=2) + "\n"
    if not args.write_artifacts:
        assert CARD.read_text() == card_text, "Card stale; review source, then explicitly use --write-artifacts"
    input_paths = [SOURCE, CHECKER, Path(__file__), HERE / "source-review.json"]
    input_hashes = {p.name: digest(p) for p in input_paths}
    compiler = ["java", "--module", "jdk.compiler/com.sun.tools.javac.Main"]
    compiler_version = subprocess.check_output(compiler + ["-version"], text=True,
                                               stderr=subprocess.STDOUT).strip()
    runtime = subprocess.check_output(["java", "-version"], text=True,
                                      stderr=subprocess.STDOUT).strip()
    with tempfile.TemporaryDirectory(prefix="adapter-java-") as build:
        compile_command = compiler + ["-encoding", "UTF-8", "-d", build, str(SOURCE), str(CHECKER)]
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
        demo = subprocess.check_output(["java", "-cp", build, "AdapterDemo"], text=True).strip()
        checked = subprocess.run(["java", "-cp", build, "VerifyAdapter"],
                                 check=True, capture_output=True, text=True)
    result = json.loads(checked.stdout)
    cases = checked.stderr.strip().splitlines()
    assert result["passed"] is True and result["behaviorCases"] == 12 and len(cases) == 12
    assert demo == "教学模拟，不会外发\n订单17发货提醒：ACCEPTED/Q17\n已受理，等待送达回执；并非已送达"
    assert input_hashes == {p.name: digest(p) for p in input_paths}, "Inputs changed during verification"
    report = {"status": "passed", "executedBy": "Codex pattern_java",
              "checkedAtBeijing": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              "compiler": compiler_version, "runtime": runtime,
              "compileCommand": compiler + ["-encoding", "UTF-8", "-d", "<temporary build>",
                                               "AdapterDemo.java", "VerifyAdapter.java"],
              "runCommands": ["java -cp <temporary build> AdapterDemo",
                              "java -cp <temporary build> VerifyAdapter"],
              "sources": input_hashes, "cardSha256": sha(card_text.encode()),
              "cardLineCount": len(expected["lines"]), "longestCardLineCharacters": max(map(len, expected["lines"])),
              "allDisplayedLinesMatchSource": True, "demoStdout": demo,
              "results": result, "behaviorMatrix": cases,
              "scope": "Complete local Java program and contract behavior, plus exact source excerpt. No real vendor/network delivery, video-quality or learning-effect claim."}
    if args.write_artifacts:
        CARD.write_text(card_text)
        (HERE / "verified-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
