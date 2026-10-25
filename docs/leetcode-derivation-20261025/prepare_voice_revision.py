"""Map identical old text+TTS to immutable takes; synthesize only missing new takes.

Uses shared prep/gen/build for all actual voice processing. Does not generate,
trim, normalize, place, or infer any audio itself. Run only after editorial signoff.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('slug')
ap.add_argument('--take-name', default='approach')
a = ap.parse_args()
EP = ROOT / 'episodes-codex' / a.slug
BEFORE = EP / 'revisions/approach-first/before'

def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def textsha(s): return hashlib.sha256(s.encode()).hexdigest()

old = load(BEFORE/'voice/sents.json')
old_picks = load(BEFORE/'voice/picks.json')
params = load(EP/'voice/params.json')
params.setdefault('tts', {})['threads'] = 1
(EP/'voice/params.json').write_text(json.dumps(params, ensure_ascii=False, indent=2)+'\n')
prep = subprocess.run([sys.executable, str(ROOT/'episodes/_shared/voice/prep.py'), '--dir', str(EP)], check=True, capture_output=True, text=True)
(EP/'voice/prep-approach.log').write_text(prep.stdout+prep.stderr)
new = load(EP/'voice/sents.json')
assert len(new) == load(EP/'episode-config.json')['shotCount']*2
old_by_text = {}
for row in old: old_by_text.setdefault((row['text'], row['tts']), []).append(row)
picks, jobs, reused = {}, [], []
for row in new:
    sid, take = row['id'], a.take_name
    picks[sid] = take
    stem = EP/'voice/takes'/f'{sid}-{take}'
    if Path(str(stem)+'.wav').exists():
        assert load(Path(str(stem)+'.txt.json')) == row['tts'], f'{sid}: existing revision take is stale; choose a new --take-name'
    candidates = old_by_text.get((row['text'], row['tts']), [])
    if candidates:
        chosen = next((q for q in candidates if q['id']==sid), candidates[0])
        old_take = old_picks.get(chosen['id'], 'a')
        source = EP/'voice/takes'/f"{chosen['id']}-{old_take}"
        assert load(Path(str(source)+'.txt.json')) == row['tts']
        files = {}
        for suffix in ['.wav', '.txt.json', '.raw.wav']:
            src, dst = Path(str(source)+suffix), Path(str(stem)+suffix)
            if not src.exists():
                assert suffix == '.raw.wav'
                continue
            if dst.exists(): assert sha(dst) == sha(src), str(dst)
            else: shutil.copy2(src, dst)
            files[suffix] = {'source': str(src.relative_to(EP)), 'destination': str(dst.relative_to(EP)), 'sha256': sha(src)}
        reused.append({'oldId': chosen['id'], 'oldTake': old_take, 'newId': sid, 'newTake': take, 'textSha256': textsha(row['text']), 'ttsSha256': textsha(row['tts']), 'files': files})
    elif not Path(str(stem)+'.wav').exists():
        jobs.append([sid, take, None])
(EP/'voice/picks.json').write_text(json.dumps(picks, ensure_ascii=False, indent=2)+'\n')
(EP/'voice/jobs-approach.json').write_text(json.dumps(jobs, ensure_ascii=False, indent=2)+'\n')
report={'method':'Shared prep; exact (text,tts) match only; old selected WAV/raw/text bytes copied unchanged under a new explicit revision take name. No audio processing is duplicated.', 'oldSentences':len(old), 'newSentences':len(new), 'reusedSentences':len(reused), 'newTTSJobs':len(jobs), 'takeName':a.take_name, 'reused':reused, 'jobs':jobs}
(EP/'revisions/approach-first/voice-reuse.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
script = (EP/'script.md').read_bytes()
lines = [line[3:].strip() for line in script.decode().splitlines() if line.startswith('旁白：')]
(EP/'voice/script-narration-sha256.json').write_text(json.dumps({'scriptSha256':hashlib.sha256(script).hexdigest(), 'narrationSha256':textsha('\n'.join(lines)), 'narrationLines':len(lines), 'sentences':len(new), 'narrationDefinition':'UTF-8 of narration lines without prefix, joined by LF, no trailing LF.', 'note':'Approach-first revision; unchanged exact-text takes reused, only new wording synthesized with shared MiMo tools.'},ensure_ascii=False,indent=2)+'\n')
(EP/'voice/substitutions.md').write_text('# 思路推导修订配音\n\n沿用冰糖原速。未改文字与送模文本按完整相等映射，原选中WAV/raw/文本字节不变；新句使用独立修订take名。映射及完整SHA见 `revisions/approach-first/voice-reuse.json`。\n\n整轨、裁尾、起音和铺轨继续使用共享工具。没有逐字ASR或全片人工听辨，不将声学/文本/文件检查写成这些能力。背景音乐由后续共享混音添加，5秒代码卡仅无旁白。\n')
print(json.dumps({k:report[k] for k in ['oldSentences','newSentences','reusedSentences','newTTSJobs','takeName']},ensure_ascii=False))
