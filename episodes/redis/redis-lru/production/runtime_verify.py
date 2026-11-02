#!/usr/bin/env python3
"""Run actual Redis8.4.0 on isolated loopback16700; no performance benchmark.

We inspect observed evictions, not hidden sample/pool state. This cannot certify
the video's predetermined sample stream; the finite model has that separate role.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import socket, subprocess, json, time, hashlib, shutil

D=Path(__file__).resolve().parent
R=D/'runtime';R.mkdir(exist_ok=True)
BIN=Path('/workspace/work/redis-batch/runtime/redis-60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/redis-server')
PORT=16700

class Client:
    def __init__(self):
        self.s=socket.create_connection(('127.0.0.1',PORT),timeout=4)
        self.f=self.s.makefile('rb')
        self.commands=[]
    def cmd(self,*args,record=True):
        parts=[a if isinstance(a,bytes) else str(a).encode() for a in args]
        self.s.sendall(b'*'+str(len(parts)).encode()+b'\r\n'+b''.join(b'$'+str(len(p)).encode()+b'\r\n'+p+b'\r\n' for p in parts))
        result=self.read()
        def plain(value):
            if isinstance(value,bytes):return value.decode(errors='replace')
            if isinstance(value,list):return [plain(v) for v in value]
            return value
        if record:self.commands.append({'command':[a if not isinstance(a,bytes) else '<%d byte value>'%len(a) for a in args],'reply':plain(result)})
        return result
    def read(self):
        t=self.f.read(1);v=self.f.readline()[:-2]
        if t==b'+':return v
        if t==b'-':raise RuntimeError(v.decode())
        if t==b':':return int(v)
        if t==b'$':
            n=int(v)
            if n<0:return None
            result=self.f.read(n);assert self.f.read(2)==b'\r\n';return result
        if t==b'*':return [self.read() for _ in range(int(v))]
        raise RuntimeError((t,v))
    def close(self):self.f.close();self.s.close()

def info(c,section):
    raw=c.cmd('INFO',section,record=False).decode()
    return {k:v for line in raw.splitlines() if line and not line.startswith('#') for k,v in [line.split(':',1)]}

def main():
    assert BIN.is_file(),BIN
    manifest=Path('/workspace/work/redis-batch/runtime/runtime-manifest.json')
    if manifest.exists():shutil.copyfile(manifest,R/'shared-runtime-manifest.json')
    trials=[];assertions=[]
    def check(name,value):
        assert value,name;assertions.append(name)
    for n in range(1,4):
        trial=R/f'trial-{n}';trial.mkdir(exist_ok=True)
        cfg=trial/'redis.conf'
        cfg.write_text(f'bind 127.0.0.1\nport {PORT}\nprotected-mode yes\nsave ""\nappendonly no\nmaxmemory 0\nmaxmemory-policy allkeys-lru\nmaxmemory-samples 1\nlazyfree-lazy-eviction no\nloglevel notice\nlogfile {trial / "redis.log"}\ndir {trial}\n')
        p=subprocess.Popen([str(BIN),str(cfg)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        c=None
        try:
            for _ in range(100):
                try:c=Client();break
                except OSError:time.sleep(.05)
            assert c is not None,'start'
            check(f'trial{n} ping',c.cmd('PING')==b'PONG')
            server=info(c,'server');check(f'trial{n} exact Redis version',server['redis_version']=='8.4.0')
            for key in 'ABCDEFGH':c.cmd('SET',key,b'v'*65536)
            check(f'trial{n} eight initial keys',c.cmd('DBSIZE')==8)
            # Reads separated beyond the one-second approximate LRU clock.
            for key in 'ABCDEFGH':
                c.cmd('GET',key,record=False)
                time.sleep(1.10)
            ages={key:c.cmd('OBJECT','IDLETIME',key) for key in 'ABCDEFGH'}
            check(f'trial{n} A uniquely oldest',ages['A']>max(v for k,v in ages.items() if k!='A'))
            check(f'trial{n} all keys lack TTL',all(c.cmd('TTL',k)==-1 for k in 'ABCDEFGH'))
            memory=info(c,'memory');stats0=info(c,'stats')
            limit=int(memory['used_memory'])+32768
            c.cmd('CONFIG','SET','maxmemory',limit)
            c.cmd('SET','I',b'v'*65536)
            c.cmd('PING')
            after=info(c,'stats')
            c.cmd('CONFIG','SET','maxmemory',0)
            keys=sorted(k.decode() for k in c.cmd('KEYS','*'))
            evicted=sorted(set('ABCDEFGHI')-set(keys))
            evicted_count=int(after['evicted_keys'])-int(stats0['evicted_keys'])
            check(f'trial{n} actual eviction occurred',evicted_count>0 and len(evicted)>0)
            check(f'trial{n} no TTL expiration',int(after['expired_keys'])==0)
            trial_result={'trial':n,'server':server,'sampleCount':1,'policy':'allkeys-lru','valueBytes':65536,'agesBeforePressureSeconds':ages,'memoryBeforePressure':memory,'configuredMaxmemoryBytes':limit,'statsBeforePressure':stats0,'statsAfterPressure':after,'survivors':keys,'absentKeys':evicted,'evictedCountDelta':evicted_count,'globallyOldestAStillExists':'A' in keys,'counterexampleObserved':'A' in keys and any(k!='A' for k in evicted),'limit':'Does not expose internal random samples or pool; no RNG seed, latency, throughput or cache-hit claim.'}
            (trial/'commands.json').write_text(json.dumps(c.commands,ensure_ascii=False,indent=2)+'\n')
            (trial/'result.json').write_text(json.dumps(trial_result,ensure_ascii=False,indent=2)+'\n')
            trials.append(trial_result)
            if trial_result['counterexampleObserved']:break
        finally:
            if c:
                try:c.cmd('SHUTDOWN','NOSAVE')
                except Exception:pass
                c.close()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=5)
    result={'kind':'actual-local-Redis-process-experiment','checkedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(),'binary':str(BIN),'binarySHA256':hashlib.sha256(BIN.read_bytes()).hexdigest(),'port':PORT,'assertions':assertions,'passed':True,'counterexampleObserved':any(t['counterexampleObserved'] for t in trials),'trials':trials,'scope':'Actual loopback Redis8.4.0 allkeys-lru/samples1 noTTL, no persistence/replication; observed key loss and stats only; differs deliberately from 3-sample scripted teaching sequence.'}
    (R/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'assertions':len(assertions),'trials':len(trials),'counterexampleObserved':result['counterexampleObserved']},ensure_ascii=False))

if __name__=='__main__':main()
