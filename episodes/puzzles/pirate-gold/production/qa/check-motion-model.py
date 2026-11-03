"""Read-only independent reverse-induction check; writes only this QA result.

The expected allocations are derived here from the rules, independently of the
animation implementation and without changing production/model-data.json.
"""
from pathlib import Path
from itertools import combinations
import json, hashlib

D = Path(__file__).resolve().parent.parent
actual = json.loads((D / 'model-data.json').read_text())
expected = []
baseline = {}
for n in range(1, 6):
    players = list(range(6-n, 6))
    proposer = players[0]
    quota = (n+1)//2
    needed = quota-1
    costs = {p: baseline[p]+1 for p in players[1:]}
    choices = list(combinations(players[1:], needed))
    winners = min(choices, key=lambda pick: (sum(costs[p] for p in pick), pick))
    allocation = {p: 0 for p in players}
    for p in winners:
        allocation[p] = costs[p]
    allocation[proposer] = 100-sum(costs[p] for p in winners)
    yes = [proposer] + [p for p in players[1:] if allocation[p] > baseline[p]]
    assert sum(allocation.values()) == 100 and allocation[proposer] >= 0
    assert len(yes) >= quota
    model = next(r for r in actual['rounds'] if r['n'] == n)
    assert model['players'] == players
    assert model['quota'] == quota
    assert model['allocation'] == {str(p): a for p, a in allocation.items()}
    expected.append({'n': n, 'players': players, 'quota': quota,
                     'rejectBaseline': baseline, 'minimumCoinCosts': costs,
                     'allocation': allocation, 'yesVotes': yes})
    baseline = allocation

assert [r['quota'] for r in expected[1:]] == [1, 2, 2, 3]
assert expected[-1]['allocation'] == {1:98, 2:0, 3:1, 4:0, 5:1}
assert expected[-1]['minimumCoinCosts'][4] == 2
assert expected[-1]['yesVotes'] == [1, 3, 5]
report = {'executor': 'Independent motion QA', 'passed': True,
          'method': 'Enumerate minimal sets of strict improvements over the next-round baseline; proposer has one vote.',
          'modelSHA256': hashlib.sha256((D/'model-data.json').read_bytes()).hexdigest(),
          'rounds': expected,
          'scope': 'Mathematical model only; does not assert animation or media passed.'}
(D/'qa/motion-model-independent.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print('independent reverse induction PASS: quotas 1/2/2/3, final 98/0/1/0/1')
