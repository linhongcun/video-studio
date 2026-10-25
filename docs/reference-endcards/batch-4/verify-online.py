#!/usr/bin/env python3
"""Check only batch 4: --local-only, or --version vX.Y.Z --deployment-run ID --commit FULL40.

Exactly 13 ordinary canonical full GETs: message-queue, rate-limit and
circuit-breaker each get HTML/MP4/poster/complete VTT, plus changelog. Explicit
tag/Release/Pages identity is required; remote media is streamed, never saved.
"""
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent))
from _batch_runtime import configure_batch

QA = configure_batch(OUT, ("message-queue", "rate-limit", "circuit-breaker"))
QA.ONLINE.__doc__ = __doc__

if __name__ == "__main__":
    raise SystemExit(QA.ONLINE.main())
