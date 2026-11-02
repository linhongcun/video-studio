#!/usr/bin/env python3
"""Independent complete decode of three stopped-source previews; no rendering or production writes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

Q = Path(__file__).resolve().parent
D = Q.parents[1]
REM = D / 'remotion'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
report_path = Q / 'decode-independent.json'
assert not report_path.exists() and not (Q / 'extra').exists(), 'Preserve every prior raw attempt'
handoff_path = REM / 'actual-handoff.json'
handoff = read(handoff_path)
author_path = REM / 'qa-actual-clips/report.json'
author = read(author_path)
decoded_path = REM / 'qa-actual-clips/decode-review.json'
decoded = read(decoded_path)
assert handoff['productionInputsStopped'] and author['sourceUnchanged']
assert author['props'] == author['resolvedProps'] == {'showSubtitles': False, 'hideSubtitles': True}
for relative, digest in handoff['sourceHashes'].items():
    assert sha((REM / relative).resolve()) == digest
for relative, digest in author['sourceHashes'].items():
    assert digest == handoff['sourceHashes'][relative] == sha((REM / relative).resolve())
assert len(author['clips']) == 3 and sum(x['frames'] for x in author['clips']) == 1868
EXTRA = [[2473, 2474, 2545, 2546, 2695, 2696, 2926, 2927],
         [3595, 3596, 3661, 3662, 3783, 3784, 3887, 3888],
         [4295, 4296, 4369, 4370, 4386, 4436, 4487, 4622]]
started = datetime.now(timezone.utc).isoformat()


def execute(pair):
    index, clip = pair
    previous = decoded['clips'][index]
    video = REM / clip['file']
    assert sha(video) == clip['sha256'] == previous['sha256']
    assert clip['frames'] == clip['to'] - clip['from'] + 1 == previous['frames']
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(video)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    assert (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) == (1920, 1080, '30/1', clip['frames'])
    assert a['codec_name'] == 'aac' and int(a['sample_rate']) == 48000
    raw = Q / 'extra' / clip['name']
    raw.mkdir(parents=True)
    frames = EXTRA[index]
    local = [n - clip['from'] for n in frames]
    assert all(0 <= n < clip['frames'] for n in local)
    select = '+'.join(f'eq(n,{n})' for n in local)
    command = ['ffmpeg', '-v', 'error', '-xerror', '-err_detect', 'explode', '-threads', '2',
               '-filter_threads', '1', '-i', str(video), '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '/dev/null',
               '-map', '0:v:0', '-vf', f"select='{select}'", '-fps_mode', 'vfr', str(raw / 'n%03d.png')]
    run = subprocess.run(command, capture_output=True, text=True)
    (raw / 'decode.stderr.txt').write_text(run.stderr)
    attempt = {'command': command, 'exit': run.returncode, 'stderr': run.stderr, 'videoSHA256': clip['sha256']}
    (raw / 'decode-attempt.json').write_text(json.dumps(attempt, indent=2) + '\n')
    assert run.returncode == 0 and not run.stderr, 'Raw failure retained'
    generated = sorted(raw.glob('n*.png'))
    assert len(generated) == len(frames)
    extras = [{'globalN': n, 'localN': n - clip['from'], 'file': p.relative_to(D).as_posix(), 'sha256': sha(p)}
              for n, p in zip(frames, generated)]
    # Exact source/clip-identity reuse of author-produced integer-n samples.
    reused = []
    original_pngs = sorted((REM / 'qa-actual-clips' / (clip['name'] + '-decoded')).glob('f*.png'))
    expected_local = list(range(0, clip['frames'], 24))
    assert len(original_pngs) == len(expected_local) == previous['sequenceSamples']
    for n, p in zip(expected_local, original_pngs):
        assert Image.open(p).size == (1920, 1080)
        reused.append({'globalN': clip['from'] + n, 'localN': n, 'file': p.relative_to(D).as_posix(),
                       'sha256': sha(p), 'provenance': 'author decoded PNG from same exact clip SHA; retained integer-n command in named author decode report'})
    contacts = [{'file': (REM / p).relative_to(D).as_posix(), 'sha256': sha(REM / p),
                 'provenance': 'author contact sheet of exact same-clip every24-n samples'} for p in previous['contacts']]
    font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 20)
    sheet = Image.new('RGB', (1920, math.ceil(len(extras) / 2) * 576), '#181310')
    draw = ImageDraw.Draw(sheet)
    for i, sample in enumerate(extras):
        x, y = (i % 2) * 960, (i // 2) * 576
        sheet.paste(Image.open(D / sample['file']).convert('RGB').resize((960, 540)), (x, y))
        draw.text((x + 8, y + 544), f"global n={sample['globalN']} / local n={sample['localN']}", fill='white', font=font)
    contact = raw / 'key-neighbors.jpg'
    sheet.save(contact, quality=95)
    contacts.append({'file': contact.relative_to(D).as_posix(), 'sha256': sha(contact),
                     'provenance': 'fresh exact-n key neighbors from this independent complete video/AAC decode'})
    assert sha(video) == clip['sha256']
    return {'name': clip['name'], 'clip': video.relative_to(D).as_posix(), 'sha256': clip['sha256'],
            'globalRange': [clip['from'], clip['to']], 'frames': clip['frames'],
            'video': {k: v.get(k) for k in ['codec_name', 'width', 'height', 'r_frame_rate', 'nb_frames', 'pix_fmt', 'color_range', 'color_space']},
            'audio': {k: a.get(k) for k in ['codec_name', 'sample_rate', 'channels']},
            'independentCompleteVideoAndAACDecode': attempt, 'reusedEvery24IntegerNSamples': reused,
            'freshExactKeyNeighbors': extras, 'contactsForActualVisualReview': contacts}


with ThreadPoolExecutor(max_workers=3) as executor:
    clips = list(executor.map(execute, enumerate(author['clips'])))
assert all(sha((REM / rel).resolve()) == digest for rel, digest in handoff['sourceHashes'].items())
report = {'kind': 'independent-complete-three-preview-decode-and-bound-source-samples',
          'reviewer': '/root/mq_publication', 'startedAtUTC': started, 'finishedAtUTC': datetime.now(timezone.utc).isoformat(),
          'machinePass': True, 'visualReviewed': False, 'sourceHashesRelativeToRemotion': handoff['sourceHashes'],
          'handoff': {'file': handoff_path.relative_to(D).as_posix(), 'sha256': sha(handoff_path)},
          'authorClipReport': {'file': author_path.relative_to(D).as_posix(), 'sha256': sha(author_path)},
          'authorDecodeProvenance': {'file': decoded_path.relative_to(D).as_posix(), 'sha256': sha(decoded_path)},
          'props': author['props'], 'resolvedProps': author['resolvedProps'], 'clips': clips,
          'counts': {'clipFrames': 1868, 'reusedEvery24IntegerNSamples': sum(len(x['reusedEvery24IntegerNSamples']) for x in clips),
                     'freshExactKeyNeighborSamples': sum(len(x['freshExactKeyNeighbors']) for x in clips),
                     'contactSheets': sum(len(x['contactsForActualVisualReview']) for x in clips)},
          'sourceUnchanged': True,
          'limits': ['Raw Remotion bounded previews, not normalized limited-BT709 formal final media.',
                     'Complete video and AAC decode is performed independently here; no audio listening/ASR or full-film review claim.',
                     'Author every24-n images are explicitly reused from the same checked source/clip SHA; fresh exact neighbors are separately identified.',
                     'Every contact and selected original PNG require actual viewing before any visual acceptance.']}
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'machinePass': True, 'out': str(report_path), 'counts': report['counts']}))
