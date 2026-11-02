"""Fresh three-branch recovery run. Only this new runtime archive and owned tmp are written."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,socket,subprocess,signal,time,shutil,re
R=Path(__file__).resolve().parent;REPO=next(p for p in R.parents if(p/'AGENTS.md').is_file());W=Path('/tmp/mq05-consumer-replay-20261102');K=W/'kafka_2.13-4.4.0';PG=W/'pg18-install';stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');O=R/'runs'/('recovery-'+stamp);O.mkdir(parents=True);T=W/'runs'/('recovery-'+stamp);T.mkdir(parents=True);(T/'classes').mkdir();(T/'pg-socket').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat();save=lambda n,v:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for name in ['Mq05ReplayProbe.java','client-log4j2.yaml','run_experiment.py']:shutil.copy2(R/name,O/name)
kafka=json.loads((R/'dependencies/kafka-verification.json').read_text());assert hashlib.sha512(Path(kafka['artifact']).read_bytes()).hexdigest()==kafka['expectedSha512'];assert all(sha(K/x['path'])==x['sha256']for x in kafka['binAndLibFiles']);pgbuild=json.loads((R/'postgres-build-latest.json').read_text());assert pgbuild['status']=='pass';pgfiles=json.loads((Path(pgbuild['outputDirectory'])/'installed-files-sha256.json').read_text());assert all(sha(PG/x['path'])==x['sha256']for x in pgfiles);jdbc=W/'postgresql-42.7.8.jar';jproof=json.loads((R/'dependencies/jdbc-verification.json').read_text());assert sha(jdbc)==jproof['sha256']
save('dependency-inputs.json',{'checkedAtUTC':now(),'freshDependencies':True,'kafkaVerificationSHA256':sha(R/'dependencies/kafka-verification.json'),'kafkaTgzSHA512':kafka['expectedSha512'],'postgresBuildReceiptSHA256':sha(R/'postgres-build-latest.json'),'postgresBuild':pgbuild,'postgresInstalledFileChecks':len(pgfiles),'jdbcSHA256':sha(jdbc),'javaExecutable':shutil.which('java'),'sourceSHA256':{n:sha(O/n)for n in ['Mq05ReplayProbe.java','client-log4j2.yaml','run_experiment.py']}})
reserved=[]
for i in range(3):s=socket.socket();s.bind(('127.0.0.1',0));reserved.append(s)
bp,cp,pp=[s.getsockname()[1]for s in reserved]
for s in reserved:s.close()
bootstrap=f'127.0.0.1:{bp}';pgurl=f'jdbc:postgresql://127.0.0.1:{pp}/postgres';save('endpoints.json',{'bootstrap':bootstrap,'controllerPort':cp,'postgresPort':pp,'localOnly':True,'auth':'PostgreSQL trust only task-owned local server; no secret credentials','ownedTempDirectory':str(T)})
server=f'''process.roles=broker,controller
node.id=1
controller.quorum.voters=1@127.0.0.1:{cp}
listeners=PLAINTEXT://127.0.0.1:{bp},CONTROLLER://127.0.0.1:{cp}
advertised.listeners=PLAINTEXT://127.0.0.1:{bp}
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
controller.listener.names=CONTROLLER
inter.broker.listener.name=PLAINTEXT
log.dirs={T/'kafka-data'}
metadata.log.dir={T/'kafka-metadata'}
num.network.threads=2
num.io.threads=2
num.partitions=1
log.segment.bytes=1048576
log.retention.hours=24
log.cleaner.enable=false
offsets.topic.replication.factor=1
offsets.topic.num.partitions=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
min.insync.replicas=1
group.initial.rebalance.delay.ms=0
''';(O/'server.properties').write_text(server)
env=dict(os.environ,KAFKA_HEAP_OPTS='-Xms256m -Xmx512m',KAFKA_LOG4J_OPTS='-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'));commands=[];processes=[];streams=[];status='failed';error=None;cases=[];cleanup=[]
def command(name,args,expected=0,timeout=120):
 args=[str(x)for x in args];entry={'name':name,'argv':args,'startedAtUTC':now(),'expectedExitCode':expected};commands.append(entry);save('commands.json',commands)
 with(O/(name+'.stdout.txt')).open('wb')as out,(O/(name+'.stderr.txt')).open('wb')as err:
  p=subprocess.Popen(args,cwd=T,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,start_new_session=True)
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();entry.update(timedOut=True,exitCode=p.returncode,finishedAtUTC=now());save('commands.json',commands);raise
 entry.update(exitCode=code,finishedAtUTC=now());save('commands.json',commands);print(name,'exit',code,'expected',expected,flush=True);assert code==expected,(name,code)
 return (O/(name+'.stdout.txt')).read_text()
def start(name,args,port):
 log=(O/(name+'.stdout-stderr.txt')).open('wb');streams.append(log);p=subprocess.Popen([str(x)for x in args],cwd=T,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);processes.append((name,p));save(name+'-process.json',{'pid':p.pid,'processGroup':p.pid,'argv':[str(x)for x in args],'startedAtUTC':now(),'ownerRun':O.name})
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  assert p.poll()is None,(name,'exited')
  try:
   with socket.create_connection(('127.0.0.1',port),.2):break
  except OSError:time.sleep(.1)
 else:raise TimeoutError(name+' startup')
 print(name,'listener-ready',flush=True)
def observations(text,kind):return [json.loads(line.split(' ',2)[2])for line in text.splitlines()if line.startswith('OBS '+kind+' ')]
try:
 command('java-version',['java','-version']);command('postgres-version',[PG/'bin/postgres','--version']);classpath=os.pathsep.join(str(p)for p in sorted((K/'libs').glob('*.jar')))+os.pathsep+str(jdbc)
 command('compile',['java','-m','jdk.compiler/com.sun.tools.javac.Main','-proc:none','-cp',classpath,'-d',T/'classes',O/'Mq05ReplayProbe.java']);java=['java','-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'),'-cp',str(T/'classes')+os.pathsep+classpath,'Mq05ReplayProbe']
 command('initdb',[PG/'bin/initdb','-D',T/'pg-data','--no-locale','--encoding=UTF8','--auth-local=trust','--auth-host=trust']);start('postgres',[PG/'bin/postgres','-D',T/'pg-data','-h','127.0.0.1','-p',pp,'-k',T/'pg-socket','-c','shared_buffers=32MB','-c','max_connections=25'],pp)
 cluster=command('cluster-id',[K/'bin/kafka-storage.sh','random-uuid']).strip().splitlines()[-1];command('format-storage',[K/'bin/kafka-storage.sh','format','--cluster-id',cluster,'--config',O/'server.properties']);start('broker',[K/'bin/kafka-server-start.sh',O/'server.properties'],bp)
 for branch in ['unsafe','safe','early-commit']:
  topic='mq05-'+branch+'-'+stamp.lower().replace('.','-');group='points-'+branch+'-'+stamp.lower().replace('.','-');args=[bootstrap,pgurl,topic,group,branch];outputs={}
  for label,mode,expected in [('setup','setup',0),('A-halt','A',86),('after-A','inspect',0),('B-restart','B',0),('after-B','inspect',0)]:
   text=command(branch+'-'+label,java+[mode]+args,expected=expected,timeout=90);outputs[label]=text
   if expected:assert observations(text,'INTENTIONAL_HALT')and not observations(text,'RESULT')
   else:assert observations(text,'RESULT')[-1]['data']['pass']is True
  segments=sorted((T/'kafka-data'/(topic+'-0')).glob('*.log'));assert len(segments)==1
  dest=O/'physical'/branch;dest.mkdir(parents=True);copy=dest/segments[0].name;shutil.copy2(segments[0],copy);assert copy.read_bytes()==segments[0].read_bytes()
  dump=command(branch+'-physical-log',[K/'bin/kafka-dump-log.sh','--files',copy,'--print-data-log']);recordlines=[line for line in dump.splitlines()if re.search(r'^\s*\|\s*offset:\s*0\b',line)];assert len(recordlines)==1,(branch,'physical-count',recordlines);assert 'E01'in recordlines[0]and'7042'in recordlines[0]and'17'in recordlines[0]and'10'in recordlines[0];assert 'isvalid: true'in dump.lower() or 'isValid: true'in dump
  a=observations(outputs['after-A'],'INDEPENDENT_SNAPSHOT')[-1]['data'];b=observations(outputs['after-B'],'INDEPENDENT_SNAPSHOT')[-1]['data'];wantA=0 if branch=='early-commit'else 10;wantB={'unsafe':20,'safe':10,'early-commit':0}[branch];assert a['database']['points']==wantA and b['database']['points']==wantB;assert a['committed']==(1 if branch=='early-commit'else 0)and b['committed']==1;assert a['logStart']==b['logStart']==0 and a['LEO']==b['LEO']==1
  assert a['database']['markerCount']==b['database']['markerCount']==(1 if branch=='safe'else 0)
  if branch!='early-commit':assert observations(outputs['A-halt'],'RECORD_DELIVERED')[-1]['data']['value']==observations(outputs['B-restart'],'RECORD_DELIVERED')[-1]['data']['value']and observations(outputs['A-halt'],'RECORD_DELIVERED')[-1]['data']['offset']==observations(outputs['B-restart'],'RECORD_DELIVERED')[-1]['data']['offset']==0
  fetch=(O/(branch+'-B-restart.stderr.txt')).read_text();wanted=1 if branch=='early-commit'else0;fetchLines=[line for line in fetch.splitlines()if 'fetchOffset='+str(wanted)in line and topic in line];assert fetchLines,(branch,'No actual Fetch offset witness',fetch[-900:])
  case={'id':branch,'topic':topic,'group':group,'oneProducerApplicationSendCall':1,'physicalLogRecords':len(recordlines),'physicalLogSHA256':sha(copy),'physicalLogCopy':str(copy.relative_to(R)),'actualFetchOffsetAfterRestart':wanted,'actualFetchWitnessLines':fetchLines,'afterA':a,'afterB':b,'intentionalHaltExit':86,'pass':True};cases.append(case);save('cases-progress.json',cases);print('CASE_PASS',branch,flush=True)
 status='pass'
except BaseException as e:error=repr(e);raise
finally:
 for name,p in reversed(processes):
  if p.poll()is None:
   try:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=25)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  cleanup.append({'process':name,'pid':p.pid,'exitCode':p.returncode,'stopped':p.poll()is not None,'atUTC':now()})
 for stream in streams:stream.close()
 closed=[]
 for port in [bp,cp,pp]:
  try:
   with socket.create_connection(('127.0.0.1',port),.2):closed.append({'port':port,'closed':False})
  except OSError:closed.append({'port':port,'closed':True})
 if all(item['stopped']for item in cleanup)and all(item['closed']for item in closed):shutil.rmtree(T);removed=True
 else:removed=False
 checks=[]
 for p in O.glob('*.stdout.txt'):
  checks.extend(observations(p.read_text(),'ASSERT'))
 report={'status':status,'pass':status=='pass','error':error,'finishedAtUTC':now(),'run':O.name,'sourceIdentity':{n:sha(O/n)for n in ['Mq05ReplayProbe.java','client-log4j2.yaml','run_experiment.py']},'actualRuntime':'Kafka4.4.0/1156b2752aaa28ea;PostgreSQL18.0;singleRF1/ISR1;classicmanualcommit/maxPoll1','cases':cases,'assertions':len(checks),'allObservedAssertionsPass':all(c['data']['pass']for c in checks),'cleanup':cleanup,'ports':closed,'ownedTempDataRemoved':removed,'limits':['Finite actual recovery processes, not benchmark or real powerloss','Only oneproducerappend per branch; no producer resend as redelivery cause','A halted before B; same-group sequential recovery, not stable simultaneous partition owners','Earlycommit skips retained record rather than deleting it','Safe marker and business effect same localDBtx; Kafkaoffsetcommit remains an independent operation','Raw failures and logs kept; no historical files or shared production sources written']};save('report.json',report);(R/'latest-run.json').write_text(json.dumps({'run':O.name,'report':str((O/'report.json').relative_to(R)),'sha256':sha(O/'report.json'),'pass':report['pass']},indent=2)+'\n');print(json.dumps({'status':status,'error':error,'cases':len(cases),'assertions':len(checks),'cleanupStopped':cleanup,'ports':closed,'run':str(O)}),flush=True)
