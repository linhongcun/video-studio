"""Read-only source and bounded preview validation; writes only our QA evidence."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import wave

REPO = Path('/workspace/video-studio')
QA = REPO / 'docs/archive/2026-11/redis-mechanisms/qa'
OUT = QA / 'lru-independent-decision-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def ref(path):
    path = Path(path)
    return {'file': str(path), 'sha256': sha(path)}


def validate_hashes(mapping):
    checked = []
    for path, expected in mapping.items():
        path = Path(path)
        if not path.is_absolute():
            path = REPO / path
        actual = sha(path)
        assert actual == expected, (str(path), expected, actual)
        checked.append(ref(path))
    return checked


current = read(QA / 'lru-independent-source-v2/source-preview-review.json')
main = REPO / 'episodes/redis/redis-lru/production/remotion/src/Main.tsx'
assert sha(main) == 'ca6d89306940e19b230df4993215dbe669d3ca2485398059808a7a0642266997'
source_checked = validate_hashes(current['sourceSHA256'])
handoff_path = REPO / 'episodes/redis/redis-lru/production/qa-self/actual-handoff.json'
handoff = read(handoff_path)
assert handoff['mainSHA256'] == sha(main)
handoff_checked = validate_hashes(handoff['currentInputSHA256'])
assert len(handoff_checked) == 25

initial = read(QA / 'lru-independent-source-v1/source-preview-review.json')
initial_changes = []
for path, before in initial['sourceSHA256'].items():
    actual = sha(path)
    if actual != before:
        initial_changes.append({'file': path, 'before': before, 'now': actual})
assert {d['file'] for d in initial_changes} == {str(main), str(handoff_path)}

decoded_path = QA / 'lru-independent-decoded-clips-v3/decoded-sequences.json'
decoded = read(decoded_path)
assert len(decoded['samples']) == 101
for sample in decoded['samples']:
    assert sha(sample['file']) == sample['sha256']
clip_checks = []
for clip in decoded['clips']:
    report_path = QA / clip['name'] / 'short-clip-review.json'
    assert sha(report_path) == clip['reportSha256']
    report = read(report_path)
    assert report['sourceInputsUnchanged'] and report['machinePass']
    validate_hashes(report['sourceSHA256'])
    assert sha(clip['actualVideoFile']) == clip['videoSha256']
    probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames',
        '-show_streams', '-show_format', '-of', 'json', clip['actualVideoFile']]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert int(video['nb_read_frames']) == clip['last'] - clip['first'] + 1
    assert int(video['nb_read_frames']) == clip['decodedVideoFrames']
    run(['ffmpeg', '-v', 'error', '-i', clip['actualVideoFile'], '-f', 'null', '-'])
    clip_checks.append({**clip, 'actualProbe': probe, 'completeVideoAndAudioDecodePassed': True})
assert sum(c['decodedVideoFrames'] for c in clip_checks) == 1452

remux_path = QA / 'lru-independent-clip-pool-to-I-remux-v2/remux-review.json'
remux = read(remux_path)
validate_hashes(remux['inputs'])
assert sha(remux['file']) == remux['sha256']
silent = next(p for p in remux['inputs'] if p.endswith('motion-silent.mp4'))
packets = []
payload_hashes = []
for path in [silent, remux['file']]:
    result = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_packets', '-show_entries', 'packet=pts,dts,duration,pts_time,dts_time,duration_time,size',
        '-of', 'json', path]))
    assert len(result['packets']) == 449
    packets.append(result['packets'])
    payload_hashes.append(run(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:v:0',
        '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).strip())
assert packets[0] == packets[1]
assert payload_hashes[0] == payload_hashes[1] == remux['compressedVideoPayloadHash']
packet_proof = OUT / '449-frame-packet-proof.json'
assert not packet_proof.exists()
packet_proof.write_text(json.dumps({'silent': ref(silent), 'remux': ref(remux['file']),
    'packetFields': ['pts', 'dts', 'duration', 'pts_time', 'dts_time', 'duration_time', 'size'],
    'packetsIdentical': True, 'compressedPayloadHashes': payload_hashes,
    'all449VideoPackets': packets[0]}, indent=2) + '\n')

voice = REPO / 'episodes/redis/redis-lru/production/voice.wav'
slice_path = next(p for p in remux['inputs'] if p.endswith('.wav'))
with wave.open(str(voice)) as whole, wave.open(slice_path) as part:
    assert whole.getframerate() == part.getframerate() == 48000
    assert whole.getnchannels() == part.getnchannels()
    assert whole.getsampwidth() == part.getsampwidth()
    assert part.getnframes() == 449 * 1600
    whole.setpos(1950 * 1600)
    whole_bytes = whole.readframes(449 * 1600)
    slice_bytes = part.readframes(part.getnframes())
    assert whole_bytes == slice_bytes
    pcm = {'source': ref(voice), 'slice': ref(slice_path), 'sampleRate': 48000,
        'startSample': 1950 * 1600, 'endSampleExclusive': 2399 * 1600,
        'sampleFrames': 449 * 1600, 'originalPCMBytesIdentical': True,
        'pcmSHA256': hashlib.sha256(slice_bytes).hexdigest()}

contact_sets = []
for name, count in [
    ('lru-independent-source-contacts-v1', 9),
    ('lru-independent-caption-contacts-v1', 2),
    ('lru-independent-source-contacts-v2', 3),
    ('lru-independent-caption-contacts-v2', 1),
    ('lru-independent-decoded-contacts-v3', 13),
]:
    p = QA / name / 'contacts.json'
    d = read(p)
    assert sha(d['sourceReport']) == d['sourceReportSHA256']
    assert len(d['files']) == count
    for item in d['files']:
        assert sha(item['file']) == item['sha256']
    contact_sets.append({'manifest': ref(p), 'contactSheetCount': count,
        'allContactSheetsActuallyViewedByIndependentReviewer': True})

result = {
    'kind': 'independent-lru-final-read-only-evidence-validation',
    'createdAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'script': ref(__file__),
    'main': ref(main), 'handoff': ref(handoff_path),
    'currentPreviewBoundInputs': source_checked,
    'currentAuthorHandoff25Inputs': handoff_checked,
    'initial26BoundInputsNowChanged': initial_changes,
    'initialChangeExplanation': 'Only the approved two-line Main change and the later author-owned handoff metadata update; initial source/PNG reports are preserved.',
    'decodedSamples': len(decoded['samples']), 'decodedSampleHashesVerified': True,
    'clips': clip_checks,
    'clip449PacketProof': ref(packet_proof), 'clip449OriginalPCM': pcm,
    'contactSets': contact_sets,
    'scope': 'Read-only bounded preview evidence. No production edits, full encode, freeze or publication.',
    'passed': True,
}
target = OUT / 'final-verification.json'
assert not target.exists()
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'report': str(target), 'sha256': sha(target), 'passed': True,
    'videoFrames': sum(c['decodedVideoFrames'] for c in clip_checks),
    'selectedDecodedPNGs': len(decoded['samples'])}, ensure_ascii=False))
