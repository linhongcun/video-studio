#!/usr/bin/env python3
"""Check only batch 3: --local-only, or --version vX.Y.Z --deployment-run ID --commit FULL40.

Online mode performs 13 ordinary canonical full GETs (three episodes × HTML,
MP4, poster and complete VTT, plus changelog), then binds tag/Release/Pages to
the explicit commit. Remote media is streamed into SHA-256 and never saved.
"""
from _qa import ONLINE

ONLINE.__doc__ = __doc__

if __name__ == "__main__":
    raise SystemExit(ONLINE.main())
