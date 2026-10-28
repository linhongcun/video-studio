from pathlib import Path
import json,hashlib,subprocess,datetime
OUT=Path('/workspace/work/mq-cover-plan/delivery-update')
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
initial=json.loads((OUT/'before.json').read_text())
prior=json.loads(Path('/workspace/work/mq-cover-plan/applied/application-report.json').read_text())
expected=next(x for x in prior['entries'] if x['number']==308)['afterBodySha256']
release='https://github.com/linhongcun/video-studio/releases/tag/v0.84.1'
episode='https://linhongcun.github.io/video-studio/episodes/message-queue/'
def api(method,payload=None):
 cmd=['gh','api','--method',method,'repos/linhongcun/video-studio/issues/308']
 if payload:cmd+=['--input',str(payload)]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=55)
 if r.returncode:raise RuntimeError(r.stderr.strip())
 return r.stdout,json.loads(r.stdout)
raw,before=api('GET');(OUT/'prepatch.json').write_text(raw)
assert before['state']=='open' and 'Kafka' in before['title']
parallel=sha(before['body'])!=expected or before['title']!=initial['title']
body=before['body']
changes=[
 ('本轮同步将既有EP.10 / message-queue改造成Kafka入门并统一封面','本轮已将既有EP.10 / message-queue改造成Kafka入门并统一封面'),
 ('**Kafka版MQ01正在制作；其余8期未开工，具体脚本与配置仍待各期定稿。**',f'**Kafka版MQ01已随[v0.84.1]({release})交付并通过线上核验；其余8期未开工，具体脚本与配置仍待各期定稿。** [观看新版视频与图文]({episode})'),
 ('Kafka改造进行中；旧版已交付',f'[v0.84.1]({release})已交付；线上核验通过'),
 ('仅本轮MQ01开工，不自动启动其余8题。','本轮仅交付MQ01，不自动启动其余8题。')]
for old,new in changes:
 assert body.count(old)==1,'Ambiguous concurrent status text; stop instead of overwriting: '+old
 body=body.replace(old,new,1)
assert '| 9 | [MQ15' in body
assert body.count('| 未开工 |')==before['body'].count('| 未开工 |')==8
assert 'Kafka版MQ01正在制作' not in body and 'Kafka改造进行中' not in body
for n in [298,299,317,318,319,320,321,322,324,325,326,327,328,329]:assert f'#{n}' in body
payload={'title':before['title'],'body':body}
(OUT/'patch.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
raw,response=api('PATCH',OUT/'patch.json');(OUT/'patch-response.json').write_text(raw)
raw,after=api('GET');(OUT/'after.json').write_text(raw)
assert after['title']==before['title'] and after['body']==body and after['state']==before['state']=='open'
assert response['title']==after['title'] and response['body']==after['body']
receipt={'checkedAt':now(),'issue':308,'issueUrl':after['html_url'],'action':'title/body PATCH; unchanged Kafka title, four exact delivery-status text substitutions','expectedAppliedBodySha256':expected,'initialBodySha256':sha(initial['body']),'prepatchBodySha256':sha(before['body']),'matchedPriorAppliedBody':sha(before['body'])==expected,'concurrentChangeMerged':parallel,'preservedKafkaTitle':after['title'],'afterBodySha256':sha(after['body']),'patchPayloadSha256':hashlib.sha256((OUT/'patch.json').read_bytes()).hexdigest(),'substitutions':[{'from':a,'to':b} for a,b in changes],'release':release,'episode':episode,'remainingEightUnstarted':True,'mq15NumberPreserved':True,'closed309Touched':False,'cancelledFourteenTouched':False,'commentsCreated':0,'issueState':after['state'],'passed':True}
(OUT/'operation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'issueUrl':after['html_url'],'matchedPriorAppliedBody':receipt['matchedPriorAppliedBody'],'concurrentChangeMerged':parallel,'afterBodySha256':receipt['afterBodySha256'],'receipt':str(OUT/'operation-receipt.json'),'receiptSha256':hashlib.sha256((OUT/'operation-receipt.json').read_bytes()).hexdigest()},ensure_ascii=False))
