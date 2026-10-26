#!/usr/bin/env python3
"""Independent narrow-change and unchanged-graph proof after actual bounded QA."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, re
from PIL import Image, ImageChops
D = Path(__file__).resolve().parent
O = D.parents[2]
R = next(p for p in D.parents if (p / 'AGENTS.md').exists())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def canonical(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def number_paths(v, p='$'):
    if type(v) in (int, float): return {p:v}
    if isinstance(v, dict): return {q:x for k,w in v.items() for q,x in number_paths(w,p+'.'+str(k)).items()}
    if isinstance(v, list): return {q:x for k,w in enumerate(v) for q,x in number_paths(w,p+'['+str(k)+']').items()}
    return {}
def main():
    checks = Counter()
    def check(v, name):
        checks[name] += 1
        if not v: raise AssertionError(name)
    b = load(D/'qa-revision-baseline-protection.json')
    for p,h in b['originalFrozenInputs'].items():check(sha(R/p)==h,'original139frozen-inputs-remain-exact')
    for p,h in b['originalTopLevelFiles'].items():check(sha(R/p)==h,'original492historical-files-remain-exact')
    old_sb,new_sb = load(O/'storyboard.json'),load(D/'storyboard.json')
    old_shots = [s for c in old_sb['scenes'] for s in c['shots']]
    new_shots = [s for c in new_sb['scenes'] for s in c['shots']]
    check(number_paths(old_sb)==number_paths(new_sb),'all-storyboard-numeric-paths-and-values-exact')
    check(len(old_shots)==len(new_shots)==10,'ten-shot-count-exact')
    read_fields = ['id','visualType','from','durationInFrames','narration','voice','cueFrames','subtitles']
    for old,new in zip(old_shots,new_shots):
        for field in read_fields:check(old[field]==new[field],'every-actually-rendered-shot-field-exact')
    for field in ['width','height','fps']:check(old_sb['meta'][field]==new_sb['meta'][field],'Root-actually-read-meta-exact')
    check(sum(s['durationInFrames'] for s in new_shots)==4482,'body4482frames-exact')
    check((D/'remotion/src/placeholders/storyboard.json').read_bytes()==(D/'storyboard.json').read_bytes(),'actual-placeholder-equals-final-SB')
    unchanged_files = ['model.json','build_model.py','covers.json','voice.wav','captions.srt','voice/sents.json','voice/shot_frames.json','voice/cues.json','voice/cue_tests.json','remotion/public/audio/voice.wav','remotion/package-lock.json','remotion/remotion.config.ts']
    unchanged_files += [str(p.relative_to(D)) for p in (D/'remotion/src').glob('*') if p.is_file() and p.name not in ['Main.tsx','theme.ts']]
    for rel in unchanged_files:check(sha(D/rel)==sha(O/rel),'unchanged-physical-runtime-or-timing-input-exact')
    old_theme=(O/'remotion/src/theme.ts').read_text();new_theme=(D/'remotion/src/theme.ts').read_text()
    old_import=re.search(r"from '([^']+)'",old_theme).group(1);new_import=re.search(r"from '([^']+)'",new_theme).group(1)
    check(old_theme.replace(old_import,new_import)==new_theme,'theme-only-relative-import-rebased')
    check((O/'remotion/src'/old_import).resolve()==(D/'remotion/src'/new_import).resolve()==(R/'episodes/_shared/theme/pageTheme').resolve(),'theme-import-resolves-exact-same-shared-module')
    check(sha(D/'voice.wav')=='0c48b0538985b74cce8e31e8ed6f45196ae03d6b2cdc09886b26eba2b9932805','voice-is-original0c48')
    old_pkg,new_pkg = load(O/'remotion/package.json'),load(D/'remotion/package.json')
    for field in ['dependencies','devDependencies']:check(old_pkg.get(field)==new_pkg.get(field),'actual-runtime-package-versions-exact')
    narration = lambda p: re.findall(r'^旁白：(.*)$',p.read_text(),re.M)
    old_lines,new_lines = narration(O/'script.md'),narration(D/'script.md')
    check(old_lines==new_lines and len(new_lines)==10,'ten-narration-lines-byte-exact')
    sentences=[s for line in new_lines for s in re.split(r'(?<=[。！？])',line) if s]
    prepared=load(D/'voice/sents.json')
    check(len(sentences)==20 and sentences==[s['text'] for s in prepared],'independently-parsed20sentences-match-original-TTS-requests')
    old_main,new_main = (O/'remotion/src/Main.tsx').read_text(),(D/'remotion/src/Main.tsx').read_text()
    function_names=['shots','sentenceSpan','stages','current','eventLink','Search','Goal','Upper','Descend','Locate','Height','Splice','Boundary','ShotView','Main']
    preserved_functions={}
    for name in function_names:
        pattern=r'^(?:export )?const '+name+r'(?:\:[^=]+)?=.*$'
        old=re.search(pattern,old_main,re.M).group(0);new=re.search(pattern,new_main,re.M).group(0)
        check(old==new,'original-unmodified-runtime-function-line-exact');preserved_functions[name]=hashlib.sha256(new.encode()).hexdigest()
    old_scene=re.search(r'^export const Scene=.*$',old_main,re.M).group(0)
    new_scene=re.search(r'^export const Scene=.*$',new_main,re.M).group(0)
    check(old_scene.replace("note='上下对齐并相连的框属于同一个节点，不是两份数据'","note='目标仍是55 · 先准备上层链接，再重新查找'")==new_scene,'Scene-dispatch-only-sparse-note-changed')
    for key in ['goal','linear','descend','locate','height',"'splice-bottom'","'splice-upper'",'boundary']:
        pattern=r'^ '+re.escape(key)+r':.*$';check(re.search(pattern,old_main,re.M).group(0)==re.search(pattern,new_main,re.M).group(0),'unmodified-shot-header-exact')
    old_plan,new_plan=load(O/'qa-preflight-plan.json'),load(D/'qa-clear-parts-plan.json')
    check(old_plan['events']==new_plan['events'] and len(new_plan['events'])==15,'all15actual-motion-event-windows-exact')
    raw=load(D/'remotion/out/clear-parts-preflight/samples.json')
    dom=load(D/'qa-clear-parts-dom.json')
    check(raw['status']=='completed' and dom['status']=='passed','actual-new-bounded-DOM-preflight-passed')
    check(len(raw['samples'])==len(raw['audits'])==40 and len(raw['clips'])==2,'actual-bounded-sample-and-clip-counts')
    sample_by={s['frame']:s for s in raw['samples']}
    old_by={s['frame']:s for s in load(O/'qa-preflight-evidence/samples.json')['samples']}
    graph_witnesses=[];roi=(75,300,1745,750)
    for frame in [2072,3134,3798]:
        old,new=old_by[frame],sample_by[frame]
        old_file=O/'qa-preflight-evidence/images'/Path(old['file']).name
        check(sha(old_file)==old['sha256'],'original-viewed-witness-PNG-exact')
        a=Image.open(old_file).convert('RGB').crop(roi);c=Image.open(new['file']).convert('RGB').crop(roi)
        check(ImageChops.difference(a,c).getbbox() is None,'unchanged-actual-graph-region-pixels-exact-zero-tolerance')
        graph_witnesses.append({'frame':frame,'originalPNG_SHA256':old['sha256'],'newPNG_SHA256':new['sha256'],'fullPNGByteIdentical':old['sha256']==new['sha256'],'graphROI1920x1080':list(roi),'graphPixelDifferences':0})
    for p,h in raw['sourceSHA'].items():check(sha(R/p)==h,'all-actually-rendered-sources-still-exact')
    report={'status':'passed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Independent bounded02tail→03bridge/structure→04same55requery preservation proof. Superseded06/07 changes are absent. Old QA keeps its original identity.','assertionsExecuted':sum(checks.values()),'assertionsByCategory':dict(checks),'all15OperationWindowsExact':True,'storyboardNumericValuesExact':len(number_paths(new_sb)),'actuallyRenderedShotFieldsExact':read_fields,'actualBodyFrames':4482,'narrationSentencesExact':20,'actualVoiceSHA256':sha(D/'voice.wav'),'unchangedRuntimeFunctionSHA256':preserved_functions,'themeImportOnlyRebasedToSamePhysicalModule':True,'actualGraphPixelWitnesses':graph_witnesses,'currentInputs':{n:sha(D/n) for n in ['script.md','plan.json','storyboard.json','words.json','model.json','covers.json','remotion/src/Main.tsx','remotion/src/graphics.tsx']},'producerVoiceProofSHA256':sha(D/'qa-voice-reuse-provenance.json'),'baselineProtectionSHA256':sha(D/'qa-revision-baseline-protection.json'),'originalBodyQAReportSHA256':sha(O/'qa-preflight.json'),'actualDOMReportSHA256':sha(D/'qa-clear-parts-dom.json'),'checkerSHA256':sha(__file__),'mustFixRemaining':[],'limitations':['Forty new actual DOM/PNG samples and two short real clips supplement preserved algorithm/source evidence; no rerun of the old231-state matrix or1360-frame insertion clip is claimed.','Final encoded film and voice/media/publication gates remain separate.']}
    (D/'qa-clear-parts-preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'assertions':report['assertionsExecuted'],'numericValues':report['storyboardNumericValuesExact'],'graphWitnesses':3}))
if __name__=='__main__':main()
