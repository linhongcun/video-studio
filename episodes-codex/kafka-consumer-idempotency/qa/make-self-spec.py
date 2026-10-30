#!/usr/bin/env python3
"""Prepare exact samples only from the measured current board, never mock timing."""
from pathlib import Path
import hashlib, json, math

D = Path(__file__).resolve().parent.parent
board = json.loads((D/'storyboard.json').read_text())
shots = [s for scene in board['scenes'] for s in scene['shots']]
samples = {}
timing = []

def add(frame, label, state=None):
    frame = int(frame)
    row = samples.setdefault(frame, {'frame': frame, 'labels': []})
    row['labels'].append(label)
    if state:
        row['expectedState'] = state

for shot in shots:
    n = int(shot['id']); start = shot['from']; duration = shot['durationInFrames']
    a, b = shot['voice'][0]['localStart'], shot['voice'][0]['localEnd']
    c, e = shot['voice'][1]['localStart'], shot['voice'][1]['localEnd']
    at = lambda p: a + (b-a)*p
    after = lambda p: c + (e-c)*p
    initial, edges, artwork = None, [], []
    if n == 1: initial, edges = 'business-committed-offset-old', [(at(.68), 'unguarded-twenty')]
    if n == 2: initial, edges = 'record-delivered', [(at(.55), 'business-committed-offset-old'), (c+15, 'crashed-before-offset-commit'), (after(.48), 'restored-zero'), (e-15, 'same-record-redelivered')]
    if n == 3: initial, edges = 'same-record-redelivered', [(at(.62), 'unguarded-twenty')]
    if n == 4: initial, edges, artwork = 'query-reset', [(after(.36), 'both-select-absent')], [(at(.53), 'reset overlay removed')]
    if n == 5: initial, edges = 'both-select-absent', [(at(.25), 'unsafe-first-award-committed'), (at(.68), 'unsafe-second-award-committed'), (after(.3), 'unsafe-late-mark'), (after(.68), 'unsafe-conflict-too-late')]
    if n == 6: initial, artwork = 'safe-reset', [(at(.45), 'reset overlay removed'), (c+12, 'both stable keys travel')]
    if n == 7: initial, edges = 'safe-reset', [(at(.12), 'index-check-protected'), (at(.48), 't1-insert-returned'), (at(.86), 't1-award-pending')]
    if n == 8: initial, edges = 'safe-reset', [(at(.12), 'index-check-protected'), (at(.68), 't1-insert-returned'), (c, 't1-award-pending'), (c+22, 't2-ordinary-select-absent'), (c+54, 't2-waits-for-t1')]
    if n == 9: initial, edges = 't2-waits-for-t1', [(at(.45), 't1-committed'), (after(.36), 't2-rechecked-existing')]
    if n == 10: initial, edges = 't2-rechecked-existing', [(at(.42), 't2-skipped-award'), (after(.24), 'redelivery-skipped'), (after(.82), 'offset-committed-separately')]
    if n == 11: initial, edges, artwork = 'rollback-reset-pending', [(after(.3), 't1-aborted')], [(at(.7), 'reset overlay removed')]
    if n == 12: initial, edges = 't1-aborted', [(at(.26), 't2-insert-after-abort'), (at(.62), 't2-award-pending'), (c+18, 't2-committed-after-abort')]
    if n == 13: initial, edges, artwork = 'split-reset', [(at(.8), 'mark-only-committed'), (c+15, 'failed-after-mark'), (after(.58), 'split-skips-needed-award')], [(at(.4), 'reset overlay removed')]
    def expected(local):
        value = initial
        for edge, next_state in edges:
            if local >= edge:
                value = next_state
        return value
    for local, label in [(0, 'start'), (duration//2, 'middle'), (duration-20, 'stable ending')]:
        add(start+local, f'shot{n:02} {label}', expected(local))
    for edge, label in edges + artwork:
        first = math.ceil(edge)
        for local, side in [(first-1, 'before'), (first, 'after')]:
            add(start+local, f'shot{n:02} {label} {side}', expected(local))
    # Interior flashback/current, actual moving-envelope and completion-label checks.
    extras = [at(.35), after(.2)] if n in [2, 4, 6, 7, 8, 9, 12] else []
    if n == 12: extras += [c+14, c+17, c+18]  # formerly premature completion wording risk.
    if n == 8: extras += [c+14, c+53, c+54]
    for local in extras:
        local = int(local)
        add(start+local, f'shot{n:02} interior or label guard', expected(local))
    timing.append({'shot': shot['id'], 'from': start, 'duration': duration,
                   'initialState': initial, 'voiceLocal': {'a': a, 'b': b, 'c': c, 'e': e},
                   'stateThresholds': [{'local': t, 'state': id} for t, id in edges],
                   'artworkThresholds': [{'local': t, 'label': label} for t, label in artwork]})

for figure in json.loads((D/'article-figure-plan.json').read_text())['figures']:
    if figure.get('frame') is not None:
        add(figure['frame'], 'exact article '+figure['file'], figure['modelState'])

rows = []
for row in sorted(samples.values(), key=lambda s: s['frame']):
    row['label'] = ' | '.join(row.pop('labels'))
    rows.append(row)
(D/'qa/self-frame-spec.json').write_text(json.dumps({'samples': rows}, ensure_ascii=False, indent=2)+'\n')
(D/'qa/state-timing.json').write_text(json.dumps({'status': 'current measured board, source-owner sampling plan',
    'MainSHA256': hashlib.sha256((D/'remotion/src/Main.tsx').read_bytes()).hexdigest(),
    'boardSHA256': hashlib.sha256((D/'storyboard.json').read_bytes()).hexdigest(),
    'voiceSHA256': hashlib.sha256((D/'voice.wav').read_bytes()).hexdigest(), 'shots': timing}, ensure_ascii=False, indent=2)+'\n')
print(len(rows), 'exact frame samples from', sum(s['durationInFrames'] for s in shots), 'measured frames')
