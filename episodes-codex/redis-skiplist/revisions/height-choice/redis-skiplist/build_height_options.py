#!/usr/bin/env python3
"""Build two independent fixed-height examples from the same pre-insertion graph.

These are legal forward-link teaching cases, not observed Redis RNG draws.
The one-level result is a counterexample, never an intermediate state that
is later promoted into the two-level insertion.
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json

D = Path(__file__).resolve().parent


def snapshot(nodes, head, levels):
    paths = []
    for level in range(levels):
        path, current = [], head
        while nodes[current]['forward'][level] is not None:
            current = nodes[current]['forward'][level]
            assert current not in path and nodes[current]['height'] > level
            path.append(current)
        paths.append(path)
    return {'nodes': deepcopy(nodes), 'levels': paths,
            'reachableBottom': list(paths[0])}


def build_case(model, height):
    nodes = deepcopy(model['before']['nodes'])
    new_id = model['newNode']['id']
    nodes[new_id] = {'id': new_id, 'value': model['target'],
                     'height': height, 'forward': [None] * height}
    allocated = snapshot(nodes, model['head'], model['levelCount'])
    writes = []
    for level in range(height):
        predecessor = model['search']['predecessors'][level]
        successor = nodes[predecessor]['forward'][level]
        for owner, target, role in [(new_id, successor, 'new-successor'),
                                    (predecessor, new_id, 'predecessor-link')]:
            old = nodes[owner]['forward'][level]
            nodes[owner]['forward'][level] = target
            writes.append({'level': level, 'owner': owner, 'oldTarget': old,
                           'newTarget': target, 'role': role,
                           'snapshot': snapshot(nodes, model['head'], model['levelCount'])})
    return {'selectedHeightBeforeWiring': height,
            'allocated': allocated, 'pointerWrites': writes,
            'completeAfterWrites': 2 * height,
            'after': snapshot(nodes, model['head'], model['levelCount'])}


def main():
    original_bytes = (D / 'model.json').read_bytes()
    model = json.loads(original_bytes)
    cases = {f'height{height}': build_case(model, height) for height in [1, 2]}
    assert model['newNode']['id'] not in model['before']['nodes']
    assert (D / 'model.json').read_bytes() == original_bytes
    assert cases['height1']['after']['levels'][1] == model['before']['levels'][1]
    assert cases['height1']['after']['nodes']['n55']['height'] == 1
    assert cases['height2']['after'] == model['after']
    assert [w['snapshot'] for w in cases['height2']['pointerWrites']] == [
        w['snapshot'] for w in model['insertion']['pointerWrites']]
    result = {'schemaVersion': 1, 'kind': 'independent-height-choice-examples',
              'baseModelSHA256': hashlib.sha256(original_bytes).hexdigest(),
              'sameBeforeForBothCases': deepcopy(model['before']),
              'levelCountOfWholeSkiplist': model['levelCount'],
              'heightSelection': 'Fixed legal choices before wiring; not a Redis RNG replay.',
              'forwardLinksOnly': True,
              'hiddenRedisSpanUpdatesAreNotClaimedUnchanged': True,
              'cases': cases}
    (D / 'height-options.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cases': [1, 2], 'baseModelUnchanged': True,
                      'twoLevelCaseMatchesOriginal': True}))


if __name__ == '__main__':
    main()
