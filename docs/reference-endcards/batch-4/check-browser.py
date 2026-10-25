#!/usr/bin/env python3
"""Check final batch-4 build: --base-url http://127.0.0.1:4321/video-studio/.

Only message-queue, rate-limit and circuit-breaker: three desktop 1x tail plays,
painted subtitle boundaries, and every mobile native fullscreen reference page.
Saved screenshots need actual view_image review before the report can pass.
"""
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent))
from _batch_runtime import browser_engine, configure_batch

QA = configure_batch(OUT, ("message-queue", "rate-limit", "circuit-breaker"))
ENGINE = browser_engine(QA)
ENGINE.__doc__ = __doc__

if __name__ == "__main__":
    raise SystemExit(ENGINE.main())
