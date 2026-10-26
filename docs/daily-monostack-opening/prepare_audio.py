"""Assemble the approved opening revision with shared voice tools only."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / 'episodes-codex/daily-temperatures'
BEFORE = EP / 'revisions/problem-fit-opening-before'
SEED = EP / 'voice/opening-mini'
TAKE = 'problem-fit'
PY = sys.executable

def read(p):
    return json.loads(p.read_text())

def save(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(rel, *args):
    subprocess.run([PY, str(ROOT / rel), *map(str, args)], cwd=ROOT, check=True)

approval = read(Path(__file__).parent / 'editorial-approval.json')
assert approval['status'] == 'passed' and approval['scriptSHA256'] == sha(EP / 'script.md')
run('episodes/_shared/voice/prep.py', '--dir', EP)
old = read(BEFORE / 'voice/sents.json')
old_picks = read(BEFORE / 'voice/picks.json')
seed = read(SEED / 'voice/sents.json')
current = read(EP / 'voice/sents.json')
assert len(current) == 28 == read(EP / 'episode-config.json')['shotCount'] * 2
old_text = {(s['text'], s['tts']): s for s in old}
seed_text = {(s['text'], s['tts']): s for s in seed}
picks, provenance = {}, []
for s in current:
    key = (s['text'], s['tts'])
    if key in old_text:
        source = old_text[key]
        source_take = old_picks[source['id']]
        stem = BEFORE / 'voice/takes' / f"{source['id']}-{source_take}"
        status = 'reused-exact-text'
    else:
        source = seed_text[key]
        source_take = 'a'
        stem = SEED / 'voice/takes' / f"{source['id']}-a"
        status = 'new-approved-opening-sentence'
    target = EP / 'voice/takes' / f"{s['id']}-{TAKE}"
    assert read(Path(str(stem) + '.txt.json')) == s['tts']
    files = []
    for suffix in ['.wav', '.raw.wav', '.txt.json']:
        src, dst = Path(str(stem) + suffix), Path(str(target) + suffix)
        assert src.is_file()
        if dst.exists():
            assert sha(dst) == sha(src)
        else:
            shutil.copy2(src, dst)
        files.append({'source': str(src.relative_to(EP)), 'target': str(dst.relative_to(EP)), 'sha256': sha(src)})
    picks[s['id']] = TAKE
    provenance.append({'id': s['id'], 'text': s['text'], 'tts': s['tts'], 'status': status,
                       'sourceId': source['id'], 'sourceTake': source_take, 'files': files})
assert sum(p['status'] == 'reused-exact-text' for p in provenance) == 24
assert sum(p['status'] == 'new-approved-opening-sentence' for p in provenance) == 4
save(EP / 'voice/picks.json', picks)
save(EP / 'voice/problem-fit-provenance.json', {'status': 'mapped', 'scriptSHA256': sha(EP / 'script.md'),
     'reusedSentences': 24, 'newSentences': 4, 'takeName': TAKE, 'rows': provenance,
     'method': 'Exact text+TTS plus selected raw/WAV/text SHA; four fresh takes came from the approved shared prep/gen seed during checkout. Shared build/cut/onset/place are sole implementations.'})
lines = re.findall(r'^旁白：(.+)$', (EP / 'script.md').read_text(), re.M)
save(EP / 'voice/script-narration-sha256.json', {'scriptSha256': sha(EP / 'script.md'),
     'narrationSha256': hashlib.sha256('\n'.join(lines).encode()).hexdigest(),
     'narrationLines': len(lines), 'sentences': len(current),
     'narrationDefinition': 'Narration lines joined by LF without trailing LF; full script hashed separately.'})
params = read(EP / 'voice/params.json')
params['extraAfter'] = {}
save(EP / 'voice/params.json', params)
run('episodes/_shared/voice/build.py', '--dir', EP)
initial = read(EP / 'voice/build.json')
phase_dir = EP / 'revisions/problem-fit-phase-alignment'
phase_dir.mkdir(exist_ok=True)
for name in ['voice/build.json', 'voice/params.json', 'voice.wav']:
    dst = phase_dir / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(EP / name, dst)
old_rows = read(BEFORE / 'voice/build.json')['sentences']
old_by_slug = {}
for row in old_rows:
    old_by_slug.setdefault(row['shot'].split('-', 1)[1], row)
new_by_slug = {}
for row in initial['sentences']:
    new_by_slug.setdefault(row['shot'].split('-', 1)[1], row)
samples_per_frame = 1600
a = (old_by_slug['output']['startSample'] - new_by_slug['output']['startSample']) % samples_per_frame
b = (old_by_slug['order']['startSample'] - new_by_slug['order']['startSample'] - a) % samples_per_frame
c = (old_by_slug['first-days']['startSample'] - new_by_slug['first-days']['startSample'] - a - b) % samples_per_frame
if c > samples_per_frame // 2:
    c -= samples_per_frame
assert 33600 + c > 0
extra = {'01-problem': a, '04-stack-basics': b, '05-order': c}
params['extraAfter'] = {key: value / 48000 for key, value in extra.items() if value}
save(EP / 'voice/params.json', params)
save(EP / 'voice/problem-fit-phase-alignment.json', {'status': 'parameters-derived-from-real-build',
     'initialBuildSHA256': sha(phase_dir / 'voice/build.json'), 'baselineBuildSHA256': sha(BEFORE / 'voice/build.json'),
     'samplesPerFrame': samples_per_frame, 'extraAfterSamples': extra,
     'method': 'Align each reused group startSample modulo1600; fresh shots carry nonnegative subframe silence. The removed name shot requires a signed inter-shot-silence correction after reused order; no speech is trimmed.',
     'oldEntrySamples': {k: old_by_slug[k]['startSample'] for k in ['output', 'order', 'first-days']},
     'initialNewEntrySamples': {k: new_by_slug[k]['startSample'] for k in ['output', 'order', 'first-days']}})
run('episodes/_shared/voice/build.py', '--dir', EP)
run('episodes-codex/daily-temperatures/prepare_code_endcard.py')
run('episodes/_shared/place_v2.py', '--dir', EP, '--mode', 'whole', '--report', EP / 'voice/place-problem-fit.json')
run('episodes/_shared/label_onset_strict.py', '--dir', EP, '--out', EP / 'label-onset-problem-fit.txt')
run('episodes-codex/_shared/check_sentence_episode.py', EP)
assert approval['scriptSHA256'] == sha(EP / 'script.md')
print(json.dumps({'reused': 24, 'new': 4, 'bodyFrames': read(EP / 'words.json')['durationFrames'],
                  'voiceSHA256': sha(EP / 'voice.wav'), 'extraAfterSamples': extra}, ensure_ascii=False))
