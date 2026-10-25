#!/usr/bin/env python3
"""Shared-build four revised sentences, then splice exact baseline PCM.

No TTS, trimming, normalization, limiting or onset algorithm is implemented
here. Default rebuilds only the persistent mini with the shared builder.
--compose-only consumes an already checked mini; --verify is read-only.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
BASE = D / 'revisions/binary-opening/baseline'
MINI = D / 'voice/binary-mini'
SR, FPS, SPF = 48000, 30, 1600
FIRST, LAST, LEAD = 755, 1676, 1
BASE_SHA = '2ea3e8b68eee14f11b6c5699bb865fe17d2c92f25a82d6e2cdcc249086b6ef2c'
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import lufs


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path)) as audio:
        assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (SR, 1, 2)
        return audio.readframes(audio.getnframes())


def write_pcm(path, data):
    with wave.open(str(path), 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SR)
        audio.writeframes(data)


def expected():
    assert sha(BASE / 'voice.wav') == BASE_SHA
    archived = read(BASE / 'manifest.json')['filesSHA256']
    for relative in ['voice/build.json', 'voice/sents.json', 'voice/picks.json',
                     'voice/input-provenance.json', 'voice/script-narration-sha256.json',
                     'words.json', 'storyboard.json']:
        assert sha(BASE / relative) == archived[relative], relative
    provenance = read(MINI / 'voice/input-provenance.json')
    assert sha(D / 'script.md') == provenance['mainScriptSHA256']
    assert sha(D / 'plan.json') == provenance['mainPlanSHA256']
    assert (D / 'voice/input-provenance.json').read_bytes() == (BASE / 'voice/input-provenance.json').read_bytes()
    assert (D / 'voice/script-narration-sha256.json').read_bytes() == (BASE / 'voice/script-narration-sha256.json').read_bytes()
    sents = read(D / 'voice/sents.json')
    old = {r['id']: r for r in read(BASE / 'voice/build.json')['sentences']}
    new = {r['id']: r for r in read(MINI / 'voice/build.json')['sentences']}
    assert len(sents) == 24 and len(new) == 4
    assert {r['id'] for r in sents if r['shot'][:2] in {'03', '04'}} == set(new)
    source = pcm(BASE / 'voice.wav')
    stage = pcm(MINI / 'voice.wav')
    assert not any(stage[:LEAD * SPF * 2]), 'Only a verified zero lead frame may be removed'
    mini_frames = read(MINI / 'voice/build.json')['summary']['frames']
    assert len(stage) == mini_frames * SPF * 2
    block = stage[LEAD * SPF * 2:]
    length = mini_frames - LEAD
    delta = length - (LAST - FIRST)
    result = source[:FIRST * SPF * 2] + block + source[LAST * SPF * 2:]
    rows, picks = [], {}
    for sent in sents:
        changed = sent['id'] in new
        origin = new[sent['id']] if changed else old[sent['id']]
        assert (sent['text'], sent['tts']) == (origin['text'], origin['tts'])
        take_root = MINI / 'voice/takes' if changed else D / 'voice/takes'
        take_name = f"{sent['id']}-{origin['take']}"
        assert read(take_root / (take_name + '.txt.json')) == sent['tts']
        if not changed:
            original_frozen = read(BASE / 'source-sha256.json')
            for suffix in ['.wav', '.raw.wav', '.txt.json']:
                relative = 'voice/takes/' + take_name + suffix
                assert sha(D / relative) == original_frozen[relative], relative
        offset = FIRST - LEAD if changed else (delta if int(sent['shot'][:2]) >= 5 else 0)
        row = copy.deepcopy(origin)
        for key in ['startSample', 'endSample']:
            row[key] += offset * SPF
        for key in ['startFrame', 'endFrame']:
            row[key] = round(row[key] + offset, 2)
        if rows:
            row['gapBefore'] = round((row['startSample'] - rows[-1]['endSample']) / SR, 4)
        rows.append(row)
        picks[sent['id']] = row['take']
    frames = len(result) // (SPF * 2)
    assert frames == 5257 + delta and len(result) == frames * SPF * 2
    return result, rows, picks, dict(newBlockFrames=length, deltaFrames=delta, frames=frames,
                                   samples=frames * SPF, source=source, old=old, new=new)


def verify():
    result, rows, picks, info = expected()
    current = pcm(D / 'voice.wav')
    assert current == result, 'Whole PCM differs from baseline-prefix + shared-mini + baseline-suffix'
    build = read(D / 'voice/build.json')
    assert build['sentences'] == rows and read(D / 'voice/picks.json') == picks
    assert build['summary']['sha'] == sha(D / 'voice.wav')
    checks = []
    for row in rows:
        segment = current[row['startSample'] * 2:row['endSample'] * 2]
        assert pcm(D / 'voice/sentences' / (row['id'] + '.wav')) == segment
        changed = row['id'] in info['new']
        if not changed:
            old = info['old'][row['id']]
            original = info['source'][old['startSample'] * 2:old['endSample'] * 2]
            assert original == segment, row['id']
            checks.append(dict(id=row['id'], take=row['take'], oldStartSample=old['startSample'],
                               oldEndSample=old['endSample'], newStartSample=row['startSample'],
                               newEndSample=row['endSample'], pcmSHA256=hashlib.sha256(segment).hexdigest(), exact=True))
    assert len(checks) == 20
    assert current[:FIRST * SPF * 2] == info['source'][:FIRST * SPF * 2]
    assert current[(FIRST + info['newBlockFrames']) * SPF * 2:] == info['source'][LAST * SPF * 2:]
    return dict(frames=info['frames'], samples=info['samples'], seconds=info['frames'] / FPS,
                deltaFrames=info['deltaFrames'], newBlockFrames=info['newBlockFrames'],
                audioSHA256=sha(D / 'voice.wav'), baselineVoiceSHA256=BASE_SHA,
                originalRangeFrames=[FIRST, LAST], originalRangeConvention='half-open',
                originalPrefixPCMExact=True, originalSuffixPCMExact=True, all20ReusedSentencePCMExact=True,
                reusedSentences=checks, originalGenerationArtifactsByteExact=True,
                noWholeTrackNormalization=True, ASRPerformed=False, semanticListeningPerformed=False)


def compose():
    result, rows, picks, info = expected()
    retained_assets = {r['id']: sha(D / 'voice/sentences' / (r['id'] + '.wav'))
                       for r in rows if r['id'] not in info['new']}
    # Persist actual selected assets where the shared freezer expects them.
    for path in (MINI / 'voice/takes').iterdir():
        destination = D / 'voice/takes' / path.name
        if destination.exists():
            assert destination.read_bytes() == path.read_bytes(), destination
        else:
            destination.write_bytes(path.read_bytes())
    write_pcm(D / 'voice.wav', result)
    for row in rows:
        write_pcm(D / 'voice/sentences' / (row['id'] + '.wav'),
                  result[row['startSample'] * 2:row['endSample'] * 2])
    assert all(sha(D / 'voice/sentences' / (sid + '.wav')) == digest
               for sid, digest in retained_assets.items()), 'A reused sentence WAV asset changed'
    signal = np.frombuffer(result, '<i2').astype(np.float32) / 32767
    splices = [dict(pair=a['id'] + '->' + b['id'],
                    lufs_diff=round(abs(a['lufs'] - b['lufs']), 2),
                    gapFrames=round((b['startSample'] - a['endSample']) / SPF, 2))
               for a, b in zip(rows, rows[1:])]
    summary = dict(frames=info['frames'], samples=info['samples'], seconds=info['frames'] / FPS,
                   sha=sha(D / 'voice.wav'), track_lufs=lufs(signal), peak=float(np.abs(signal).max()),
                   extraAfter={}, max_neighbour_lufs_diff=max(r['lufs_diff'] for r in splices),
                   inner_dropouts=[r['id'] for r in rows if r['maxInnerSilenceS'] >= .5],
                   assemblyMethod='Exact baseline prefix/suffix plus only four sentences from shared mini build; no full-track DSP.')
    summary['max_join_sample_jump'] = max(float(np.abs(np.diff(signal[max(0, sample-480):sample+480])).max())
                                         for row in rows for sample in [row['startSample'], row['endSample']])
    save(D / 'voice/build.json', dict(summary=summary, sentences=rows, splices=splices))
    save(D / 'voice/picks.json', picks)
    proof = verify()
    proof.update(checkedAtUTC=datetime.now(timezone.utc).isoformat(), wrapper='build_binary_voice.py',
                 mini='voice/binary-mini', miniAudioSHA256=sha(MINI / 'voice.wav'),
                 currentScriptSHA256=sha(D / 'script.md'), currentPlanSHA256=sha(D / 'plan.json'),
                 all20ReusedSentenceWAVFilesByteExact=True,
                 reusedSentenceWAVFileSHA256s=retained_assets,
                 originalGeneration='voice/input-provenance.json',
                 newGeneration='voice/binary-input-provenance.json')
    save(D / 'voice/binary-opening-composition.json', proof)
    print(json.dumps({k: v for k, v in proof.items() if k != 'reusedSentences'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--compose-only', action='store_true')
    args = parser.parse_args()
    assert not (args.verify and args.compose_only)
    if args.verify:
        report = verify()
        print(json.dumps({k: v for k, v in report.items() if k != 'reusedSentences'}, ensure_ascii=False))
    else:
        if not args.compose_only:
            subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/build.py'),
                            '--dir', str(MINI)], check=True)
        compose()
