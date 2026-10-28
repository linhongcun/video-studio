#!/usr/bin/env python3
"""Package reviewed LeetCode MP4s and immutable existing covers; no render/wait.

Run after all eleven final MP4s have been installed and the final-media-summary
exists. The only writes are beneath work/leetcode-video-style. No source media,
production metadata, frozen input or cover template is modified.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
from typing import Mapping
import zipfile

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/leetcode-video-style'
BASELINE = 'd04a30c12b1ce0fb5743f20ce61f9db8908311ad'
DATE = '20261028'
MAX_BYTES = 95 * 1024 * 1024  # Every committed Git file must be strictly below this.
GROUPS = {'A': (1, 3, 11, 42, 46, 70), 'B': (200, 206, 547, 704, 739)}
SIZES = ('16x9', '4x3', '3x4')
Source = Path | bytes


def sha256(value: Source) -> str:
    h = hashlib.sha256()
    if isinstance(value, bytes):
        h.update(value)
    else:
        with value.open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                h.update(block)
    return h.hexdigest()


def record(value: Source) -> dict:
    return {'bytes': len(value) if isinstance(value, bytes) else value.stat().st_size,
            'sha256': sha256(value)}


def safe_name(name: str) -> str:
    path = PurePosixPath(name)
    if (not name or '\\' in name or '\x00' in name or path.is_absolute()
            or any(part in ('', '.', '..') for part in name.split('/'))
            or ':' in path.parts[0]):
        raise ValueError(f'Unsafe ZIP path: {name!r}')
    return name


def work_path(value: str | Path) -> Path:
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(WORK):
        raise ValueError(f'Output must stay beneath {WORK}: {path}')
    return path


def validate_zip(path: Path, expected: Mapping[str, dict]) -> dict:
    """Read every uncompressed member, checking safe names, CRC, size and SHA."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f'Duplicate ZIP paths: {path}')
        for name in names:
            safe_name(name)
        if set(names) != set(expected):
            raise ValueError(f'ZIP entry set mismatch: {path}')
        bad = archive.testzip()
        if bad is not None:
            raise ValueError(f'ZIP CRC failed: {path}: {bad}')
        checked = {}
        for name in names:
            h = hashlib.sha256()
            count = 0
            with archive.open(name) as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b''):
                    h.update(block)
                    count += len(block)
            actual = {'bytes': count, 'sha256': h.hexdigest()}
            if actual != expected[name]:
                raise ValueError(f'ZIP payload identity mismatch: {path}: {name}')
            checked[name] = actual
    return {'status': 'passed', 'crc': True, 'safeRelativePaths': True,
            'allEntryBytesAndSHA256MatchSources': True, 'entries': checked}


def build_zip(path: Path, entries: Mapping[str, Source]) -> dict:
    expected = {safe_name(name): record(value) for name, value in entries.items()}
    # MP4/JPG payloads are already compressed; a low deflate level avoids costly
    # recompression while measuring the actual resulting ZIP against the limit.
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for name, value in entries.items():
            if isinstance(value, bytes):
                archive.writestr(name, value)
            else:
                archive.write(value, arcname=name)
    validation = validate_zip(path, expected)
    return {'file': path.name, **record(path), 'totalEntries': len(entries),
            'validation': validation}


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)


def read_summary(path: Path, catalog: list[dict]) -> dict[str, dict]:
    if not path.is_file():
        raise ValueError(f'All final media must be installed first; missing {path}')
    rows = json.loads(path.read_text())
    if not isinstance(rows, list):
        raise ValueError('final-media-summary must be a list of actual installed records')
    by_slug = {row['slug']: row for row in rows}
    expected = {entry['slug'] for entry in catalog}
    if len(by_slug) != len(rows) or set(by_slug) != expected:
        raise ValueError('final-media-summary must contain each of the eleven slugs exactly once')
    if len({row.get('sha256') for row in rows}) != len(rows):
        raise ValueError('Distinct lessons must have distinct final movie identities')
    for slug, row in by_slug.items():
        digest = row.get('sha256', '')
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError(f'Missing complete final SHA-256: {slug}')
        if not isinstance(row.get('bytes'), int) or row['bytes'] <= 0:
            raise ValueError(f'Missing actual final byte count: {slug}')
        if row.get('fullBaselineAACPacketsAndTimingEqual') is not True:
            raise ValueError(f'Complete original audio identity not confirmed: {slug}')
        if row.get('bodyFramesAndPTSVerifiedByAppendixEngine') is not True:
            raise ValueError(f'Complete body/code-page frame identity not confirmed: {slug}')
    return by_slug


def package(summary_path: Path, delivery: Path, output: Path) -> dict:
    catalog = json.loads(git_bytes('episodes-codex/_shared/leetcode-covers/catalog.json'))['episodes']
    numbers = [entry['number'] for entry in catalog]
    if len(numbers) != 11 or set(numbers) != set(GROUPS['A'] + GROUPS['B']):
        raise ValueError('Unexpected baseline LeetCode episode set')
    rows = read_summary(summary_path, catalog)
    if not delivery.is_dir():
        raise ValueError(f'Missing final delivery directory: {delivery}')
    output.mkdir(parents=True, exist_ok=True)
    candidates = defaultdict(list)
    for movie in sorted(delivery.glob('*.mp4')):
        candidates[sha256(movie)].append(movie)
    sources: dict[str, Source] = {}
    movie_states = {}
    episode_files = {}
    restored_covers = []
    for episode in catalog:
        slug, number = episode['slug'], episode['number']
        row = rows[slug]
        matched = candidates.get(row['sha256'], [])
        if not matched:
            raise ValueError(f'No delivery MP4 matches final SHA for LC{number}: {slug}')
        name = safe_name(f"LC{number}-{''.join(episode['title'])}.mp4")
        canonical = delivery / name
        movie = canonical if canonical in matched else matched[0]
        if movie.stat().st_size != row['bytes']:
            raise ValueError(f'Final movie byte count mismatch: {movie}')
        sources[name] = movie
        movie_states[movie] = {**record(movie), 'mtimeNs': movie.stat().st_mtime_ns}
        names = [name]
        style_bytes = git_bytes(f'episodes/{slug}/cover-style.json')
        style = json.loads(style_bytes)
        if style['problemNumber'] != number:
            raise ValueError(f'Baseline cover identity differs: {slug}')
        for size in SIZES:
            git_path = f'episodes/{slug}/cover-{size}.jpg'
            data = git_bytes(git_path)
            expected = style['covers'][size]['jpgSha256']
            if sha256(data) != expected:
                raise ValueError(f'Baseline cover manifest mismatch: {git_path}')
            cover_name = safe_name(f'covers/{slug}/cover-{size}.jpg')
            cover = delivery / cover_name
            # Cover files are delivery-only immutable copies, never production inputs.
            if cover.exists() and cover.read_bytes() != data:
                raise ValueError(f'Existing delivery cover differs from baseline: {cover}')
            cover.parent.mkdir(parents=True, exist_ok=True)
            if not cover.exists():
                cover.write_bytes(data)
            sources[cover_name] = cover
            names.append(cover_name)
            restored_covers.append({'slug': slug, 'problemNumber': number, 'size': size,
                                    'gitPath': git_path, **record(data),
                                    'coverStyleSHA256': sha256(style_bytes)})
        episode_files[number] = names
    explanation = '''LeetCode 系列视频与封面交付说明

本轮11期：LC1、3、11、42、46、70、200、206、547、704、739。
视频正文沿用现有系列封面的深蓝、暖金、青色和题号标识。
原完整音轨、旁白时间点、推导动作与模型、完整 Python 代码页及参考资料附录保留。
33张JPG为Git基线 d04a30c12b1ce0fb5743f20ce61f9db8908311ad 的原封面，未重新生成。
本轮仅更新GitHub站点；没有向外部视频平台重发。

默认A包含LC1/3/11/42/46/70，B包含LC200/206/547/704/739。
若默认包达到95MiB，则该组按题拆包；实际文件名、题号和完整SHA见package-manifest.json。
每题含一条1080p MP4与16:9、4:3、3:4三张封面。ZIP不代表新的观看认可或真机/全片听辨。
'''.encode('utf-8')
    readme = delivery / '说明.txt'
    if readme.exists() and readme.read_bytes() != explanation:
        raise ValueError(f'Existing delivery explanation differs: {readme}')
    if not readme.exists():
        readme.write_bytes(explanation)
    sources['说明.txt'] = readme
    all_file_records = {name: record(value) for name, value in sources.items()}
    packages = []
    plan = []
    for group, selected in GROUPS.items():
        def entries_for(chosen):
            names = [name for number in chosen for name in episode_files[number]] + ['说明.txt']
            return {name: sources[name] for name in names}
        grouped = build_zip(output / f'leetcode-video-style-{DATE}-{group}.zip', entries_for(selected))
        if grouped['bytes'] < MAX_BYTES:
            grouped.update({'group': group, 'problemNumbers': list(selected), 'partitionMode': 'group'})
            packages.append(grouped)
            plan.append({'group': group, 'mode': 'group', 'files': [grouped['file']], 'problemNumbers': list(selected)})
        else:
            (output / grouped['file']).unlink()
            split = []
            for number in selected:
                result = build_zip(output / f'leetcode-video-style-{DATE}-{group}-LC{number}.zip', entries_for((number,)))
                if result['bytes'] >= MAX_BYTES:
                    (output / result['file']).unlink()
                    raise ValueError(f'LC{number} ZIP itself exceeds 95MiB; no oversized file was retained')
                result.update({'group': group, 'problemNumbers': [number], 'partitionMode': 'per-episode-fallback'})
                packages.append(result)
                split.append(result['file'])
            plan.append({'group': group, 'mode': 'per-episode-fallback',
                         'reason': 'Actual grouped ZIP reached the strict 95MiB limit',
                         'rejectedGroupedBytes': grouped['bytes'], 'files': split,
                         'problemNumbers': list(selected)})
    for movie, before in movie_states.items():
        if {**record(movie), 'mtimeNs': movie.stat().st_mtime_ns} != before:
            raise ValueError(f'Final source movie changed while packaging: {movie}')
    manifest = {'schemaVersion': 1, 'createdAtUTC': datetime.now(timezone.utc).isoformat(),
                'baselineCommit': BASELINE,
                'summary': str(summary_path.relative_to(ROOT)), 'summarySHA256': sha256(summary_path),
                'recognition': 'Delivery MP4s selected by actual final SHA-256 and byte count, not filenames or baseline MP4s.',
                'groupPlan': plan, 'packages': packages, 'files': all_file_records,
                'restoredOriginalCovers': restored_covers,
                'validation': {'status': 'passed', 'movieCount': 11, 'coverCount': 33,
                               'allMoviesUnchangedIncludingMtime': True,
                               'noBaselineMP4RestoredOrUsed': True,
                               'everyPackageStrictlyBelowBytes': MAX_BYTES,
                               'everyEntryPathCRCBytesAndSHA256Verified': True},
                'scope': 'GitHub site only; no external platform repost or new listening/ASR/physical-device claim.'}
    checksum_lines = [f"{entry['sha256']}  {entry['file']}" for entry in packages]
    checksum_lines += [f"{entry['sha256']}  delivery/{name}" for name, entry in sorted(all_file_records.items())]
    (output / 'SHA256SUMS.txt').write_text('\n'.join(checksum_lines) + '\n')
    (output / 'package-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


def self_test() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='package-selftest-', dir=WORK) as scratch:
        path = Path(scratch) / 'synthetic.zip'
        entries = {'sample.bin': b'\x00\x01tiny synthetic payload\xff', 'covers/test/说明.txt': '校验'.encode()}
        result = build_zip(path, entries)
        assert result['validation']['status'] == 'passed' and result['totalEntries'] == 2
        bad = {name: record(value) for name, value in entries.items()}
        bad['sample.bin']['sha256'] = '0' * 64
        try:
            validate_zip(path, bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Mismatched payload SHA was accepted')
        unsafe = Path(scratch) / 'unsafe.zip'
        with zipfile.ZipFile(unsafe, 'w') as archive:
            archive.writestr('../escape.txt', b'x')
        try:
            validate_zip(unsafe, {'../escape.txt': record(b'x')})
        except ValueError:
            pass
        else:
            raise AssertionError('Unsafe ZIP path was accepted')
    print('Package self-test passed: tiny synthetic ZIP CRC/bytes/SHA, wrong SHA and traversal rejection.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', default='docs/archive/2026-10/leetcode-video-style/final-media-summary.json')
    parser.add_argument('--delivery', default='work/leetcode-video-style/delivery')
    parser.add_argument('--output-dir', default='work/leetcode-video-style')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    summary = Path(args.summary)
    if not summary.is_absolute():
        summary = ROOT / summary
    manifest = package(summary.resolve(), work_path(args.delivery), work_path(args.output_dir))
    for item in manifest['packages']:
        print(f"{item['file']}: {item['bytes']} bytes; SHA256 {item['sha256']}; LC {item['problemNumbers']}")
    print('11 final MP4s and 33 original covers verified; all ZIPs are strictly below 95MiB.')


if __name__ == '__main__':
    main()
