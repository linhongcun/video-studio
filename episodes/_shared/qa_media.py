#!/usr/bin/env python3
"""Compact QA media helper for new episodes and archive reports.

Converts large QA frame PNG captures to JPEG (~74% smaller) and compresses
oversized (>500 KB) QA sampling JSON files to .json.gz so new episodes keep
visual verification evidence without bloating Git.

Examples:
  python3 episodes/_shared/qa_media.py compress-frames EPDIR/qa --quality 4
  python3 episodes/_shared/qa_media.py compress-json EPDIR/qa/samples.json
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys


def compress_png_dir(directory: Path, *, quality: int = 4, remove_png: bool = False, dry_run: bool = False) -> dict:
    directory = directory.resolve()
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('ffmpeg is required to convert QA PNGs to JPEG')

    pngs = sorted(p for p in directory.rglob('*.png') if p.is_file() and not p.is_symlink())
    before = after = converted = 0
    for png in pngs:
        jpg = png.with_suffix('.jpg')
        sz = png.stat().st_size
        before += sz
        if dry_run:
            converted += 1
            continue
        subprocess.run([ffmpeg, '-y', '-v', 'error', '-i', str(png), '-q:v', str(quality), str(jpg)], check=True)
        after += jpg.stat().st_size
        converted += 1
        if remove_png:
            png.unlink()
    return {
        'directory': str(directory),
        'files': converted,
        'pngBytes': before,
        'jpgBytes': after,
        'savedRatio': round(1 - (after / before), 4) if (before and not dry_run) else None,
        'dryRun': dry_run,
    }


def compress_large_json(path: Path, *, remove_source: bool = False, min_bytes: int = 512 * 1024) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    sz = path.stat().st_size
    if sz < min_bytes:
        return {'path': str(path), 'skipped': True, 'reason': f'below threshold ({sz} < {min_bytes})'}
    gz = path.with_name(path.name + '.gz')
    with path.open('rb') as src, gzip.open(gz, 'wb', compresslevel=9) as dst:
        shutil.copyfileobj(src, dst)
    gz_sz = gz.stat().st_size
    if remove_source:
        path.unlink()
    return {
        'path': str(path),
        'gzipPath': str(gz),
        'sourceBytes': sz,
        'gzipBytes': gz_sz,
        'ratio': round(gz_sz / sz, 4) if sz else 1.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)

    p_img = sub.add_parser('compress-frames', help='Convert QA PNG screenshots to JPEG')
    p_img.add_argument('directory', type=Path)
    p_img.add_argument('--quality', type=int, default=4, help='ffmpeg -q:v scale (2=highest, 4=recommended)')
    p_img.add_argument('--remove-png', action='store_true', help='Remove original PNG after JPEG succeeds')
    p_img.add_argument('--dry-run', action='store_true')

    p_js = sub.add_parser('compress-json', help='Gzip oversized QA JSON files (>512 KB)')
    p_js.add_argument('file', type=Path)
    p_js.add_argument('--min-bytes', type=int, default=512 * 1024)
    p_js.add_argument('--remove-source', action='store_true')

    args = parser.parse_args(argv)
    if args.command == 'compress-frames':
        res = compress_png_dir(args.directory, quality=args.quality, remove_png=args.remove_png, dry_run=args.dry_run)
    else:
        res = compress_large_json(args.file, remove_source=args.remove_source, min_bytes=args.min_bytes)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
