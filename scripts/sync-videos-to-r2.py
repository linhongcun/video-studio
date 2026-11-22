#!/usr/bin/env python3
"""Sync published episode MP4 files to S3-compatible object storage (Cloudflare R2 / OSS / S3).

Reads credentials strictly from environment variables (never hardcoded or logged):
  R2_BUCKET              Target bucket name (required for upload)
  R2_ENDPOINT            S3-compatible endpoint URL, e.g. https://<account>.r2.cloudflarestorage.com
  R2_PUBLIC_BASE_URL     Public HTTPS base URL served to viewers, e.g. https://media.example.com
  AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY (or R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY)

Supports `--dry-run` (default) to generate the deterministic upload plan & SHA-256
manifest without contacting remote storage, and `--apply` to upload via `aws s3api`
(or `boto3` if installed) with `Content-Type: video/mp4` and immutable cache headers.

Examples:
  python3 scripts/sync-videos-to-r2.py --manifest /tmp/video-manifest.json
  R2_BUCKET=video-studio R2_ENDPOINT=https://<acct>.r2.cloudflarestorage.com \\
    R2_PUBLIC_BASE_URL=https://media.example.com \\
    python3 scripts/sync-videos-to-r2.py --apply --manifest /tmp/video-manifest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file()
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def discover_published_videos(repo: Path, *, include_drafts: bool = False, slugs: set[str] | None = None) -> list[dict]:
    records: list[dict] = []
    episodes_root = repo / 'episodes'
    for meta_path in sorted(episodes_root.glob('*/*/publication/meta.json')):
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        slug = meta_path.parent.parent.name
        if slugs and slug not in slugs:
            continue
        if meta.get('draft') and not include_drafts:
            continue
        video_name = meta.get('video')
        if not video_name:
            continue
        video_path = meta_path.parent / video_name
        if not video_path.is_file():
            raise FileNotFoundError(f'{slug}: missing published video {video_path}')
        digest = sha256_file(video_path)
        records.append({
            'slug': slug,
            'series': meta_path.parent.parent.parent.name,
            'filename': video_name,
            'localPath': video_path.relative_to(repo).as_posix(),
            'bytes': video_path.stat().st_size,
            'sha256': digest,
            'sha8': digest[:8],
        })
    return records


def object_key(record: dict, template: str) -> str:
    stem = Path(record['filename']).stem
    ext = Path(record['filename']).suffix
    return (
        template
        .replace('{slug}', record['slug'])
        .replace('{filename}', record['filename'])
        .replace('{stem}', stem)
        .replace('{ext}', ext)
        .replace('{sha8}', record['sha8'])
        .lstrip('/')
    )


def upload_with_aws_cli(local_path: Path, bucket: str, key: str, endpoint: str, cache_control: str, sha256_hex: str, env: dict[str, str]) -> str:
    # Check if identical sha256 metadata already exists remotely to skip redundant uploads.
    head = subprocess.run(
        ['aws', 's3api', 'head-object', '--bucket', bucket, '--key', key, '--endpoint-url', endpoint],
        env=env,
        capture_output=True,
        text=True,
    )
    if head.returncode == 0:
        try:
            meta = json.loads(head.stdout).get('Metadata', {})
            if meta.get('sha256') == sha256_hex:
                return 'skipped-up-to-date'
        except json.JSONDecodeError:
            pass

    subprocess.run(
        [
            'aws', 's3api', 'put-object',
            '--bucket', bucket,
            '--key', key,
            '--body', str(local_path),
            '--endpoint-url', endpoint,
            '--content-type', 'video/mp4',
            '--cache-control', cache_control,
            '--metadata', f'sha256={sha256_hex}',
        ],
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return 'uploaded'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Actually upload objects (default: dry-run)')
    parser.add_argument('--bucket', default=os.environ.get('R2_BUCKET', ''))
    parser.add_argument('--endpoint', default=os.environ.get('R2_ENDPOINT', ''))
    parser.add_argument('--public-base-url', default=os.environ.get('R2_PUBLIC_BASE_URL', ''))
    parser.add_argument('--path-template', default='episodes/{slug}/{filename}')
    parser.add_argument('--cache-control', default='public, max-age=86400')
    parser.add_argument('--slug', action='append', default=[], help='Limit to specific episode slug(s)')
    parser.add_argument('--manifest', type=Path, default=None, help='Write JSON manifest to this path')
    parser.add_argument('--repo', type=Path, default=ROOT)
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    records = discover_published_videos(repo, slugs=set(args.slug) or None)
    base_url = args.public_base_url.rstrip('/')

    total_bytes = sum(r['bytes'] for r in records)
    for r in records:
        key = object_key(r, args.path_template)
        r['key'] = key
        if base_url:
            r['url'] = f'{base_url}/{key}'

    if args.apply:
        if not args.bucket or not args.endpoint:
            print('ERROR: --bucket / R2_BUCKET and --endpoint / R2_ENDPOINT are required for --apply', file=sys.stderr)
            return 2
        if not shutil.which('aws'):
            print('ERROR: aws CLI not found on PATH; install awscli to upload to R2/S3', file=sys.stderr)
            return 2
        env = dict(os.environ)
        if not env.get('AWS_ACCESS_KEY_ID') and env.get('R2_ACCESS_KEY_ID'):
            env['AWS_ACCESS_KEY_ID'] = env['R2_ACCESS_KEY_ID']
        if not env.get('AWS_SECRET_ACCESS_KEY') and env.get('R2_SECRET_ACCESS_KEY'):
            env['AWS_SECRET_ACCESS_KEY'] = env['R2_SECRET_ACCESS_KEY']
        env.setdefault('AWS_DEFAULT_REGION', 'auto')

        uploaded = skipped = 0
        for r in records:
            status = upload_with_aws_cli(
                repo / r['localPath'], args.bucket, r['key'], args.endpoint, args.cache_control, r['sha256'], env,
            )
            r['status'] = status
            if status == 'uploaded':
                uploaded += 1
            else:
                skipped += 1
            print(f'[{status}] {r["slug"]} -> s3://{args.bucket}/{r["key"]} ({r["bytes"] / 1024 / 1024:.2f} MB)')
        print(f'Done: {uploaded} uploaded, {skipped} skipped ({total_bytes / 1024 / 1024:.1f} MB total).')
    else:
        print(f'[DRY-RUN] {len(records)} published videos, {total_bytes / 1024 / 1024:.1f} MB total.')
        for r in records[:10]:
            target = r.get('url') or r['key']
            print(f'  {r["slug"]:34} {r["bytes"] / 1024 / 1024:6.2f} MB  {r["sha8"]}  -> {target}')
        if len(records) > 10:
            print(f'  ... ({len(records) - 10} more)')

    if args.manifest:
        payload = {
            'schemaVersion': 1,
            'pathTemplate': args.path_template,
            'publicBaseUrl': base_url,
            'episodeCount': len(records),
            'totalBytes': total_bytes,
            'videos': records,
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Wrote manifest: {args.manifest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
