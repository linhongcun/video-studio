"""Locate series-organized episodes and historical repository file references.

Old evidence records retain their original bytes. Resolve those recorded paths
here rather than editing the evidence to describe a later directory layout.
"""
from __future__ import annotations

from pathlib import Path
from functools import lru_cache
import hashlib
import json
import os
import re


_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


@lru_cache(maxsize=4)
def _read_migration_ledger(file: Path, modified_ns: int):
    return json.loads(file.read_text())


@lru_cache(maxsize=256)
def _manifest_identity(file: Path, modified_ns: int, size: int):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def repo_root(start=None) -> Path:
    """Find the repository from a file/directory, independent of its depth."""
    location = Path(start) if start is not None else Path(__file__)
    location = location.resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "site/package.json").is_file():
            return candidate
    raise ValueError(f"Cannot locate video-studio repository from {location}")


def _episode_directory(slug: str, root=None) -> Path:
    if not isinstance(slug, str) or not _SLUG.fullmatch(slug):
        raise ValueError(f"Invalid episode slug: {slug!r}")
    root = repo_root(root) if root is not None else repo_root()
    candidates = sorted((root / "episodes").glob(f"*/{slug}/publication/meta.json"))
    if len(candidates) != 1:
        raise ValueError(f"Expected one publication record for {slug}; found {len(candidates)}")
    directory = candidates[0].parent.parent.resolve()
    if not directory.is_relative_to(root / "episodes"):
        raise ValueError(f"Episode directory leaves repository: {slug}")
    return directory


def production_directory(slug: str, root=None) -> Path:
    return _episode_directory(slug, root) / "production"


def publication_directory(slug: str, root=None) -> Path:
    return _episode_directory(slug, root) / "publication"


def episode_slug(directory) -> str:
    """Find the owning episode of a production/publication revision."""
    location = Path(directory).resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        if candidate.name in {'production', 'publication'} \
                and (candidate.parent / 'publication/meta.json').is_file():
            return candidate.parent.name
    raise ValueError(f'Cannot locate an episode publication record from {location}')


def resolve_repo_path(relative, root=None) -> Path:
    """Resolve current or pre-migration paths recorded relative to the repo.

    Historical paths may also contain the original absolute checkout prefix.
    Returned paths must remain inside the current repository; existence is left
    to the caller because renderers also resolve paths for future outputs.
    """
    root = repo_root(root) if root is not None else repo_root()
    value = str(relative).replace("\\", "/")
    path = Path(value)
    if path.is_absolute():
        if path.is_relative_to(root):
            path = path.relative_to(root)
        elif "/video-studio/" in value:
            path = Path(value.split("/video-studio/", 1)[1])
        else:
            raise ValueError(f"Path outside repository: {relative}")
    parts = path.parts
    if parts and parts[0] == "episodes-codex":
        if len(parts) == 1:
            candidate = root / "episodes"
        elif parts[1] in {"_shared", "_template"}:
            candidate = root.joinpath("episodes", *parts[1:])
        elif len(parts) == 2 and parts[1].endswith('.py'):
            candidate = root / 'scripts' / parts[1]
        else:
            candidate = production_directory(parts[1], root).joinpath(*parts[2:])
    elif len(parts) >= 2 and parts[0] == "episodes" and not parts[1].startswith("_"):
        # Current paths include series/slug/{production,publication}. Old paths
        # have the slug immediately after episodes/; metadata disambiguates it.
        current = root / path
        if len(parts) >= 4 and parts[3] in {"production", "publication"}:
            candidate = current
        else:
            matches = list((root / "episodes").glob(f"*/{parts[1]}/publication/meta.json"))
            candidate = publication_directory(parts[1], root).joinpath(*parts[2:]) if matches else current
    else:
        candidate = root / path
    candidate = candidate.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"Path outside repository: {relative}")
    return candidate


def resolve_frozen_path(manifest: Path, relative: str) -> Path:
    """Locate an unchanged historical freeze entry after its physical move.

    The migration record only translates locations. Original expected hashes
    remain authoritative; this function never accepts changed input bytes.
    A new or edited freeze already uses its actual directory as the base.
    """
    root = repo_root()
    manifest = Path(manifest).resolve()
    if not manifest.is_relative_to(root):
        raise ValueError(f'Freeze manifest outside repository: {manifest}')
    ledger_file = root / 'docs/archive/2026-11/episode-layout/migration.json'
    ledger = _read_migration_ledger(ledger_file, ledger_file.stat().st_mtime_ns) if ledger_file.is_file() else {}
    record = ledger.get('legacyManifests', {}).get(manifest.relative_to(root).as_posix())
    identity = manifest.stat()
    current_sha = _manifest_identity(manifest, identity.st_mtime_ns, identity.st_size)
    if isinstance(record, dict) and current_sha == record.get('sha256'):
        original = Path(record['oldPath'])
        original = root / original if not original.is_absolute() else original
        old_target = Path(os.path.normpath(original.parent / relative))
        if not old_target.is_relative_to(root):
            raise ValueError(f'Frozen input outside repository: {relative}')
        name = old_target.relative_to(root).as_posix()
        prefixes = ledger.get('pathPrefixes', {})
        if isinstance(prefixes, dict):
            entries = prefixes.items()
        else:
            entries = ((entry['old'], entry['new']) if isinstance(entry, dict) else entry for entry in prefixes)
        for old, new in sorted(entries, key=lambda entry: len(entry[0]), reverse=True):
            old = old.rstrip('/')
            if name == old or name.startswith(old + '/'):
                name = new.rstrip('/') + name[len(old):]
                break
        candidate = (root / name).resolve()
    else:
        candidate = (manifest.parent / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f'Frozen input outside repository: {relative}')
    return candidate
