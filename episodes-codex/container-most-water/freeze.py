#!/usr/bin/env python3
"""Freeze current reference inputs while retaining the complete old body record.

The accepted Git MP4 is an immutable input to this reference-only revision.
This entry never assembles, requests TTS, or writes a storyboard/placeholder.
The historical record is retained separately; the expanded current manifest
is not a claim to have reproduced the old MP4. --verify is read-only.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
ARCHIVE = D/'revisions/reference-endcards'
HISTORICAL = ARCHIVE/'before-source-sha256.json'
HISTORICAL_SHA256 = '3ab8e8964a74209cecf3d3241069ee34c4cfc8f21bbd60541fab1bb135f542ce'
HISTORICAL_COUNT = 210
HAD_LOCAL_FREEZER = True
# These absent legacy splice/cache files remain declared only in the pinned archive.
HISTORICAL_ONLY_KEYS = ['remotion/out/approach-07-10.mp4', 'remotion/out/approach-12.mp4', 'remotion/out/approach-16.mp4', 'remotion/out/approach-18.mp4', 'remotion/out/approach-20-21.mp4', 'remotion/out/approach-baseline/src/CodeCard.tsx', 'remotion/out/approach-baseline/src/Cover.tsx', 'remotion/out/approach-baseline/src/Main.tsx', 'remotion/out/approach-baseline/src/Root.tsx', 'remotion/out/approach-baseline/src/data.ts', 'remotion/out/approach-baseline/src/index.ts', 'remotion/out/approach-baseline/src/placeholders/storyboard.json', 'remotion/out/approach-baseline/src/theme.ts', 'remotion/out/approach-baseline/storyboard.json', 'remotion/out/approach-baseline/video.mp4', 'remotion/out/approach-baseline/voice.wav']
MANIFEST = D/'source-sha256.json'
WRAPPER = ROOT/'episodes-codex/_shared/render_with_references.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def historical_inputs():
    assert sha(HISTORICAL) == HISTORICAL_SHA256, 'Archived body input record changed'
    original = read(HISTORICAL)
    assert len(original) == HISTORICAL_COUNT
    relocated = {name:ARCHIVE/('before-'+name) for name in ['article.mdx','research.md']}
    relocated['remotion/package.json'] = ARCHIVE/'before-remotion-package.json'
    if HAD_LOCAL_FREEZER:
        relocated['freeze.py'] = ARCHIVE/'before-freeze.py'
    for relative, expected in original.items():
        if relative in HISTORICAL_ONLY_KEYS:
            continue  # Historical SHA declaration, not a current verified file.
        path = relocated.get(relative, D/relative)
        assert path.resolve().is_relative_to(ROOT) and path.is_file(), relative
        assert sha(path) == expected, ('Original recorded input changed', relative)
    assert set(HISTORICAL_ONLY_KEYS) <= set(original)
    present = {key:value for key,value in original.items() if key not in HISTORICAL_ONLY_KEYS}
    return present, list(relocated.values())


def validate_body():
    storyboard, words = read(D/'storyboard.json'), read(D/'words.json')
    assert not storyboard['meta'].get('provisionalTiming') and not storyboard['meta'].get('pendingAudio')
    assert words['scriptSha256'] == sha(D/'script.md')
    assert words['audioSha256'] == sha(D/'voice.wav')
    assert (D/'voice.wav').read_bytes() == (D/'remotion/public/audio/voice.wav').read_bytes()
    assert storyboard['meta']['durationInFrames'] == words['durationFrames']
    # These files already belong to the accepted body; only compare their bytes.
    raw = (D/'storyboard.json').read_bytes()
    snapshot = D/f'storyboard.{sha(D/"storyboard.json")[:8]}.json'
    assert snapshot.read_bytes() == raw, 'Assembled storyboard snapshot differs'
    assert (D/'remotion/src/placeholders/storyboard.json').read_bytes() == raw, 'Placeholder differs'
    if (D/'episode-config.json').is_file():
        config = read(D/'episode-config.json')
        assert storyboard['meta']['covers'] == read(D/'covers.json')
        assert storyboard['meta']['title'] == config['title']
        assert len(words['shots']) == config['shotCount']
        assert sum(shot['durationInFrames'] for scene in storyboard['scenes']
                   for shot in scene['shots']) == words['durationFrames']

    card = storyboard['meta']['unvoicedEndCard']
    assert card['kind'] == 'full-python-solution' and card['durationInFrames'] == 150
    assert card['from'] + card['durationInFrames'] == storyboard['meta']['durationInFrames']
    assert sha(D/card['codeSource']) == card['codeSourceSha256']
    assert sha(D/card['displaySource']) == card['displaySourceSha256']
    assert read(D/card['displaySource'])['lines'] == (D/card['codeSource']).read_text().splitlines()
    assert card['from'] > max(voice['wavEnd'] for scene in storyboard['scenes']
                             for shot in scene['shots'] for voice in shot['voice'])

    if (D/'approach-remix-plan.json').is_file():
        plan = read(D/'approach-remix-plan.json')
        assert all(clip['sha256'] for clip in plan['clips']), 'Recorded splice clip SHA missing'
        assert (D/plan['visualReview']).is_file(), 'Recorded visual-reuse review missing'
        for relative in plan['freezeRequirements']['files']:
            key = os.path.relpath((D/relative).resolve(), D)
            if key not in HISTORICAL_ONLY_KEYS:
                assert (D/relative).is_file(), relative
        # The missing clips themselves are archived declarations, never recreated here.


def verify():
    original, _ = historical_inputs()
    validate_body()
    manifest = read(MANIFEST)
    assert isinstance(manifest, dict) and manifest
    assert set(original) <= set(manifest), 'An original input key was dropped'
    for relative, expected in manifest.items():
        path = (D/relative).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and sha(path) == expected, relative
    spec = importlib.util.spec_from_file_location('reference_wrapper', WRAPPER)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    wrapper.verify_freeze(D)
    print(json.dumps({'status':'passed','inputs':len(manifest),'readOnly':True,
                      'manifestSHA256':sha(MANIFEST),'historicalDeclared':HISTORICAL_COUNT,
                      'historicalPresentVerified':len(original),'historicalMissing':len(HISTORICAL_ONLY_KEYS)},ensure_ascii=False))


def saved_evidence(value):
    """Bind saved files once even when later excerpts refer to the same file."""
    mentioned, verified = set(), set()

    def visit(item):
        if isinstance(item, dict):
            keys = [key for key in ['savedPath','savedResponsePath','archivePath','savedCapturePath']
                    if isinstance(item.get(key), str)]
            expected = [item.get('sha256'),item.get('recordSHA256'),
                        item.get('get', {}).get('sha256'),
                        item.get('originalRetrieval', {}).get('sha256'),
                        item.get('copiedOriginalBinding', {}).get('completeSHA256')]
            expected = [digest for digest in expected if digest]
            for key in keys:
                path = ROOT/item[key]
                assert path.resolve().is_relative_to(ROOT) and path.is_file(), path
                mentioned.add(path)
                if expected:
                    actual = sha(path)
                    assert all(actual == digest for digest in expected), ('Raw evidence changed', path)
                    verified.add(path)
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    assert mentioned <= verified, ('Saved evidence lacks a complete SHA binding', mentioned-verified)
    return sorted(verified)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Check current and historical inputs without writing them.')
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    original, snapshots = historical_inputs()
    validate_body()
    subprocess.run(['node',str(ROOT/'site/scripts/check-references.mjs'),'--sources',str(D)],
                   cwd=ROOT,check=True)
    # Preserve every present legacy key; absent cache declarations stay in the pinned archive.
    files = [D/relative for relative in original]
    files += [Path(__file__).resolve(),HISTORICAL,*snapshots,
              ARCHIVE/'baseline.json',ARCHIVE/'before-render-result.json',D/'references.json',
              D/'article.mdx',D/'research.md',D/'remotion/package.json',WRAPPER,
              ROOT/'site/scripts/check-references.mjs',ROOT/'episodes/_shared/theme/pageTheme.ts']
    files += [ROOT/'episodes-codex/_shared'/name for name in [
        'append_references_bibliography.py','append_references_original.py','append_references.py',
        'requirements-reference-appendix.txt']]
    evidence = set()
    for source in read(D/'references.json')['sources']:
        records = [source['verification'],source['titleEvidence']]
        if 'quotation' in source:
            records.append(source['quotation'])
        evidence.update(ROOT/record['evidence'] for record in records)
    for path in evidence:
        files.append(path)
        files += saved_evidence(read(path))
    paths = sorted({path.resolve() for path in files})
    forbidden = {'render-result.json','reference-appendix.json','reference-appendix-media-check.json'}
    for path in paths:
        assert path.is_relative_to(ROOT) and path.is_file(), path
        # New receipts/media are outputs; retain any explicitly recorded legacy input.
        relative = os.path.relpath(path,D)
        assert relative in original or (path.suffix != '.mp4' and path.name not in forbidden), path
    current = {os.path.relpath(path,D):sha(path) for path in paths}
    assert set(original) <= set(current), 'An original input key was dropped'
    MANIFEST.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
    verify()


if __name__ == '__main__':
    main()
