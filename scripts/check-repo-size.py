#!/usr/bin/env python3
"""Repository size & bloat gate for CI and pre-commit checks.

Blocks newly added bloated binaries while allowing a fixed, shrink-only legacy
baseline (`scripts/repo-size-legacy.json`) so existing frozen files are never
modified or broken.

Checks on Git-tracked files (or staged files with --check-staged):
  1. Force-tracked gitignored files (e.g. production/**/*.mp4, remotion/public/audio/voice.wav).
  2. Banned bulky formats: .raw, .yuv, .zip, .ttc, .ttf, .otf.
  3. Embedded-bitmap SVGs (> 512 KB containing `data:image/`).
  4. Non-publication files exceeding MAX_NON_PUB_BYTES (5 MiB), excluding
     `episodes/<series>/<slug>/publication/video.mp4` and fixed regression fixtures.

Usage:
  python3 scripts/check-repo-size.py
  python3 scripts/check-repo-size.py --check-staged
  python3 scripts/check-repo-size.py --write-legacy   # refresh/shrink baseline after cleanup
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file()
)
DEFAULT_LEGACY = ROOT / 'scripts/repo-size-legacy.json'

BANNED_EXTS = {'.raw', '.yuv', '.zip', '.ttc', '.ttf', '.otf'}
MAX_NON_PUB_BYTES = 5 * 1024 * 1024  # 5 MiB
MAX_SVG_BITMAP_BYTES = 512 * 1024    # 512 KiB
PUB_VIDEO_RE = re.compile(r'^episodes/[a-z0-9-]+/[a-z0-9-]+/publication/video\.mp4$')
DATA_IMAGE_RE = re.compile(rb'data:image/[a-z0-9.+-]+;base64,', re.IGNORECASE)


def git_paths(repo: Path, args: list[str]) -> list[str]:
    out = subprocess.check_output(['git', *args], cwd=repo)
    return [p for p in out.decode('utf-8', errors='replace').split('\0') if p]


def git_tracked_sizes(repo: Path, *, staged_only: bool = False) -> dict[str, int]:
    """Return {posix_path: byte_size} for tracked (or staged) blobs without requiring full sparse checkout."""
    if staged_only:
        paths = git_paths(repo, ['diff', '--cached', '--name-only', '--diff-filter=ACM', '-z'])
        sizes: dict[str, int] = {}
        for rel in paths:
            fp = repo / rel
            if fp.is_file() and not fp.is_symlink():
                sizes[rel] = fp.stat().st_size
        return sizes

    # Use git ls-tree HEAD + staged index via `git ls-files --stage` so it works identically
    # under CI sparse-checkout where production media files are not checked out on disk.
    sizes = {}
    out = subprocess.check_output(['git', 'ls-tree', '-r', '-l', '-z', 'HEAD'], cwd=repo)
    for entry in out.decode('utf-8', errors='replace').split('\0'):
        if not entry or '\t' not in entry:
            continue
        meta, rel = entry.split('\t', 1)
        parts = meta.split()
        if len(parts) >= 4 and parts[1] == 'blob' and parts[3] != '-':
            sizes[rel] = int(parts[3])
    # Overlay staged additions/modifications and deletions
    diff_out = subprocess.check_output(['git', 'diff', '--cached', '--name-status', '-z'], cwd=repo)
    tokens = diff_out.decode('utf-8', errors='replace').split('\0')
    i = 0
    while i < len(tokens):
        status = tokens[i]
        i += 1
        if not status:
            continue
        if status.startswith(('R', 'C')):
            if i + 1 < len(tokens):
                old_p, new_p = tokens[i], tokens[i + 1]
                i += 2
                if status.startswith('R'):
                    sizes.pop(old_p, None)
                fp = repo / new_p
                if fp.is_file() and not fp.is_symlink():
                    sizes[new_p] = fp.stat().st_size
        else:
            if i < len(tokens):
                rel = tokens[i]
                i += 1
                if status == 'D':
                    sizes.pop(rel, None)
                else:
                    fp = repo / rel
                    if fp.is_file() and not fp.is_symlink():
                        sizes[rel] = fp.stat().st_size
    return sizes


def is_embedded_bitmap_svg(repo: Path, rel: str, size: int) -> bool:
    if size <= MAX_SVG_BITMAP_BYTES or not rel.lower().endswith('.svg'):
        return False
    fp = repo / rel
    if fp.is_file() and not fp.is_symlink():
        sample = fp.read_bytes()[:256 * 1024]
    else:
        # Sparse checkout fallback: read blob header from Git index/HEAD
        p = subprocess.run(['git', 'cat-file', 'blob', f':{rel}'], cwd=repo, capture_output=True)
        if p.returncode != 0:
            return False
        sample = p.stdout[:256 * 1024]
    return bool(DATA_IMAGE_RE.search(sample))


def collect_findings(repo: Path, *, staged_only: bool = False) -> dict[str, list[str]]:
    sizes = git_tracked_sizes(repo, staged_only=staged_only)
    tracked_set = set(sizes)

    ignored_tracked = [
        p for p in git_paths(repo, ['ls-files', '-i', '-c', '--exclude-standard', '-z'])
        if p in tracked_set
    ]
    banned_format: list[str] = []
    oversized: list[str] = []
    embedded_svg: list[str] = []

    for rel, size in sorted(sizes.items()):
        ext = PurePosixPath(rel).suffix.lower()
        if ext in BANNED_EXTS:
            banned_format.append(rel)
        if is_embedded_bitmap_svg(repo, rel, size):
            embedded_svg.append(rel)
        if size > MAX_NON_PUB_BYTES and not PUB_VIDEO_RE.fullmatch(rel):
            oversized.append(rel)

    return {
        'forceTrackedIgnored': sorted(set(ignored_tracked)),
        'bannedFormat': sorted(set(banned_format)),
        'embeddedBitmapSvg': sorted(set(embedded_svg)),
        'oversizedNonPublication': sorted(set(oversized)),
    }


def load_legacy(path: Path) -> dict[str, set[str]]:
    if not path.is_file():
        return {k: set() for k in ('forceTrackedIgnored', 'bannedFormat', 'embeddedBitmapSvg', 'oversizedNonPublication')}
    data = json.loads(path.read_text(encoding='utf-8'))
    return {
        key: set(data.get(key, []))
        for key in ('forceTrackedIgnored', 'bannedFormat', 'embeddedBitmapSvg', 'oversizedNonPublication')
    }


def write_legacy(repo: Path, path: Path, findings: dict[str, list[str]]) -> None:
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    payload = {
        'schemaVersion': 1,
        'baselineCommit': head,
        'policy': {
            'maxNonPublicationBytes': MAX_NON_PUB_BYTES,
            'maxSvgBitmapBytes': MAX_SVG_BITMAP_BYTES,
            'bannedExtensions': sorted(BANNED_EXTS),
            'note': 'Shrink-only historical exemption baseline. Never expand this list for new episodes.',
        },
        **findings,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--legacy', type=Path, default=None)
    parser.add_argument('--check-staged', action='store_true', help='Only check staged additions/modifications')
    parser.add_argument('--write-legacy', action='store_true', help='Write current tracked findings into legacy baseline')
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    legacy_path = (args.legacy or (repo / 'scripts/repo-size-legacy.json')).resolve()
    findings = collect_findings(repo, staged_only=args.check_staged)

    if args.write_legacy:
        write_legacy(repo, legacy_path, findings)
        counts = ', '.join(f'{k}={len(v)}' for k, v in findings.items())
        print(f'Wrote {legacy_path.relative_to(repo)}: {counts}')
        return 0

    legacy = load_legacy(legacy_path)
    violations: list[str] = []
    labels = {
        'forceTrackedIgnored': 'Force-tracked gitignored file (remove with `git rm --cached`)',
        'bannedFormat': 'Banned binary format (.raw/.yuv/.zip/.ttc/.ttf/.otf)',
        'embeddedBitmapSvg': 'SVG > 512 KB with embedded base64 raster image',
        'oversizedNonPublication': f'Non-publication file > {MAX_NON_PUB_BYTES // (1024 * 1024)} MiB',
    }
    for key, paths in findings.items():
        new_items = [p for p in paths if p not in legacy[key]]
        for p in new_items:
            violations.append(f'  [{key}] {p}  ({labels[key]})')

    if violations:
        print(f'Repository size gate FAILED ({len(violations)} new violation(s)):', file=sys.stderr)
        for line in violations:
            print(line, file=sys.stderr)
        return 1

    counts = ', '.join(f'{k}={len(v)}' for k, v in findings.items())
    mode = 'staged' if args.check_staged else 'repo'
    print(f'Repository size gate passed ({mode}; legacy baseline items: {counts}).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
