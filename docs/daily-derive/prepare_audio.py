"""Exact take mapping and sample-phase settings; all audio algorithms are shared."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
EP=ROOT/'episodes-codex/daily-temperatures'
BEFORE=EP/'revisions/derive-before'
OLDER=EP/'revisions/problem-fit-opening-before'
SEED=EP/'voice/derive-mini'
TAKE='derive'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def run(path,*args):subprocess.run([sys.executable,str(ROOT/path),*map(str,args)],cwd=ROOT,check=True)
approval=read(Path(__file__).parent/'editorial-approval.json')
assert approval['status']=='passed' and approval['scriptSHA256']==sha(EP/'script.md')
run('episodes/_shared/voice/prep.py','--dir',EP)
lookup={}
for folder,status in [(SEED,'new-approved'),(OLDER,'reused-prior-pure-problem'),(BEFORE,'reused-latest')]:
    picks=read(folder/'voice/picks.json') if (folder/'voice/picks.json').exists() else {}
    for row in read(folder/'voice/sents.json'):
        stem=folder/'voice/takes'/f"{row['id']}-{picks.get(row['id'],'a')}"
        lookup[(row['text'],row['tts'])]=(row,stem,status)
current=read(EP/'voice/sents.json');assert len(current)==30
picks={};provenance=[]
for row in current:
    source,stem,status=lookup[(row['text'],row['tts'])]
    target=EP/'voice/takes'/f"{row['id']}-{TAKE}"
    assert read(Path(str(stem)+'.txt.json'))==row['tts']
    files=[]
    for suffix in ['.wav','.raw.wav','.txt.json']:
        src,dst=Path(str(stem)+suffix),Path(str(target)+suffix)
        assert src.is_file()
        if dst.exists():assert sha(src)==sha(dst)
        else:shutil.copy2(src,dst)
        files.append({'source':str(src.relative_to(EP)),'target':str(dst.relative_to(EP)),'sha256':sha(src)})
    picks[row['id']]=TAKE
    provenance.append({'id':row['id'],'text':row['text'],'tts':row['tts'],'status':status,'files':files})
assert sum(r['status']=='new-approved' for r in provenance)==4
save(EP/'voice/picks.json',picks)
save(EP/'voice/derive-provenance.json',{'status':'mapped','new':4,'reused':26,'scriptSHA256':sha(EP/'script.md'),'rows':provenance,'method':'Exact text+TTS and raw/WAV/text triples; no local cut/onset/normalization algorithm.'})
lines=re.findall(r'^旁白：(.+)$',(EP/'script.md').read_text(),re.M)
save(EP/'voice/script-narration-sha256.json',{'scriptSha256':sha(EP/'script.md'),'narrationSha256':hashlib.sha256('\n'.join(lines).encode()).hexdigest(),'narrationLines':len(lines),'sentences':len(current),'narrationDefinition':'Narration lines joined by LF without trailing LF; full script hashed separately.'})
params=read(EP/'voice/params.json');params['extraAfter']={};save(EP/'voice/params.json',params)
run('episodes/_shared/voice/build.py','--dir',EP)
initial=read(EP/'voice/build.json');phase=EP/'revisions/derive-phase-initial';phase.mkdir(exist_ok=True)
for name in ['voice/build.json','voice/params.json']:
    dest=phase/name;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(EP/name,dest)
def first_by_slug(rows):
    result={}
    for row in rows:result.setdefault(row['shot'].split('-',1)[1],row)
    return result
old=first_by_slug(read(BEFORE/'voice/build.json')['sentences']);new=first_by_slug(initial['sentences'])
extra={};running=0
for predecessor,entry in [('01-problem','output'),('04-stack-basics','order'),('06-name','first-days')]:
    delta=(old[entry]['startSample']-new[entry]['startSample']-running)%1600
    extra[predecessor]=delta;running+=delta
params['extraAfter']={k:v/48000 for k,v in extra.items() if v};save(EP/'voice/params.json',params)
save(EP/'voice/derive-phase-alignment.json',{'status':'derived-from-actual-samples','extraAfterSamples':extra,'samplesPerFrame':1600,'initialBuildSHA256':sha(phase/'voice/build.json'),'baselineBuildSHA256':sha(BEFORE/'voice/build.json'),'method':'Only nonnegative subframe silence after fresh shots; align each reused group entry modulo1600. Reused shot internals stay unchanged.'})
run('episodes/_shared/voice/build.py','--dir',EP)
run('episodes-codex/daily-temperatures/prepare_code_endcard.py')
run('episodes/_shared/place_v2.py','--dir',EP,'--mode','whole','--report',EP/'voice/place-derive.json')
run('episodes/_shared/label_onset_strict.py','--dir',EP,'--out',EP/'label-onset-derive.txt')
run('episodes-codex/_shared/check_sentence_episode.py',EP)
assert approval['scriptSHA256']==sha(EP/'script.md')
print(json.dumps({'new':4,'reused':26,'bodyFrames':read(EP/'words.json')['durationFrames'],'voiceSHA256':sha(EP/'voice.wav'),'extraAfterSamples':extra}))
