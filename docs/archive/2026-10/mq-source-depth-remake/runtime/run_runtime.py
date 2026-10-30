#!/usr/bin/env python3
"""Reproduce the isolated single-node API experiment; never changes repo media.

Downloads are handled separately by download_distribution.py. Requires Java21
with jdk.compiler. Only task-owned broker process group and task-owned data dirs
are stopped/removed. Raw stdout/stderr are preserved per unique run directory.
"""
from pathlib import Path
import datetime,hashlib,json,os,shutil,signal,socket,subprocess,tarfile,time,sys
GROUPS_ONLY='--groups-only' in sys.argv[1:]
if any(x!='--groups-only' for x in sys.argv[1:]):raise ValueError('only optional --groups-only supported')
R=Path(__file__).resolve().parent
W=Path('/tmp/mq-source-depth-runtime')
K=W/'kafka_2.13-4.4.0'
verify=json.loads((R/'distribution-verification.json').read_text())
artifact=W/'kafka_2.13-4.4.0.tgz'
assert verify['match'] and hashlib.sha512(artifact.read_bytes()).hexdigest()==verify['expectedSha512']
for port in [19092,19093]:
    s=socket.socket()
    try:s.bind(('127.0.0.1',port))
    finally:s.close()
if not K.exists():
    with tarfile.open(artifact,'r:gz') as archive:archive.extractall(W,filter='data')
run_id='run-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
O=R/'runs'/run_id;O.mkdir(parents=True)
for name in ['KafkaDepthProbe.java','server.properties','client-log4j2.yaml','distribution-verification.json']:
    shutil.copy2(R/name,O/name)
for name in ['data','metadata']:
    if (W/name).exists():raise RuntimeError('Refuse to overwrite prior data '+str(W/name))
env=os.environ.copy()
env['KAFKA_HEAP_OPTS']='-Xms256m -Xmx512m'
env['KAFKA_LOG4J_OPTS']='-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml')
commands=[]
def command(name,args,timeout=120):
    record={'name':name,'argv':[str(x) for x in args],'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:
        result=subprocess.run([str(x) for x in args],cwd=W,env=env,stdout=out,stderr=err,timeout=timeout)
    record['exitCode']=result.returncode;record['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();commands.append(record)
    (O/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    print('COMMAND',name,'exit='+str(result.returncode),flush=True)
    if result.returncode:raise RuntimeError(name+' failed; raw logs '+str(O))
    return (O/(name+'.stdout.txt')).read_text()
broker=None;broker_log=None;status='failed';error=None
try:
    command('java-version',['java','-version'])
    command('java-compiler',['java','com.sun.tools.javac.Main','-version'])
    command('kafka-version',[K/'bin/kafka-topics.sh','--version'])
    cluster_id=command('cluster-id',[K/'bin/kafka-storage.sh','random-uuid']).strip().splitlines()[-1]
    command('format-storage',[K/'bin/kafka-storage.sh','format','--cluster-id',cluster_id,'--config',O/'server.properties'])
    broker_log=(O/'broker.stdout-stderr.txt').open('wb')
    broker=subprocess.Popen([str(K/'bin/kafka-server-start.sh'),str(O/'server.properties')],cwd=W,env=env,stdin=subprocess.DEVNULL,stdout=broker_log,stderr=subprocess.STDOUT,start_new_session=True)
    (O/'broker-pid.json').write_text(json.dumps({'pid':broker.pid,'processGroup':broker.pid,'clusterId':cluster_id,'ownedBy':'run_runtime.py'},indent=2)+'\n')
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        if broker.poll() is not None:raise RuntimeError('Broker exited during startup')
        try:
            with socket.create_connection(('127.0.0.1',19092),timeout=.2):break
        except OSError:time.sleep(.2)
    else:raise RuntimeError('Broker listener not ready')
    print('BROKER_READY pid='+str(broker.pid),flush=True)
    java=['java','-Dlog4j2.configurationFile='+str(O/'client-log4j2.yaml'),'-cp',str(K/'libs/*'),str(O/'KafkaDepthProbe.java')]
    command('producer',java+['producer'])
    segment=W/'data/mq-depth-orders-0/00000000000000000000.log'
    assert segment.exists(),segment
    command('physical-log-before-consumers',[K/'bin/kafka-dump-log.sh','--files',segment,'--print-data-log'])
    command('groups',java+['groups'],timeout=120)
    if not GROUPS_ONLY:command('position',java+['position'],timeout=90)
    # API-level checks are process exit assertions, not synthesized observations.
    raw=(O/'physical-log-before-consumers.stdout.txt').read_text()
    assert 'E01' in raw and 'E03' in raw,'physical log dump missing expected record payload'
    counts={name:sum(line.startswith('ASSERT PASS ') for line in (O/(name+'.stdout.txt')).read_text().splitlines()) for name in (['producer','groups'] if GROUPS_ONLY else ['producer','groups','position'])}
    assert all('RESULT PASS mode='+name in (O/(name+'.stdout.txt')).read_text() for name in counts)
    (O/'assertion-summary.json').write_text(json.dumps({'status':'pass','counts':counts,'total':sum(counts.values()),'physicalSegmentDumpContains':['E01','E03'],'scope':('RF1 real Kafka4.4.0; dynamic classic Range groups only, producer seeding; position experiment not rerun' if GROUPS_ONLY else 'RF1 single-node real Kafka4.4.0; actual dynamic classic stable assignments; manual-assignment position/commit recovery; no business handlers or complex unknown-response fault injection')},indent=2)+'\n')
    status='pass'
except BaseException as exc:
    error=repr(exc)
    print('RUN_FAILED',error,flush=True)
    raise
finally:
    cleanup={'brokerStarted':broker is not None,'brokerStopped':broker is None,'removed':[]}
    if broker is not None:
        if broker.poll() is None:
            os.killpg(broker.pid,signal.SIGTERM)
            try:broker.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(broker.pid,signal.SIGKILL);broker.wait(timeout=10)
        cleanup['brokerStopped']=broker.poll() is not None;cleanup['brokerExitCode']=broker.returncode
    if broker_log is not None:broker_log.close()
    physical=[]
    for part in [0,1]:
        p=W/f'data/mq-depth-orders-{part}/00000000000000000000.log'
        if p.exists():physical.append({'partition':part,'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (O/'physical-segment-sha256.json').write_text(json.dumps(physical,indent=2)+'\n')
    for name in ['data','metadata']:
        p=W/name
        if p.exists():shutil.rmtree(p);cleanup['removed'].append(str(p))
    (O/'cleanup.json').write_text(json.dumps(cleanup,indent=2)+'\n')
    result={'runId':run_id,'requestedMode':('dynamic-groups-only' if GROUPS_ONLY else 'full-dynamic-groups-and-position'),'status':status,'error':error,'outputDirectory':str(O),'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cleanup':cleanup}
    (O/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    (R/'latest-run.json').write_text(json.dumps(result,indent=2)+'\n')
    hashes=[]
    for p in sorted(O.rglob('*')):
        if p.is_file():hashes.append({'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (O/'files-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
