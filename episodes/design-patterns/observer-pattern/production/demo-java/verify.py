"""Compile the complete Java demo, run checks, and audit the video excerpt.

Default is read-only for tracked inputs. --write-artifacts explicitly refreshes
java-card.json and verified-results.json after an intentional source change.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
import tempfile

SOURCE_NAME = "ObserverDemo.java"
CHECKER_NAME = "VerifyObserver.java"
MAIN_CLASS = "ObserverDemo"
CHECKER_CLASS = "VerifyObserver"
EXCERPTS = [("// CARD_CONTRACT_BEGIN", "// CARD_CONTRACT_END", 4), ("// CARD_NOTIFY_BEGIN", "// CARD_NOTIFY_SPLIT", 12), ("// CARD_LOOP_BEGIN", "// CARD_LOOP_END", 16), ("// CARD_USAGE_BEGIN", "// CARD_USAGE_END", 8)]
SEPARATE_GROUPS = True
ROLE_MAPPING = {"订单来源与名单": "Order", "共同观察者约定": "OrderObserver", "通知事实": "OrderChange", "订单摘要": "SummaryObserver", "变化记录": "ChangeLogObserver", "订阅与取消的使用": "main"}
CARD_SCOPE = "Four exact source excerpts: shared contract, inside Order.changeStatus, notification loop, and inside main. Method/context comments are real source lines; this is not a standalone full program."
OMITTED = ["Order fields and subscribe/unsubscribe methods", "SummaryObserver and ChangeLogObserver full implementations", "input/no-change/reentrancy guards and try/finally notification lifecycle", "imports and enclosing class"]

HERE = Path(__file__).resolve().parent
EP = HERE.parent
SOURCE = HERE / SOURCE_NAME
CARD = EP / "remotion/src/java-card.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def card_data():
    source_lines = SOURCE.read_text().splitlines()
    lines = []
    mappings = []
    ranges = []
    for index, (start_marker, end_marker, indent) in enumerate(EXCERPTS):
        begin = next(i for i, line in enumerate(source_lines) if line.strip() == start_marker) + 1
        end = next(i for i, line in enumerate(source_lines) if line.strip() == end_marker)
        assert begin < end
        if index and SEPARATE_GROUPS:
            lines.append("")
            mappings.append({"line": None, "removeIndent": 0})
        ranges.append({"from": begin + 1, "to": end, "removeIndent": indent})
        for position in range(begin, end):
            raw = source_lines[position]
            assert not raw or raw.startswith(" " * indent)
            lines.append(raw[indent:] if raw else "")
            mappings.append({"line": position + 1, "removeIndent": indent})
    assert 18 <= len(lines) <= 22, len(lines)
    for line, mapping in zip(lines, mappings):
        if mapping["line"] is not None:
            raw = source_lines[mapping["line"] - 1]
            assert line == (raw[mapping["removeIndent"]:] if raw else "")
        else:
            assert line == ""
    return {"title": "Java关键代码 · 节选", "subtitle": "暂停查看", "language": "Java",
            "lines": lines, "sourceFile": "demo-java/" + SOURCE_NAME,
            "sourceSha256": digest(SOURCE), "excerptRanges": ranges,
            "lineSources": mappings, "lineCount": len(lines),
            "longestLineCharacters": max(map(len, lines)),
            "roleMapping": ROLE_MAPPING, "scope": CARD_SCOPE,
            "omittedSections": OMITTED}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifacts", action="store_true")
    args = parser.parse_args()
    expected = card_data()
    if args.write_artifacts:
        CARD.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n")
    assert json.loads(CARD.read_text()) == expected, "Card is stale: explicitly refresh after source review"
    compiler = ["java", "--module", "jdk.compiler/com.sun.tools.javac.Main"]
    compiler_version = subprocess.check_output(compiler + ["-version"], text=True, stderr=subprocess.STDOUT).strip()
    runtime = subprocess.check_output(["java", "-version"], text=True, stderr=subprocess.STDOUT).strip()
    with tempfile.TemporaryDirectory(prefix="pattern-java-") as build:
        command = compiler + ["-encoding", "UTF-8", "-d", build, str(SOURCE), str(HERE / CHECKER_NAME)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        demo = subprocess.check_output(["java", "-cp", build, MAIN_CLASS], text=True).strip()
        result = json.loads(subprocess.check_output(["java", "-cp", build, CHECKER_CLASS], text=True))
    assert result["passed"] is True
    report = {"status": "passed", "checkedAtBeijing": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              "executedBy": "Codex pattern_java", "compiler": compiler_version,
              "runtime": runtime, "compileCommand": compiler + ["-encoding", "UTF-8", "-d", "<temporary build>", SOURCE_NAME, CHECKER_NAME],
              "runCommands": ["java -cp <temporary build> " + MAIN_CLASS, "java -cp <temporary build> " + CHECKER_CLASS],
              "sources": {SOURCE_NAME: digest(SOURCE), CHECKER_NAME: digest(HERE / CHECKER_NAME)},
              "cardSha256": digest(CARD), "cardLineCount": len(expected["lines"]),
              "allDisplayedNonblankLinesMatchSource": True,
              "demoStdout": demo, "results": result,
              "scope": "Complete Java program compilation and example behavior; card is an explicitly labeled excerpt. No video or learning-effect claim."}
    if args.write_artifacts:
        (HERE / "verified-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
