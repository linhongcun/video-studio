#!/usr/bin/env python3
"""Read-only text, selected-take, PCM and signal audit; never recognizes speech."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import sys
import traceback

sys.dont_write_bytecode = True
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def longest_quiet(audio):
    windows = np.abs(audio[:len(audio) // 480 * 480]).reshape(-1, 480)
    quiet = windows.max(axis=1) <= .005
    edges = np.flatnonzero(np.diff(np.r_[False, quiet, False].astype(np.int8)))
    return float(np.max(edges[1::2] - edges[::2], initial=0)) / 100


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('production', type=Path)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--approval', type=Path, required=True,
                    help='Actual current editorial receipt; script/narration hashes are verified.')
    ap.add_argument('--receipt', type=Path, action='append', default=[],
                    help='Optional actual production receipts; no historical schema is presumed.')
    args = ap.parse_args()
    d, out = args.production.resolve(), args.out_dir.resolve()
    assert out.is_relative_to(HERE) and out != HERE, 'Reports belong in a new child of this QA archive'
    assert not out.exists(), 'Preserve previous attempts; choose a fresh --out-dir'
    out.mkdir(parents=True)
    report = {'kind': 'independent-readonly-voice-signal-audit', 'production': str(d),
              'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'reviewerScriptSHA256': sha(__file__), 'machinePass': False,
              'semanticListeningPerformed': False, 'asrPerformed': False,
              'inputSHA256': {}, 'sentences': [], 'flags': [], 'checks': []}

    def save():
        (out / 'voice-signal-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def track(path):
        path = Path(path).resolve()
        assert path.is_file(), f'Missing actual input: {path}'
        report['inputSHA256'][str(path)] = sha(path)
        return path

    def check(label, condition):
        report['checks'].append({'check': label, 'passed': bool(condition)})
        assert condition, label

    save()
    try:
        sys.path.insert(0, str(ROOT / 'episodes/_shared'))
        from episode_paths import episode_slug, production_directory
        check('actual production directory', d.is_relative_to(production_directory(episode_slug(d), root=ROOT)))
        shared = track(ROOT / 'episodes/_shared/voice/common.py')
        module_spec = importlib.util.spec_from_file_location('readonly_actual_voice_common', shared)
        common = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(common)
        required = ['script.md', 'voice.wav', 'voice/build.json', 'voice/sents.json',
                    'voice/params.json', 'words.json', 'storyboard.json', 'remotion/public/audio/voice.wav']
        for name in required:
            track(d / name)
        picks_path = d / 'voice/picks.json'
        picks = read(track(picks_path)) if picks_path.exists() else {}
        params = common.load_params(d / 'voice')
        approval = read(track(args.approval))
        narration = ''.join(re.findall(r'^旁白：(.*)$', (d / 'script.md').read_text(), re.M))
        narration_sha = hashlib.sha256(narration.encode()).hexdigest()
        check('current editorial script identity', approval['scriptSHA256'] == sha(d / 'script.md'))
        check('current editorial narration identity', approval['narrationSHA256'] == narration_sha)
        receipts = []
        for receipt_path in args.receipt:
            receipt_path = track(receipt_path)
            receipt = read(receipt_path)
            receipts.append({'path': str(receipt_path), 'sha256': sha(receipt_path), 'recordedStatus': receipt.get('status')})
            for key, expected in [('scriptSHA256', sha(d / 'script.md')), ('narrationSHA256', narration_sha),
                                  ('voiceSHA256', sha(d / 'voice.wav')), ('voiceParametersSHA256', sha(d / 'voice/params.json'))]:
                if key in receipt:
                    check('supplied receipt current ' + key, receipt[key] == expected)
        report['productionReceipts'] = receipts
        sents, build = read(d / 'voice/sents.json'), read(d / 'voice/build.json')
        check('prepared text exactly matches narration', ''.join(s['text'] for s in sents) == narration)
        check('sentence count matches build and editorial receipt', len(sents) == len(build['sentences']) == approval['sentences'])
        check('public voice is byte-identical', sha(d / 'voice.wav') == sha(d / 'remotion/public/audio/voice.wav'))
        audio, sr = sf.read(d / 'voice.wav')
        check('actual mono 48kHz track', sr == 48000 and audio.ndim == 1)
        check('actual samples/frames agree', len(audio) == build['summary']['samples'] == build['summary']['frames'] * 1600)
        check('build binds actual voice bytes', sha(d / 'voice.wav') == build['summary']['sha'])
        check('selected picks name known sentences', set(picks).issubset({s['id'] for s in sents}))
        previous_end = 0
        for sent, row in zip(sents, build['sentences']):
            sid = sent['id']
            check(sid + ': text/id/tts match build', all(sent[k] == row[k] for k in ['id', 'text', 'tts']))
            check(sid + ': selected take matches picks', row['take'] == picks.get(sid, 'a'))
            take = track(d / 'voice/takes' / f"{sid}-{row['take']}.wav")
            request = track(take.with_suffix('.txt.json'))
            check(sid + ': selected exact TTS request text', read(request) == sent['tts'])
            raw = common.load(str(take))
            cut, tail = common.cut(raw)
            nz = np.flatnonzero(np.abs(cut) > 1e-4)
            check(sid + ': selected take contains voiced cut', len(nz) > 0)
            trimmed = cut[:nz[-1] + 1]
            sentence_file = track(d / 'voice/sentences' / f'{sid}.wav')
            actual, sentence_sr = sf.read(sentence_file)
            start, end = row['startSample'], row['endSample']
            check(sid + ': valid ordered sample interval', type(start) is int and type(end) is int and previous_end <= start < end <= len(audio))
            check(sid + ': sample-exact selected sentence in track', sentence_sr == 48000 and np.array_equal(audio[start:end], actual))
            check(sid + ': selected source cut has exact sample length', len(trimmed) == len(actual))
            check(sid + ': previous silent gap is exact zero', np.max(np.abs(audio[previous_end:start]), initial=0) == 0)
            previous_end = end
            # Gain normalization and true-peak limiting alter amplitude. Correlation
            # screens source identity without pretending those samples are equal.
            denom = float(np.linalg.norm(trimmed.astype(float)) * np.linalg.norm(actual))
            correlation = float(np.dot(trimmed.astype(float), actual) / denom) if denom else 0.0
            check(sid + ': selected take signal corresponds to actual sentence', correlation >= .98)
            check(sid + ': recorded trailing cut duration', round(tail, 2) == row['tailCut'])
            quiet = longest_quiet(actual)
            voiced = np.flatnonzero(np.abs(trimmed) > .01)
            check(sid + ': retained source speech exceeds cut threshold', len(voiced) > 0)
            peak = float(np.max(np.abs(raw)))
            clipped = int(np.sum(np.abs(raw) >= .9999))
            flags = []
            if tail < .25:
                flags.append('discarded final take tail shorter than250ms')
            if max(quiet, row['maxInnerSilenceS']) >= .5:
                flags.append('sentence contains at least500ms low-amplitude span')
            if clipped:
                flags.append('selected raw take contains near-full-scale samples')
            if flags:
                report['flags'].append({'sentence': sid, 'selectedTake': row['take'], 'flags': flags})
            report['sentences'].append({'id': sid, 'take': row['take'], 'requestTextSHA256': sha(request),
                'takeSHA256': sha(take), 'sentenceSHA256': sha(sentence_file),
                'sourceCutToActualCorrelation': correlation, 'actualSampleInterval': [start, end],
                'discardedTailSeconds': float(tail), 'cutLeadingAbove01Seconds': int(voiced[0]) / 48000,
                'cutTrailingBelow01Seconds': (len(trimmed) - 1 - int(voiced[-1])) / 48000,
                'rawPeak': peak, 'rawNearFullScaleSamples': clipped,
                'actualInt16MaxQuietSeconds': quiet, 'buildFloatMaxQuietSeconds': row['maxInnerSilenceS'],
                'quietWindowThresholdDifference': abs(quiet - row['maxInnerSilenceS']) > 1e-9,
                'flags': flags})
            save()
        check('actual zero-valued trailing silence', np.max(np.abs(audio[previous_end:]), initial=0) == 0)
        words, board = read(d / 'words.json'), read(d / 'storyboard.json')
        check('timing binds actual script and voice', words['audioSha256'] == sha(d / 'voice.wav') and words['scriptSha256'] == sha(d / 'script.md'))
        check('timing/build body frame identity', words['durationFrames'] == board['meta']['durationInFrames'] == build['summary']['frames'])
        check('timing declares no invented word alignment', words.get('asrModel') == 'none' and words.get('wordAlignment') is False)
        loudness = common.lufs(audio.astype(np.float32))
        true_peak = float(20 * np.log10(np.max(np.abs(resample_poly(audio, 4, 1)))))
        check('independently measured loudness matches build', abs(loudness - build['summary']['track_lufs']) <= .1)
        if abs(loudness - params['trackLufs']) > .3:
            report['flags'].append({'track': 'voice.wav', 'flags': ['track loudness differs from configured target by more than0.3LU']})
        if true_peak > params['tpStopDb'] + .15:
            report['flags'].append({'track': 'voice.wav', 'flags': ['actual oversampled peak exceeds configured stop threshold']})
        report.update(trackLUFS=loudness, truePeakDbTP=true_peak, bodyFrames=build['summary']['frames'],
                      sentenceCount=len(sents), canonicalNarrationSHA256=narration_sha, machinePass=True,
                      status='signal-flags-require-review' if report['flags'] else 'pass-signal-screening')
        report['candidateGuidance'] = {
            'automaticRegenerationPerformed': False,
            'scope': 'Signals flag risks, not a diagnosis of a wrong or missing word.',
            'ifNeeded': 'Preserve original takes/track/receipts. Request at most two bounded candidates for flagged sentence IDs using exactly the same approved TTS request text; compare candidates before choosing. Rebuild with shared tools and rerun current text/PCM audit; do not speed audio up or silently rewrite narration.'}
    except Exception as exc:
        report.update(status='failed-structural-or-provenance-check', failure={'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()})
    finally:
        changed = [p for p, value in report['inputSHA256'].items() if not Path(p).is_file() or sha(p) != value]
        report['sourceInputsUnchanged'] = not changed
        if changed:
            report.update(machinePass=False, status='inputs-changed-during-review', changedInputs=changed)
        report['finishedAtUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        report['signalPass'] = report['machinePass'] and not report['flags'] and not changed
        report['limitations'] = ['No ASR, phoneme/word recognition, full semantic listening or tone correctness claim.',
            'Shared cut/loudness helpers are used read-only. Float build and quantized PCM quiet-window results may differ at a threshold.',
            'PNG, dynamic, encoded media and actual viewer comprehension are separate reviews.']
        save()
    print(json.dumps({'status': report['status'], 'machinePass': report['machinePass'], 'flags': report['flags'], 'report': str(out / 'voice-signal-review.json')}, ensure_ascii=False))
    return 0 if report['machinePass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
