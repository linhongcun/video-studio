"""Run MQ05 against isolated real Kafka4.4 RF1 and PostgreSQL18 processes.

All process groups and data paths are task-owned. Intentional worker halt occurs
after the local DB COMMIT and before any Kafka offset commit; nonzero halt exits
are explicitly checked, not relabeled as normal process success.
"""
from pathlib import Path
import datetime,hashlib,json,os,shutil,signal,socket,subprocess,time

R=Path(__file__).resolve().parent;W=Path('/tmp/mq05-07-runtime')
K=Path('/tmp/mq-source-depth-runtime/kafka_2.13-4.4.0');PG=W/'pg18-install'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
run_id='mq05-'+stamp;O=R/'runs'/run_id;O.mkdir(parents=True)
T=W/'runs'/run_id;T.mkdir(parents=True)
for d in ['classes','pg-socket']:(T/d).mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(O/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
for name in ['Mq05Probe.java','schema.sql','client-log4j2.yaml','run_mq05.py']:shutil.copy2(R/name,O/name)
reuse=json.loads((R/'dependencies/kafka-reuse-verification.json').read_text())
assert hashlib.sha512(Path(reuse['artifact']).read_bytes()).hexdigest().lower()==reuse['expectedSha512'].lower()
for item in reuse['extractedBinAndLibFiles']:assert sha(K/item['path'])==item['sha256'],item['path']
build=json.loads((R/'postgres-build-latest.json').read_text());assert build['status']=='pass'
for item in json.loads((Path(build['outputDirectory'])/'installed-files-sha256.json').read_text()):assert sha(PG/item['path'])==item['sha256']
jar=W/'postgresql-42.7.8.jar';jdbc=json.loads((R/'dependencies/jdbc-verification.json').read_text());assert sha(jar)==jdbc['sha256']
save('dependency-inputs.json',{'kafkaReuseVerificationSHA256':sha(R/'dependencies/kafka-reuse-verification.json'),'kafkaTgzSHA512':reuse['expectedSha512'],'postgresBuild':build,'jdbcVerification':jdbc,'sourceInputs':{p.name:sha(p) for p in O.iterdir() if p.is_file()}})
sockets=[];ports=[]
for _ in range(3):
 s=socket.socket();s.bind(('127.0.0.1',0));sockets.append(s);ports.append(s.getsockname()[1])
broker_port,controller_port,pg_port=ports
for s in sockets:s.close()
bootstrap=f'127.0.0.1:{broker_port}';pgurl=f'jdbc:postgresql://127.0.0.1:{pg_port}/postgres'
save('endpoints.json',{'bootstrap':bootstrap,'controller':controller_port,'postgresPort':pg_port,'listenAddress':'127.0.0.1','topic':'mq05-orders','partitions':1,'replicationFactor':1,'groupProtocol':'classic','databaseLocalAuth':'trust, isolated loopback only','logicalConsumer':'points','eventId':'E01','accountId':17,'delta':10})
config=f'''process.roles=broker,controller
node.id=1
controller.quorum.voters=1@127.0.0.1:{controller_port}
listeners=PLAINTEXT://127.0.0.1:{broker_port},CONTROLLER://127.0.0.1:{controller_port}
advertised.listeners=PLAINTEXT://127.0.0.1:{broker_port}
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
controller.listener.names=CONTROLLER
inter.broker.listener.name=PLAINTEXT
log.dirs={T/'kafka-data'}
metadata.log.dir={T/'kafka-metadata'}
num.network.threads=2
num.io.threads=2
num.partitions=1
log.segment.bytes=1048576
log.retention.hours=1
log.cleaner.enable=false
offsets.topic.replication.factor=1
offsets.topic.num.partitions=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
min.insync.replicas=1
group.initial.rebalance.delay.ms=0
'''
(O/'server.properties').write_text(config)
env=dict(os.environ,KAFKA_HEAP_OPTS='-Xms256m -Xmx512m',KAFKA_LOG4J_OPTS='-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'))
commands=[];processes=[];streams=[];status='failed';error=None;cleanup=[]
def command(name,args,expected=0,timeout=150):
 record={'name':name,'argv':[str(x) for x in args],'expectedExitCode':expected,'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:
  p=subprocess.Popen([str(x) for x in args],cwd=T,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGKILL);p.wait();record.update(exitCode=p.returncode,timedOut=True);commands.append(record);save('commands.json',commands);raise
 record.update(exitCode=code,finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());commands.append(record);save('commands.json',commands)
 print(name,'exit='+str(code),'expected='+str(expected),flush=True)
 if code!=expected:raise RuntimeError(name+' failed; raw evidence '+str(O))
 return (O/(name+'.stdout.txt')).read_text()
def start(name,args,port):
 log=(O/(name+'.stdout-stderr.txt')).open('wb');streams.append(log)
 p=subprocess.Popen([str(x) for x in args],cwd=T,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);processes.append((name,p))
 save(name+'-process.json',{'pid':p.pid,'processGroup':p.pid,'argv':[str(x) for x in args],'ownerRun':run_id})
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  if p.poll() is not None:raise RuntimeError(name+' exited during startup')
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.2):break
  except OSError:time.sleep(.1)
 else:raise RuntimeError(name+' listener timeout')
 print(name,'listener-ready',flush=True)
def observations(text,kind):return [json.loads(line.split(' ',2)[2]) for line in text.splitlines() if line.startswith('OBS '+kind+' ')]
try:
 command('java-version',['java','-version'])
 command('postgres-version',[PG/'bin/postgres','--version'])
 command('initdb',[PG/'bin/initdb','-D',T/'pg-data','--no-locale','--encoding=UTF8','--auth-local=trust','--auth-host=trust'])
 start('postgres',[PG/'bin/postgres','-D',T/'pg-data','-h','127.0.0.1','-p',pg_port,'-k',T/'pg-socket','-c','shared_buffers=32MB','-c','max_connections=30'],pg_port)
 cluster=command('cluster-id',[K/'bin/kafka-storage.sh','random-uuid']).strip().splitlines()[-1]
 command('format-storage',[K/'bin/kafka-storage.sh','format','--cluster-id',cluster,'--config',O/'server.properties'])
 start('broker',[K/'bin/kafka-server-start.sh',O/'server.properties'],broker_port)
 cp=os.pathsep.join(str(p) for p in sorted((K/'libs').glob('*.jar')))+os.pathsep+str(jar)
 command('compile',['java','-m','jdk.compiler/com.sun.tools.javac.Main','-proc:none','-cp',cp,'-d',T/'classes',O/'Mq05Probe.java'])
 java=['java','-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'),'-cp',str(T/'classes')+os.pathsep+cp,'Mq05Probe']
 outputs={}
 for name,mode,expected in [('setup','setup',0),('db-concurrency','db-concurrency',0),('reset-before-naive','reset',0),('naive-crash','naive-crash',23),('naive-replay','naive-replay',0),('reset-before-dedup','reset',0),('dedup-crash','dedup-crash',24),('dedup-replay','dedup-replay',0),('verify-final','verify-final',0)]:
  text=command(name,java+[mode,bootstrap,pgurl,stamp],expected=expected);outputs[name]=text
  if expected:assert observations(text,'PROCESS_HALT_BEFORE_KAFKA_COMMIT'),'No actual controlled halt witness'
  else:assert 'RESULT PASS mode='+mode in text
 segments=sorted((T/'kafka-data/mq05-orders-0').glob('*.log'));assert len(segments)==1
 dump=command('physical-log',[K/'bin/kafka-dump-log.sh','--files',segments[0],'--print-data-log']);assert 'E01' in dump and '7042' in dump
 save('physical-segment.json',[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in segments])
 naive=observations(outputs['naive-replay'],'DB_COMMIT');dedup=observations(outputs['dedup-replay'],'DB_COMMIT');blocking=observations(outputs['db-concurrency'],'ACTUAL_POSTGRES_BLOCKING');races=observations(outputs['db-concurrency'],'RACE_FINAL')
 assert naive[-1]['points']==20 and dedup[-1]['points']==10 and dedup[-1]['inserted'] is False
 assert len(blocking)==2 and len(races)==2 and all(x['database']['points']==10 and x['database']['markerCount']==1 for x in races)
 counts={name:sum(line.startswith('ASSERT PASS ') for line in text.splitlines()) for name,text in outputs.items()}
 save('assertion-summary.json',{'status':'pass','counts':counts,'total':sum(counts.values()),'noDedupReplayPoints':20,'dedupReplayPoints':10,'actualPostgresBlocking':blocking,'transactionRaceOutcomes':races,'physicalLogRecord':'E01 orders7042 P0@0','scope':'Real Kafka4.4 classic/RF1 and real PostgreSQL18.0, one local event, controlled worker halt after DB COMMIT/before independent Kafka offset commit; two PostgreSQL tasks compete, not two stable Kafka owners of one partition. No distributed DB+Kafka atomic transaction, production failover, benchmark or external service guarantee tested.'})
 status='pass'
except BaseException as exc:error=repr(exc);print('FAILED',error,flush=True);raise
finally:
 for name,p in reversed(processes):
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=20)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
  cleanup.append({'name':name,'pid':p.pid,'processGroup':p.pid,'stopped':p.poll() is not None,'exitCode':p.returncode,'onlyOwnedProcessGroup':True})
 for log in streams:log.close()
 removed=[]
 if status=='pass':
  for name in ['pg-data','pg-socket','kafka-data','kafka-metadata']:
   path=T/name
   if path.exists():shutil.rmtree(path);removed.append(str(path))
 save('cleanup.json',{'processes':cleanup,'removedOwnedPaths':removed,'failedRunDataPreserved':status!='pass'})
 result={'runId':run_id,'status':status,'error':error,'outputDirectory':str(O),'temporaryDirectory':str(T),'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cleanup':cleanup}
 save('result.json',result);(R/'latest-mq05-run.json').write_text(json.dumps(result,indent=2)+'\n')
 save('files-sha256.json',[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.rglob('*')) if p.is_file()])
 print(json.dumps(result),flush=True)
