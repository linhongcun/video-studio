#!/usr/bin/env python3
"""Offline unit tests for scripts/check-repo-size.py and scripts/clean-local-cache.py."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CHECK_SIZE = ROOT / 'scripts/check-repo-size.py'
CLEAN_CACHE = ROOT / 'scripts/clean-local-cache.py'


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def init_mini_repo(repo: Path) -> None:
    run(['git', 'init'], repo)
    run(['git', 'config', 'user.email', 'test@example.com'], repo)
    run(['git', 'config', 'user.name', 'Test'], repo)
    (repo / 'AGENTS.md').write_text('# test\n', encoding='utf-8')
    (repo / 'site').mkdir(parents=True, exist_ok=True)
    (repo / 'site/package.json').write_text('{"name":"test"}\n', encoding='utf-8')
    (repo / '.gitignore').write_text('node_modules\n*.mp4\n!episodes/*/*/publication/video.mp4\n*.raw\n', encoding='utf-8')
    (repo / 'scripts').mkdir(parents=True, exist_ok=True)
    run(['git', 'add', '.'], repo)
    run(['git', 'commit', '-m', 'init'], repo)


def test_repo_size_gate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        init_mini_repo(repo)
        legacy = repo / 'scripts/repo-size-legacy.json'

        # 1. Valid published video > 5 MiB must pass
        pub_video = repo / 'episodes/request/demo/publication/video.mp4'
        pub_video.parent.mkdir(parents=True, exist_ok=True)
        pub_video.write_bytes(b'0' * (6 * 1024 * 1024))
        run(['git', 'add', str(pub_video)], repo)
        run(['git', 'commit', '-m', 'add pub video'], repo)
        r = run([sys.executable, str(CHECK_SIZE), '--repo', str(repo), '--legacy', str(legacy)], repo)
        assert r.returncode == 0, r.stderr

        # 2. Force-tracked production mp4 must fail
        prod_mp4 = repo / 'episodes/request/demo/production/video.mp4'
        prod_mp4.parent.mkdir(parents=True, exist_ok=True)
        prod_mp4.write_bytes(b'1' * 1024)
        run(['git', 'add', '-f', str(prod_mp4)], repo)
        r_fail = run([sys.executable, str(CHECK_SIZE), '--repo', str(repo), '--legacy', str(legacy)], repo, check=False)
        assert r_fail.returncode == 1 and 'forceTrackedIgnored' in r_fail.stderr, r_fail.stderr

        # 3. Recording into legacy baseline allows historical file, while a second new file still fails
        run(['git', 'commit', '-m', 'legacy mp4'], repo)
        run([sys.executable, str(CHECK_SIZE), '--repo', str(repo), '--legacy', str(legacy), '--write-legacy'], repo)
        r_ok = run([sys.executable, str(CHECK_SIZE), '--repo', str(repo), '--legacy', str(legacy)], repo)
        assert r_ok.returncode == 0, r_ok.stderr

        # 4. New banned .raw file and embedded-bitmap SVG must fail
        raw_file = repo / 'docs/sample.raw'
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        raw_file.write_bytes(b'raw')
        run(['git', 'add', '-f', str(raw_file)], repo)
        svg_file = repo / 'docs/bloated.svg'
        svg_file.write_text('<svg><image href="data:image/png;base64,' + ('A' * 600_000) + '"/></svg>', encoding='utf-8')
        run(['git', 'add', str(svg_file)], repo)
        r_bad = run([sys.executable, str(CHECK_SIZE), '--repo', str(repo), '--legacy', str(legacy)], repo, check=False)
        assert r_bad.returncode == 1
        assert 'bannedFormat' in r_bad.stderr and 'embeddedBitmapSvg' in r_bad.stderr, r_bad.stderr


def test_clean_local_cache() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        init_mini_repo(repo)

        # Create rebuildable ignored caches
        (repo / 'site/dist').mkdir(parents=True, exist_ok=True)
        (repo / 'site/dist/index.html').write_text('ok', encoding='utf-8')
        keep_nm = repo / 'episodes/leetcode/keep-ep/production/remotion/node_modules'
        drop_nm = repo / 'episodes/leetcode/drop-ep/production/remotion/node_modules'
        keep_nm.mkdir(parents=True, exist_ok=True)
        drop_nm.mkdir(parents=True, exist_ok=True)
        (keep_nm / 'a.js').write_text('x', encoding='utf-8')
        (drop_nm / 'b.js').write_text('y', encoding='utf-8')

        # Tracked file inside site/public/episodes must NEVER be deleted
        tracked = repo / 'episodes/leetcode/keep-ep/production/readme.txt'
        tracked.write_text('keep me', encoding='utf-8')
        run(['git', 'add', str(tracked)], repo)
        run(['git', 'commit', '-m', 'add tracked'], repo)

        # Dry-run leaves everything untouched
        r_dry = run([sys.executable, str(CLEAN_CACHE), '--repo', str(repo), '--keep', 'keep-ep'], repo)
        assert '[DRY-RUN]' in r_dry.stdout
        assert (repo / 'site/dist').exists() and drop_nm.exists() and keep_nm.exists()

        # Apply deletes site/dist and drop_nm, preserves keep_nm and tracked files
        r_app = run([sys.executable, str(CLEAN_CACHE), '--repo', str(repo), '--keep', 'keep-ep', '--apply'], repo)
        assert '[APPLY]' in r_app.stdout
        assert not (repo / 'site/dist').exists()
        assert not drop_nm.exists()
        assert keep_nm.exists()
        assert tracked.is_file()


def main() -> int:
    test_repo_size_gate()
    test_clean_local_cache()
    print('test_repo_size_and_cache ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
