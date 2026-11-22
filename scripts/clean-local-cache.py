#!/usr/bin/env python3
"""Safely preview and remove rebuildable gitignored local caches.

Default mode is --dry-run (read-only). Pass --apply to actually remove caches.
Never deletes any file tracked by Git.

Examples:
  python3 scripts/clean-local-cache.py
  python3 scripts/clean-local-cache.py --apply
  python3 scripts/clean-local-cache.py --apply --keep rotting-oranges --git-gc
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file()
)


def fmt_bytes(size: int) -> str:
    value = float(size)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if value < 1024 or unit == 'TB':
            return f'{value:.1f} {unit}' if unit != 'B' else f'{int(value)} B'
        value /= 1024
    return f'{size} B'


def dir_size(path: Path) -> int:
    if path.is_symlink():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, _, files in os.walk(path, followlinks=False):
        for name in files:
            fp = Path(root) / name
            if not fp.is_symlink():
                try:
                    total += fp.stat().st_size
                except OSError:
                    pass
    return total


def tracked_set(repo: Path) -> set[str]:
    out = subprocess.check_output(['git', 'ls-files', '-z'], cwd=repo)
    return {p for p in out.decode('utf-8', errors='replace').split('\0') if p}


def contains_tracked(rel_path: str, tracked: set[str]) -> bool:
    prefix = rel_path.rstrip('/') + '/'
    return rel_path in tracked or any(item.startswith(prefix) for item in tracked)


def find_candidates(repo: Path, tracked: set[str], *, keep_slugs: set[str], include_site_nm: bool) -> list[tuple[str, Path, int]]:
    candidates: list[tuple[str, Path, int]] = []
    seen: set[Path] = set()

    def add(category: str, target: Path) -> None:
        resolved = target.resolve()
        if not target.exists() or target.is_symlink() or resolved in seen:
            return
        rel = target.relative_to(repo).as_posix()
        if contains_tracked(rel, tracked):
            return
        seen.add(resolved)
        candidates.append((category, target, dir_size(target)))

    # 1. Site rebuildable build / copy outputs
    for rel in ('site/dist', 'site/public/episodes', 'site/public/videos', 'site/.astro', '.remotion'):
        add('site-cache', repo / rel)

    if include_site_nm:
        add('site-node-modules', repo / 'site/node_modules')

    # 2. Rebuildable production node_modules, out/, and __pycache__ under episodes/
    episodes_dir = repo / 'episodes'
    if episodes_dir.is_dir():
        for root, dirs, _ in os.walk(episodes_dir, followlinks=False):
            root_path = Path(root)
            rel_parts = root_path.relative_to(repo).parts
            slug = rel_parts[2] if len(rel_parts) >= 3 and not rel_parts[1].startswith('_') else None
            pruned = []
            for d in list(dirs):
                target = root_path / d
                if d == 'node_modules':
                    if slug and slug in keep_slugs:
                        pruned.append(d)
                        continue
                    add('remotion-node-modules', target)
                    pruned.append(d)
                elif d == 'out' and 'production' in rel_parts:
                    add('render-out', target)
                    pruned.append(d)
                elif d == '__pycache__':
                    add('pycache', target)
                    pruned.append(d)
            for d in pruned:
                dirs.remove(d)

    # 3. scripts/__pycache__
    add('pycache', repo / 'scripts/__pycache__')
    return sorted(candidates, key=lambda item: (-item[2], item[1].as_posix()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Actually delete matched rebuildable caches (default: dry-run)')
    parser.add_argument('--keep', action='append', default=[], metavar='SLUG', help='Keep node_modules for this episode slug (repeatable)')
    parser.add_argument('--include-site-node-modules', action='store_true', help='Also include site/node_modules')
    parser.add_argument('--git-gc', action='store_true', help='Run `git gc --prune=now` when --apply is set')
    parser.add_argument('--repo', type=Path, default=ROOT, help='Repository root (defaults to current repo)')
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    tracked = tracked_set(repo)
    keep_slugs = set(args.keep)
    items = find_candidates(
        repo,
        tracked,
        keep_slugs=keep_slugs,
        include_site_nm=args.include_site_node_modules,
    )

    total = sum(sz for _, _, sz in items)
    mode = 'APPLY' if args.apply else 'DRY-RUN'
    print(f'[{mode}] Found {len(items)} rebuildable cache paths totaling {fmt_bytes(total)}')
    for cat, path, sz in items:
        rel = path.relative_to(repo).as_posix()
        print(f'  {fmt_bytes(sz):>10}  [{cat}]  {rel}')
        if args.apply:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)

    if args.git_gc:
        if args.apply:
            print('[APPLY] Running `git gc --prune=now`...')
            subprocess.run(['git', 'gc', '--prune=now'], cwd=repo, check=True)
        else:
            print('[DRY-RUN] Would run `git gc --prune=now`')

    if not args.apply and items:
        print('\nRe-run with --apply to delete the listed rebuildable caches.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
