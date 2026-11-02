#!/usr/bin/env python3
"""Finite teaching model of sampled scores and a persistent eviction pool.

This is deliberately not a Redis execution trace or its dictionary RNG. The
explicit sample input drives the visual example; actual Redis is verified in
runtime_verify.py. Scores stay as captured when sampled; pick checks existence.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

D = Path(__file__).resolve().parent
checks = []

def check(name, value):
    assert value, name
    checks.append(name)

@dataclass
class Entry:
    key: str
    sampledIdle: int
    sampledRound: int

class Pool:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.entries = []
    def populate(self, samples, idle, round_number):
        for key in samples:
            self.entries.append(Entry(key, idle[key], round_number))
            self.entries.sort(key=lambda x: x.sampledIdle)
            self.entries = self.entries[-self.capacity:]
    def pick(self, live):
        ghosts = []
        while self.entries:
            entry = self.entries.pop()
            if entry.key in live:
                return entry, ghosts
            ghosts.append(entry.key)
        return None, ghosts
    def snapshot(self):
        return [asdict(e) for e in self.entries]

def run():
    idle = dict(zip('ABCDEFGH', range(90, 10, -10)))
    live = set(idle)
    states = []
    pool = Pool()
    def save(name, **details):
        states.append(dict(id=name, live=sorted(live), pool=pool.snapshot(), **details))
    check('initial eight distinct keys', len(live)==8)
    check('global oldest A90', max(live, key=idle.get)=='A' and idle['A']==90)
    save('initial', idle=idle.copy(), exactLRUVictim='A', sampledLRUVictim=None)
    pool.populate(list('CDE'), idle, 1)
    check('first pool ascending sampled score', [e.key for e in pool.entries]==list('EDC'))
    check('actual fixed capacity 16', pool.capacity==16)
    save('first-populated', samples=list('CDE'), idle=idle.copy())
    victim, ghosts = pool.pick(live)
    check('first chosen C70', (victim.key,victim.sampledIdle)==('C',70))
    check('first selection exists', not ghosts and victim.key in live)
    live.remove(victim.key); live.add('I'); idle['I']=0
    check('first victim differs from global A', 'A' in live and victim.key!='A')
    check('I replaces C in equal-cell teaching model', len(live)==8)
    check('D and E remain candidates', [e.key for e in pool.entries]==list('ED'))
    save('first-evicted', victim=asdict(victim), inserted='I', idle=idle.copy())
    previous = pool.snapshot()
    pool.populate(list('FGH'), idle, 2)
    check('second pool retains both earlier entries', all(p in pool.snapshot() for p in previous))
    check('new sample excludes D', 'D' not in list('FGH'))
    check('combined second order', [e.key for e in pool.entries]==list('HGFED'))
    save('second-populated', samples=list('FGH'), idle=idle.copy())
    victim, ghosts = pool.pick(live)
    check('retained D60 wins second round', (victim.key,victim.sampledIdle,victim.sampledRound)==('D',60,1))
    live.remove('D');live.add('J');idle['J']=0
    check('second victim absent from fresh sample', victim.key not in list('FGH'))
    check('A remains after two approximated choices', 'A' in live)
    check('J replaces D with no duplicate keys', len(live)==8)
    save('second-evicted', victim=asdict(victim), inserted='J', idle=idle.copy())
    live.remove('E')
    check('ghost record survives external deletion', 'E' not in live and any(e.key=='E' for e in pool.entries))
    # DEL alone frees capacity; it is not a trigger to evict another key.
    live.add('K');idle['K']=0
    pool.populate(list('IJK'),idle,3)
    check('later K fills vacancy before L needs eviction', len(live)==8 and 'K' in live)
    check('new samples cannot outrank stale E50 in ghost vignette', all(idle[k]==0 for k in 'IJK'))
    save('ghost-before-check', externallyDeleted='E', insertedAfterDeletion='K', pendingWrite='L', freshSamples=list('IJK'), idle=idle.copy())
    victim, ghosts = pool.pick(live)
    check('missing E candidate skipped', ghosts==['E'])
    check('next existing F wins ghost branch', victim.key=='F' and victim.sampledIdle==40)
    save('ghost-skipped', skipped=ghosts, nextExisting=asdict(victim), idle=idle.copy())
    # Captured scores do not silently refresh when a live key is read again.
    stale = Pool();stale.populate(['A'],{'A':90},1)
    current = {'A':0};victim,_=stale.pick({'A'})
    check('pool uses captured score after a later read', victim.sampledIdle==90 and current['A']==0)
    duplicate = Pool(); duplicate.populate(['X'],{'X':5},1);duplicate.populate(['X'],{'X':5},2)
    check('duplicate candidates are allowed', len(duplicate.entries)==2)
    first,_=duplicate.pick({'X'});second,skipped=duplicate.pick(set())
    check('duplicate becomes ghost after real deletion', first.key=='X' and second is None and skipped==['X'])
    full = Pool();full.populate([str(i) for i in range(1,17)],{str(i):i for i in range(1,17)},1)
    full.populate(['low'],{'low':0},2)
    check('full pool rejects worse candidate', len(full.entries)==16 and all(e.key!='low' for e in full.entries))
    full.populate(['high'],{'high':100},3)
    check('full pool keeps better candidate within bounded capacity', len(full.entries)==16 and full.entries[-1].key=='high' and all(e.key!='1' for e in full.entries))
    result={'kind':'finite-explicit-sample-teaching-model','actualRedisExecution':False,'sourceVersion':'Redis8.4.0 / 60ba86f3c8b4e1ec96451171753a0a38e5c45a0c','assumptions':['single DB/allkeys-lru','no TTL','equal-size visualization cells; real maxmemory is bytes','two continuous evictions use unchanged sampled scores, no intervening reads','sample stream is supplied explicitly, not Redis RNG','16 actual pool slots; occupied entries visualized enlarged','main example has distinct sampled scores; this finite model does not claim exact C equal-score tie insertion order'],'checks':checks,'checkCount':len(checks),'passed':True,'states':states}
    (D/'model.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'checks':len(checks),'states':len(states)},ensure_ascii=False))

if __name__=='__main__':run()
