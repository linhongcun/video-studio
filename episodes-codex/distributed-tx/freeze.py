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
HISTORICAL_SHA256 = 'f80ef0fa3cdf42b74a09f6c8c1b36573b7c92c71565cb22d659791101d657f70'
HISTORICAL_COUNT = 194
HAD_LOCAL_FREEZER = True
# These absent legacy splice/cache files remain declared only in the pinned archive.
HISTORICAL_ONLY_KEYS = []
JAVA_BODY_REL = None
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


def validate_java_tail(storyboard, words):
    if JAVA_BODY_REL is None:
        assert not storyboard['meta'].get('javaEndCard')
        return
    # Reuse the original pure derivation functions. Do not call verify(), which
    # writes a QA report, or append(), which changes the narration/body inputs.
    helper_path = ROOT/'episodes-codex/_shared/append_java_endcard.py'
    spec = importlib.util.spec_from_file_location('original_java_derivation', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    body = D/JAVA_BODY_REL
    saved = helper.load_body(body)
    card = storyboard['meta']['javaEndCard']
    assert card['kind'] == 'java-design-pattern' and card['durationInFrames'] == 150
    assert card['from'] == saved['bodyFrames']
    assert card['from'] + card['durationInFrames'] == storyboard['meta']['durationInFrames']
    expected_words, expected_sb, expected_shots = helper.expected_final(
        body, saved, card['durationInFrames'], sha(D/'voice.wav'))
    assert words == expected_words and storyboard == expected_sb
    assert read(D/'voice/shot_frames.json') == expected_shots
    _, original_pcm = helper.read_pcm(body/'voice.wav')
    _, final_pcm = helper.read_pcm(D/'voice.wav')
    assert len(original_pcm) == saved['bodyFrames'] * 1600 * 2
    assert len(final_pcm) == storyboard['meta']['durationInFrames'] * 1600 * 2
    assert final_pcm[:len(original_pcm)] == original_pcm
    assert not any(final_pcm[len(original_pcm):]), 'Java tail narration must remain digital silence'
    assert (D/'captions.srt').read_bytes() == (body/'captions.srt').read_bytes()
    assert all(shot['from'] + sub['to'] < card['from']
               for scene in storyboard['scenes'] for shot in scene['shots']
               for sub in shot['subtitles'])
    assert max(voice['wavEnd'] for scene in storyboard['scenes']
               for shot in scene['shots'] for voice in shot['voice']) <= card['from']
    display = read(D/'remotion/src/java-card.json')
    assert display['language'] == 'Java' and sha(D/display['sourceFile']) == display['sourceSha256']


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

    assert not storyboard['meta'].get('unvoicedEndCard'), 'These bodies have no Python card'
    validate_java_tail(storyboard, words)


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
    # Prior bibliography records are original text evidence, distinct from the
    # layout preview PNG paths that also occur in this source JSON.
    for record in value.get('priorTitleAndAuthorBibliography', []):
        path = ROOT/record['path']
        assert path.resolve().is_relative_to(ROOT) and path.is_file(), path
        assert sha(path) == record['fileSHA256'], ('Prior bibliography changed', path)
        mentioned.add(path)
        verified.add(path)
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
        # A title evidence file may itself be an official raw text capture.
        # Only structured JSON evidence can declare further saved dependencies.
        if path.suffix == '.json':
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
