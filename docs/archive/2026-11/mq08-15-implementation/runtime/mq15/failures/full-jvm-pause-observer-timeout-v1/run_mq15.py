#!/usr/bin/env python3
"""Finite actual Kafka cluster observations; no animation-model outputs."""
from pathlib import Path
import base64, datetime, hashlib, json, os, queue, select, shutil, signal, socket, struct, subprocess, threading, time, uuid

A=Path(__file__).resolve().parent
K=Path('/tmp/mq08-15-runtime/kafka_2.13-4.4.0')
CP=os.pathsep.join([str(A/'classes')]+[str(p) for p in sorted((K/'libs').glob('*.jar'))])
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
SHA=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()

class GateProxy:
    def __init__(self,listen_port,backend_port,log):
        self.backend=backend_port;self.log=log;self.paused=False;self.closed=False;self.lock=threading.Lock();self.pairs=set()
        self.server=socket.socket();self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);self.server.bind(('127.0.0.1',listen_port));self.server.listen();self.server.settimeout(.2)
        self.thread=threading.Thread(target=self.accept,daemon=True);self.thread.start()
    def record(self,event,**kwargs):
        with self.log.open('a')as f:f.write(json.dumps({'atUTC':NOW(),'event':event,**kwargs})+'\n')
    def accept(self):
        while not self.closed:
            try:c,addr=self.server.accept()
            except (TimeoutError,socket.timeout):continue
            except OSError:return
            with self.lock:
                if self.paused or self.closed:c.close();continue
                try:b=socket.create_connection(('127.0.0.1',self.backend),timeout=1);b.settimeout(None)
                except OSError:c.close();continue
                pair=(c,b);self.pairs.add(pair)
            threading.Thread(target=self.forward,args=(pair,),daemon=True).start()
    def forward(self,pair):
        c,b=pair
        try:
            while not self.closed:
                ready,_,_=select.select([c,b],[],[],.2)
                for src in ready:
                    data=src.recv(65536)
                    if not data:return
                    (b if src is c else c).sendall(data)
        except OSError:pass
        finally:
            with self.lock:self.pairs.discard(pair)
            for s in pair:
                try:s.close()
                except OSError:pass
    def pause(self):
        with self.lock:
            self.paused=True;current=list(self.pairs)
            for pair in current:
                for s in pair:
                    try:s.shutdown(socket.SHUT_RDWR)
                    except OSError:pass
                    try:s.close()
                    except OSError:pass
        self.record('replication_gate_closed',existingConnectionsClosed=len(current),controllerListenerUnaffected=True)
    def resume(self):
        with self.lock:self.paused=False
        self.record('replication_gate_opened')
    def close(self):
        self.pause();self.closed=True;self.server.close();self.thread.join(timeout=1)

class Probe:
    def __init__(self,bootstrap,out):
        self.out=out;self.err=(out/'probe.stderr').open('w');self.p=subprocess.Popen(['java','-Xmx128m',f'-Dlog4j.configurationFile={A/"log4j2.yaml"}','-cp',CP,'Mq15Probe',bootstrap],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True,bufsize=1,start_new_session=True)
        self.q=queue.Queue();threading.Thread(target=self.read,daemon=True).start()
    def read(self):
        for line in self.p.stdout:self.q.put(line)
    def cmd(self,*parts,timeout=20):
        command='|'.join(str(p)for p in parts);self.p.stdin.write(command+'\n');self.p.stdin.flush()
        line=self.q.get(timeout=timeout);x=json.loads(line)
        with (self.out/'probe.jsonl').open('a')as f:f.write(line)
        assert x['ok'],x
        return x['result']
    def close(self):
        if self.p.poll() is None:
            try:self.p.stdin.write('quit\n');self.p.stdin.flush();self.p.wait(timeout=5)
            except BaseException:os.killpg(self.p.pid,signal.SIGKILL);self.p.wait()
        self.err.close()

def free_port():
    with socket.socket()as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

def physical(data,topic):
    result={}
    for node in [1,2,3]:
        files=sorted((data/f'node{node}'/'data'/f'{topic}-0').glob('*.log'));batches=[];end=0
        for f in files:
            raw=f.read_bytes();pos=0
            while pos+12<=len(raw):
                base,length=struct.unpack_from('>qi',raw,pos)
                if length==0:break
                assert length>=49 and pos+12+length<=len(raw),(f,pos,len(raw),length)
                magic=raw[pos+16];assert magic==2,(f,magic)
                delta=struct.unpack_from('>i',raw,pos+23)[0];last=base+delta;end=max(end,last+1)
                batches.append({'baseOffset':base,'lastOffset':last,'batchLength':length,'containsE01Bytes':b'E01'in raw[pos:pos+12+length]});pos+=12+length
        result[node]={'physicalLEO':end,'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':SHA(f)}for f in files],'batches':batches}
    return result

def main():
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');R=A/'runs'/stamp;R.mkdir(parents=True);T=Path('/tmp/mq08-15-runtime')/f'mq15-{stamp}';T.mkdir();(T/'OWNED-BY-MQ15').write_text(stamp)
    proc={};handles=[];gates={};probe=None;checks=[];observations=[];report={'startedAtUTC':NOW(),'tempDir':str(T),'out':str(R),'version':'4.4.0','sourceCommit':'1156b2752aaa28eafc0b4c4d387e63356793268d','pass':False,'cases':{},'sources':{p.name:SHA(p)for p in [A/'Mq15Probe.java',Path(__file__)]},'cleanup':{}}
    def emit(s):print(s,flush=True)
    def ck(name,ok,detail=None):
        entry={'atUTC':NOW(),'name':name,'pass':bool(ok),'detail':detail};checks.append(entry)
        with (R/'assertions.jsonl').open('a')as f:f.write(json.dumps(entry)+'\n')
        assert ok,entry
    def wait(name,fn,timeout=35):
        deadline=time.monotonic()+timeout;last=None
        while time.monotonic()<deadline:
            last=fn()
            if last:return last
            time.sleep(.1)
        raise AssertionError(f'timeout {name}; last {last}')
    def meta(topic):return probe.cmd('meta',topic)
    def wait_isr(topic,n):return wait(f'ISR{n} {topic}',lambda:(m if len((m:=meta(topic))['isr'])==n else None),timeout=50)
    def future(label,state='success'):
        v=wait('future '+label,lambda:(x if (x:=probe.cmd('result',label))['state']!='pending' else None),timeout=30)
        ck(label+' future '+state,v['state']==state,v);return v
    def snapshot(label,topic,with_hw=True):
        m=meta(topic);v={'atUTC':NOW(),'label':label,'topic':topic,'metadata':m,'physical':physical(T,topic)}
        if with_hw:v['consumerEndOffset']=probe.cmd('hw',topic)['consumerEndOffset']
        S=R/'snapshots'/label;S.mkdir(parents=True)
        for node,p in v['physical'].items():
            for i,f in enumerate(p['files']):
                src=Path(f['path']);dest=S/f'node{node}-{i}.log';dest.write_bytes(src.read_bytes());f['snapshot']=str(dest.relative_to(R));f['snapshotSHA256']=SHA(dest)
        (S/'observation.json').write_text(json.dumps(v,indent=2)+'\n');observations.append(v);return v
    def create(label):
        topic='mq15-'+label+'-'+stamp[-10:].lower();probe.cmd('create',topic);wait_isr(topic,3);cfg=probe.cmd('config',topic);ck(label+' RF3/minISR2/clean',cfg['min.insync.replicas']=='2'and cfg['unclean.leader.election.enable']=='false',cfg);return topic
    def start(node):
        env=os.environ.copy();env['KAFKA_HEAP_OPTS']='-Xms256m -Xmx384m';env['KAFKA_LOG4J_OPTS']=f'-Dlog4j.configurationFile={A/"log4j2.yaml"}';env['LOG_DIR']=str(T/f'node{node}'/'service-logs')
        h=(R/f'broker{node}-start{sum(1 for x in R.glob(f"broker{node}-start*.log"))+1}.log').open('w');handles.append(h)
        p=subprocess.Popen([str(K/'bin/kafka-server-start.sh'),str(R/f'broker{node}.properties')],stdout=h,stderr=subprocess.STDOUT,env=env,start_new_session=True);proc[node]=p;emit(f'broker {node} launched PID {p.pid}')
    def kill(node,reason):
        p=proc[node];os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10);emit(f'broker {node} killed: {reason}')
    try:
        # Own fresh dependency identity is checked again before launching anything.
        dep=A.parent/'dependencies';manifest=json.loads((dep/'kafka-distribution-files-sha256.json').read_text());ck('fresh distribution tree',all(SHA(K/f)==h for f,h in manifest.items()),len(manifest))
        report['dependencyIdentity']={'filesManifest':str(dep/'kafka-distribution-files-sha256.json'),'manifestSHA256':SHA(dep/'kafka-distribution-files-sha256.json'),'archiveSHA512':hashlib.file_digest((K.parent/'kafka_2.13-4.4.0.tgz').open('rb'),'sha512').hexdigest()}
        ports={n:{k:free_port()for k in ['client','backend','proxy','controller']}for n in [1,2,3]};report['ports']=ports;cluster=base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip('=');voters=','.join(f'{n}@127.0.0.1:{ports[n]["controller"]}'for n in [1,2,3]);report['clusterId']=cluster
        for node in [1,2,3]:
            d=T/f'node{node}';d.mkdir();p=ports[node];cfg={'process.roles':'broker,controller','node.id':node,'controller.quorum.voters':voters,'listeners':f'CLIENT://127.0.0.1:{p["client"]},REPLICATION://127.0.0.1:{p["backend"]},CONTROLLER://127.0.0.1:{p["controller"]}','advertised.listeners':f'CLIENT://127.0.0.1:{p["client"]},REPLICATION://127.0.0.1:{p["proxy"]}','listener.security.protocol.map':'CLIENT:PLAINTEXT,REPLICATION:PLAINTEXT,CONTROLLER:PLAINTEXT','inter.broker.listener.name':'REPLICATION','controller.listener.names':'CONTROLLER','log.dirs':d/'data','metadata.log.dir':d/'metadata','auto.create.topics.enable':'false','num.partitions':1,'default.replication.factor':3,'min.insync.replicas':2,'unclean.leader.election.enable':'false','offsets.topic.replication.factor':3,'offsets.topic.num.partitions':1,'transaction.state.log.replication.factor':3,'transaction.state.log.min.isr':2,'group.initial.rebalance.delay.ms':0,'replica.lag.time.max.ms':20000,'num.network.threads':2,'num.io.threads':2,'background.threads':2,'log.segment.bytes':1048576,'log.index.size.max.bytes':1048576,'controller.quorum.election.timeout.ms':1000,'controller.quorum.fetch.timeout.ms':2000}
            config=R/f'broker{node}.properties';config.write_text(''.join(f'{k}={v}\n'for k,v in cfg.items()));cmd=[str(K/'bin/kafka-storage.sh'),'format','-t',cluster,'-c',str(config),'--feature','kraft.version=0','--feature','eligible.leader.replicas.version=0'];r=subprocess.run(cmd,capture_output=True,text=True);(R/f'format{node}.stdout').write_text(r.stdout);(R/f'format{node}.stderr').write_text(r.stderr);ck('format node'+str(node),r.returncode==0,{'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});gates[node]=GateProxy(p['proxy'],p['backend'],R/f'gate{node}.jsonl')
        for node in [1,2,3]:start(node)
        bootstrap=','.join(f'127.0.0.1:{ports[n]["client"]}'for n in [1,2,3]);probe=Probe(bootstrap,R)
        f=probe.cmd('features',timeout=30);report['features']=f;ck('actual client version/commit',f['version']=='4.4.0'and f['commit']=='1156b2752aaa28ea',f);elr=f['finalized'].get('eligible.leader.replicas.version');ck('actual ELR level0 or absent-zero',elr is None or elr['max']==0,f);emit('three brokers running; features returned')
        # Healthy baselines each start at an independent empty partition.
        for acks,name in [('1','healthy-acks1'),('all','healthy-all')]:
            topic=create(name);probe.cmd('prepare',acks,topic);probe.cmd('send',name,topic,acks,'{"eventId":"E01","orderId":7042}');v=future(name);ck(name+' offset0',v['offset']==0,v);wait(name+' replicas',lambda:all(x['physicalLEO']==1 for x in physical(T,topic).values()));snap=snapshot(name,topic);ck(name+' all physical copies',all(x['physicalLEO']==1 for x in snap['physical'].values()),snap);report['cases'][name]={'topic':topic,'result':v,'snapshot':name};
        emit('healthy ack1/all passed')
        # Slow third member remains ISR: freeze one follower briefly, not the controller leader.
        topic=create('slow-current-isr');m=meta(topic);controller=probe.cmd('controller')['leaderId'];slow=next(n for n in m['isr']if n!=m['leader']and n!=controller);fast=next(n for n in m['isr']if n not in [m['leader'],slow]);probe.cmd('prepare','all',topic);os.killpg(proc[slow].pid,signal.SIGSTOP);stop_at=NOW();probe.cmd('send','slow-all',topic,'all','{"eventId":"E01","orderId":7042}');wait('two physical replicas',lambda:physical(T,topic)[fast]['physicalLEO']==1,timeout=8);before=snapshot('slow-before-resume',topic);v=probe.cmd('result','slow-all');ck('ISR3 all still pending despite two copies',len(before['metadata']['isr'])==3 and before['physical'][slow]['physicalLEO']==0 and before['physical'][fast]['physicalLEO']==1 and before['physical'][m['leader']]['physicalLEO']==1 and v['state']=='pending',{'snapshot':before,'future':v,'slow':slow,'fast':fast});ck('slow ISR3 consumer HW below offset1',before['consumerEndOffset']<1,before['consumerEndOffset']);os.killpg(proc[slow].pid,signal.SIGCONT);v=future('slow-all');wait_isr(topic,3);after=snapshot('slow-after-resume',topic);ck('slow resumed copy acknowledged',after['physical'][slow]['physicalLEO']==1 and v['state']=='success',after);report['cases']['slow-current-isr']={'topic':topic,'slow':slow,'fast':fast,'controllerLeader':controller,'SIGSTOPatUTC':stop_at,'before':'slow-before-resume','after':'slow-after-resume'};emit('slow third ISR member held ackall pending; resume passed')
        # A single stopped follower leaves two controllers available and ISR becomes2.
        topic=create('stable-isr2');m=meta(topic);controller=probe.cmd('controller')['leaderId'];stopped=next(n for n in m['isr']if n!=m['leader']and n!=controller);os.killpg(proc[stopped].pid,signal.SIGSTOP);m2=wait_isr(topic,2);probe.cmd('prepare','all',topic);probe.cmd('send','isr2-all',topic,'all','{"eventId":"E01","orderId":7042}');v=future('isr2-all');before=snapshot('isr2-ack',topic);ck('stable ISR2 all succeeds with two copies',len(before['metadata']['isr'])==2 and before['physical'][stopped]['physicalLEO']==0 and v['state']=='success',before);os.killpg(proc[stopped].pid,signal.SIGCONT);wait_isr(topic,3);report['cases']['stable-isr2']={'topic':topic,'stopped':stopped,'result':v,'snapshot':'isr2-ack'};emit('stable ISR2 ackall passed')
        # Gate replication data only; all controller processes stay running.
        topic=create('stable-isr1');leader=meta(topic)['leader'];probe.cmd('prepare','all',topic);gates[leader].pause();wait_isr(topic,1);before=snapshot('isr1-before-send',topic);probe.cmd('send','isr1-all',topic,'all','{"eventId":"E01","orderId":7042}');v=future('isr1-all','failure');after=snapshot('isr1-after-reject',topic);ck('ISR1 fails NotEnoughReplicas',v['exception'].endswith('NotEnoughReplicasException'),v);ck('ISR1 failure did not append',before['physical'][leader]['physicalLEO']==after['physical'][leader]['physicalLEO']==0,after);gates[leader].resume();wait_isr(topic,3);report['cases']['stable-isr1']={'topic':topic,'leader':leader,'result':v,'before':'isr1-before-send','after':'isr1-after-reject'};emit('stable ISR1 preappend rejection passed')
        # Already successful all branch survives one leader process loss and clean election.
        topic=report['cases']['healthy-all']['topic'];m=wait_isr(topic,3);old=m['leader'];snapshot('all-before-leader-kill',topic);kill(old,'all acknowledged survival case');new=wait('all clean election',lambda:(m if (m:=meta(topic))['leader']not in [-1,old]else None),timeout=30);s=snapshot('all-after-clean-election',topic);records=probe.cmd('read',topic)['records'];ck('all record retained after clean election',len(records)==1 and records[0]['value']=='{"eventId":"E01","orderId":7042}'and s['consumerEndOffset']==1,{'snapshot':s,'records':records});report['cases']['all-leader-failure']={'topic':topic,'oldLeader':old,'newLeader':new['leader'],'records':records,'snapshot':'all-after-clean-election'};start(old);wait_isr(topic,3);emit('all acknowledged E01 survived leader kill; old broker restored')
        # Gate both followers before an acks1 append, then kill while still gated.
        topic=create('acks1-loss');m=wait_isr(topic,3);old=m['leader'];probe.cmd('prepare','1',topic);gates[old].pause();probe.cmd('send','acks1-loss',topic,'1','{"eventId":"E01","orderId":7042}');v=future('acks1-loss');before=snapshot('acks1-before-kill',topic);ck('acks1 acknowledged only leader physical record',v['state']=='success'and len(before['metadata']['isr'])==3 and before['physical'][old]['physicalLEO']==1 and all(x['physicalLEO']==0 for n,x in before['physical'].items()if n!=old),before);ck('acks1 before fault HW0',before['consumerEndOffset']==0,before);kill(old,'acks1 acknowledged before followers received E01; replication gate remains closed');new=wait('acks1 clean election',lambda:(m if (m:=meta(topic))['leader']not in [-1,old]else None),timeout=30);after=snapshot('acks1-after-clean-election',topic);records=probe.cmd('read',topic)['records'];ck('clean new leader has no E01',after['physical'][new['leader']]['physicalLEO']==0 and after['consumerEndOffset']==0 and records==[],{'snapshot':after,'records':records});ck('offline former leader file still contains E01',after['physical'][old]['physicalLEO']==1 and any(x['containsE01Bytes']for x in after['physical'][old]['batches']),after['physical'][old]);report['cases']['acks1-leader-failure']={'topic':topic,'oldLeader':old,'newLeader':new['leader'],'result':v,'before':'acks1-before-kill','after':'acks1-after-clean-election','newLeaderVisibleRecords':records};emit('acks1 leader-loss controlled case passed')
        # Validate copied physical batches with the official distribution reader.
        logs=[p for p in (R/'snapshots').rglob('*.log')if p.stat().st_size]
        cmd=[str(K/'bin/kafka-dump-log.sh'),'--files',','.join(str(p)for p in logs),'--print-data-log','--deep-iteration'];dr=subprocess.run(cmd,capture_output=True,text=True,timeout=40);(R/'official-log-dump.stdout').write_text(dr.stdout);(R/'official-log-dump.stderr').write_text(dr.stderr);ck('official dump copied physical records',dr.returncode==0,{'exit':dr.returncode,'files':len(logs)});report['pass']=True
    except BaseException as exc:
        import traceback
        report['error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};emit('FAILED '+str(exc));raise
    finally:
        if probe:
            try:probe.close()
            except BaseException as exc:report['probeCloseError']=repr(exc)
        for node,p in proc.items():
            if p.poll()is None:
                try:os.killpg(p.pid,signal.SIGCONT);os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
                except BaseException:
                    if p.poll()is None:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
        for g in gates.values():g.close()
        for h in handles:h.close()
        report['cleanup']={'brokerPIDs':{n:p.pid for n,p in proc.items()},'allTrackedBrokersExited':all(p.poll()is not None for p in proc.values()),'allProxyListenersClosed':all(g.closed for g in gates.values())}
        assert (T/'OWNED-BY-MQ15').read_text()==stamp
        shutil.rmtree(T);report['cleanup']['ownTemporaryDataRemoved']=not T.exists();report['finishedAtUTC']=NOW();report['assertions']=len(checks);report['observations']=len(observations);report['limits']=['Loopback Java process and TCP replication gate tests, not throughput benchmarking or machine powerloss.','Actual protocol observer consumer endOffsets is separately reported from physical replica LEO parsed from copied record batches and checked using official DumpLogSegments.','Combined KRaft controllers share each broker JVM. One SIGSTOP/kill leaves two controllers available; dual replication gate preserves all controller listeners/processes.','No claim that offline former leader bytes disappear: ack1loss case explicitly preserves the former leader physical E01 while the clean elected leader has no record.'];(R/'report.json').write_text(json.dumps(report,indent=2)+'\n');(A/'latest-run.txt').write_text(str(R)+'\n');emit(json.dumps({'report':str(R/'report.json'),'pass':report['pass'],'assertions':len(checks),'cleanup':report['cleanup']}))

if __name__=='__main__':main()
