from pathlib import Path
import json,datetime,hashlib
ROOT=Path(__file__).resolve().parents[5];BASE=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()

def load(slug,name):
 p=BASE/slug/name/'report.json';d=json.loads(p.read_text());assert d['pass'] and d['sourceUnchanged'] and not d['browserLogs'];return d

def states(s,key):return [x['attrs'] for x in s['metrics']['states'] if key in x['attrs']]
def one(s,key):
 xs=states(s,key);assert len(xs)==1,(s['frame'],key,xs);return xs[0]
def texts(s):return '\n'.join(x['text'] for x in s['metrics']['texts'])
def check(rows,label,condition,frames):
 assert condition,label
 rows.append({'check':label,'passed':True,'frames':frames})

for slug in ['twelve-balls','prisoners-light']:
 r=load(slug,'preflight-v1-progress');caps=load(slug,'preflight-v1-captions');m={s['frame']:s for s in r['samples']};rows=[]
 check(rows,'Both actual-timing captures retain identical source hashes',r['sourceHashes']==caps['sourceHashes'],list(m))
 if slug=='twelve-balls':
  affected=[s for s in r['samples'] if s['shot']=='12']
  check(rows,'All affected samples remain unexecuted construction with2 current weighings and post-second capacity3',all(one(s,'data-balanced-construction-phase')['data-current-remaining-weighings']=='2' and one(s,'data-balanced-construction-phase')['data-required-post-second-capacity']=='3' and one(s,'data-balanced-construction-phase')['data-proposal-status']=='unexecuted' for s in affected),[s['frame'] for s in affected])
  check(rows,'All12 physical ball identities occur exactly once in each board-rendering frame',all(sorted(int(x['data-ball']) for x in states(s,'data-ball'))==list(range(1,13)) for s in affected if states(s,'data-physical-ball-count')),[s['frame'] for s in affected])
  check(rows,'Normal reference1–8 and8 heavy/light candidates are established before arrangement',one(m[4859],'data-physical-ball-count')['data-known-normal']=='1,2,3,4,5,6,7,8' and len(one(m[4859],'data-physical-ball-count')['data-current-candidates'].split(','))==8,[4859])
  check(rows,'Budget explicitly means after second weighing; current budget is not reduced early','第二称后余1称' in texts(m[4994]) and '当前尚余2称' in texts(m[4994]),[4994])
  check(rows,'Final arrangement uses9/10/11 versus normal1/2/3 and equal group sizes',one(m[5301],'data-left-balls')['data-left-balls']=='9,10,11' and one(m[5301],'data-left-balls')['data-right-balls']=='1,2,3' and one(m[5301],'data-left-balls')['data-comparison-legal']=='equal-count',[5301])
  check(rows,'Moving intermediate frame is labeled construction and does not expose candidate predictions',one(m[5169],'data-left-balls')['data-migrating']=='true' and not states(m[5169],'data-construction-prediction'),[5169])
  expected={5349:[('L','9H,10H,11H')],5417:[('L','9H,10H,11H'),('R','9L,10L,11L')],5475:[('L','9H,10H,11H'),('R','9L,10L,11L'),('B','12H,12L')]}
  for f,want in expected.items():
   got=[(x['data-construction-prediction'],x['data-predicted-cases']) for x in states(m[f],'data-construction-prediction')]
   check(rows,'Prediction reveal retains exact candidate sets at frame'+str(f),got==want,[f])
  check(rows,'Previous and following scene boundaries contain no retained construction-phase DOM',not states(m[4788],'data-balanced-construction-phase') and not states(m[5523],'data-balanced-construction-phase'),[4788,4789,5522,5523])
  findings=['Actual viewed progression restores the alternative first-balanced premise before constructing another weighing.','The explanation proceeds from8 candidates to post-second capacity, fixed-ball rearrangement, then separate3/3/2 predictions.','No actual outcome is selected in scene12; known normal balls come from first balance, not an external reference.','Moving candidates retain their identities, labels are withheld during migration, and native long captions remain inside their region.']
  contact_count=4
 else:
  expected={895:('lamp-limit','0'),925:('lamp-limit','0'),1011:('private-count','0'),1157:('private-count','0'),1344:('observe-on','0'),1380:('switch-off','0'),1425:('count-one','1'),1489:('count-one','1')}
  for f,want in expected.items():
   x=one(m[f],'data-role-stage');check(rows,'Role cause and receiving order at frame'+str(f),(x['data-role-stage'],x['data-private-counter-value'])==want,[f])
  check(rows,'Wrong sender-off stays hypothetical and keeps original on+unsent pending state',one(m[1670],'data-rule-phase')['data-rule-phase']=='wrong-off-loss' and one(m[1670],'data-rule-phase')['data-counterfactual']=='true' and one(m[1670],'data-rule-phase')['data-actual-pending-signal']=='1' and one(m[1670],'data-rule-phase')['data-sender-sent']=='false' and '错误做法示意，非主例' in texts(m[1670]),[1670])
  check(rows,'Exiting wrong example restores original pending-on and unsent state',all(one(m[f],'data-rule-phase')['data-rule-phase']=='restore-original' and one(m[f],'data-rule-phase')['data-actual-pending-signal']=='1' and one(m[f],'data-rule-phase')['data-sender-sent']=='false' and one(m[f],'data-rule-phase')['data-counterfactual']=='false' for f in [1744,1750]),[1744,1750])
  check(rows,'Successful off-send changes own memory only with pending signal creation',one(m[1775],'data-rule-phase')['data-sender-sent']=='false' and one(m[1775],'data-rule-phase')['data-actual-pending-signal']=='0' and one(m[1840],'data-rule-phase')['data-sender-sent']=='true' and one(m[1840],'data-rule-phase')['data-actual-pending-signal']=='1',[1775,1840])
  check(rows,'Unsent sender meeting lit lamp retains eligibility',one(m[1940],'data-rule-phase')['data-rule-phase']=='on-wait' and one(m[1940],'data-rule-phase')['data-sender-sent']=='false' and one(m[1940],'data-rule-phase')['data-actual-pending-signal']=='1',[1940])
  check(rows,'Scene05 independently resets the original example to off,count0,all unsent,no committed visits',one(m[2076],'data-main-example')['data-view-light']=='off' and one(m[2076],'data-main-example')['data-view-count']=='0' and one(m[2076],'data-main-example')['data-view-sent']=='' and one(m[2076],'data-main-example')['data-model-committed-visits']=='0',[2075,2076])
  findings=['Actual viewed03 separates binary shared lamp state from the fixed receiver private cumulative count.','The counter sees on, turns it off, and only then records one; example previews remain distinct from actual12 visits.','Wrong sender-off is visibly marked as a counterfactual; original on+unsent state is retained and explicitly restored.','All three correct sender conditions are illustrated, with qualification retained when lit; scene05 initializes the original main example without preview state leaking in.','Native two-line03 and one-line04 caption samples are readable within the subtitle region.']
  contact_count=6
 contacts=[str((BASE/slug/'preflight-v1-progress'/('contact-%02d.jpg'%k)).relative_to(ROOT)) for k in range(1,contact_count+1)]
 captions=[s['file'] for s in caps['samples']]
 review={'status':'passed','reviewedAt':now,'reviewer':'Codex independent motion QA','episode':slug,
  'sourceHashes':r['sourceHashes'],'actualDOMChecks':rows,'progressFrameCount':len(r['samples']),'captionFrameCount':len(caps['samples']),
  'imagesActuallyViewed':contacts+captions,'findings':findings,'blockingFindings':[],
  'scope':'Independent actual-timing multistage stills and DOM capture. Native caption images actually viewed. No full realtime playback, ASR, semantic listening, physical-device, or user-acceptance claim. Encoded final MP4 review remains pending.'}
 (BASE/slug/'preflight-visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'episode':slug,'status':'passed','progressFrames':len(r['samples']),'nativeCaptionFrames':len(caps['samples']),'actualDOMChecks':len(rows)}))
