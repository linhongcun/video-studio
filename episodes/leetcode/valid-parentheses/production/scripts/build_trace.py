import argparse
import json
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCTION))

from paren_trace import validate_with_trace


MAIN = "{[()]}()"
CASES = {"question": "([)]", "empty": "())", "leftover": "(()"}


def run(s: str) -> dict:
    valid, events = validate_with_trace(s)
    return {"s": s, "chars": list(s), "valid": valid, "events": events}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the LC20 bracket-stack event trace.")
    parser.add_argument("--output", type=Path, default=PRODUCTION / "trace/main-example.json")
    args = parser.parse_args()
    data = {"label": "教学示例", "main": run(MAIN), "cases": {name: run(s) for name, s in CASES.items()}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + chr(10))
    print(f"wrote {args.output.relative_to(PRODUCTION)} ({len(data['main']['events'])} main events)")


if __name__ == "__main__":
    main()
