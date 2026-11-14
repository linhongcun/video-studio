import json
import re
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
script = (EP / 'script.md').read_text()
matches = re.findall(r'(?ms)^###\s+(\d+)\s+[\w-]+\s*\n旁白：(.*?)(?=^###\s+|^##\s+|\Z)', script)
sentences_by_id = {}
for shot_id, narration in matches:
    sentences = [part.strip() for part in re.split(r'(?<=[。！？])', narration) if part.strip()]
    if len(sentences) != 2:
        raise ValueError(f'{shot_id}: expected two narration sentences, got {len(sentences)}')
    sentences_by_id[int(shot_id)] = sentences

plan = json.loads((EP / 'plan.json').read_text())
if set(sentences_by_id) != {int(item['id']) for item in plan}:
    raise ValueError('Script shot IDs and plan IDs differ')
visual_terms = {cue['term'] for item in plan for cue in item['cues']}
if len(visual_terms) > 3:
    raise ValueError(f'Plan has {len(visual_terms)} visible cue terms; shared sentence QA allows at most 3.')

for item in plan:
    shot_id = int(item['id'])
    sentences = sentences_by_id[shot_id]
    for cue in item['cues']:
        sentence = cue['sentence']
        if sentence not in (0, 1) or not sentences[sentence].startswith(cue['term']):
            raise ValueError(
                f"{shot_id}: cue {cue['term']!r} does not prefix sentence {sentence}"
            )
    action_ids = set()
    for action in item['actions']:
        if action['id'] in action_ids:
            raise ValueError(f"{shot_id}: duplicate action id {action['id']!r}")
        action_ids.add(action['id'])
        sentence = action['sentence']
        if sentence not in (0, 1) or not sentences[sentence].startswith(action['cue']):
            raise ValueError(
                f"{shot_id}: action {action['id']!r} cue {action['cue']!r} does not prefix sentence {sentence}"
            )

print(f'Plan cue preflight passed: {len(plan)} shots, {sum(len(item["cues"]) for item in plan)} visible sentence cues ({len(visual_terms)} unique), {sum(len(item["actions"]) for item in plan)} exact sentence-bound actions.')
