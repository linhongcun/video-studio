#!/usr/bin/env python3
"""Actual fixed Redis8.4.0 processes: known-five minority and majority failover.

Local isolated ports16500..16507. No performance claim. Own processes only.
"""
from pathlib import Path
import datetime,hashlib,json,socket,subprocess,time,traceback,sys

D=Path(__file__).resolve().parent
BINARY=Path('/workspace/work/redis-batch/runtime/redis-60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/redis-server')
STAMP=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%dT%H%M%S%z')
OUT=D/'actual-runtime'/STAMP
OUT.mkdir(parents=True,exist_ok=False)
EVENTS=[]

class RedisError(Exception): pass
def command(port,*parts):
    with socket.create_connection(('127.0.0.1',port),timeout=2) as connection:
        connection.settimeout(2)
        data=[str(p).encode() for p in parts]
        connection.sendall(b'*'+str(len(data)).encode()+b'\r\n'+b''.join(b'$'+str(len(p)).encode()+b'\r\n'+p+b'\r\n' for p in data))
        reader=connection.makefile('rb')
        def read():
            kind=reader.read(1);line=reader.readline().removesuffix(b'\r\n')
            if kind==b'+':return line.decode()
            if kind==b'-':raise RedisError(line.decode())
            if kind==b':':return int(line)
            if kind==b'$':
                length=int(line)
                if length<0:return None
                value=reader.read(length);assert reader.read(2)==b'\r\n';return value.decode()
            if kind==b'*':return [read() for _ in range(int(line))]
            raise RuntimeError('Unexpected RESP response')
        return read()

def pairs(value):return dict(zip(value[::2],value[1::2]))
def info(port):
    return dict(line.split(':',1) for line in command(port,'INFO','replication').splitlines() if ':' in line and not line.startswith('#'))
def event(name,**values):EVENTS.append(dict(event=name,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),**values))
def wait(check,timeout=30):
    start=time.monotonic()
    while time.monotonic()-start<timeout:
        try:
            result=check()
            if result:return result
        except (OSError,RedisError,KeyError):pass
        time.sleep(.1)
    raise AssertionError('Timed out: '+getattr(check,'__name__','condition'))

def run_case(name,available):
    folder=OUT/name;folder.mkdir()
    processes={}
    def launch(port,lines,sentinel=False):
        directory=folder/str(port);directory.mkdir()
        config=directory/'redis.conf'
        config.write_text('\n'.join(['bind 127.0.0.1','protected-mode yes',f'port {port}','daemonize no',f'dir {directory}',f'logfile {directory}/redis.log','save ""','appendonly no']+lines)+'\n')
        output=open(directory/'stdout.log','wb')
        process=subprocess.Popen([str(BINARY),str(config)]+(['--sentinel'] if sentinel else []),stdout=output,stderr=subprocess.STDOUT)
        processes[port]=process
        wait(lambda:command(port,'PING')=='PONG',10)
        return process
    try:
        launch(16500,[])
        launch(16501,['replicaof 127.0.0.1 16500','replica-priority 0'])
        launch(16502,['replicaof 127.0.0.1 16500','replica-priority 100'])
        for port in range(16503,16508):
            launch(port,['sentinel monitor sample 127.0.0.1 16500 2','sentinel down-after-milliseconds sample 700','sentinel failover-timeout sample 3000','sentinel parallel-syncs sample 1'],True)
        wait(lambda:all(int(pairs(command(port,'SENTINEL','MASTER','sample'))['num-other-sentinels'])==4 for port in range(16503,16508)))
        wait(lambda:info(16501).get('master_link_status')=='up' and info(16502).get('master_link_status')=='up')
        command(16500,'SET','sample:key','before-failure')
        wait(lambda:command(16501,'GET','sample:key')=='before-failure' and command(16502,'GET','sample:key')=='before-failure')
        before={str(port):pairs(command(port,'SENTINEL','MASTER','sample')) for port in range(16503,16508)}
        replicas=[pairs(row) for row in command(16503,'SENTINEL','REPLICAS','sample')]
        assert len(replicas)==2
        assert sorted(int(r['slave-priority']) for r in replicas)==[0,100]
        event(name+'-known-five',sentinels=before,replicas=replicas,data={str(p):info(p) for p in (16500,16501,16502)})
        for port in range(16503+available,16508):
            processes[port].terminate();processes[port].wait(timeout=5)
        processes[16500].terminate();processes[16500].wait(timeout=5)
        event(name+'-master-and-other-sentinels-stopped',activeSentinels=list(range(16503,16503+available)))
        if available==2:
            wait(lambda:all('o_down' in pairs(command(p,'SENTINEL','MASTER','sample'))['flags'] for p in (16503,16504)),15)
            snapshots=[]
            for _ in range(16):
                try:quorum=command(16503,'SENTINEL','CKQUORUM','sample')
                except RedisError as error:quorum={'error':str(error)}
                snapshot={'master':pairs(command(16503,'SENTINEL','MASTER','sample')),'ckquorum':quorum,'replicas':{str(p):info(p) for p in (16501,16502)}}
                assert snapshot['master']['port']=='16500'
                assert snapshot['master']['num-other-sentinels']=='4'
                assert all(v['role']=='slave' for v in snapshot['replicas'].values())
                assert isinstance(quorum,dict) and 'NOQUORUM' in quorum['error']
                snapshots.append(snapshot);time.sleep(.5)
            event(name+'-diagnosis-passes-authorization-blocks',snapshots=snapshots,observedSeconds=8,assertions=['ODOWN','known-five retained','CKQUORUM NOQUORUM','old master address retained','both replicas remain replicas'])
        else:
            wait(lambda:pairs(command(16503,'SENTINEL','MASTER','sample'))['port']=='16502',30)
            wait(lambda:info(16502)['role']=='master' and info(16501).get('master_port')=='16502' and info(16501).get('master_link_status')=='up',20)
            assert command(16502,'GET','sample:key')=='before-failure'
            command(16502,'SET','sample:after','new-master')
            wait(lambda:command(16501,'GET','sample:after')=='new-master')
            snapshots={str(p):pairs(command(p,'SENTINEL','MASTER','sample')) for p in (16503,16504,16505)}
            event(name+'-majority-promotes-eligible-replica',sentinels=snapshots,roles={str(p):info(p) for p in (16501,16502)},assertions=['R1 priority0 not promoted','R2 priority100 promoted','R1 follows new master','old key readable','new key replicates'])
        return {'passed':True,'case':name,'availableSentinels':available,'knownSentinels':5,'quorum':2}
    finally:
        for process in processes.values():
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)

report={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary':str(BINARY),'binarySHA256':hashlib.sha256(BINARY.read_bytes()).hexdigest(),'sourceCommit':'60ba86f3c8b4e1ec96451171753a0a38e5c45a0c','ports':list(range(16500,16508)),'scope':'Real local processes with process termination; not power loss, latency benchmark, async-loss reproduction, or general correctness proof.'}
try:
    report['cases']=[run_case('minority-two',2),run_case('majority-three',3)]
    report['passed']=True
except Exception:
    report['passed']=False;report['error']=traceback.format_exc();raise
finally:
    report['events']=EVENTS
    report['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (D/'runtime-latest.json').write_text(json.dumps({'run':str(OUT.relative_to(D)),'reportSHA256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),'passed':report['passed']},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'path':str(OUT),'passed':report['passed'],'cases':report.get('cases'),'error':report.get('error')},ensure_ascii=False,indent=2))
