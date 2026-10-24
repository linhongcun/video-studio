#!/usr/bin/env python3
"""Fail if a tracked or staged file looks like it carries a secret.

Scans `git ls-files --cached --others --exclude-standard` (tracked, staged and
untracked-but-not-ignored files), so a key file that .gitignore misses is
caught before `git add`. Fails on: any *.env / .env file not ignored;
sk-... keys; AKIA/AKID access key ids; private key blocks; Bearer tokens;
NAME_KEY/SECRET/TOKEN/PASSWORD = <long literal>; "api-key"/"api_key": "<long literal>".
Long hex strings are NOT failures here: goldens carry sha256 hashes
(audioSha256, scriptSha256, sha). Binary files and files > 2 MB are skipped.

  python3 episodes/_shared/tests/secret_scan.py      # from anywhere in the repo
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAT = [
    ('sk- key', re.compile(r'\bsk-[A-Za-z0-9_\-]{16,}')),
    ('access key id', re.compile(r'\b(AKIA[0-9A-Z]{16}|AKID[0-9A-Za-z]{13,})\b')),
    ('private key', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('bearer token', re.compile(r'Bearer\s+[A-Za-z0-9._\-]{20,}')),
    ('assigned secret', re.compile(r'(?i)\b[A-Z0-9_]*(API_?KEY|SECRET|TOKEN|PASSWORD|PASSWD)\s*[:=]\s*["\']?(?!process\.env|os\.environ|os\.getenv|import\.meta\.env)[A-Za-z0-9_\-./+]{16,}')),
    ('quoted secret', re.compile(r'(?i)["\'](api[-_]?key|secret|token|password|authorization)["\']\s*[:,]\s*["\'][A-Za-z0-9_\-./+]{16,}["\']')),
]
SELF = Path(__file__).resolve()


def main():
    r = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT, capture_output=True)
    if r.returncode:
        print('skip secret_scan, not a git checkout'); return 0
    files = r.stdout.decode().split('\0')
    bad = []
    for f in filter(None, files):
        p = ROOT / f
        if p.name == '.env' or p.name.endswith('.env'):
            bad.append((f, 0, 'env file not ignored')); continue
        if p.resolve() == SELF or not p.is_file() or p.stat().st_size > 2_000_000: continue
        b = p.read_bytes()
        if b'\0' in b[:8192]: continue
        for n, line in enumerate(b.decode('utf-8', 'replace').split('\n'), 1):
            for name, rx in PAT:
                if rx.search(line): bad.append((f, n, name))
    for f, n, name in bad: print(f'secret_scan: {f}:{n}: {name}')   # location only, never the value
    print('secret_scan', 'FAIL' if bad else 'ok', f'({len(files)-1} files)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
