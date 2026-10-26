#!/usr/bin/env python3
"""Independent actual-DOM oracle for the eight-cell teaching revision.

No Scene.state, stages implementation, or producer module is imported.
Recorded operation arrivals locate before/after samples; legal states are
computed as independent set union/removal over verified model positions.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from zoneinfo import ZoneInfo

D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').exists())
COUNTS=Counter()
FAILURES=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,category,detail=None):
    COUNTS[category]+=1
    if not ok:FAILURES.append({'category':category,'detail':detail})
def overlap(a,b):
    return min(a['x']+a['w'],b['x']+b['w'])>max(a['x'],b['x'])+2 and min(a['y']+a['h'],b['y']+b['h'])>max(a['y'],b['y'])+2
def before_after(rows,t):
    before=next((r for r in reversed(rows)if r['local']<t),None)
    after=next((r for r in rows if r['local']>=t),None)
    return before,after
def numbers(s):return [float(v)for v in re.findall(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)',s)]

def main():
    path=D/'remotion/out/preflight/samples.json';R=json.loads(path.read_text())
    M=json.loads((D/'model.json').read_text());S=json.loads((D/'storyboard.json').read_text())
    E=json.loads((D/'qa-animation-events.json').read_text());P=json.loads((D/'qa-preflight-plan.json').read_text())
    check(R['status']=='completed','complete-render-report')
    check(sorted(s['frame']for s in R['samples'])==P['frames'],'complete-planned-matrix')
    check(len(R['samples'])==len(R['audits'])==P['sampleCount'],'actual-sample-audit-count')
    check(not R['violations'],'actual-layout-gate',len(R['violations']))
    for name,wanted in R['sourceSHA'].items():
        p=(ROOT/name).resolve();check(p.is_relative_to(ROOT)and p.exists()and sha(p)==wanted,'actual-source-identity',name)
    check(E['inputs']['storyboard.json']==sha(D/'storyboard.json'),'event-storyboard-identity')
    check(E['inputs']['Main.tsx']==sha(D/'remotion/src/Main.tsx'),'event-clock-source-identity')
    shots=[];offset=0
    for scene in S['scenes']:
        for original in scene['shots']:
            shot={**original,'id':str(original['id']).zfill(2),'from':offset};shots.append(shot);offset+=shot['durationInFrames']
    check(offset==P['bodyFrames']==E['bodyFrames'],'actual-body-timing-total',offset)
    byshot={s['id']:s for s in shots};events={s['id']:s for s in E['shots']}
    normal=set(M['snapshots']['afterB']);samples={r['frame']:r for r in R['samples']}
    groups=defaultdict(list);rows=[];geometry={};last_dots={};boundary_witnesses=[]
    for A in sorted(R['audits'],key=lambda v:v['frame']):
        frame=A['frame'];sample=samples[frame];sid=str(sample['shot']).zfill(2);shot=byshot[sid];f=frame-shot['from'];kind=shot['visualType']
        check(sample['local']==f and sample['visualType']==kind,'actual-frame-shot-binding',frame)
        check(Path(sample['file']).is_file()and sha(Path(sample['file']))==sample['sha256'],'actual-png-identity',frame)
        bits=A['bits'];indices=[v['index']for v in bits]
        check(indices==sorted(set(indices))and all(0<=v<8 for v in indices),'actual-index-domain',frame)
        check(indices==list(range(len(indices)))and (1<=len(indices)<=8 if kind=='bits'else len(indices)==8),'actual-visible-eight-cell-row',frame)
        ones=set()
        for b in bits:
            v=b['bitValueText'].strip();check(v in {'0','1'}and v==str(b['value']),'actual-bit-glyph-attribute',frame)
            check(b['indexText'].strip()==str(b['index']),'actual-index-glyph',frame)
            if v=='1':ones.add(b['index'])
            box=tuple(b[k]for k in ['x','y','w','h'])
            if b['index']in geometry:check(all(abs(x-y)<.05 for x,y in zip(box,geometry[b['index']])),'stable-cell-location',(frame,b['index']))
            else:geometry[b['index']]=box
        members=[]
        for member in A['members']:
            actual=re.findall(r'\b[A-D]\b',member['actualTexts'][-1])if member['actualTexts']else[]
            check(actual==member['keys'],'actual-member-glyph-attribute',frame);members.append(actual)
        check(len(members)<=1,'single-explanatory-members-list',frame)
        flows=A['flows'];check(len(flows)<=1,'single-active-hash-flow',frame)
        flow=flows[0]if flows else None
        if flow:
            key=flow['elementGlyph'].strip();check(key in {'A','B','C','D'}and key==flow['element'],'actual-flow-element-glyph',frame)
            comparison=kind=='extra-position';slot=flow['slot']if comparison else 0
            item=next(v for v in M['items']if v['key']==key);wanted=item['comparisonPositions'if comparison else'singlePositions'][slot]
            check(flow['position']==wanted,'actual-flow-model-position',(frame,key,slot))
            glyph=flow['positionGlyph'].strip()
            if glyph:check(re.fullmatch(r'位置\s*'+str(wanted),glyph)is not None,'actual-position-glyph',(frame,glyph))
            if comparison:
                check(('固定规则①'if slot==0 else'固定规则②')in flow['actualTexts'],'actual-rule-identity',frame)
            curves=[g for g in flow['geometry']if g.get('d')and'Q'in g['d']]
            check(len(curves)<=1,'single-output-curve',frame)
            target=next(b for b in bits if b['index']==wanted)
            if curves:
                c=curves[0];p=numbers(c['d']);check(len(p)==6,'actual-quadratic-path-shape',frame)
                if len(p)==6:
                    check(abs(p[-2]-(target['x']+target['w']/2))<.05 and abs(p[-1]-target['y'])<.05,
                          'actual-path-ends-at-visible-target-cell',(frame,wanted))
                    check(bool(glyph),'output-path-has-visible-position',frame)
            circles=[g for g in flow['geometry']if g['tag'].lower()=='circle']
            check(len(circles)<=1,'at-most-one-moving-element',frame)
            for circle in circles:
                x,y=float(circle['cx']),float(circle['cy'])
                if y<=400:
                    line=next((g for g in flow['geometry']if g['tag'].lower()=='line'),None)
                    check(line is not None and abs(y-float(line['y1']))<.05 and float(line['x1'])<=x<=float(line['x2']),
                          'actual-input-dot-follows-arrow',frame)
                elif curves:
                    p=numbers(curves[0]['d']);lo,hi=0.,1.
                    check(p[1]<=p[3]<=p[5]and p[1]<=y<=p[5],'drawn-output-curve-monotone-range',frame)
                    for _ in range(55):
                        t=(lo+hi)/2;curve_y=(1-t)**2*p[1]+2*(1-t)*t*p[3]+t*t*p[5]
                        if curve_y<y:lo=t
                        else:hi=t
                    t=(lo+hi)/2;curve_x=(1-t)**2*p[0]+2*(1-t)*t*p[2]+t*t*p[4]
                    check(abs(x-curve_x)<.05,'actual-output-dot-on-drawn-curve',frame)
                    signature=(sid,flow['kind'],key,wanted,slot)
                    if signature in last_dots:check(y+1e-5>=last_dots[signature],'actual-motion-forward-within-operation',frame)
                    last_dots[signature]=y
                else:check(False,'output-dot-requires-drawn-curve',frame)
        expected_caption=next((c['text']for c in shot['subtitles']if f>=c['from']and f<=c['to']),None)
        captions=A.get('captions',[]);check([c['text']for c in captions]==([expected_caption]if expected_caption else[]),'actual-caption-text-and-window',frame)
        for caption in captions:
            check(caption['x']>=0 and caption['x']+caption['w']<=1920 and caption['y']>=0 and caption['y']+caption['h']<=1080,'actual-caption-canvas-bounds',frame)
            for t in A['texts']:check(not overlap(caption,t),'actual-caption-svg-text-separation',(frame,t['text']))
        op_events=[e for e in events[sid]['events']if'arrive'in e]
        writes=[e for e in op_events if e['kind']=='write'];clears=[e for e in op_events if e['kind']=='clear']
        expected=set()
        if kind in {'insert-b','query-zero','query-one','tradeoff'}:expected=normal
        elif kind=='insert-a':expected={e['position']for e in writes if f>=e['arrive']}
        elif kind=='unsafe-delete':
            restore=next(e['begin']for e in events[sid]['events']if e['kind']=='restore')
            expected=normal if f>=restore else normal-{e['position']for e in clears if f>=e['arrive']}
        elif kind=='extra-position':expected={e['position']for e in writes if f>=e['arrive']}
        check(ones==expected,'independent-set-state-oracle',(frame,sorted(ones),sorted(expected)))
        if kind=='insert-b':
            arrived=f>=writes[0]['arrive'];check(members==[['A','B']if arrived else['A']],'B-member-only-after-completed-write',frame)
        elif kind in {'query-zero','query-one'}:check(members==[['A','B']],'queries-retain-original-members',frame)
        elif kind=='extra-position':
            a_done=all(f>=e['arrive']for e in writes if e['element']=='A');b_done=all(f>=e['arrive']for e in writes if e['element']=='B')
            wanted=['A','B']if b_done else['A']if a_done else[]
            check(members==[wanted],'rebuilt-member-completion-gate',frame)
            if flow and flow['element']=='C':check(b_done and ones=={1,2,3},'no-C-query-before-complete-rebuild',frame)
        results=A['results']
        for result in results:
            label=' '.join(result['actualTexts']);rk=result['kind']
            if rk=='absent':
                check(flow is not None,'absence-needs-actual-query-flow',frame)
                if flow:check(flow['position']not in ones and flow['kind']=='read','actual-absence-result-has-observed-zero',frame)
            elif rk=='possible':
                check(flow is not None and flow['element']=='C'and flow['position']in ones,'actual-possible-result-has-C-mark',frame)
            elif rk=='invalid-reject':
                check(kind=='unsafe-delete'and flow is not None and flow['element']=='B'and 3 not in ones and members==[['B']],
                      'wrong-clear-rejection-explicit-witness',frame)
                check(any('错误'in t['text']for t in A['texts']),'wrong-operation-clearly-labeled',frame)
            elif rk=='reset':
                check(kind=='unsafe-delete'and ones==normal and members==[['A','B']],'bit-and-member-reset-together',frame)
                check(not(flow and any(g.get('d')and'Q'in g['d']for g in flow['geometry'])),'reset-clears-active-output-path',frame)
        row={'frame':frame,'local':f,'shot':sid,'visualType':kind,'ones':ones,'members':members,'flow':flow,'results':results,'audit':A}
        groups[sid].append(row);rows.append(row)

    for shot in shots:
        sid=shot['id'];part=groups[sid];ev=events[sid]
        check(part[0]['local']==0 and part[-1]['local']==shot['durationInFrames']-1,'shot-start-tail-coverage',sid)
        for i,voice in enumerate(shot['voice']):
            check(abs(ev['sentenceSpans'][i][0]-shot['cueFrames']['sentences'][i])<1e-7 and abs(ev['sentenceSpans'][i][1]-voice['localEnd'])<1e-7,
                  'real-sentence-window-identity',(sid,i))
        for event in ev['events']:
            if'arrive'not in event:continue
            check(ev['sentenceSpans'][event['sentence']][0]<=event['begin']<event['arrive']<=event['end']<=ev['sentenceSpans'][event['sentence']][1]+1e-7,
                  'operation-inside-actual-sentence-envelope',(sid,event['kind'],event['element'],event['position']))
            left,right=before_after(part,event['arrive']);check(left is not None and right is not None,'actual-arrival-bracket',(sid,event['position']))
            if left is None or right is None:continue
            if event['kind']=='write':
                check(event['position']in right['ones'],'actual-write-visible-after-arrival',(sid,right['frame'],event['position']))
                if event['position']not in left['ones']:check(right['ones']-left['ones']=={event['position']},'only-target-changes-at-write-boundary',(sid,event['position']))
            if event['kind']=='clear':check(event['position']in left['ones']and event['position']not in right['ones'],'actual-clear-boundary',(sid,event['position']))
            boundary_witnesses.append({'shot':sid,'kind':event['kind'],'element':event['element'],'position':event['position'],'localArrival':event['arrive'],'beforeActualFrame':left['frame'],'afterActualFrame':right['frame']})
        if shot['visualType']=='unsafe-delete':
            restore=next(e['begin']for e in ev['events']if e['kind']=='restore')
            check(restore>=math.ceil(shot['voice'][1]['localEnd'])+2,'restore-after-completed-spoken-counterexample',(restore,shot['voice'][1]['localEnd']))
            left,right=before_after(part,restore);check(left is not None and right is not None,'actual-reset-bracket',sid)
            if left and right:check(left['ones']==set()and right['ones']==normal and right['members']==[['A','B']],'actual-reset-restores-array-and-truth',sid)
        if shot['visualType']=='extra-position':
            check(part[0]['ones']==set()and part[0]['members']==[[]],'separate-rebuild-starts-empty')
            check(part[-1]['ones']=={1,2,3}and part[-1]['members']==[['A','B']],'separate-rebuild-completes-original-set')
            writes=[e for e in ev['events']if e['kind']=='write'];reads=[e for e in ev['events']if e['kind']=='read']
            check([(e['element'],e['position'])for e in writes]==[('A',3),('A',2),('B',3),('B',1)],'rebuilt-write-operation-contract')
            check([(e['element'],e['position'])for e in reads]==[('C',3),('C',5)],'rebuilt-query-operation-contract')
            check(max(e['arrive']for e in writes)<min(e['begin']for e in reads),'rebuild-finishes-before-any-C-probe')
            check(any(r['kind']=='absent'for r in part[-1]['results']),'rebuilt-C-zero-conclusion-visible')
    report={'status':'passed'if not FAILURES else'failed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'checkedAtBeijing':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
            'scope':'Independent actual SVG/DOM glyph, member, path/dot geometry and source-informed phase-boundary state checks; no Scene.state or producer imports.',
            'inputs':{name:sha(D/name)for name in ['model.json','storyboard.json','qa-animation-events.json','qa-preflight-plan.json']},'samplesSHA256':sha(path),'checkerSHA256':sha(Path(__file__)),
            'actualSamples':len(rows),'shots':len(shots),'bodyFrames':offset,'assertionsExecuted':sum(COUNTS.values()),'assertionsByCategory':dict(sorted(COUNTS.items())),
            'failures':FAILURES,'arrivalWitnesses':boundary_witnesses,
            'actualStates':[{'globalFrame':r['frame'],'localFrame':r['local'],'shot':r['shot'],'actualOneGlyphs':sorted(r['ones']),'actualMemberGlyphs':r['members'],
                             'actualInputGlyph':r['flow']['elementGlyph']if r['flow']else None,'actualPositionGlyph':r['flow']['positionGlyph']if r['flow']else None,'visibleResultKinds':[x['kind']for x in r['results']]}for r in rows],
            'limits':['Event timestamps select observed before/after phases; they are not an independent speech recognizer.','Actual DOM geometry/glyph agreement does not replace separately recorded image/continuous-decoded-stage visual review.','No audio listening, final encoded film or site behavior is checked here.']}
    (D/'qa-dom-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (D/'qa-dom-independent.md').write_text('# 8格核心修订独立DOM复核\n\n状态：'+report['status']+'。实际'+str(len(rows))+'帧、9镜；执行'+format(report['assertionsExecuted'],',')+'项检查，失败'+str(len(FAILURES))+'项。\n\n不用Scene.state或制作函数：实际核对位值/下标glyph、成员文字、元素/位置文字和实际SVG路径/运动点几何。通过集合增删oracle对照每个采样状态，并核单路径、非目标位保持、碰撞不计数、D0/C1、错清B误拒及话音结束后的恢复。08从空8格开始，A3/2与B3/1完整加入后才允许C3/5查询；实际字幕和画面文字分离另行核对。\n\n事件表只定位真实句窗口和操作边界，不作为画面正确的自证。图像和连续解码阶段实看另见动态独立报告；本报告不冒称音频或正式成片通过。\n')
    print(json.dumps({'status':report['status'],'actualSamples':len(rows),'assertionsExecuted':report['assertionsExecuted'],'failureCount':len(FAILURES),'firstFailures':FAILURES[:8]},ensure_ascii=False))
    if FAILURES:raise SystemExit(1)

if __name__=='__main__':main()
