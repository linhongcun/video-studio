#!/usr/bin/env python3
"""Independent direct-data assertions, not the author's model.verify or Kafka runtime."""
from pathlib import Path
import datetime,hashlib,json
D=Path(__file__).resolve().parents[1]
M=json.loads((D/"model.json").read_text());B={s["id"]:s for s in M["timeline"]}; checks=[]
def ck(name,ok):
 checks.append({"name":name,"pass":bool(ok)})
 if not ok: raise AssertionError(name)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Independent expected schedule; no import or regeneration of production model.
expected=[
 ("normal-initial","A","none","none","none","not-called",[]),
 ("normal-buffered","A","future","pending","none","pending",[]),
 ("normal-appended","A","future","pending","none","pending",[0]),
 ("normal-confirmed","A","future","success","success","confirmed",[0]),
 ("normal-business-pending","A","future","success","success","confirmed",[0]),
 ("unknown-initial","A","none","none","none","not-called",[]),
 ("unknown-buffered","A","future","pending","none","pending",[]),
 ("unknown-appended","A","future","pending","none","pending",[0]),
 ("unknown-request-timeout","A","future","pending","none","pending",[0]),
 ("unknown-auto-retry","A","future","pending","none","pending",[0]),
 ("unknown-delivery-timeout","A","future","failed","delivery-timeout","unknown",[0]),
 ("unknown-producer-closed","A","future","failed","delivery-timeout","unknown",[0]),
 ("unknown-app-resend-buffered","B","future","pending","none","pending",[0]),
 ("unknown-app-resend-appended","B","future","pending","none","pending",[0,1]),
 ("unknown-app-resend-confirmed","B","future","success","success","confirmed",[0,1]),
 ("serialization-initial","A","none","none","none","not-called",[]),
 ("serialization-thrown","A","throws","none","none","definitely-not-sent",[])]
ck("exact ordered stages",list(B)==[r[0] for r in expected])
for name,session,ret,future,callback,observed,offsets in expected:
 s=B[name];p=s["producer"];records=s["log"]["records"]
 ck(name+" sender observation",[p["sessionId"],p["sendReturn"],p["futureState"],p["callbackResult"],p["senderObservedResult"]]==[session,ret,future,callback,observed])
 ck(name+" log truth",[r["offset"] for r in records]==offsets and s["log"]["endOffset"]==len(offsets))
 ck(name+" stable business identity",all((r["eventId"],r["orderId"],r["topic"],r["partition"])==("E01","7042","orders","P0") for r in records))
 ck(name+" consumer boundary",s["consumer"]=={"businessComplete":False,"status":"通知待处理","handledEventIds":[]})
 if future=="success":
  off=0 if session=="A" else 1
  ck(name+" exact metadata",p["metadata"]=={"topic":"orders","partition":"P0","offset":off} and p["error"] is None)
 else:ck(name+" no valid success metadata",p["metadata"] is None)
initials=[B[k] for k in ["normal-initial","unknown-initial","serialization-initial"]]
ck("exact same initial values after two explicit comparison resets",all({k:v for k,v in s.items() if k in ["producer","attempts","log","consumer","automaticRetryCount","links"]}=={k:v for k,v in initials[0].items() if k in ["producer","attempts","log","consumer","automaticRetryCount","links"]} for s in initials))
ck("only branch initial stages carry reset",[s["id"] for s in M["timeline"] if s["resetBefore"]]==[s["id"] for s in initials])
a=B["unknown-appended"];r=B["unknown-auto-retry"];u=B["unknown-delivery-timeout"];z=B["unknown-app-resend-confirmed"]
ck("internal retry preserves complete existing log",a["log"]==r["log"]==u["log"])
ck("internal retry preserves original attempt",a["attempts"]==r["attempts"] and r["producer"]["applicationSendCount"]==1 and r["automaticRetryCount"]==1)
ck("final delivery failure type and Future.get wrapper",u["producer"]["error"]["type"]=="org.apache.kafka.common.errors.TimeoutException" and u["producer"]["error"]["futureGetException"]=="java.util.concurrent.ExecutionException")
ck("old producer closed before new session",B["unknown-producer-closed"]["producer"]["active"] is False and B["unknown-app-resend-buffered"]["producer"]["sessionId"]=="B")
ck("original failed attempt unchanged after later send success",z["attempts"][0]==u["attempts"][0] and z["attempts"][1]["futureState"]=="success")
ck("original log record not moved or changed on application resend",z["log"]["records"][0]==u["log"]["records"][0])
ck("new record is same event distinct producer session",z["log"]["records"][0]["eventId"]==z["log"]["records"][1]["eventId"] and [q["attemptIdentity"]["producerSession"] for q in z["log"]["records"]]==["A","B"])
l=B["serialization-thrown"]
ck("chosen synchronous serializer failure has no attempt Future buffer or Produce",l["attempts"]==[] and not l["producer"]["payloadInAccumulator"] and not l["producer"]["recordProduceSent"] and l["producer"]["error"]["type"]=="org.apache.kafka.common.errors.SerializationException")
c=M["conditions"]
ck("explicit compatible idempotent config",c["acks"]=="all" and c["enable.idempotence"] is True and c["retries"]>0 and 1<=c["max.in.flight.requests.per.connection"]<=5)
ck("explicit time budget",c["delivery.timeout.ms"]==120000 and c["request.timeout.ms"]==45000 and c["linger.ms"]==0 and c["delivery.timeout.ms"]>=c["request.timeout.ms"]+c["linger.ms"])
ck("ISR premise valid but not measured",c["topic.replicationFactor"]==3 and c["topic.min.insync.replicas"]==2 and c["currentISRCount"]==3 and c["transactional.id"] is None)
e=json.loads((D/"sources/source-evidence.json").read_text());source_integrity=[]
for x in e["files"]:
 p=D/"sources"/x["file"]
 ok=p.is_file() and digest(p)==x["sha256"]
 source_integrity.append({"file":x["file"],"pass":ok})
ck("fixed official source bytes match evidence",all(x["pass"] for x in source_integrity))
report={"schemaVersion":1,"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"executor":"Codex independent QA agent","status":"pass-independent-direct-model-review","checkCount":len(checks),"checks":checks,"snapshotCount":len(B),"modelSha256":digest(D/"model.json"),"modelImplementationSha256":digest(D/"model.py"),"authorCheckReportSha256":digest(D/"model-verification.json"),"sourceEvidenceSha256":digest(D/"sources/source-evidence.json"),"sourceByteIntegrity":source_integrity,"independence":"Read all actual serialized snapshots and production implementation, then assert independently fixed expected observations/logs/identities directly against model.json. Did not import model.py, rerun its verify(), regenerate production files or claim its76 assertions as independent tests.","sourceInterpretation":[{"files":["KafkaProducer.java:927-951","KafkaProducer.java:1048-1157","SerializationException.java:20-27"],"result":"Future is asynchronous result object; chosen serialization throws synchronously before accumulator append; neither general Future return nor arbitrary failure proves append/absence."},{"files":["Sender.java:183-215","Sender.java:362-375","ProducerBatch.java:263-303","FutureRecordMetadata.java:68-79"],"result":"Delivery expiry can finalize in-flight send failure while Broker truth is successful; late success does not rewrite FAILED. get(timeout) is only bounded waiting and is not used as final failure."},{"files":["KafkaProducer.java:165-182","ProducerConfig.java:133-185,368-379","RecordMetadata.java:47-70"],"result":"Internal idempotent retry differs from new application send in new session; stable eventId may have offset0 and1. Success metadata under fixed acks=all locates the append, not consumer business."}],"limitations":["Finite legal teaching schedules with one representative retry; no real Kafka Broker/client/serializer/network/ISR/disk test or comprehensive retry state machine.","Model success assumes the fixed acknowledgement premise; replica behavior and all fault combinations are not simulated.","No novice comprehension or user viewing approval is inferred."]}
(D/"qa/model-independent.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:report[k] for k in ["status","checkCount","snapshotCount","modelSha256"]}))
