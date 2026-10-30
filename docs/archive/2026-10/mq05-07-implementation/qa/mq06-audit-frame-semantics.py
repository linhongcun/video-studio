"""Check actual rendered DOM fields plus causal invariants; no author mutations."""
from pathlib import Path
import argparse,hashlib,json
ap=argparse.ArgumentParser();ap.add_argument('--dir',required=True,type=Path);ap.add_argument('--name',default='preflight-v1');args=ap.parse_args();D=args.dir.resolve();Q=D/'qa-independent'
report=json.loads((Q/(args.name+'.json')).read_text());model=json.loads((D/'model.json').read_text());states={s['id']:s for s in model['timeline']};issues=[];observed={}
assert report['sourceUnchanged']and report['sourceHashes']['model.json']==hashlib.sha256((D/'model.json').read_bytes()).hexdigest()
def fail(sample,detail):issues.append({'frame':sample['frame'],'state':sample['metrics']['modelState'],'detail':detail})
field_map={'data-log-records':lambda s:s['log'],'data-buffer':lambda s:s['consumer']['buffer'],'data-returned':lambda s:s['consumer']['returned'],'data-position':lambda s:s['consumer']['position'],'data-scan-offset':lambda s:s['consumer']['scanOffset'],'data-projection':lambda s:s['application']['projection'],'data-app-mode':lambda s:s['application']['mode'],'data-dispatch-order':lambda s:s['application']['dispatchOrder'],'data-completion-order':lambda s:s['application']['completionOrder'],'data-route':lambda s:s['producer']['routing']}
json_fields={'data-log-records','data-buffer','data-returned','data-position','data-dispatch-order','data-completion-order','data-route'}
for sample in report['samples']:
 metrics=sample['metrics'];sid=metrics['modelState'];texts=[t['text']for t in metrics['texts']];joined='\n'.join(texts)
 if sid is None:continue
 s=states[sid];entries=[e['attrs']for e in metrics['data']if e['attrs'].get('data-model-state')==sid]
 if len(entries)!=1:fail(sample,'Expected one actual model wrapper');continue
 attrs=entries[0];observed[sid]=observed.get(sid,0)+1
 for field,get in field_map.items():
  actual=attrs.get(field)
  if field in json_fields:actual=json.loads(actual)
  elif field=='data-scan-offset':actual=int(actual)
  if actual!=get(s):fail(sample,field+' does not reflect source snapshot')
 buffer=json.loads(attrs['data-buffer']);returned=json.loads(attrs['data-returned']);position=json.loads(attrs['data-position']);completion=json.loads(attrs['data-completion-order']);projection=attrs['data-projection']
 if returned not in [[],['E01','E02']]:fail(sample,'This selected two-record collection must not return a partial prefix')
 if sid in ['collector-paid','collector-buffered-both']and(position['P0']!=0 or returned):fail(sample,'Outer position/returned advanced during internal collection')
 if sid=='collector-both'and(position['P0']!=2 or returned!=['E01','E02']or buffer!=returned):fail(sample,'Collection completion must update position2 and preserve returned order')
 if sample.get('shot')=='07'and sid in ['collector-paid','collector-buffered-both']and not any('客户端内部' in t for t in texts):fail(sample,'Internal collection was visually labeled as application delivery')
 if sample.get('shot')=='07'and sid=='collector-both'and not any('交给应用的P0返回列表'in t for t in texts):fail(sample,'Returned list not visibly distinguished from internal collection')
 if completion:
  expected='PAID'if completion[-1]=='E01'else'REFUNDED'
  if projection!=expected:fail(sample,'Projection changed without corresponding final write')
 elif projection!='PENDING':fail(sample,'Projection changed before a completed write')
 app=any(e['attrs'].get('data-panel')=='application-projection'for e in metrics['data'])
 if app:
  label={'PENDING':'待支付','PAID':'已支付','REFUNDED':'已退款'}[projection]
  if not any(t['text']==label and t['x']>=1400 and 330<=t['y']<=420 for t in metrics['texts']):fail(sample,'Visible order-status value does not match actual projection')
  a=s['application']
  if a['mode']!='concurrent'and a['tasks']['E02']in ['running','complete']and a['tasks']['E01']!='complete':fail(sample,'Refund started before actual payment completion in serial path')
  for event in ['E01','E02']:
   if a['tasks'][event]=='complete'and ('已写：'+('已支付'if event=='E01'else'已退款'))not in joined:fail(sample,event+' completed marker not actually visible')
 if sample.get('shot')=='05'and not s['producer']['routing']:
  if '都计算出P0'in joined or 'P0：E01 / E02'in joined:fail(sample,'Specific routing result appears before route calculation completes')
 if sid in ['async-refund-done','async-paid-resumed']and '最后写回已支付'in joined:fail(sample,'Async final-result title appears before late payment write')
 if sid.startswith('serial-')and sid!='serial-refund-done'and '三段顺序一致，最终已退款'in joined:fail(sample,'Serial final result appears before refund completion')
 if sid.startswith('ordered-')and sid!='ordered-refund-done'and '按E01、E02写完，订单状态最终已退款'in joined:fail(sample,'Per-order final result appears before refund completion')
 if sid in ['async-reset','ordered-reset']:
  log=json.loads(attrs['data-log-records'])
  if [x['eventId']for x in log['P0']]!=['E01','E02']or position['P0']!=0 or returned or projection!='PENDING':fail(sample,'Independent reset changed original log or kept previous projection/delivery')
scope={'source':'fixed Kafka4.4 implementation plus finite teaching states','actualRuntime':'RF1 fixture max.poll.records1, two real polls accumulated before application schedule contrast','teachingCollection':'Legal source path collects2 records in one outer collection; not claimed as the fixture poll size','business':'Page-status teaching projection and real Java latch fixture only; no payment/refund execution or durable DB proof','formalMedia':'Fresh source previews only, not formal MP4 acceptance'}
result={'machinePass':report['machinePass']and not issues,'sourceHashes':report['sourceHashes'],'samples':len(report['samples']),'observedModelStates':observed,'issues':issues,'scope':scope,'visualReviewed':False}
(Q/'frame-semantics-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'machinePass':result['machinePass'],'samples':result['samples'],'states':len(observed),'issues':issues},ensure_ascii=False))
