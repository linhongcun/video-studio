"""Independent RF1 broker run for MQ06 or MQ07; only task-owned processes/data."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,signal,socket,subprocess,time
ap=argparse.ArgumentParser();ap.add_argument('episode',choices=['mq06','mq07']);args=ap.parse_args()
R=Path(__file__).resolve().parent;W=Path('/tmp/mq05-07-runtime');K=Path('/tmp/mq-source-depth-runtime/kafka_2.13-4.4.0')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run_id=args.episode+'-'+stamp
O=R/'runs'/run_id;O.mkdir(parents=True);T=W/'runs'/run_id;T.mkdir(parents=True);(T/'classes').mkdir()
cls='Mq06Probe' if args.episode=='mq06' else 'Mq07Probe'
for name in [cls+'.java','KafkaProbeSupport.java','run_kafka_probe.py','client-log4j2.yaml']:shutil.copy2(R/name,O/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(O/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
reuse=json.loads((R/'dependencies/kafka-reuse-verification.json').read_text())
assert hashlib.sha512(Path(reuse['artifact']).read_bytes()).hexdigest().lower()==reuse['expectedSha512'].lower()
for item in reuse['extractedBinAndLibFiles']:assert sha(K/item['path'])==item['sha256']
save('dependency-inputs.json',{'kafkaDistributionSHA512':reuse['expectedSha512'],'reusedFilesFreshlyChecked':len(reuse['extractedBinAndLibFiles']),'verificationSHA256':sha(R/'dependencies/kafka-reuse-verification.json'),'sourceInputs':{p.name:sha(p) for p in O.iterdir() if p.is_file()}})
held=[];ports=[]
for _ in range(2):s=socket.socket();s.bind(('127.0.0.1',0));held.append(s);ports.append(s.getsockname()[1])
broker_port,controller_port=ports
for s in held:s.close()
bootstrap=f'127.0.0.1:{broker_port}'
(O/'server.properties').write_text(f'''process.roles=broker,controller
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
num.partitions=2
log.segment.bytes=1048576
log.retention.hours=1
log.cleaner.enable=false
offsets.topic.replication.factor=1
offsets.topic.num.partitions=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
min.insync.replicas=1
group.initial.rebalance.delay.ms=0
''')
env=dict(os.environ,KAFKA_HEAP_OPTS='-Xms256m -Xmx512m',KAFKA_LOG4J_OPTS='-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'))
commands=[];broker=None;log=None;status='failed';error=None
def command(name,argv,timeout=180):
 record={'name':name,'argv':[str(x) for x in argv],'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:
  p=subprocess.Popen([str(x) for x in argv],cwd=T,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,start_new_session=True)
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();record.update(exitCode=p.returncode,timedOut=True);commands.append(record);save('commands.json',commands);raise
 record.update(exitCode=code,finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());commands.append(record);save('commands.json',commands);print(name,'exit='+str(code),flush=True)
 if code:raise RuntimeError(name+' failed; '+str(O))
 return (O/(name+'.stdout.txt')).read_text()
try:
 command('java-version',['java','-version'])
 cp=os.pathsep.join(str(p) for p in sorted((K/'libs').glob('*.jar')))
 command('compile',['java','-m','jdk.compiler/com.sun.tools.javac.Main','-proc:none','-cp',cp,'-d',T/'classes',O/'KafkaProbeSupport.java',O/(cls+'.java')])
 cluster=command('cluster-id',[K/'bin/kafka-storage.sh','random-uuid']).strip().splitlines()[-1]
 command('format-storage',[K/'bin/kafka-storage.sh','format','--cluster-id',cluster,'--config',O/'server.properties'])
 log=(O/'broker.stdout-stderr.txt').open('wb');broker=subprocess.Popen([str(K/'bin/kafka-server-start.sh'),str(O/'server.properties')],cwd=T,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 save('broker-process.json',{'pid':broker.pid,'processGroup':broker.pid,'ownedRun':run_id,'bootstrap':bootstrap})
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  if broker.poll() is not None:raise RuntimeError('Broker exited during startup')
  try:
   with socket.create_connection(('127.0.0.1',broker_port),timeout=.2):break
  except OSError:time.sleep(.1)
 else:raise RuntimeError('Broker listener timeout')
 text=command('probe',['java','-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'),'-cp',str(T/'classes')+os.pathsep+cp,cls,bootstrap,stamp],timeout=180)
 assert 'RESULT PASS probe='+args.episode in text
 observations=[]
 for line in text.splitlines():
  if line.startswith('OBS '):_,kind,data=line.split(' ',2);observations.append({'kind':kind,'data':json.loads(data)})
 save('observations.json',observations)
 segments=sorted((T/'kafka-data').glob('orders-*/*.log'));assert len(segments)==2
 for i,segment in enumerate(segments):command('physical-log-P'+str(i),[K/'bin/kafka-dump-log.sh','--files',segment,'--print-data-log'])
 save('physical-segments.json',[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in segments])
 count=sum(line.startswith('ASSERT PASS ') for line in text.splitlines())
 save('assertion-summary.json',{'status':'pass','actualPrintedAssertions':count,'episode':args.episode,'scope':next(x['data'] for x in observations if x['kind']=='SCOPE'),'observationsFile':'observations.json','sourceSHA256':sha(O/(cls+'.java'))})
 status='pass'
except BaseException as exc:error=repr(exc);print('FAILED',error,flush=True);raise
finally:
 cleanup={'brokerStarted':broker is not None,'brokerStopped':broker is None,'onlyOwnedProcessGroup':True,'removedOwnedPaths':[]}
 if broker is not None:
  if broker.poll() is None:
   os.killpg(broker.pid,signal.SIGTERM)
   try:broker.wait(timeout=20)
   except subprocess.TimeoutExpired:os.killpg(broker.pid,signal.SIGKILL);broker.wait(timeout=10)
  cleanup.update(brokerStopped=broker.poll() is not None,brokerPID=broker.pid,brokerExitCode=broker.returncode)
 if log:log.close()
 if status=='pass':
  for name in ['kafka-data','kafka-metadata']:
   p=T/name
   if p.exists():shutil.rmtree(p);cleanup['removedOwnedPaths'].append(str(p))
 save('cleanup.json',cleanup)
 result={'runId':run_id,'status':status,'error':error,'outputDirectory':str(O),'temporaryDirectory':str(T),'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cleanup':cleanup}
 save('result.json',result);(R/('latest-'+args.episode+'-run.json')).write_text(json.dumps(result,indent=2)+'\n')
 save('files-sha256.json',[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.rglob('*')) if p.is_file()]);print(json.dumps(result),flush=True)
