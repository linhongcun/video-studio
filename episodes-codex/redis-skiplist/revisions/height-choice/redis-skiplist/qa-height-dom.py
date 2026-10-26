#!/usr/bin/env python3
"""Check actual SVG glyphs, painted forward edges and actor geometry.
Reads Chromium audit output, never imports production scene or uses Scene.state.
"""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import argparse,hashlib,json,math,re,traceback
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'AGENTS.md').exists())
N=Counter();failures=[]
def test(value,label,details=None):
 N[label]+=1
 if not value:failures.append({'label':label,'details':details})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b,eps=.06):return abs(float(a)-float(b))<=eps
def pathpoint(d,t):
 nums=[float(n) for n in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',d)]
 if 'C' in d:
  assert len(nums)==8,(d,nums)
  x0,y0,x1,y1,x2,y2,x3,y3=nums;u=1-t
  return(u*u*u*x0+3*u*u*t*x1+3*u*t*t*x2+t*t*t*x3,u*u*u*y0+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3)
 assert 'L' in d and len(nums)==4,(d,nums)
 x0,y0,x1,y1=nums;return(x0+(x1-x0)*t,y0+(y1-y0)*t)
def graph_edges(snap,levels):return {(n['id'],level,target) for n in snap['nodes'].values() for level,target in enumerate(n['forward']) if target is not None and level in levels}
def rectangle(port):return next(g for g in port['geometry'] if g['tag']=='rect')
def main():
 p=argparse.ArgumentParser();p.add_argument('--samples',type=Path,default=D/'remotion/out/height-preflight/samples.json');p.add_argument('--smoke',action='store_true');args=p.parse_args()
 report=json.loads(args.samples.read_text());model=json.loads((D/'model.json').read_text());sb=json.loads((D/'storyboard.json').read_text());height_options=json.loads((D/'height-options.json').read_text());assert report['status'] in ['completed','smoke-completed-awaiting-full-preflight']
 for path,h in report['sourceSHA'].items():test(sha(R/path)==h,'source-still-rendered-version',path)
 test(len(report['samples'])==len(report['audits']),'one-real-DOM-audit-per-image')
 for row in report['samples']:test(sha(Path(row['file']))==row['sha256'],'actual-PNG-identity',row['file'])
 shots=[s for c in sb['scenes'] for s in c['shots']];states={'before':model['before'],'allocated':model['insertion']['allocated'],**{'write'+str(i+1):w['snapshot'] for i,w in enumerate(model['insertion']['pointerWrites'])}}
 states['after']=model['after'];states['height1Complete']=height_options['cases']['height1']['after'];possible_by_type={'goal':['before'],'linear':['before'],'sparse':['before'],'upper':['before'],'descend':['before'],'locate':['before'],'height':['height1Complete','before','allocated'],'splice-bottom':['allocated','write1','write2'],'splice-upper':['write2','write3','write4'],'boundary':['after']}
 actor_samples=defaultdict(list);painted_positions=defaultdict(list);state_observed=defaultdict(set);phase_rows=[];all_values={n['id']:n['value'] for n in model['after']['nodes'].values()}
 for audit in report['audits']:
  frame=audit['frame'];shot=next(s for s in shots if s['from']<=frame<s['from']+s['durationInFrames']);local=frame-shot['from'];typ=shot['visualType'];ports={(p['node'],p['level']):p for p in audit['ports']};levels={k[1] for k in ports};nodes={n['id']:n for n in audit['nodes']}
  test(not audit['violations'],'actual-layout-clean',{'frame':frame,'violations':audit['violations']})
  # Revised legal phase: structure bridge has deliberately no diagram or actor.
  if typ=='sparse' and local<55:
   test(not audit['nodes'] and not audit['ports'] and not audit['edges'],'bridge-has-no-main-graph',frame)
   test(not audit['cursors'] and not audit['motions'] and not audit['comparisons'],'bridge-has-no-active-query',frame)
   text=[t['text'] for t in audit['texts']]
   test(all(t in text for t in ['逐个查找已结束','50 < 55 < 60','下一步：增加一层链接','能少经过一些节点吗？']),'bridge-actual-big-text-closes-query-and-asks-next-structure-question',frame)
   test(any(t['text']=='下一步：增加一层链接' and t['h']>=80 for t in audit['texts']),'bridge-next-step-is-actually-prominent',frame)
   active=next((x for x in shot['subtitles'] if x['from']<=local<=x['to']),None)
   test([c['text'] for c in audit['captions']]==([active['text']] if active else []),'actual-caption-text-and-frame-window',frame)
   for caption in audit['captions']:
    for text in audit['texts']:
     overlap=(min(caption['x']+caption['w'],text['x']+text['w'])>max(caption['x'],text['x'])+2 and min(caption['y']+caption['h'],text['y']+text['h'])>max(caption['y'],text['y'])+2)
     test(not overlap,'actual-caption-and-SVG-text-separated',frame)
   phase_rows.append({'frame':frame,'type':typ,'phase':'explicit-structure-bridge','nodes':0,'cursors':0})
   continue

  test(len(nodes)==len(audit['nodes']),'logical-node-groups-unique',frame);test(len(ports)==len(audit['ports']),'visible-port-unique',frame)
  test('head' in nodes and set(model['before']['nodes'])<=set(nodes),'all-original-nodes-still-visible',frame)
  test(set(nodes)<=set(model['after']['nodes']),'no-invented-node',frame)
  test(set(k[0] for k in ports if k[1]==0)==set(nodes),'all-visible-logical-nodes-have-base-value-port',frame)
  second=local>=float(shot['cueFrames']['sentences'][1])
  expected_new=False
  if typ=='height':
   if not second:expected_new=True
   else:
    a=float(shot['cueFrames']['sentences'][1]);b=float(shot['voice'][1]['localEnd']);t=max(0,min(1,(local-a-(b-a)*.2)/((b-a)*.25)));opacity=t*t*(3-2*t);expected_new=opacity>.04
  elif typ in ['splice-bottom','splice-upper','boundary']:expected_new=True
  test(('n55' in nodes)==expected_new,'new55-visibility-follows-height1-or-reset-allocated2-phase',frame)
  if typ in ['height','splice-bottom','splice-upper']:
   test(any(t['text']=='新节点 55' for t in audit['texts']),'new-node-label-remains-valid-during-and-after-splice',frame)
  test(not (typ=='boundary' or typ=='splice-upper' and local>=shot['cueFrames']['sentences'][1]) or not any('待接' in t['text'] for t in audit['texts']),'completed-diagram-has-no-pending-insertion-label',frame)
  for identity,node in nodes.items():
   expected='head' if identity=='head' else str(all_values[identity]);test(node['value']==expected,'actual-node-value-attribute',frame)
   for text in node['actualTexts']:test(text==('起点' if identity=='head' else expected),'actual-node-value-glyph',{'frame':frame,'text':text})
  for (identity,level),port in ports.items():
   expected='head' if identity=='head' else str(all_values[identity]);test(port['value']==expected,'actual-port-value-attribute',frame);test(port['actualTexts']==['起点' if identity=='head' else expected],'actual-port-value-glyph',frame)
   rect=rectangle(port);test(rect['x']>=0 and rect['y']>=0 and rect['x']+rect['w']<=1920 and rect['y']+rect['h']<=1080,'actual-node-rectangle-not-clipped',frame)
   if (identity,0) in ports and level:
    base=rectangle(ports[(identity,0)]);test(close(rect['x']+rect['w']/2,base['x']+base['w']/2),'same-node-levels-share-column',frame)
  edge_rows=[e for e in audit['edges'] if e['kind']=='actual'];edge_set={(e['from'],e['level'],e['to']) for e in edge_rows};test(len(edge_rows)==len(edge_set),'no-duplicate-actual-edge',frame)
  test(len({(a,l) for a,l,b in edge_set})==len(edge_set),'one-actual-successor-per-port',frame)
  candidates=[]
  for name in possible_by_type[typ]:
   state=states[name]
   if edge_set==graph_edges(state,levels):
    compatible=True
    for key,port in ports.items():
     identity,level=key
     if identity not in state['nodes'] or level>=state['nodes'][identity]['height'] or port['next']!=(state['nodes'][identity]['forward'][level] or 'null'):compatible=False
    if compatible:candidates.append(name)
  test(bool(candidates),'actual-drawn-links-and-ports-equal-legal-model-state',{'frame':frame,'shot':typ,'actual':sorted(edge_set)})
  if typ=='height':
   cue=shot['cueFrames']['labels']['层高'];a=float(shot['cueFrames']['sentences'][1]);b=float(shot['voice'][1]['localEnd']);reset_end=a+(b-a)*.2
   test(not audit['cursors'] and not audit['motions'] and not audit['comparisons'],'height-choice-is-not-an-active-query',frame)
   if local<a:
    test('height1Complete' in candidates,'actual-height1-is-complete-legal-alternative',frame)
    test(set(k[1] for k in ports if k[0]=='n55')=={0},'height1-new55-has-no-upper-port',frame)
    test({(e['from'],e['to']) for e in edge_rows if e['level']==1}=={('head','n40'),('n40','n70')},'height1-whole-table-still-has-original-upper-level',frame)
    test(any(r['kind']==('height1-complete' if local>=cue else 'height-ready') for r in audit['results']),'height1-formal-definition-appears-at-real-acoustic-cue',frame)
    test(any('层高' in t['text'] for t in audit['texts'])==(local>=cue),'formal-term-not-in-SVG-before-actual-cue',frame)
    test(any('新55只有1层' in t['text'] for t in audit['texts']),'height1-is-node-height-not-whole-table-height',frame)
    test(not any('只有新55' in t['text'] for t in audit['texts']),'height1-wording-does-not-claim-other-nodes-have-no-height1',frame)
   elif local<reset_end:
    test('before' in candidates and 'n55' not in nodes,'explicit-reset-restores8-original-nodes-without55',frame)
    test(any(r['kind']=='reset-before-height2' and any('原8个节点' in t and '尚未插入' in t for t in r['actualTexts']) for r in audit['results']),'reset-is-actually-labeled-and-held',frame)
   else:
    test('allocated' in candidates,'preselected-height2-has-no-forward-splice-yet',frame)
    test(any(r['kind']=='height2-allocated' and any('预先选2层' in t and '还没有接入' in t for t in r['actualTexts']) for r in audit['results']),'height2-preselection-and-not-reachable-are-actually-labeled',frame)
    if expected_new:test(set(k[1] for k in ports if k[0]=='n55')=={0,1} and nodes['n55']['inserted']=='false','allocated-height2-first-visible55-has-both-slots-and-is-unreachable',frame)
   test(any('本例预先选2层' in t['text'] for t in audit['texts']) if second else True,'height2-branch-choice-stated-before-any-write',frame)
  if typ=='splice-upper':
   test(any(t['text']=='本例层高为2，所以继续接上层' for t in audit['texts']) and any('预先选了两层' in t['text'] or '预先选了2层' in t['text'] for t in audit['texts']),'upper-wiring-is-explicitly-conditional-on-preselected2',frame)
  state_observed[typ].update(candidates);phase_rows.append({'frame':frame,'type':typ,'possibleStates':candidates,'edges':len(edge_set),'new55Visible':'n55' in nodes})
  successor={(a,l):b for a,l,b in edge_set};reachable=[];cur='head';seen={'head'}
  while (cur,0) in successor:
   cur=successor[(cur,0)];test(cur not in seen,'actual-painted-bottom-is-acyclic',frame)
   if cur in seen:break
   seen.add(cur);reachable.append(cur)
  for identity,node in nodes.items():test((node['inserted']=='true')==(identity=='head' or identity in reachable),'inserted-marker-matches-painted-reachability',{'frame':frame,'node':identity})
  for edge in audit['edges']:
   a=(edge['from'],edge['level']);b=(edge['to'],edge['level']);test(a in ports and b in ports,'drawn-edge-connects-existing-visible-ports',{'frame':frame,'edge':edge})
   if a not in ports or b not in ports:continue
   rect_a,rect_b=rectangle(ports[a]),rectangle(ports[b]);curves=[g for g in edge['geometry'] if g['tag']=='path'];test(len(curves)==2,'actual-path-and-arrowhead-painted',frame)
   if len(curves)<2:continue
   start=pathpoint(curves[0]['d'],0);end=pathpoint(curves[0]['d'],1)
   arrow=[float(n) for n in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',curves[1]['d'])]
   test(len(arrow)==6 and close(arrow[2],end[0]) and close(arrow[3],end[1]),'actual-arrowhead-tip-at-target-endpoint',frame)
   test(all(g.get('stroke') not in ['none','transparent','rgba(0, 0, 0, 0)'] for g in curves),'actual-link-and-arrowhead-have-painted-stroke',frame)
   test(close(start[0],rect_a['x']+rect_a['w']) and close(start[1],rect_a['y']+rect_a['h']/2),'painted-edge-starts-at-owner-port',frame);test(close(end[0],rect_b['x']) and close(end[1],rect_b['y']+rect_b['h']/2),'painted-edge-ends-at-target-port',frame)
   for key,port in ports.items():
    if key in [a,b]:continue
    rect=rectangle(port)
    crossed=[]
    for k in range(1,40):
     x,y=pathpoint(curves[0]['d'],k/40)
     if rect['x']+1<x<rect['x']+rect['w']-1 and rect['y']+1<y<rect['y']+rect['h']-1:crossed.append(k)
    test(not crossed,'actual-edge-does-not-falsely-cross-other-node-port',{'frame':frame,'edge':(a,b),'foreignPort':key,'points':crossed})
   if edge['kind']=='proposed' and 'strokeDasharray' in curves[0]:test(curves[0]['strokeDasharray'] not in ['none','0px',''],'proposed-link-is-actually-dashed',frame)
  # Independently interpret the declared sentence-window phase contract, then
  # compare the actual painted cursor/comparison/pointer state at this exact frame.
  def stage(sentence,count,fr,to):
   a=float(shot['cueFrames']['sentences'][sentence]);b=float(shot['voice'][sentence]['localEnd']);start=a+(b-a)*fr;length=(b-a)*(to-fr)/count
   rows=[{'index':i,'raw':(local-start)/length-i} for i in range(count)]
   chosen=next((r for r in rows if 0<=r['raw']<1),next((r for r in reversed(rows) if r['raw']>=0),rows[0]))
   return chosen,rows
  second=local>=float(shot['cueFrames']['sentences'][1]);expected_cursor=None;expected_compare=None;expected_motion_points=0
  if typ=='linear':
   st,rows=stage(1 if second else 0,1 if second else 5,.08,.96);event=model['linearSearch']['events'][5 if second else st['index']]
   expected_cursor=(event['cursorAfter'] if st['raw']>=.72 and event['canAdvance'] else event['current'],0)
   if st['raw']>=0:expected_compare=(event['current'],event['candidate'])
   expected_motion_points=int(event['canAdvance'] and .18<=st['raw']<.72)
   if second and st['raw']>=.72:expected_cursor=None;expected_compare=None
  elif typ=='upper':
   expected_cursor=('head',1)
   if second:
    st,rows=stage(1,1,.08,.91);event=model['search']['events'][0];expected_cursor=('n40' if st['raw']>=.72 else 'head',1)
    if st['raw']>=0:expected_compare=(event['current'],event['candidate'])
    expected_motion_points=int(.18<=st['raw']<.72)
  elif typ=='descend':
   st,rows=stage(1 if second else 0,1,.08,.91);expected_cursor=('n40',0 if second and st['raw']>=.72 else 1)
   if not second and st['raw']>=0:expected_compare=('n40','n70')
   expected_motion_points=int(second and .18<=st['raw']<.72)
  elif typ=='locate':
   st,rows=stage(1 if second else 0,1,.08,.93);event=model['search']['events'][3 if second else 2];expected_cursor=(event['cursorAfter'] if st['raw']>=.72 and event['canAdvance'] else event['current'],0)
   if st['raw']>=0:expected_compare=(event['current'],event['candidate'])
   expected_motion_points=int(event['canAdvance'] and .18<=st['raw']<.72)
  elif typ=='sparse':
   expected_cursor=None
   a=float(shot['cueFrames']['sentences'][0]);b=float(shot['voice'][0]['localEnd']);t=max(0,min(1,(local-a-(b-a)*.35)/((b-a)*.59)));up=t*t*(3-2*t)
   test(set(k[0] for k in ports if k[1]==1)==({'head','n40','n70'} if up>.04 else set()),'upper-layer-visible-only-during-revised-structure-fade',frame)
   test(not audit['comparisons'] and not audit['motions'],'structure-preparation-has-no-query-actors',frame)
  elif typ=='height':expected_cursor=None
  elif typ in ['splice-bottom','splice-upper']:
   st,rows=stage(0,2,.08,.96);offset=2 if typ=='splice-upper' else 0;completed=offset+sum(r['raw']>=.72 for r in rows);write=model['insertion']['pointerWrites'][offset+st['index']];expected_cursor=(write['owner'],write['level']);expected_state=model['insertion']['allocated'] if completed==0 else model['insertion']['pointerWrites'][completed-1]['snapshot']
   test(edge_set==graph_edges(expected_state,levels),'pointer-state-commits-at-exact-declared-arrival-frame',{'frame':frame,'expectedCompleted':completed})
   expected_motion_points=int(.18<=st['raw']<.72)
  if typ=='linear' and local>=490:
   test(any(r['kind']=='linear-search-complete' and r['actualTexts']==['逐个查找结束：55在50与60之间'] for r in audit['results']),'linear-tail-explicitly-completed-before-structure-cut',frame)
   test(not audit['cursors'] and not audit['comparisons'] and not audit['motions'],'completed-linear-query-actors-cleared',frame)
   test(all(g.get('stroke')!='rgb(255, 204, 112)' for e in audit['edges'] for g in e['geometry']),'completed-linear-has-no-active-gold-link',frame)
  if typ=='upper':
   test(any(t['text']=='现在用跳表重新查找55' for t in audit['texts']) and any('同一个55' in t['text'] for t in audit['texts']),'requery-actual-heading-explicit-same55-and-restart',frame)
  observed_cursor=[(c['node'],c['level']) for c in audit['cursors']]
  test(observed_cursor==([expected_cursor] if expected_cursor else []),'actual-cursor-agrees-with-independent-frame-phase',{'frame':frame,'expected':expected_cursor,'observed':observed_cursor})
  test([(c['current'],c['candidate']) for c in audit['comparisons']]==([expected_compare] if expected_compare else []),'actual-comparison-agrees-with-independent-frame-phase',frame)
  test(sum(g['tag']=='circle' for m in audit['motions'] for g in m['geometry'])==expected_motion_points,'actual-moving-point-exists-only-during-motion-phase',frame)
  test(len(audit['cursors'])<=1,'single-visible-cursor',frame)
  for cursor in audit['cursors']:
   key=(cursor['node'],cursor['level']);test(key in ports,'cursor-on-real-visible-port',frame)
   if key in ports:
    rect=rectangle(ports[key]);shape=next(g for g in cursor['geometry'] if g['tag']=='rect');test(close(shape['x']+shape['w']/2,rect['x']+rect['w']/2) and close(shape['y']+shape['h']/2,rect['y']+rect['h']/2),'cursor-rectangle-actually-encloses-declared-port',frame)
  circles=[g for m in audit['motions'] for g in m['geometry'] if g['tag']=='circle'];test(len(circles)<=1,'single-moving-point',frame)
  for motion in audit['motions']:
   key=(shot['id'],motion['kind'],motion['from'],motion['to'],motion['level']);actor_samples[key].append((frame,motion['progress']))
   points=[g for g in motion['geometry'] if g['tag']=='circle'];test(0<=motion['progress']<=1,'actual-motion-progress-bounded',frame)
   if not points:continue
   point=points[0];x,y=float(point['cx']),float(point['cy'])
   if motion['kind']=='descend':
    node=motion['from'];test(node==motion['to']=='n40','descend-stays-at-original40',frame)
    top,bottom=rectangle(ports[(node,1)]),rectangle(ports[(node,0)]);start=top['y']+top['h']+8;end=bottom['y']-8
    test(close(x,top['x']+top['w']/2) and close(y,start+(end-start)*motion['progress']),'actual-descend-circle-follows-same-column',frame)
   else:
    matching=[e for e in audit['edges'] if e['from']==motion['from'] and e['to']==motion['to'] and e['level']==motion['level']]
    test(bool(matching),'moving-point-has-actual-painted-route',frame)
    if matching:
     route=next(g for g in matching[0]['geometry'] if g['tag']=='path')
     if 'C' in route['d']:
      expect=pathpoint(route['d'],motion['progress']);on_path=close(x,expect[0]) and close(y,expect[1]);painted_progress=motion['progress']
     else:
      # A painted straight segment permits nonuniform speed along its line.
      # Require actual geometric membership, then track its physical projection.
      start,end=pathpoint(route['d'],0),pathpoint(route['d'],1);dx,dy=end[0]-start[0],end[1]-start[1];painted_progress=((x-start[0])*dx+(y-start[1])*dy)/(dx*dx+dy*dy);expect=(start[0]+painted_progress*dx,start[1]+painted_progress*dy);on_path=0<=painted_progress<=1 and close(x,expect[0]) and close(y,expect[1])
     test(on_path,'actual-moving-circle-on-painted-link',frame);painted_positions[key].append((frame,painted_progress))
  for compare in audit['comparisons']:
   test(compare['target']=='55','actual-comparison-target55',frame);candidate=compare['candidate'];test(candidate in nodes,'candidate-actually-drawn',frame)
   if candidate in all_values:test((compare['canAdvance']=='true')==(all_values[candidate]<55),'candidate-decision-agrees-with-actual-value',frame)
   test(any(a==compare['current'] and b==candidate for a,l,b in edge_set),'candidate-is-real-current-successor',frame)
  cue_kinds={'goal':('链表','linked-list','goal'),'upper':('跳表','skiplist','upper-ready')}
  if typ in cue_kinds and (typ!='upper' or not second):
   term,shown,waiting=cue_kinds[typ];cue=shot['cueFrames']['labels'][term]
   test(any(r['kind']==(shown if local>=cue else waiting) for r in audit['results']),'formal-term-label-at-real-cue-frame',{'frame':frame,'term':term,'cue':cue})
  active=next((x for x in shot['subtitles'] if x['from']<=local<=x['to']),None)
  test([c['text'] for c in audit['captions']]==([active['text']] if active else []),'actual-caption-text-and-frame-window',frame)
  for caption in audit['captions']:
   test(caption['x']>=0 and caption['x']+caption['w']<=1920+.1 and caption['y']>=0 and caption['y']+caption['h']<=1080+.1,'actual-caption-inside-canvas',frame)
   for text in audit['texts']:
    overlap=(min(caption['x']+caption['w'],text['x']+text['w'])>max(caption['x'],text['x'])+2 and min(caption['y']+caption['h'],text['y']+text['h'])>max(caption['y'],text['y'])+2)
    test(not overlap,'actual-caption-and-SVG-text-separated',frame)
 for key,rows in actor_samples.items():
  rows.sort()
  for left,right in zip(rows,rows[1:]):test(left[1]<=right[1]+1e-10,'motion-progress-does-not-reverse-within-operation',{'actor':key,'frames':[left,right]})
 for key,rows in painted_positions.items():
  rows.sort()
  for left,right in zip(rows,rows[1:]):test(left[1]<=right[1]+1e-10,'actual-painted-motion-position-does-not-reverse',{'actor':key,'frames':[left,right]})
 if not args.smoke:
  test('write1' in state_observed['splice-bottom'] and 'write2' in state_observed['splice-bottom'],'actual-bottom-both-writes-witnessed')
  test('write3' in state_observed['splice-upper'] and 'write4' in state_observed['splice-upper'],'actual-upper-both-writes-witnessed')
 for path,h in report['sourceSHA'].items():test(sha(R/path)==h,'source-still-unchanged-at-end',path)
 output={'status':'passed' if not failures else 'failed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Independent bounded height-choice actual glyph/edge/cursor/phase checks; legalheight1 complete, readable resetbefore and preselectedheight2 allocation are distinct. No production algorithm import or Scene.state.','samplesSHA256':sha(args.samples),'checkerSHA256':sha(Path(__file__)),'inputs':{n:sha(D/n) for n in ['model.json','storyboard.json','plan.json']},'actualSamples':len(report['audits']),'geometryToleranceCSSPixels':.06,'assertionsExecuted':sum(N.values()),'assertionsByCategory':dict(N),'phaseObservations':phase_rows,'failures':failures,'limitations':['Only sampled actual DOM boundaries; continuous encoded clip and visual inspection are separate.','No TTS semantic or encoded final-film conclusion.']}
 out=D/('qa-height-dom-smoke.json' if args.smoke else 'qa-height-dom.json');out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':output['status'],'samples':output['actualSamples'],'assertions':sum(N.values()),'failures':len(failures)}))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
