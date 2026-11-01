"""Audit a visual revision against its actual released Git inputs.

Run from the repository root. --encoded also checks the new viewing copies;
it must only be used after the revised media have been encoded and reviewed.
"""

import sys as _episode_path_sys
from pathlib import Path as _EpisodePath
_episode_path_sys.path.insert(0, str(next(parent for parent in _EpisodePath(__file__).resolve().parents
                                       if (parent / 'episode_paths.py').is_file())))
from episode_paths import repo_root, production_directory, publication_directory, resolve_repo_path, resolve_frozen_path
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--baseline', required=True, help='Released Git commit or tag')
parser.add_argument('--encoded', action='store_true')
args = parser.parse_args()
root = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
slugs = ['tx-2pc', 'tx-tcc', 'tx-saga', 'tx-outbox']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def previous(path):
    return subprocess.check_output(['git', 'show', f'{args.baseline}:{path}'], cwd=root)


records = []
for slug in slugs:
    relative = Path('episodes-codex') / slug
    episode = resolve_repo_path(relative)
    unchanged = ['voice.wav', 'remotion/public/audio/voice.wav', 'script.md',
                 'words.json', 'captions.srt', 'voice/picks.json', 'voice/sents.json']
    digests = {}
    for name in unchanged:
        data = (episode / name).read_bytes()
        assert data == previous((relative / name).as_posix()), (slug, name)
        digests[name] = sha(data)
    original = json.loads(previous((relative / 'storyboard.json').as_posix()))
    current = json.loads((episode / 'storyboard.json').read_text())
    assert current['scenes'] == original['scenes'], f'{slug}: narration/shot timing changed'
    for key in ['fps', 'durationInFrames', 'width', 'height', 'timingSource']:
        assert current['meta'][key] == original['meta'][key], (slug, key)
    assert current['meta']['visualRevision'] == 2
    item = dict(slug=slug, unchangedFiles=digests,
                originalShotTimingPreserved=True,
                frames=current['meta']['durationInFrames'])
    if args.encoded:
        media = json.loads((episode / 'render-result.json').read_text())
        movie = (episode / 'video.mp4').read_bytes()
        assert sha(movie) == media['sha256']
        assert media['visualRevision'] == 2
        assert movie == (publication_directory(slug, root=root) / 'video.mp4').read_bytes()
        old_media = json.loads(previous((relative / 'render-result.json').as_posix()))
        assert media['sha256'] != old_media['sha256'], f'{slug}: old movie still present'
        item.update(sha256=media['sha256'], releasedCopyMatches=True)
    records.append(item)

preserved = {}
for slug in ['distributed-tx', 'distributed-tx-intro']:
    episode = production_directory(slug, root=root)
    manifest_path = episode / 'source-sha256.json'
    manifest = json.loads(manifest_path.read_text())
    for name, digest in manifest.items():
        assert sha(resolve_frozen_path(manifest_path, name).read_bytes()) == digest, (slug, name)
    for prefix in ['episodes-codex', 'episodes']:
        relative = Path(prefix) / slug / 'video.mp4'
        assert resolve_repo_path(relative).read_bytes() == previous(relative.as_posix()), str(relative)
    preserved[slug] = len(manifest)

print(json.dumps(dict(baseline=args.baseline, scope='encoded copies' if args.encoded else 'inputs',
                      episodes=records, preservedEarlierFrozenInputs=preserved),
                 ensure_ascii=False, indent=2))
