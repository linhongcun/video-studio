#!/usr/bin/env python3
"""Check identities/reuse and three untouched PNGs, not the old333-model suite."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re,wave
D=Path(__file__).resolve().parent
C=D.parents[1]/'clear-parts/redis-skiplist'
R=next(p for p in D.parents if(p/'AGENTS.md').exists())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def main():
    checks=Counter()
    def check(v,k):
        checks[k]+=1
        if not v:raise AssertionError(k)
    baseline=load(D/'qa-revision-baseline-protection.json')
    for p,h in baseline['originalFrozenInputs'].items():check(sha(R/p)==h,'protected-original-frozen-file-exact')
    for p,h in baseline['originalCompleteFiles'].items():check(sha(R/p)==h,'protected-original-complete-file-exact')
    check(sha(D/'height-options.json')=='ca0abf5dcef32e4cb96cd5912530a6b922a66894461a21d1a6b5be47b0700e50','formal-height-options-exact-audited-identity')
    check(sha(D/'model.json')=='7f614b6796e74e8a58c786bcb09cd26ffec9e5cb134611c550a565fbe763167b','main-model-exact-audited-identity')
    previous_model_qa=load(D/'qa-height-options-independent.json')
    check(previous_model_qa['formalHeightOptionsSHA256']==sha(D/'height-options.json') and previous_model_qa['status']=='passed','prior-formal-model-QA-keeps-its-actual-identity-no-rerun')
    for rel in ['remotion/src/graphics.tsx','remotion/src/Cover.tsx','remotion/src/LayoutAudit.tsx','remotion/src/Root.tsx','remotion/src/types.d.ts','remotion/src/types.ts','remotion/src/theme.ts','covers.json','references.json','remotion/package-lock.json']:
        check(sha(D/rel)==sha(C/rel),'untouched-rendering-dependency-exact')
    old_main,new_main=(C/'remotion/src/Main.tsx').read_text(),(D/'remotion/src/Main.tsx').read_text()
    functions=['shots','sentenceSpan','stages','current','eventLink','Search','Goal','Linear','Sparse','Upper','Descend','Locate','Splice','Boundary','ShotView','Main']
    stable_functions={}
    for name in functions:
        pattern=r'^(?:export )?const '+name+r'(?:\:[^=]+)?=.*$';a=re.search(pattern,old_main,re.M).group(0);b=re.search(pattern,new_main,re.M).group(0)
        check(a==b,'unchanged-motion-or-scene-function-line-exact');stable_functions[name]=hashlib.sha256(b.encode()).hexdigest()
    old_sb,new_sb=load(C/'storyboard.json'),load(D/'storyboard.json');old_shots=[s for c in old_sb['scenes'] for s in c['shots']];shots=[s for c in new_sb['scenes'] for s in c['shots']]
    check(sum(s['durationInFrames'] for s in shots)==4557,'actual-new-body4557-not-old4482')
    for k in ['width','height','fps']:check(old_sb['meta'][k]==new_sb['meta'][k],'actual-Root-format-exact')
    for old,new in zip(old_shots[:6],shots[:6]):
        for k in ['id','visualType','from','durationInFrames','voice','cueFrames','subtitles']:check(old[k]==new[k],'01to06-actual-global-and-local-read-fields-exact')
    for identity,shift in [('08',11),('10',75)]:
        old=next(s for s in old_shots if s['id']==identity);new=next(s for s in shots if s['id']==identity)
        check(new['from']-old['from']==shift,'unchanged-shot-known-global-shift-exact')
        for k in ['durationInFrames','cueFrames','subtitles']:check(old[k]==new[k],'08and10-local-durations-cues-subtitles-exact')
        for a,b in zip(old['voice'],new['voice']):
            for k in ['localStart','localEnd']:check(a[k]==b[k],'08and10-local-sentence-windows-exact-after-phase-padding')
    check((D/'storyboard.json').read_bytes()==(D/'remotion/src/placeholders/storyboard.json').read_bytes(),'physical-placeholder-exact-final-storyboard')
    reuse=load(D/'voice/reused-source-baseline.json');prepared={s['id']:s for s in load(D/'voice/sents.json')}
    check(len(reuse['rows'])==17,'exactly17-reused-original-source-sentences')
    for row in reuse['rows']:
        check(prepared[row['id']]['text']==row['text'] and prepared[row['id']]['tts']==row['tts'],'reused17-text-and-request-strings-exact')
        for f in row['files'].values():check(sha(R/f['originalPath'])==sha(D/f['revisionPath'])==f['sha256'],'reused-original-raw48k-request-files-exact')
        with wave.open(str(C/'voice/sentences'/f"{row['id']}.wav"),'rb') as a,wave.open(str(D/'voice/sentences'/f"{row['id']}.wav"),'rb') as b:
            check(a.getparams()[:4]==b.getparams()[:4],'reused-normalized-sentence-duration-format-exact-not-PCM-gain-claim')
    voiceqa,timing=load(D/'qa-voice.json'),load(D/'qa-voice-timing.json');voice_hash=sha(D/'voice.wav')
    check(voice_hash==sha(D/'remotion/public/audio/voice.wav')==voiceqa['voiceSHA256']=='e63140e9dbb8c0a9a841212563c090cf3aa199eeccf417077dc6c0a441d04b4b','actual-new-voice-and-public-copy-current-identity')
    check(voiceqa['status']=='passed' and timing['status']=='passed-fresh-mixed-source-voice-and-timing-qa','fresh-current-voice-QA-passed-not-historical-claim')
    check(timing['freshSentenceIds']==['07-height-1','07-height-2','09-splice-upper-1'],'only-three-selected-new-sentences')
    check(voiceqa['sharedBuilderReplay']['voiceSHA256']==voice_hash and all(row['trackWindowEqualsSentencePCM'] for row in voiceqa['rows']),'passed-real-shared-replay-and20-current-PCM-window-proof-bound')
    plan=load(D/'qa-height-preflight-plan.json');h=plan['heightPhases'];check(-6<=h['formalMinusAcousticFrames']<=2 and new_sb['meta']['onsetRule']['window']==[-6,2],'height-first-term-cue-uses-current-acoustic-onset-and-original-rule')
    raw=load(D/'remotion/out/height-preflight/samples.json');check(raw['status']=='completed','actual-bounded-render-completed')
    current={r['frame']:r for r in raw['samples']};old={r['frame']:r for r in load(C/'qa-clear-parts-evidence/samples.json')['samples']};witnesses=[]
    for frame in [881,955,1382]:
        old_file=C/'qa-clear-parts-evidence/images'/Path(old[frame]['file']).name
        check(sha(old_file)==old[frame]['sha256']==sha(current[frame]['file'])==current[frame]['sha256'],'actual02to04-full-PNG-byte-reproduction-exact')
        witnesses.append({'frame':frame,'oldAndNewPNG_SHA256':current[frame]['sha256'],'fullPNGByteIdentical':True})
    for p,v in raw['sourceSHA'].items():check(sha(R/p)==v,'all-actually-rendered-inputs-still-exact')
    out={'status':'passed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Bounded height-choice preservation/actual-onset dependency proof. The previous1952-assertion/333-query model audit is reused by exactca0 identity, not rerun.','assertionsExecuted':sum(checks.values()),'assertionsByCategory':dict(checks),'actualNewBodyFrames':4557,'actualNewVoiceSHA256':voice_hash,'freshSelectedSentenceCount':3,'actualCandidateRequests':4,'reusedOriginalSourceSentenceCount':17,'normalizedOldPCMNote':'Fresh full-track normalization may change gain in reused normalized PCM. Exact reuse is at original raw/48k/request level; current20 normalized windows match the current track, not old PCM bytes.','protectedFrozenFiles':len(baseline['originalFrozenInputs']),'protectedOldCompleteFiles':len(baseline['originalCompleteFiles']),'unchangedRuntimeFunctionSHA256':stable_functions,'unchanged02to04ActualFullPNGWitnesses':witnesses,'actualHeightCue':h,'actualNewWriteArrivalFrames':[e['arrival'] for e in plan['fourWriteWindows']],'currentInputs':{p:sha(D/p) for p in ['script.md','storyboard.json','words.json','height-options.json','model.json','covers.json','remotion/src/Main.tsx','voice.wav']},'proofSHA256':{p:sha(D/p) for p in ['qa-height-options-independent.json','qa-technical-independent.json','qa-voice.json','qa-voice-timing.json','voice/input-provenance.json']},'checkerSHA256':sha(__file__),'mustFixRemaining':[],'limits':['No repeated old333-model oracle, old231-point matrix or oldlarge insertion clip.','No full-film or semantic/human voice listening conclusion; current voice proof is signal/PCM/identity based.']}
    (D/'qa-height-preservation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'passed','assertions':out['assertionsExecuted'],'unchangedFullPNG':3,'bodyFrames':4557}))
if __name__=='__main__':main()
