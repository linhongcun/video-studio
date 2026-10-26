#!/usr/bin/env python3
"""Verify only the three batch-7 FIRST reference appendices after final build.

Local: --local-only. Published: --version vX.Y.Z --deployment-run ID --commit FULL40.
Exactly 13 ordinary canonical full GETs: distributed-tx-intro/tx-2pc/tx-tcc each
get HTML, MP4, poster and complete VTT, plus changelog. Explicit tag/Release/
successful Pages-run identity is mandatory. Remote media is streamed, not saved.
New full media proofs bind baseline.originalBodySHA256; no old appendix is assumed.
"""
from _qa import ONLINE

ONLINE.__doc__ = __doc__

if __name__ == "__main__":
    raise SystemExit(ONLINE.main())
