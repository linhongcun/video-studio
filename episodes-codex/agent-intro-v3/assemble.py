"""Use shared timing assembly; add episode direction without duplicating audio math."""
from pathlib import Path
import json
import runpy
import sys

D = Path(__file__).resolve().parent
sys.argv = [str(D.parent / '_shared/assemble_sentence_episode.py'), str(D)]
runpy.run_path(sys.argv[0], run_name='__main__')
sb = json.loads((D / 'storyboard.json').read_text())
words = json.loads((D / 'words.json').read_text())
plan = json.loads((D / 'plan.json').read_text())
shots = [s for scene in sb['scenes'] for s in scene['shots']]
for shot, ws, item in zip(shots, words['shots'], plan):
    assert shot['id'] == item['id']
    assert ''.join(s['text'] for s in ws['sentences']) == item['narration']
    shot['title'] = item['title']
    shot['sampleState'] = item['state']
    shot['plannedActions'] = item['actions']
    shot['cueFrames']['sentenceEnds'] = [s['endFrame'] - shot['from'] for s in ws['sentences']]
    shot['cueFrames']['sentenceOnsets'] = [s['onsetFrame'] - shot['from'] for s in ws['sentences']]
    # The shared assembler's historical 7.5s description does not apply here.
    # gapShot/tail are already in the whole track; no extra timing hold is added.
    shot['timing']['naturalPauseFrames'] = shot['timing']['holdFrames']
    shot['timing']['holdFrames'] = 0
    shot['timing']['holdReason'] = 'Whole track with natural sentence/shot pauses; minShotFrames is disabled; no added timing hold.'
sb['meta']['openingPromise'] = 'Why does an AI agent switch from looking up an order to asking its user?'
(D / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False, indent=2) + '\n')
