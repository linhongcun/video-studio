"""Revision orchestration: exact-text take reuse; only shared voice algorithms."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];EP=ROOT/'episodes-codex/daily-temperatures';BEFORE=EP/'revisions/stack-primer-before';TAKE='stack-primer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def run(rel,*args):subprocess.run([sys.executable,str(ROOT/rel),*map(str,args)],cwd=ROOT,check=True)
approved=read(Path(__file__).parent/'editorial-approval.json')
assert approved['status']=='passed' and approved['scriptSHA256']==sha(EP/'script.md')
run('episodes/_shared/voice/prep.py','--dir',EP)
old=read(BEFORE/'voice/sents.json');old_picks=read(BEFORE/'voice/picks.json');new=read(EP/'voice/sents.json')
assert len(new)==read(EP/'episode-config.json')['shotCount']*2
by_text={}
for row in old:by_text.setdefault((row['text'],row['tts']),[]).append(row)
picks={};rows=[];jobs=[]
for row in new:
 sid=row['id'];picks[sid]=TAKE;stem=EP/'voice/takes'/f'{sid}-{TAKE}';candidates=by_text.get((row['text'],row['tts']),[])
 entry={'newId':sid,'text':row['text'],'tts':row['tts'],'take':TAKE}
 if candidates:
  chosen=next((q for q in candidates if q['id']==sid),candidates[0]);old_take=old_picks.get(chosen['id'],'a');source=EP/'voice/takes'/f"{chosen['id']}-{old_take}";files=[]
  assert read(Path(str(source)+'.txt.json'))==row['tts']
  for suffix in ['.wav','.raw.wav','.txt.json']:
   src=Path(str(source)+suffix);dst=Path(str(stem)+suffix)
   assert src.is_file()
   if dst.exists():assert sha(dst)==sha(src)
   else:shutil.copy2(src,dst)
   files.append({'source':str(src.relative_to(EP)),'target':str(dst.relative_to(EP)),'sha256':sha(src)})
  entry.update(status='reused-exact-text',oldId=chosen['id'],oldTake=old_take,files=files)
 else:
  sidecar=Path(str(stem)+'.txt.json')
  if sidecar.exists():assert read(sidecar)==row['tts']
  if not Path(str(stem)+'.wav').is_file():jobs.append([sid,TAKE,None])
  entry.update(status='new-primer-sentence')
 rows.append(entry)
(EP/'voice/picks.json').write_text(json.dumps(picks,ensure_ascii=False,indent=2)+'\n')
(EP/'voice/jobs-stack-primer.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+'\n')
assert sum(r['status']=='reused-exact-text' for r in rows)==28
assert sum(r['status']=='new-primer-sentence' for r in rows)==4
report={'status':'mapped-before-generation','scriptSHA256':sha(EP/'script.md'),'oldSentences':len(old),'newSentences':len(new),'reusedSentences':28,'newSentencesCount':4,'takeName':TAKE,'rows':rows,'method':'Exact text+TTS identity; copied selected original raw/WAV/text bytes. Shared prep/gen/build/cut/onset/place remain sole implementations.'}
(EP/'voice/stack-primer-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=re.findall(r'^旁白：(.+)$',(EP/'script.md').read_text(),re.M)
(EP/'voice/script-narration-sha256.json').write_text(json.dumps({'scriptSha256':sha(EP/'script.md'),'narrationSha256':hashlib.sha256('\n'.join(lines).encode()).hexdigest(),'narrationLines':len(lines),'sentences':len(new),'narrationDefinition':'Narration lines joined by LF without trailing LF; full script hashed separately.'},ensure_ascii=False,indent=2)+'\n')
(EP/'voice/substitutions.md').write_text('# 单调栈前置铺垫修订\n\n正常冰糖语速，28句原选中take按text+tts及raw/WAV/文本完整SHA复用，仅4句基础铺垫为新take。实际来源见stack-primer-provenance.json。共享gen/build/cut/onset/place处理声音，不使用旧成片AAC拼人声。不声称逐字ASR或全片人工听辨。\n')
run('episodes/_shared/voice/gen.py','--dir',EP,'--jobs',EP/'voice/jobs-stack-primer.json')
for row in new:
 stem=EP/'voice/takes'/f"{row['id']}-{TAKE}"
 assert Path(str(stem)+'.wav').is_file() and read(Path(str(stem)+'.txt.json'))==row['tts']
assert approved['scriptSHA256']==sha(EP/'script.md')
run('episodes/_shared/voice/build.py','--dir',EP)
subprocess.run([sys.executable,str(EP/'prepare_code_endcard.py')],cwd=ROOT,check=True)
run('episodes/_shared/place_v2.py','--dir',EP,'--mode','whole','--report',EP/'voice/place-stack-primer.json')
run('episodes/_shared/label_onset_strict.py','--dir',EP,'--out',EP/'label-onset-stack-primer.txt')
run('episodes-codex/_shared/check_sentence_episode.py',EP)
print(json.dumps({'sentences':len(new),'reused':28,'new':4,'frames':read(EP/'words.json')['durationFrames'],'voiceSHA256':sha(EP/'voice.wav')},ensure_ascii=False))
