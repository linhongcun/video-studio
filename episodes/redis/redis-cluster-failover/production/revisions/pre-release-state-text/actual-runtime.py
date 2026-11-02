#!/usr/bin/env python3
"""Six real local Redis8.4 processes; exact configs/logs, no synthetic Broker claims."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,time,traceback
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').exists())
BIN=ROOT.parent/'work/redis-batch/runtime/redis-60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src'
OUT=D/'examples/actual-runtime';OUT.mkdir(parents=True,exist_ok=True)
PORTS=list(range(16600,16606));PROCS=[];COMMANDS=[]
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def cli(port,*args,allow_error=False):
    c=[str(BIN/'redis-cli'),'-h','127.0.0.1','-p',str(port),'--raw',*map(str,args)]
    r=subprocess.run(c,capture_output=True,text=True,timeout=5)
    COMMANDS.append(dict(port=port,args=list(args),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if not allow_error:assert r.returncode==0,(args,r.stderr)
    return r.stdout.strip()
def until(label,predicate,timeout=20):
    start=time.monotonic()
    while time.monotonic()-start<timeout:
        try:
            v=predicate()
            if v:return v
        except (AssertionError,subprocess.TimeoutExpired):pass
        time.sleep(.15)
    raise AssertionError('Timed out '+label)
def stop_all():
    for p in PROCS:
        if p.poll() is None:
            try:os.kill(p.pid,signal.SIGCONT);p.terminate()
            except ProcessLookupError:pass
    for p in PROCS:
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
    PROCS.clear()
def setup(name):
    stop_all();work=OUT/name;work.mkdir(exist_ok=True)
    for i,port in enumerate(PORTS):
        q=work/str(port);q.mkdir(exist_ok=True)
        conf=f'bind 127.0.0.1\nprotected-mode no\nport {port}\ncluster-enabled yes\ncluster-config-file nodes.conf\ncluster-node-timeout 1500\ncluster-announce-ip 127.0.0.1\ncluster-announce-port {port}\ncluster-announce-bus-port {port+10000}\ncluster-require-full-coverage yes\ncluster-replica-validity-factor 10\nappendonly no\nsave ""\ndir {q}\nloglevel debug\n'
        (q/'redis.conf').write_text(conf)
        log=open(q/'process.log','w');PROCS.append(subprocess.Popen([str(BIN/'redis-server'),str(q/'redis.conf')],stdout=log,stderr=subprocess.STDOUT));log.close()
    for port in PORTS:until('ping'+str(port),lambda p=port:cli(p,'PING',allow_error=True)=='PONG',10)
    ids=[cli(p,'CLUSTER','MYID') for p in PORTS]
    for i,p in enumerate(PORTS):assert cli(p,'CLUSTER','SET-CONFIG-EPOCH',i+1)=='OK'
    for p in PORTS[1:]:assert cli(p,'CLUSTER','MEET','127.0.0.1',PORTS[0])=='OK'
    until('six-known',lambda:all('cluster_known_nodes:6' in cli(p,'CLUSTER','INFO') for p in PORTS))
    for i,p in enumerate(PORTS[:3]):
        a,b=[(0,5460),(5461,10922),(10923,16383)][i]
        assert cli(p,'CLUSTER','ADDSLOTSRANGE',a,b)=='OK'
    for i,p in enumerate(PORTS[3:]):assert cli(p,'CLUSTER','REPLICATE',ids[i])=='OK'
    until('cluster-ok',lambda:all('cluster_state:ok' in cli(p,'CLUSTER','INFO') for p in PORTS))
    until('three-replication-links',lambda:all('master_link_status:up' in cli(p,'INFO','replication') for p in PORTS[3:]))
    key=next(f'item:{i}' for i in range(30) if int(cli(PORTS[0],'CLUSTER','KEYSLOT',f'item:{i}'))<=5460)
    assert cli(PORTS[0],'SET',key,'before-failover')=='OK'
    until('replicated-value',lambda:cli(PORTS[3],'GET',key,allow_error=True)=='before-failover' or ('before-failover' in cli(PORTS[3],'DEBUG','DIGEST-VALUE',key,allow_error=True)),3) if False else None
    assert int(cli(PORTS[0],'WAIT',1,5000))>=1
    snap={str(p):dict(cluster=cli(p,'CLUSTER','NODES'),info=cli(p,'INFO','replication')) for p in PORTS}
    dump(work/'before.json',snap)
    return work,ids,key
def logs(work):
    result={}
    for p in PORTS:
        src=work/str(p)/'process.log';text=src.read_text(errors='replace');(work/(str(p)+'-log.txt')).write_text(text)
        result[str(p)]=[l for l in text.splitlines() if any(s in l.lower() for s in ['failover','election','marking node','auth granted','not possible','epoch'])]
    dump(work/'mechanism-log-excerpts.json',result);return result
def main():
    results=[];start=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    try:
        w,ids,key=setup('majority-success')
        PROCS[0].kill();PROCS[0].wait(timeout=5)
        until('A1-promoted',lambda:cli(PORTS[3],'ROLE').splitlines()[0]=='master',20)
        until('owners-converged',lambda:all(ids[3] in next((l for l in cli(p,'CLUSTER','NODES').splitlines() if l.startswith(ids[3])),'') and '0-5460' in next((l for l in cli(p,'CLUSTER','NODES').splitlines() if l.startswith(ids[3])),'') for p in PORTS[1:3]))
        value=cli(PORTS[3],'GET',key);assert value=='before-failover'
        snap={str(p):dict(nodes=cli(p,'CLUSTER','NODES'),role=cli(p,'ROLE'),info=cli(p,'CLUSTER','INFO')) for p in PORTS[1:]}
        dump(w/'after.json',snap);ls=logs(w)
        assert any('Failover auth granted' in l for l in ls[str(PORTS[1])]);assert any('Failover auth granted' in l for l in ls[str(PORTS[2])])
        assert any("Failover election won" in l for l in ls[str(PORTS[3])])
        results.append(dict(name='majority-success',passed=True,originalSlotMasters=3,expectedThreshold=2,promotedNode=ids[3],slots=[0,5460],valueRetained=value,note='WAIT completed before fault; this does not test loss of unreplicated writes.'))
        print('majority-success passed',flush=True)
        w,ids,key=setup('one-vote-only')
        os.kill(PROCS[3].pid,signal.SIGSTOP)
        PROCS[0].kill();PROCS[0].wait(timeout=5)
        until('B-C-confirm-A-FAIL',lambda:all('fail' in next((l.split()[2] for l in cli(p,'CLUSTER','NODES').splitlines() if l.startswith(ids[0])),'').split(',') for p in PORTS[1:3]),12)
        dump(w/'fail-confirmed-before-vote.json',{str(p):cli(p,'CLUSTER','NODES') for p in PORTS[1:3]})
        PROCS[2].kill();PROCS[2].wait(timeout=5)
        os.kill(PROCS[3].pid,signal.SIGCONT)
        # Candidate drains already queued FAIL messages then has only master B reachable.
        until('candidate-election-started',lambda:'Starting a failover election' in (w/str(PORTS[3])/'process.log').read_text(),10)
        time.sleep(4)
        role=cli(PORTS[3],'ROLE');nodes=cli(PORTS[3],'CLUSTER','NODES');assert role.splitlines()[0]=='slave'
        ls=logs(w);assert not any('Failover election won' in l for l in ls[str(PORTS[3])]);assert any('Failover auth granted' in l for l in ls[str(PORTS[1])])
        dump(w/'after.json',dict(candidateRole=role,candidateNodes=nodes,remainingMasterNodes=cli(PORTS[1],'CLUSTER','NODES')))
        results.append(dict(name='one-vote-only',passed=True,originalSlotMasters=3,reachableSlotMasters=1,candidateRole='slave',noPromotionObservedSeconds=4,note='Candidate SIGSTOP gated until FAIL confirmed by B/C; C killed before candidate resumed. Not a general network partition or timing guarantee.'))
        print('one-vote-only passed',flush=True)
        result=dict(passed=True,startedAt=start,finishedAt=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),version=subprocess.check_output([str(BIN/'redis-server'),'--version'],text=True).strip(),binarySHA256=hashlib.sha256((BIN/'redis-server').read_bytes()).hexdigest(),sourceCommit='60ba86f3c8b4e1ec96451171753a0a38e5c45a0c',scenarios=results,limits=['Six localhost processes; process kill/SIGSTOP, no physical power loss','Known replicated value retained in success only; asynchronous data loss covered by source/model, not this experiment','No benchmark or all possible protocol paths tested'])
    except Exception as e:
        result=dict(passed=False,startedAt=start,error=str(e),traceback=traceback.format_exc(),partialResults=results);raise
    finally:
        stop_all();dump(OUT/'commands.json',COMMANDS);dump(OUT/'result.json',result)
if __name__=='__main__':main()
