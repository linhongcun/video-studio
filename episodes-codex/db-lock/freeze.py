#!/usr/bin/env python3
"""Freeze current reference wiring while preserving the legacy body record.

This never assembles, copies or edits narration/storyboards/placeholders. The
archived legacy record is narrow historical evidence, not a reproduction claim
for the checked MP4. Current additional inputs describe the new appendix and
future default rendering. --verify is strictly read-only.
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
HISTORICAL_SHA256 = '50f640e87d50e8dec7cabd99a6dfcce40659c99fa71c350e9c83ad3812cca013'
MANIFEST = D/'source-sha256.json'
WRAPPER = ROOT/'episodes-codex/_shared/render_with_references.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def historical_inputs():
    assert sha(HISTORICAL) == HISTORICAL_SHA256, 'Archived legacy input record changed'
    original = read(HISTORICAL)
    for relative, expected in original.items():
        path = ARCHIVE/'before-remotion-package.json' if relative == 'remotion/package.json' else D/relative
        assert path.resolve().is_relative_to(ROOT) and path.is_file(), relative
        assert sha(path) == expected, ('Legacy recorded input changed', relative)
    return original


def verify():
    manifest = read(MANIFEST)
    assert isinstance(manifest, dict) and manifest
    for relative, expected in manifest.items():
        path = (D/relative).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and sha(path) == expected, relative
    spec = importlib.util.spec_from_file_location('legacy_reference_wrapper', WRAPPER)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    wrapper.verify_freeze(D)
    print(json.dumps({'status':'passed', 'inputs':len(manifest), 'readOnly':True,
                      'manifestSHA256':sha(MANIFEST)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    original = historical_inputs()
    subprocess.run(['node', str(ROOT/'site/scripts/check-references.mjs'), '--sources', str(D)],
                   cwd=ROOT, check=True)
    storyboard, words = read(D/'storyboard.json'), read(D/'words.json')
    assert words['scriptSha256'] == sha(D/'script.md')
    assert words['audioSha256'] == sha(D/'voice.wav')
    assert sha(D/'voice.wav') == sha(D/'remotion/public/audio/voice.wav')
    assert storyboard['meta']['durationInFrames'] == words['durationFrames']
    # Retain every legacy key, including the transaction's identity wrapper/assets.
    files = [D/relative for relative in original]
    files += [Path(__file__).resolve(), HISTORICAL, ARCHIVE/'before-remotion-package.json']
    files += [D/name for name in ['script.md','article.mdx','research.md','references.json',
              'pronunciation.md','assemble.py','storyboard.json','words.json','covers.json',
              'voice.wav','remotion/public/audio/voice.wav','remotion/package.json',
              'remotion/package-lock.json','remotion/remotion.config.ts','remotion/tsconfig.json']]
    for name in ['visual-direction.md','visual-direction-v2.md','knoll-props.md',
                 'voice/params.json','voice/picks.json','voice/sents.json','voice/build.json',
                 'voice/substitutions.md','voice/cues.json','voice/cue_tests.json',
                 'voice/shot_frames.json','voice/input-provenance.json',
                 'voice/script-narration-sha256.json']:
        if (D/name).is_file():
            files.append(D/name)
    files += [p for p in (D/'remotion/src').rglob('*') if p.is_file()]
    files += [p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
    picks = read(D/'voice/picks.json')
    for sentence in read(D/'voice/sents.json'):
        stem = sentence['id']+'-'+picks.get(sentence['id'],'a')
        for suffix in ['.wav','.txt.json','.raw.wav']:
            path = D/'voice/takes'/(stem+suffix)
            if suffix != '.raw.wav' or path.is_file():
                files.append(path)
    files += [ROOT/'episodes/_shared'/name for name in [
        'onset_rule.py','voice/prep.py','voice/gen.py','voice/build.py','voice/common.py',
        'tts/mimo_say.py','theme/pageTheme.ts','music/mix_bgm.py','music/Wallpaper.mp3']]
    files += [WRAPPER, ROOT/'site/scripts/check-references.mjs']
    files += [ROOT/'episodes-codex/_shared'/name for name in [
        'append_references_bibliography.py','append_references_original.py','append_references.py',
        'requirements-reference-appendix.txt']]
    for source in read(D/'references.json')['sources']:
        records = [source['verification'], source['titleEvidence']]
        if 'quotation' in source:
            records.append(source['quotation'])
        files += [ROOT/record['evidence'] for record in records]
    paths = sorted({path.resolve() for path in files})
    forbidden = {'video.mp4','body.mp4','voice.mp4','render-result.json',
                 'reference-appendix.json','reference-appendix-media-check.json'}
    for path in paths:
        assert path.is_relative_to(ROOT) and path.is_file(), path
        assert path.suffix != '.mp4' and path.name not in forbidden, path
    current = {os.path.relpath(path,D):sha(path) for path in paths}
    assert set(original) <= set(current), 'A legacy recorded key was dropped'
    MANIFEST.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
    verify()


if __name__ == '__main__':
    main()
