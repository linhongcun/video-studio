#!/usr/bin/env python3
"""Bounded final plan for the user-selected02→03→04 clarification only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math
D = Path(__file__).resolve().parent
O = D.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sb = json.loads((D / 'storyboard.json').read_text())
shots = [s for c in sb['scenes'] for s in c['shots']]
events = []
def event(s, sentence, count, fr, to, label):
    a = s['cueFrames']['sentences'][sentence]; b = s['voice'][sentence]['localEnd']
    start = a + (b-a)*fr; length = (b-a)*(to-fr)/count
    for i in range(count):
        events.append({'shot': s['id'], 'visualType': s['visualType'], 'sentence': sentence, 'operation': i, 'label': label, 'predictedPhases': {str(p): s['from'] + math.ceil(start + length*(i+p) - 1e-9) for p in [0,.18,.45,.72,1]}})
for s in shots:
    t = s['visualType']
    if t == 'linear': event(s,0,5,.08,.96,'linear-forward');event(s,1,1,.08,.96,'linear-stop')
    elif t == 'upper': event(s,1,1,.08,.91,'upper-to40')
    elif t == 'descend': event(s,0,1,.08,.91,'reject70');event(s,1,1,.08,.91,'same40-descend')
    elif t == 'locate': event(s,0,1,.08,.93,'bottom-to50');event(s,1,1,.08,.93,'reject60')
    elif t in ['splice-bottom','splice-upper']: event(s,0,2,.08,.96,'ordered-pointer-write')
old_plan = json.loads((O / 'qa-preflight-plan.json').read_text())
assert events == old_plan['events'], 'Original15 operation windows changed'
frames = sorted(set([842,880,881,882,930,954,955,956,982,1008,1009,1010,1011,1025,1060,1102,1112,1125,1241,1337,1380,1381,1382,1383,1451,1555,1648,1704,1705,3112,3113,3203,3204,3559,3560,3650,3651,2072,3134,3798]))
assert len(frames) == 40
clips = [
 {'name':'linear-complete-to-structure','range':[930,1125],'reviewFrames':[f for f in frames if 930 <= f <= 1125]},
 {'name':'structure-to-requery','range':[1337,1451],'reviewFrames':[f for f in frames if 1337 <= f <= 1451]},
]
plan = {'status':'planned-not-rendered','createdAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Exactly40 bounded actual transition/unchanged-state PNG-DOM samples and2 short silent continuous transition clips. User clarification narrows the revision to02tail→03structure→04requery;06/07 stay original.','bodyFrames':4482,'storyboardSHA256':sha(D/'storyboard.json'),'mainSourceSHA256':sha(D/'remotion/src/Main.tsx'),'frames':frames,'smokeFrames':[],'events':events,'all15OriginalEventWindowsExact':True,'clips':clips,'legalRevisedPhases':{'linearCompletion':{'firstFrame':881,'effect':'No query cursor/comparison/active edge; show completed55between50and60.'},'structureBridge':{'range':[955,1009],'effect':'No main graph and no active query; large closure→next structure question.'},'structurePreparation':{'range':[1010,1381],'effect':'Base graph retained; upper links fade during first-sentence35%→94%; no cursor/comparison.'},'same55Requery':{'firstFrame':1382,'effect':'Explicit restart heading; original head-upper cursor/motion and candidate decisions.'}},'unchangedGraphWitnessFrames':[2072,3134,3798],'limits':['The plan is source-informed and proves no rendered or visual quality by itself.','No second insertion-transition revision and no new first/second-part numbering.']}
(D/'qa-clear-parts-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'plannedPNGDOM':len(frames),'clips':[(c['name'],c['range'],len(c['reviewFrames'])) for c in clips],'preservedOperationWindows':len(events)}))
