"""Audit a visual revision against its actual released Git inputs.

Run from the repository root. --encoded also checks the new viewing copies;
it must only be used after the revised media have been encoded and reviewed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--baseline', required=True, help='Released Git commit or tag')
parser.add_argument('--encoded', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
slugs = ['tx-2pc', 'tx-tcc', 'tx-saga', 'tx-outbox']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def previous(path):
    return subprocess.check_output(['git', 'show', f'{args.baseline}:{path}'], cwd=root)


records = []
for slug in slugs:
    relative = Path('episodes-codex') / slug
    episode = root / relative
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
        assert movie == (root / 'episodes' / slug / 'video.mp4').read_bytes()
        old_media = json.loads(previous((relative / 'render-result.json').as_posix()))
        assert media['sha256'] != old_media['sha256'], f'{slug}: old movie still present'
        item.update(sha256=media['sha256'], releasedCopyMatches=True)
    records.append(item)

preserved = {}
for slug in ['distributed-tx', 'distributed-tx-intro']:
    episode = root / 'episodes-codex' / slug
    manifest = json.loads((episode / 'source-sha256.json').read_text())
    for name, digest in manifest.items():
        assert sha((episode / name).read_bytes()) == digest, (slug, name)
    for prefix in ['episodes-codex', 'episodes']:
        relative = Path(prefix) / slug / 'video.mp4'
        assert (root / relative).read_bytes() == previous(relative.as_posix()), str(relative)
    preserved[slug] = len(manifest)

print(json.dumps(dict(baseline=args.baseline, scope='encoded copies' if args.encoded else 'inputs',
                      episodes=records, preservedEarlierFrozenInputs=preserved),
                 ensure_ascii=False, indent=2))
