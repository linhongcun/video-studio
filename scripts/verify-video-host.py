#!/usr/bin/env python3
"""Read-only online verification for externally hosted episode videos.

Verifies every checked video URL against the local frozen publication MP4:
  1. HTTP Range probe (`Range: bytes=0-1023`) returns 206 Partial Content,
     `Accept-Ranges: bytes`, and `Content-Type: video/mp4` (Safari/iOS safe).
  2. Full streamed download SHA-256 matches local `publication/video.mp4`
     byte-for-byte without writing media to disk.

Examples:
  python3 scripts/verify-video-host.py --self-test
  python3 scripts/verify-video-host.py --base-url https://media.example.com --slug two-sum
  python3 scripts/verify-video-host.py --base-url https://media.example.com --all
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import urllib.request


ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file()
)
CHUNK = 256 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_one_url(url: str, expected_sha: str, expected_bytes: int, *, timeout: float = 30.0) -> dict:
    # 1. Range probe for Safari/iOS compatibility
    probe_end = min(1023, max(0, expected_bytes - 1))
    req_range = urllib.request.Request(
        url,
        headers={'Range': f'bytes=0-{probe_end}', 'User-Agent': 'video-studio-verify/1'},
    )
    with urllib.request.urlopen(req_range, timeout=timeout) as resp:
        status = resp.status
        ctype = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        accept_ranges = (resp.headers.get('Accept-Ranges') or '').strip().lower()
        content_range = resp.headers.get('Content-Range') or ''
        probe_data = resp.read()
    if status != 206:
        raise ValueError(f'{url}: expected HTTP 206 for Range probe, got {status}')
    if ctype != 'video/mp4':
        raise ValueError(f'{url}: expected Content-Type video/mp4 (required by Safari/iOS), got {ctype!r}')
    if accept_ranges and accept_ranges != 'bytes':
        raise ValueError(f'{url}: unexpected Accept-Ranges {accept_ranges!r}')
    if len(probe_data) != probe_end + 1:
        raise ValueError(f'{url}: Range probe returned {len(probe_data)} bytes, expected {probe_end + 1}')

    # 2. Full byte-for-byte SHA-256 verification
    req_full = urllib.request.Request(url, headers={'User-Agent': 'video-studio-verify/1'})
    h = hashlib.sha256()
    received = 0
    with urllib.request.urlopen(req_full, timeout=timeout) as resp:
        if resp.status != 200:
            raise ValueError(f'{url}: expected HTTP 200 for full fetch, got {resp.status}')
        while True:
            buf = resp.read(CHUNK)
            if not buf:
                break
            h.update(buf)
            received += len(buf)
    actual_sha = h.hexdigest()
    if received != expected_bytes or actual_sha != expected_sha:
        raise ValueError(
            f'{url}: SHA/size mismatch (got {actual_sha[:12]} / {received}B, '
            f'expected {expected_sha[:12]} / {expected_bytes}B)'
        )
    return {
        'url': url,
        'status': 'ok',
        'contentType': ctype,
        'contentRange': content_range,
        'bytes': received,
        'sha256': actual_sha,
    }


def load_episodes(repo: Path, slugs: set[str] | None = None) -> list[dict]:
    items: list[dict] = []
    for meta_path in sorted((repo / 'episodes').glob('*/*/publication/meta.json')):
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        slug = meta_path.parent.parent.name
        if meta.get('draft'):
            continue
        if slugs and slug not in slugs:
            continue
        video_name = meta.get('video')
        if not video_name:
            continue
        fp = meta_path.parent / video_name
        items.append({
            'slug': slug,
            'filename': video_name,
            'path': fp,
            'bytes': fp.stat().st_size,
            'sha256': sha256_file(fp),
        })
    return items


def build_url(base_url: str, template: str, item: dict) -> str:
    stem = Path(item['filename']).stem
    ext = Path(item['filename']).suffix
    rel = (
        template
        .replace('{slug}', item['slug'])
        .replace('{filename}', item['filename'])
        .replace('{stem}', stem)
        .replace('{ext}', ext)
        .replace('{sha8}', item['sha256'][:8])
        .lstrip('/')
    )
    return f'{base_url.rstrip("/")}/{rel}'


def self_test() -> int:
    payload = b'\x00\x00\x00\x18ftypmp42' + (b'video-studio-range-test-' * 200)
    expected_sha = hashlib.sha256(payload).hexdigest()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            ctype = 'application/octet-stream' if self.path.endswith('bad.mp4') else 'video/mp4'
            rng = self.headers.get('Range')
            if rng and rng.startswith('bytes='):
                a, b = rng[6:].split('-')
                start = int(a)
                end = int(b) if b else len(payload) - 1
                chunk = payload[start:end + 1]
                self.send_response(206)
                self.send_header('Content-Type', ctype)
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Range', f'bytes {start}-{end}/{len(payload)}')
                self.send_header('Content-Length', str(len(chunk)))
                self.end_headers()
                self.wfile.write(chunk)
            else:
                self.send_response(200)
                self.send_header('Content-Type', ctype)
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

    server = HTTPServer(('127.0.0.1', 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        res = verify_one_url(f'http://127.0.0.1:{port}/episodes/demo/video.mp4', expected_sha, len(payload))
        assert res['status'] == 'ok' and res['sha256'] == expected_sha
        try:
            verify_one_url(f'http://127.0.0.1:{port}/episodes/demo/bad.mp4', expected_sha, len(payload))
            raise AssertionError('Expected octet-stream video to fail Safari MIME check')
        except ValueError as err:
            assert 'video/mp4' in str(err)
        print('verify-video-host self-test passed')
    finally:
        server.shutdown()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='Run offline HTTP Range/SHA verification self-test')
    parser.add_argument('--base-url', default='', help='Override external video host base URL')
    parser.add_argument('--path-template', default='', help='Override object path template')
    parser.add_argument('--slug', action='append', default=[], help='Verify specific episode slug(s)')
    parser.add_argument('--all', action='store_true', help='Verify all published episodes')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--repo', type=Path, default=ROOT)
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    repo = args.repo.resolve()
    cfg_path = repo / 'site/src/content/video-host.json'
    cfg = json.loads(cfg_path.read_text(encoding='utf-8')) if cfg_path.is_file() else {}
    base_url = (args.base_url or cfg.get('baseUrl') or '').rstrip('/')
    template = args.path_template or cfg.get('pathTemplate') or 'episodes/{slug}/{filename}'
    if not base_url:
        print('ERROR: provide --base-url or configure site/src/content/video-host.json baseUrl', file=sys.stderr)
        return 2
    if not args.all and not args.slug:
        print('ERROR: specify --slug <slug> or --all', file=sys.stderr)
        return 2

    items = load_episodes(repo, set(args.slug) if args.slug else None)
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {
            pool.submit(verify_one_url, build_url(base_url, template, item), item['sha256'], item['bytes']): item
            for item in items
        }
        for fut in as_completed(futs):
            item = futs[fut]
            try:
                res = fut.result()
                print(f'[OK]   {item["slug"]:34} {res["sha256"][:8]}  {res["url"]}')
            except Exception as exc:
                failures.append(f'{item["slug"]}: {exc}')
                print(f'[FAIL] {item["slug"]}: {exc}', file=sys.stderr)

    if failures:
        print(f'Video host verification FAILED ({len(failures)}/{len(items)}).', file=sys.stderr)
        return 1
    print(f'Video host verification passed ({len(items)}/{len(items)} episodes, Range + video/mp4 + SHA-256).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
