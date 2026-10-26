#!/usr/bin/env python3
"""Verify only batch8's three FIRST appendices after final build.

Local: --local-only. Published: --version vX.Y.Z --deployment-run ID --commit FULL40.
Exactly13 canonical full site GETs: HTML, MP4, poster, VTT for each selected
film, plus changelog. Public GitHub REST identity reads avoid temporary CLI
credentials; all tag/Release/Pages identity assertions remain unchanged.
"""
import hashlib
import json
import ssl
import urllib.request
from datetime import datetime, timezone
from _qa import ONLINE

ONLINE.__doc__ = __doc__
_ORIGINAL_COMMAND = ONLINE.command
_PUBLIC_READS = []


def command(arguments):
    if list(arguments[:2]) != ["gh", "api"]:
        return _ORIGINAL_COMMAND(arguments)
    assert len(arguments) == 3 and arguments[2].startswith("repos/linhongcun/video-studio/")
    url = "https://api.github.com/" + arguments[2]
    record = {"url": url, "method": "GET", "authentication": "no explicit credentials",
              "checkedAtUTC": datetime.now(timezone.utc).isoformat()}
    _PUBLIC_READS.append(record)
    request = urllib.request.Request(url, headers={"User-Agent": "video-studio-reference-check/1.0",
                                                   "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=45, context=ssl.create_default_context()) as response:
        assert response.status == 200 and response.geturl() == url
        body = response.read()
        record.update(httpStatus=response.status, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                      fullResponseRead=True)
        return body


ONLINE.command = command


def main():
    result = ONLINE.main()
    # Keep the preserved validator's exact identity assertions and full-GET
    # report, including any recorded failed attempts, and name the real transport.
    if ONLINE.REPORT.exists():
        report = json.loads(ONLINE.REPORT.read_text())
        if _PUBLIC_READS and report.get("networkChecksExecuted"):
            report.update(githubIdentityTransport="Public GitHub REST over HTTPS; no explicit credentials",
                          publicGithubIdentityReads=_PUBLIC_READS)
            ONLINE.REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
