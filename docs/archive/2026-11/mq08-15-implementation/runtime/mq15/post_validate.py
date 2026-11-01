#!/usr/bin/env python3
"""Reconcile retained real-run evidence without rerunning or changing any broker."""
from pathlib import Path
import datetime, hashlib, json, re, shutil, socket, sys

A=Path(__file__).resolve().parent
R=Path(sys.argv[1]).resolve()
assert R.is_relative_to(A/'runs')
P=R/'post-validation'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
original=json.loads((R/'report.json').read_text())
assert original['pass'] is False
assert 'official dump copied physical records' in original['error']['message']
checks=[json.loads(x)for x in (R/'assertions.jsonl').read_text().splitlines()]
assert len(checks)==35 and all(x['pass']for x in checks[:-1]) and checks[-1]['pass'] is False
mapping=json.loads((P/'byte-identical-segment-copies.json').read_text())
command=json.loads((P/'command.json').read_text())
assert command['exit']==0 and (P/'official-log-dump.stderr').read_text()==''
dump=(P/'official-log-dump.stdout').read_text()
sections={}
for section in dump.split('Dumping ')[1:]:
    name,body=section.split('\n',1)
    assert 'isvalid: false'not in body
    offsets=[int(x)for x in re.findall(r'lastOffset:\s*(-?\d+)',body)]
    sections[str(Path(name).resolve())]={'physicalLEO':max(offsets)+1 if offsets else 0,'batches':len(offsets),'crcValidBatches':body.count('isvalid: true'),'payloads':re.findall(r'payload: (.*)',body)}
assert len(mapping)==33 and len(sections)==33
verified=[]
for item in mapping:
    old=R/item['old'];new=R/item['numericCopy']
    assert old.read_bytes()==new.read_bytes()
    assert sha(old)==sha(new)==item['sha256']
    label=old.parent.name;node=re.fullmatch(r'node(\d+)-\d+\.log',old.name).group(1)
    snapshot=json.loads((old.parent/'observation.json').read_text())
    actual=sections[str(new.resolve())];expected=snapshot['physical'][node]
    assert actual['physicalLEO']==expected['physicalLEO']
    assert actual['batches']==len(expected['batches'])==actual['crcValidBatches']
    assert all(x=='{"eventId":"E01","orderId":7042}'for x in actual['payloads'])
    verified.append({'snapshot':label,'node':int(node),'sha256':item['sha256'],'physicalLEO':actual['physicalLEO'],'crcValidBatches':actual['crcValidBatches'],'payloads':actual['payloads']})

# The raw experiment and failure receipts stay unchanged; this derived receipt closes the filename-only audit gap.
assert all(original['cleanup'][x]for x in ['allTrackedBrokersExited','allProxyListenersClosed','ownTemporaryDataRemoved'])
assert not Path(original['tempDir']).exists()
closed=[]
for node,ports in original['ports'].items():
    for role,port in ports.items():
        with socket.socket()as s:
            s.settimeout(.1);closed.append({'node':int(node),'role':role,'port':port,'connectRefused':s.connect_ex(('127.0.0.1',port))!=0})
assert all(x['connectRefused']for x in closed)
sources={}
for name in ['run_mq15.py','Mq15Probe.java']:
    current=A/name
    assert sha(current)==original['sources'][name]
    dest=R/('executed-'+name)
    if not dest.exists():shutil.copyfile(current,dest)
    assert sha(dest)==original['sources'][name]
    sources[name]={'file':str(dest.relative_to(A)),'sha256':sha(dest)}
feature=(R/'official-features.stdout').read_text()
elr=next(x for x in feature.splitlines()if 'eligible.leader.replicas.version'in x)
assert 'FinalizedVersionLevel: 0'in elr
hw=A.parent/'hw-source-evidence/chain-audit.json'
assert hw.exists()
facts=[]
for label in ['healthy-acks1','healthy-all','slow-before-resume','slow-after-resume','isr2-ack','isr1-before-send','isr1-after-reject','all-before-leader-kill','all-after-clean-election','acks1-before-kill','acks1-after-clean-election']:
    obs=json.loads((R/'snapshots'/label/'observation.json').read_text());facts.append({'snapshot':label,'atUTC':obs['atUTC'],'topic':obs['topic'],'leader':obs['metadata']['leader'],'ISR':obs['metadata']['isr'],'physicalLEO':{n:x['physicalLEO']for n,x in obs['physical'].items()},'leaderHWViaReadUncommittedConsumerEndOffsets':obs['consumerEndOffset']})

report={'schemaVersion':1,'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'actual-Kafka44-RF3-controlled-runtime-with-retained-post-validation-repair','pass':True,'runtimeExecutor':'/root/deploy_diagnosis/mq15_runtime','rawRunReport':str((R/'report.json').relative_to(A)),'rawRunReportSHA256':sha(R/'report.json'),'rawRunStillPassFalse':True,'status':'All seven real broker branches passed; the later official dump filename failure is closed by byte-identical numeric-name copies and successful official decode without rerunning brokers.','executedSources':sources,'actualKafkaVersion':'4.4.0','actualKafkaCommitId':'1156b2752aaa28ea','fixedFullSourceCommit':'1156b2752aaa28eafc0b4c4d387e63356793268d','dependencyIdentity':original['dependencyIdentity'],'actualELRFeatureLine':elr,'ELRZeroInterpretation':'Admin finalizedFeatures omits zero entries; the official kafka-features describe output explicitly reports FinalizedVersionLevel0. The storage format also explicitly requested this feature at0.','consumerEndOffsetsEvidence':{'sourceAudit':str(hw.relative_to(A.parent)),'sourceAuditSHA256':sha(hw),'fixedPartitionBranch':'https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/cluster/Partition.scala#L1433-L1474','interpretation':'The observation consumer explicitly uses read_uncommitted; this ListOffsets consumer request returns leader highWatermark, not physicalLEO. Replica physical bytes are measured separately.'},'producerConfig':{'enable.idempotence':False,'retries':0,'max.in.flight.requests.per.connection':1,'request.timeout.ms':120000,'delivery.timeout.ms':150000,'compression.type':'none','acksBranches':['1','all'],'notes':'Exactly one E01 JSON/order7042/key7042 to P0 in each initially empty topic. Same acks-specific producer object may be reused across distinct topics; no concurrent business sends except a single observed pending future.'},'clusterConfig':{'RF':3,'minISR':2,'uncleanLeaderElection':False,'eligibleLeaderReplicasFeature':0,'processRoles':'Three isolated combined broker/controller JVMs','listeners':'CLIENT direct, REPLICATION through owned per-leader TCP proxy, CONTROLLER direct','followerGate':'Actual request header clientId broker-<replicaId>-fetcher-0 identifies the sender; gate closes that existing connection before producing and rejects subsequent matching requests. ApiKey1/version18/clientIds were captured. Other broker/controller CLIENT paths remain reachable.','wholeLeaderReplicationGate':'Before acks1 loss test, close both existing data connections and reject new data connections; keep this gate closed until old leader is killed and a clean new leader is observed.','proxySourceEvidence':['sources/ReplicaFetcherManager.scala','sources/ReplicaFetcherThread.scala'],'noSIGSTOPInAcceptedRun':True},'realCases':original['cases'],'observedSnapshotFacts':facts,'passedRealRunAssertions':34,'officialPhysicalLogValidation':{'officialTool':'kafka-dump-log.sh --print-data-log --deep-iteration','exit':0,'emptyAndNonemptySnapshotsValidated':33,'byteIdentityPairs':33,'recordBatchCRCsValid':sum(x['crcValidBatches']for x in verified),'validation':verified,'stdout':str((P/'official-log-dump.stdout').relative_to(A)),'stdoutSHA256':sha(P/'official-log-dump.stdout'),'stderrEmpty':True},'retainedFailures':[{'path':'failures/compile-appinfoparser-v1','reason':'Kafka4.4 AppInfoParser moved to utils.internals; fixed only own runtime probe and retained original source/error.'},{'path':'runs/20261101T092135857476Z','reason':'Whole-JVM SIGSTOP caused observer Admin.describeTopics to target paused CLIENT listener and timeout. Own services stopped. Replaced with exact follower data gate; this first run is not claimed fully passed.'},{'path':str((R/'official-log-dump.stderr').relative_to(A)),'reason':'Copied segments had basename node1-0.log, which official DumpLogSegments parses as a numeric base offset and rejects. Original failed command/output/report preserved. Correctly named copies have identical bytes and were fully decoded successfully.'}],'brokerErrorScope':[{'file':'broker1-start1.log','classification':'Expected actual ISR1 preappend NotEnoughReplicasException, same failure returned to the producer.'},{'file':'broker3-start1.log','classification':'NotControllerException on wantShutDown=true broker heartbeat after observed cases, while sequentially stopping the final combined JVMs; retained raw errors, not claimed error-free service shutdown. All tracked PIDs exited and ports are now closed.'}],'cleanup':{**original['cleanup'],'postAuditAll12PortsClosed':closed},'limits':['Finite loopback process/replication-network faults, not powerloss, disk durability, throughput benchmarking or arbitrary distributed failures.','No distributed transaction or exactly-once business-effect claim.','Ack1 loss means the clean new leader lacks E01; the offline former leader still physically contains E01, explicitly preserved in snapshots.','Healthy ack1 was later observed on all three replicas; this does not mean ack1 required three copies at the moment it replied.','The test proves its gated cases and configurations; it does not claim every production failure has the same outcome.','This is runtime evidence, not animation/teaching-model output, production media review or an independent code-review gate.']}
(P/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'pass':True,'report':str(P/'report.json'),'sha256':sha(P/'report.json'),'realPassedAssertions':34,'physicalSnapshotsOfficiallyValidated':33,'validRecordBatches':sum(x['crcValidBatches']for x in verified),'allPortsClosed':True}))
