import argparse
import json
import sys
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCTION))

from merge_trace import merge_with_trace


EXAMPLE = [[8, 10], [1, 4], [2, 3], [3, 5], [5, 6], [12, 14]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the LC56 interval-scan event trace.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PRODUCTION / "trace/linear-example.json",
    )
    args = parser.parse_args()

    result, events = merge_with_trace(EXAMPLE)
    data = {
        "label": "教学示例",
        "input": EXAMPLE,
        "result": result,
        "events": events,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + chr(10))
    print(f"wrote {args.output.relative_to(PRODUCTION)} ({len(events)} events)")


if __name__ == "__main__":
    main()
