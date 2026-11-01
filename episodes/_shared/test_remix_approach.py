#!/usr/bin/env python3
"""Real synthetic-media regression for remix_approach; never renders an episode.

All movies are tiny solid-color 1080p/30fps fixtures. Pixel colors, frame order,
PTS and the decoded new voice provide independent output oracles. No production
input is modified. FFmpeg/ffprobe and the Python standard library are required.
"""
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave

TOOL = Path(__file__).with_name('remix_approach.py').resolve()


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(*args, ok=True):
    result = subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)
    if ok and result.returncode:
        raise AssertionError(result.stderr)
    if not ok and not result.returncode:
        raise AssertionError('An invalid input was unexpectedly accepted')
    return result


def movie(path, colors, old_music=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    command = ['ffmpeg', '-v', 'error', '-y']
    for color, frames in colors:
        command += ['-f', 'lavfi', '-i', f'color=c={color}:s=1920x1080:r=30:d={frames / 30:.10f}']
    if old_music:
        command += ['-f', 'lavfi', '-i', f'sine=frequency=220:sample_rate=48000:duration={sum(n for _, n in colors) / 30:.10f}']
    command += ['-filter_complex_threads', '1', '-filter_complex', ''.join(f'[{i}:v]' for i in range(len(colors))) + f'concat=n={len(colors)}:v=1:a=0[v]', '-map', '[v]']
    if old_music:
        command += ['-map', f'{len(colors)}:a', '-c:a', 'aac']
    command += ['-frames:v', str(sum(n for _, n in colors)), '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p', '-video_track_timescale', '30000', str(path)]
    subprocess.run(command, check=True)


def wav(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(48000)
        stream.writeframes(samples.tobytes())


def tone(frequency, length=4800):
    return array('h', (int(6000 * math.sin(2 * math.pi * frequency * i / 48000) * min(1, i / 100, (length - 1 - i) / 100)) for i in range(length)))


def fixture(directory, tail=0):
    episode = directory / 'episode'; before = episode / 'revisions/approach-first/before'; baseline = episode / 'remotion/out/approach-baseline'
    (episode / 'remotion/src').mkdir(parents=True); (baseline / 'src').mkdir(parents=True)
    (episode / 'remotion/src/Main.tsx').write_text('// synthetic: changed opener and new branch; body branch retained\n')
    (baseline / 'src/Main.tsx').write_text('// synthetic: original body branch\n')
    (episode / 'solution.py').write_text('class Solution:\n    def solve(self):\n        return 1\n')
    dump(episode / 'solution.json', (episode / 'solution.py').read_text().splitlines())
    code_hashes = {name: digest(episode / name) for name in ['solution.py', 'solution.json']}
    old_spec = [('problem', 12, 'old problem', 440), ('body', 12, 'same body', 550), ('closing', 12, 'old closing', 660)]
    new_spec = [('problem', 12, 'new problem', 880), ('inserted', 12, 'new reasoning', 990), ('body', 12 + tail, 'same body', 550), ('closing', 12, 'new closing', 1100)]

    def version(spec, is_old):
        plan, shots, sentences = [], [], []; cursor = 0; voice = array('h', [0]) * ((sum(row[1] for row in spec) + 150) * 1600)
        take_hashes = {}
        for index, (slug, duration, text, frequency) in enumerate(spec, 1):
            sid = f'{index:02d}'; shot_name = sid + '-' + slug
            plan.append(dict(id=sid, slug=slug, visualType=slug))
            local_voice = []; subs = []
            for number, local in [(1, 1), (2, 6)]:
                sentence_id = f'{shot_name}-{number}'; words = text + str(number) + '。'; take = episode / 'voice/takes' / (sentence_id + '-a.wav')
                samples = tone(frequency + number)
                # Old/new same-body IDs differ, but the underlying take bytes do not.
                wav(take, samples); take_hashes[str(take.relative_to(episode))] = digest(take)
                start = (cursor + local) * 1600; voice[start:start + len(samples)] = samples
                row = dict(id=sentence_id, shot=shot_name, take='a', text=words, tts=words + '好。', startFrame=cursor + local, endFrame=cursor + local + 3)
                sentences.append(row)
                local_voice.append(dict(id=sentence_id, localStart=local, localEnd=local + 3, wavStart=cursor + local, wavEnd=cursor + local + 3))
                subs.append(dict(text=words, **{'from': 0 if number == 1 else 6}, to=5 if number == 1 else duration - 1, duration=6 if number == 1 else duration - 6))
            shots.append(dict(id=sid, visualType=slug, **{'from': cursor}, durationInFrames=duration,
                              narration=''.join(item['text'] for item in subs), subtitles=subs, voice=local_voice,
                              cueFrames=dict(sentences=[1, 6], labels={}), elements=[]))
            cursor += duration
        shots[-1]['durationInFrames'] += 150; shots[-1]['codeCardFrom'] = spec[-1][1]
        sb = dict(meta=dict(fps=30, width=1920, height=1080, durationInFrames=cursor + 150,
                           unvoicedEndCard=dict(kind='full-python-solution', **{'from': cursor}, durationInFrames=150,
                                               codeSource='solution.py', displaySource='solution.json',
                                               codeSourceSha256=code_hashes['solution.py'], displaySourceSha256=code_hashes['solution.json'])),
                  scenes=[dict(shots=shots)])
        voice_path = baseline / 'voice.wav' if is_old else episode / 'voice.wav'; wav(voice_path, voice)
        build = dict(summary=dict(sha=digest(voice_path)), sentences=sentences)
        if is_old:
            dump(before / 'plan.json', plan); dump(before / 'voice/build.json', build); dump(baseline / 'storyboard.json', sb)
        else:
            dump(episode / 'plan.json', plan); dump(episode / 'voice/build.json', build); dump(episode / 'storyboard.json', sb)
        return take_hashes, sb

    old_takes, old_sb = version(old_spec, True)
    new_takes, new_sb = version(new_spec, False)
    old_manifest = dict(old_takes)
    for name, path in [('plan.json', before / 'plan.json'), ('voice/build.json', before / 'voice/build.json'),
                       ('storyboard.json', baseline / 'storyboard.json'), ('voice.wav', baseline / 'voice.wav'),
                       ('remotion/src/Main.tsx', baseline / 'src/Main.tsx')]:
        old_manifest[name] = digest(path)
    dump(before / 'source-sha256.json', old_manifest)
    movie(baseline / 'video.mp4', [('red', 12), ('green', 12), ('blue', 12), ('white', 150)], old_music=True)
    dump(episode / 'revisions/approach-first/baseline.json', dict(
        sha256={name: digest(baseline / name) for name in ['video.mp4', 'storyboard.json', 'voice.wav']},
        sourceManifestSha256=digest(before / 'source-sha256.json'), mainSourceSha256=digest(baseline / 'src/Main.tsx')))
    dump(episode / 'source-sha256.json', new_takes)
    return episode


def plan(episode, *extra, ok=True):
    return call(episode, '--plan-only', '--render-shots', '01,02,04', *extra, ok=ok)


def finish(episode, *extra, wrong_clip=False, approve_tail=False):
    plan(episode, *extra)
    saved = json.loads((episode / 'approach-remix-plan.json').read_text())
    for clip in saved['clips']:
        if clip['key'] == '01-02':
            colors = [('yellow', 12), ('cyan', 12)]
        else:
            colors = [('magenta', clip['frames'] + (1 if wrong_clip else 0))]
        movie(episode / clip['path'], colors)
    review = saved['reviewTemplate']; review['reviewedBy'] = 'Synthetic regression author'
    review['notes'] = 'Synthetic fixed-color scene definitions are the explicit visual oracle; real episode equivalence is not claimed.'
    if approve_tail:
        review['approvedTailFrameAdjustments'] = {'body': 1}
    dump(episode / saved['visualReview'], review)
    plan(episode, *extra)
    saved = json.loads((episode / 'approach-remix-plan.json').read_text())
    frozen = dict(saved['inputSHA256']); frozen['approach-remix-plan.json'] = digest(episode / 'approach-remix-plan.json')
    dump(episode / 'source-sha256.json', frozen)
    return saved


def pixels(path, frames):
    expression = '+'.join(f'eq(n\\,{frame})' for frame in frames)
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'select={expression},scale=1:1', '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return [tuple(raw[index:index + 3]) for index in range(0, len(raw), 3)]


class RemixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='approach-remix-regression-')
        self.directory = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_insert_change_multiple_intervals_boundaries_pts_voice_and_card(self):
        episode = fixture(self.directory)
        plan(episode)
        initial = json.loads((episode / 'approach-remix-plan.json').read_text())
        self.assertEqual([clip['frameRange'] for clip in initial['clips']], [[0, 23], [36, 47]])
        self.assertTrue(all(clip['sha256'] is None for clip in initial['clips']))
        final = finish(episode)
        plan_sha = digest(episode / 'approach-remix-plan.json')
        call(episode, '--run')
        self.assertEqual(plan_sha, digest(episode / 'approach-remix-plan.json'), '--run must never rewrite the plan')
        output = episode / final['output']; sample_frames = [0, 11, 12, 23, 24, 35, 36, 47, 48, 122, 197]
        expected = [(255, 255, 0)] * 2 + [(0, 255, 255)] * 2 + [(0, 128, 0)] * 2 + [(255, 0, 255)] * 2 + [(255, 255, 255)] * 3
        actual = pixels(output, sample_frames)
        self.assertEqual(len(actual), len(expected))
        for color, wanted in zip(actual, expected):
            self.assertLessEqual(max(abs(a - b) for a, b in zip(color, wanted)), 12)
        result = json.loads((episode / 'approach-remix-result.json').read_text())
        self.assertEqual(result['frames'], 198); self.assertAlmostEqual(result['lastPTS'], 197 / 30)
        decoded = array('f'); decoded.frombytes(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(output), '-map', '0:a:0', '-ac', '1', '-ar', '48000', '-f', 'f32le', '-']))
        with wave.open(str(episode / 'voice.wav')) as audio:
            reference = array('h'); reference.frombytes(audio.readframes(audio.getnframes()))
        length = 48 * 1600
        dot = sum(decoded[i] * reference[i] for i in range(length)); energy_a = sum(decoded[i] ** 2 for i in range(length)); energy_b = sum(reference[i] ** 2 for i in range(length))
        self.assertGreater(dot / math.sqrt(energy_a * energy_b), .98, 'Output audio must be the new voice, not old mixed audio')
        self.assertLess(max(abs(value) for value in decoded[50 * 1600:190 * 1600]), .001, 'The card must not inherit old background music')

    def test_rejects_wrong_mapping_and_selected_take(self):
        episode = fixture(self.directory)
        changes = episode / 'bad-map.json'; dump(changes, dict(reuseMap={'body': 'problem'}))
        result = plan(episode, '--changes', changes, ok=False)
        self.assertIn('visualType differs', result.stderr)
        take = episode / 'voice/takes/03-body-1-a.wav'
        wav(take, tone(1250))
        result = plan(episode, ok=False)
        self.assertIn('takeSha256 differs', result.stderr)

    def test_rejects_wrong_clip_frame_count(self):
        episode = fixture(self.directory)
        finish(episode, wrong_clip=True)
        result = call(episode, '--run', ok=False)
        self.assertIn('frame count must be 12, got 13', result.stderr)
        self.assertFalse((episode / 'remotion/out/voice-approach.mp4').exists())

    def test_explicit_one_frame_tail_hold(self):
        episode = fixture(self.directory, tail=1)
        self.assertIn('body length differs by 1', plan(episode, ok=False).stderr)
        finish(episode, '--allow-tail-frame-adjustment', approve_tail=True)
        call(episode, '--run')
        result = json.loads((episode / 'approach-remix-result.json').read_text())
        self.assertEqual(result['frames'], 199)
        self.assertEqual(next(item for item in result['segments'] if item.get('slug') == 'body')['proof']['tailFrameAdjustment'], 1)
        actual = pixels(episode / result['output'], [35, 36, 37, 48, 49, 198])
        expected = [(0, 128, 0), (0, 128, 0), (255, 0, 255), (255, 0, 255), (255, 255, 255), (255, 255, 255)]
        self.assertEqual(len(actual), len(expected))
        for color, wanted in zip(actual, expected):
            self.assertLessEqual(max(abs(a - b) for a, b in zip(color, wanted)), 12)

    def test_rejects_mutation_or_unreviewed_reuse_and_protects_inputs(self):
        episode = fixture(self.directory)
        self.assertIn('Output must not overwrite', plan(episode, '--output', episode / 'voice.wav', ok=False).stderr)
        note = episode / 'notes.json'; dump(note, {'meaning': 'an unrelated frozen input'})
        frozen = json.loads((episode / 'source-sha256.json').read_text()); frozen['notes.json'] = digest(note); dump(episode / 'source-sha256.json', frozen)
        self.assertIn('different frozen input', plan(episode, '--plan', note, ok=False).stderr)
        legacy = episode / 'remotion/out/legacy-intro.mp4'; shutil.copyfile(episode / 'remotion/out/approach-baseline/video.mp4', legacy)
        frozen['remotion/out/legacy-intro.mp4'] = digest(legacy); dump(episode / 'source-sha256.json', frozen)
        changes = episode / 'bad-output.json'; dump(changes, dict(clipPaths={'01-02': 'remotion/out/legacy-intro.mp4'}))
        self.assertIn('another frozen input', plan(episode, '--changes', changes, ok=False).stderr)
        finish(episode)
        review_path = episode / 'revisions/approach-first/visual-reuse-review.json'
        review = json.loads(review_path.read_text()); review['approvedReuseSlugs'] = ['body']; dump(review_path, review)
        # Bind the deliberately incomplete review, so rejection tests the review
        # contract rather than merely finding an outdated frozen hash.
        plan(episode)
        saved = json.loads((episode / 'approach-remix-plan.json').read_text()); frozen = dict(saved['inputSHA256']); frozen['approach-remix-plan.json'] = digest(episode / 'approach-remix-plan.json'); dump(episode / 'source-sha256.json', frozen)
        self.assertIn('requires explicit visual approval', call(episode, '--run', ok=False).stderr)
        review['approvedReuseSlugs'] = ['body', 'code-card']; dump(review_path, review); plan(episode)
        saved = json.loads((episode / 'approach-remix-plan.json').read_text()); frozen = dict(saved['inputSHA256']); frozen['approach-remix-plan.json'] = digest(episode / 'approach-remix-plan.json'); dump(episode / 'source-sha256.json', frozen)
        take = episode / 'voice/takes/03-body-1-a.wav'; wav(take, tone(777))
        self.assertIn('Current frozen input differs', call(episode, '--run', ok=False).stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
