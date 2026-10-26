#!/usr/bin/env python3
"""Verify this 17-video title/author migration, after the final build is ready.

Local only (no HTTP/GitHub): --local-only
Published identity: --version vX.Y.Z --deployment-run RUN_ID --commit FULL40_SHA

Exactly 69 ordinary canonical full GETs: HTML, MP4, poster and full native VTT
for each startup declaration, plus changelog. Complete remote media is streamed
into SHA-256 and never saved. The current body and title/credit bibliography are
bound to each actual production baseline, including the nested 4570-frame Bloom
project. Quotes remain in research/articles, while cards render only title/credit.
"""
from _qa import ONLINE

ONLINE.__doc__ = __doc__

if __name__ == "__main__":
    raise SystemExit(ONLINE.main())
