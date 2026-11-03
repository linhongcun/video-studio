#!/usr/bin/env python3
"""Read-only source/cut/PCM audit; deliberately no speech-recognition claims."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import sys
import wave

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
import common


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--takes-only', action='store_true')
    args = parser.parse_args()
    voice = D / 'voice'
    sents = read(voice / 'sents.json')
    picks = read(voice / 'picks.json')
    assert len(sents) == 28 and len({s['id'] for s in sents}) == 28
    narrations = re.findall(r'^旁白：(.*)$', (D / 'script.md').read_text(), re.M)
    assert ''.join(s['text'] for s in sents) == ''.join(narrations)
    provenance = read(voice / 'script-narration-sha256.json')
    assert provenance['scriptSHA256'] == sha(D / 'script.md')
    assert provenance['narrationSHA256'] == hashlib.sha256(''.join(narrations).encode()).hexdigest()
    assert provenance['sentenceCount'] == 28
    stable_files = [D / 'script.md', voice / 'sents.json', voice / 'params.json', voice / 'picks.json']
    if not args.takes_only:
        stable_files += [voice / 'build.json', D / 'voice.wav', D / 'remotion/public/audio/voice.wav', D / 'words.json', D / 'storyboard.json', D / 'plan.json']
    before = {str(p.relative_to(ROOT)): sha(p) for p in stable_files}
    rows, flags = [], []
    for sent in sents:
        take_name = picks.get(sent['id'], 'a')
        take = voice / 'takes' / f"{sent['id']}-{take_name}.wav"
        raw_path = take.with_name(take.stem + '.raw.wav')
        text_path = take.with_suffix('.txt.json')
        assert take.is_file() and raw_path.is_file() and text_path.is_file()
        assert read(text_path) == sent['tts']
        assert sent['tts'] == sent['text'] + '好。', 'Check any deliberate TTS-only substitutions explicitly'
        converted, sr = sf.read(take)
        assert sr == 48000 and converted.ndim == 1
        loaded = common.load(str(take))
        cut, tail = common.cut(loaded)
        active = np.flatnonzero(np.abs(cut) > .01)
        assert len(active), f"Empty selected sentence: {sent['id']}"
        leading = float(active[0] / sr)
        trailing = float((len(cut) - 1 - active[-1]) / sr)
        # This is a signal screen at the existing shared build's threshold,
        # not a copied clipping/onset implementation or a phonetic judgment.
        silence_frames = np.max(np.abs(cut[:len(cut)//480*480].reshape(-1,480)),axis=1) <= .005
        runs = re.findall('1+', ''.join('1' if b else '0' for b in silence_frames))
        inner = max(map(len, runs), default=0) / 100
        clipped = int(np.sum(np.abs(loaded) >= .9999))
        risks = []
        if tail < .25:
            risks.append('throwaway-tail duration below250ms')
        if inner >= .5:
            risks.append('source sentence contains silence at least500ms')
        if clipped:
            risks.append('selected source contains clipped samples')
        if risks:
            flags.append({'id': sent['id'], 'flags': risks})
        rows.append({'id': sent['id'], 'take': take_name,
                     'takeSHA256': sha(take), 'rawSHA256': sha(raw_path),
                     'requestTextSHA256': sha(text_path), 'requestMatchesSents': True,
                     'sourceFrames': len(converted), 'sourceRate': sr,
                     'sharedCutSamples': len(cut), 'tailAfterLastGapSeconds': round(tail, 6),
                     'cutLeadingAbove01Seconds': round(leading, 6),
                     'cutTrailingBelow01Seconds': round(trailing, 6),
                     'cutMaxSilenceAt005Seconds': inner,
                     'sourcePeak': float(np.max(np.abs(loaded))),
                     'sourceClippedSamples': clipped, 'flags': risks})
    report = {'checkedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'executor': 'Codex independent voice QA agent',
              'stage': 'selected-takes-only' if args.takes_only else 'selected-takes-and-whole-track',
              'status': 'signal-flags-require-review' if flags else 'passed-signal-screening',
              'selectedTakes': len(rows), 'exactNarrationAndRequestText': True,
              'flags': flags, 'sentences': rows,
              'sharedImplementationSHA256': {str(p.relative_to(ROOT)): sha(p) for p in
                  [ROOT/'episodes/_shared/voice/common.py', ROOT/'episodes/_shared/voice/build.py',
                   ROOT/'episodes/_shared/voice/gen.py', ROOT/'episodes/_shared/tts/mimo_say.py']},
              'readOnlyInputs': before,
              'limitations': ['The existing shared common.cut is imported unchanged, not copied or replaced.',
                  'Request text, source waveform, last-gap cut boundaries and signal flags are checked. No ASR, phoneme alignment or full human semantic listening was performed.',
                  'A long-pause flag is a review cue and does not by itself establish a dropout or warrant requesting a new non-deterministic TTS take.',
                  'A clean signal screen does not establish all words and tones are correct.']}
    rejected = read(voice/'candidate-a-tail-flag.json')
    candidate = voice/'takes/01-hook-1-a.wav'
    candidate_cut, candidate_tail = common.cut(common.load(str(candidate)))
    assert sha(candidate) == rejected['sourceSHA256']
    assert len(candidate_cut) == rejected['sharedCutSamples']
    assert abs(candidate_tail-rejected['tailAfterLastGapSeconds']) < 1e-8
    assert picks['01-hook-1'] == 'b'
    report['retainedRejectedCandidate'] = {
        'id':'01-hook-1','candidate':'a','sourceSHA256':sha(candidate),
        'sharedCutSamples':len(candidate_cut),'tailAfterLastGapSeconds':candidate_tail,
        'selectedInstead':'b','recordMatchesRecomputedSignal':True,
        'scope':'The short throwaway-tail flag and retained original source reproduce. This does not establish a spoken-word error.'}
    if not args.takes_only:
        build = read(voice / 'build.json')
        audio, sr = sf.read(D / 'voice.wav')
        assert sr == 48000 and audio.ndim == 1
        assert len(audio) == build['summary']['samples'] == build['summary']['frames'] * 1600
        assert sha(D / 'voice.wav') == build['summary']['sha']
        assert (D / 'voice.wav').read_bytes() == (D / 'remotion/public/audio/voice.wav').read_bytes()
        assert len(build['sentences']) == len(sents)
        for sent, row, selected in zip(sents, build['sentences'], rows):
            assert (sent['id'], sent['text'], sent['tts']) == (row['id'], row['text'], row['tts'])
            assert row['take'] == selected['take']
            sentence, rate = sf.read(voice / 'sentences' / f"{sent['id']}.wav")
            assert rate == 48000 and np.array_equal(audio[row['startSample']:row['endSample']], sentence)
            assert abs(row['tailCut'] - selected['tailAfterLastGapSeconds']) <= .0051
            selected['selectedSentenceMatchesWholeTrackPCM'] = True
            selected['builtMaxInnerSilenceSeconds'] = row['maxInnerSilenceS']
        gaps = [(0,build['sentences'][0]['startSample'])] + [
            (a['endSample'],b['startSample']) for a,b in zip(build['sentences'],build['sentences'][1:])
        ] + [(build['sentences'][-1]['endSample'],len(audio))]
        assert all(np.max(np.abs(audio[a:z]),initial=0) == 0 for a,z in gaps)
        report.update(voiceSHA256=sha(D/'voice.wav'), samples=len(audio), frames=build['summary']['frames'],
                      publicVoiceCopyByteIdentical=True, selectedSentencePCMMatchesWholeTrack=True,
                      silentGapPCMZero=True, wholeTrackLUFSFromActualSharedBuild=build['summary']['track_lufs'],
                      independentMeasuredTruePeakDbTP=float(20*np.log10(np.max(np.abs(resample_poly(audio,4,1))))),
                      sharedBuildFlags=build['summary']['inner_dropouts'],
                      sourceBuildSHA256=sha(voice/'build.json'))
        words, board, plan = read(D/'words.json'), read(D/'storyboard.json'), read(D/'plan.json')
        assert words['scriptSha256'] == sha(D/'script.md') and words['audioSha256'] == sha(D/'voice.wav')
        assert words['asrModel'] == 'none' and words['wordAlignment'] is False
        assert len(words['shots']) == 14 and sum(len(s['sentences']) for s in words['shots']) == 28
        shots = [sh for scene in board['scenes'] for sh in scene['shots']]
        assert len(shots) == 14 and len(board['scenes']) == 4
        assert sum(sh['durationInFrames'] for sh in shots) == words['durationFrames'] == build['summary']['frames']
        assert not board['meta']['pendingAudio'] and not board['meta']['provisionalTiming']
        assert board['meta']['durationInFrames'] == board['meta']['finalVideoFrames'] == words['durationFrames']
        source_identity = f"voice.wav {sha(D/'voice.wav')[:8]} + words.json {sha(D/'words.json')[:8]} + script.md {sha(D/'script.md')[:8]}"
        assert board['meta']['timingSource'] == source_identity
        assert '28' in board['meta']['audioReview'] and 'first-name' not in board['meta']['audioReview']
        assert all(item['cues'] == [] for item in plan)
        assert sum(bool(el.get('cueText')) for sh in shots for el in sh['elements']) == 0
        sys.path.insert(0, str(ROOT/'episodes/_shared'))
        from onset_rule import Rule
        with wave.open(str(D/'voice.wav')) as raw_voice:
            assert (raw_voice.getframerate(), raw_voice.getnchannels(), raw_voice.getsampwidth()) == (48000,1,2)
            samples = np.frombuffer(raw_voice.readframes(raw_voice.getnframes()),'<i2').astype(float)/32767
        rule = Rule(samples,48000)
        acoustic = []
        cursor = 0
        for ws, sh in zip(words['shots'],shots):
            assert ws['startFrame'] == sh['from'] == cursor
            assert sh['timing']['source'] == source_identity
            assert ''.join(s['text'] for s in ws['sentences']) == sh['narration']
            assert [s['text'] for s in sh['subtitles']] == [s['text'] for s in ws['sentences']]
            previous_caption = -1
            for caption in sh['subtitles']:
                assert caption['from'] == previous_caption+1 and caption['duration'] == caption['to']-caption['from']+1
                previous_caption = caption['to']
            assert previous_caption == sh['durationInFrames']-1
            for index, sentence in enumerate(ws['sentences']):
                emitted = sh['voice'][index]
                assert emitted['id'] == sentence['id']
                assert abs(sh['from']+emitted['localStart']-emitted['wavStart']) < 1e-8
                assert emitted['wavStart'] == sentence['startFrame'] and emitted['wavEnd'] == sentence['endFrame']
                measured = rule.onset(sentence['startFrame'],min(sentence['endFrame'],sentence['startFrame']+30))
                assert measured['source'] == 'pause' and abs(measured['onset']-sentence['onsetFrame']) < 1e-8
                target = sh['from']+sh['cueFrames']['sentences'][index]
                delta = target-measured['onset']
                assert -6 <= delta <= 2
                acoustic.append({'id':sentence['id'],'source':'shared acoustic sentence Rule, independently re-executed',
                                 'onsetFrame':measured['onset'],'sentenceCueAbsoluteFrame':target,
                                 'cueMinusOnsetFrames':delta,'withinMinus6Plus2':True,
                                 'rule':measured['source']+'/'+measured['kind']})
            cursor += sh['durationInFrames']
        report.update(wordsSHA256=sha(D/'words.json'),storyboardSHA256=sha(D/'storyboard.json'),
                      scriptAndBoardTimeSourceIdentityExact=True,exactContinuousSentenceSubtitles=True,
                      declaredTermLabels=0,declaredTermLabelChecks='not applicable: none declared',
                      independentSentenceOnsets=acoustic,checkedSentenceOnsetCount=len(acoustic),
                      sentenceCueWindowMin=min(r['cueMinusOnsetFrames'] for r in acoustic),
                      sentenceCueWindowMax=max(r['cueMinusOnsetFrames'] for r in acoustic))
        report['limitations'].append('The 28 checked windows are acoustic sentence-start cues. plan.cues and declared term-label count are zero; no term-label timing, word ASR or interior alignment was claimed.')
    assert before == {str(p.relative_to(ROOT)): sha(p) for p in stable_files}, 'Inputs changed during read-only QA'
    destination = D / 'qa' / ('voice-selected-takes.json' if args.takes_only else 'voice-independent.json')
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'report':str(destination.relative_to(ROOT)), 'status':report['status'],
                      'sentences':len(rows), 'flags':flags,
                      'tailMinimum':min(r['tailAfterLastGapSeconds'] for r in rows),
                      'longestSourceSilenceSeconds':max(r['cutMaxSilenceAt005Seconds'] for r in rows)},ensure_ascii=False))


if __name__ == '__main__':
    main()
