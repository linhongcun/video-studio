"""Batch orchestration only; all voice/onset/timing algorithms remain shared."""
from pathlib import Path
import hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
slug = sys.argv[1]
assert slug in ['daily-temperatures', 'permutations', 'trapping-rain-water']
EP = ROOT / 'episodes-codex' / slug
approved = json.loads((Path(__file__).parent / 'approved-scripts.json').read_text())
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(EP / 'script.md') == approved[slug]
assert (EP / 'qa-editorial.md').is_file()
assert json.loads((EP / 'qa-algorithm-independent.json').read_text())['status'] == 'passed'
def run(script, *args):
    subprocess.run([sys.executable, str(ROOT / script), *map(str, args)], cwd=ROOT, check=True)
run('episodes/_shared/voice/prep.py', '--dir', EP)
sents = json.loads((EP / 'voice/sents.json').read_text())
config = json.loads((EP / 'episode-config.json').read_text())
assert len(sents) == 2 * config['shotCount']
(EP / 'voice/picks.json').write_text(json.dumps({s['id']: 'a' for s in sents}, indent=2) + '\n')
lines = re.findall(r'^旁白：(.+)$', (EP / 'script.md').read_text(), re.M)
(EP / 'voice/script-narration-sha256.json').write_text(json.dumps({
    'scriptSha256': sha(EP / 'script.md'),
    'narrationSha256': hashlib.sha256('\n'.join(lines).encode()).hexdigest(),
    'narrationLines': len(lines), 'sentences': len(sents),
    'narrationDefinition': 'Narration lines joined with LF, no final LF; script hash covers the full file.'
}, ensure_ascii=False, indent=2) + '\n')
(EP / 'voice/substitutions.md').write_text(
    '# 实际送模与配音范围\n\n本片均为本期新生成a候选；送模文字取voice/sents.json，句尾好。是共享build裁去的抛弃尾。'
    '字幕保持script.md原句；本记录不表示逐字ASR或全片人工听辨。\n')
for s in sents:
    cached = EP / 'voice/takes' / (s['id'] + '-a.txt.json')
    if cached.exists():
        assert json.loads(cached.read_text()) == s['tts'], s['id']
run('episodes/_shared/voice/gen.py', '--dir', EP)
for s in sents:
    stem = EP / 'voice/takes' / (s['id'] + '-a')
    assert stem.with_suffix('.wav').is_file(), f'Missing actual generated take: {s["id"]}'
    assert json.loads(stem.with_suffix('.txt.json').read_text()) == s['tts']
assert sha(EP / 'script.md') == approved[slug], 'Narration changed during generation'
run('episodes/_shared/voice/build.py', '--dir', EP)
subprocess.run([sys.executable, str(EP / 'prepare_code_endcard.py')], cwd=ROOT, check=True)
run('episodes/_shared/place_v2.py', '--dir', EP, '--mode', 'whole', '--report', EP / 'voice/place_v2.json')
run('episodes/_shared/label_onset_strict.py', '--dir', EP, '--out', EP / 'label-onset-strict.txt')
run('episodes-codex/_shared/check_sentence_episode.py', EP)
summary = json.loads((EP / 'voice/build.json').read_text())['summary']
print(json.dumps({'slug': slug, 'actualFrames': summary['frames'], 'seconds': summary['seconds'],
                  'voiceSHA256': sha(EP / 'voice.wav'), 'actualSentences': len(sents)}, indent=2))
