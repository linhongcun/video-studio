"""Declare the five-second code card after the unchanged shared assembler."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

EP = Path(__file__).resolve().parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
read = lambda p: json.loads(p.read_text())
save = lambda p, value: p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
config = read(EP / 'episode-config.json')
card = dict(config['unvoicedEndCard'])
card['from'] = read(EP / 'voice/build.json')['summary']['frames'] - card['durationInFrames']
config['unvoicedEndCard']['from'] = card['from']
save(EP / 'episode-config.json', config)
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/assemble_sentence_episode.py'), str(EP)], check=True)
sb = read(EP / 'storyboard.json')
last = sb['scenes'][-1]['shots'][-1]
assert card['from'] + card['durationInFrames'] == sb['meta']['durationInFrames']
assert card['from'] > max(v['wavEnd'] for sc in sb['scenes'] for sh in sc['shots'] for v in sh['voice'])
last['codeCardFrom'] = card['from'] - last['from']
last['subtitles'][-1]['to'] = last['codeCardFrom'] - 1
last['subtitles'][-1]['duration'] = last['subtitles'][-1]['to'] - last['subtitles'][-1]['from'] + 1
last['timing']['holdReason'] = 'Final five seconds show the complete static Python solution without narration or captions.'
for field in ['codeSource', 'displaySource']:
    card[field + 'Sha256'] = hashlib.sha256((EP / card[field]).read_bytes()).hexdigest()
sb['meta']['unvoicedEndCard'] = card
sb['meta']['revisionNote'] = 'Start with isConnected and its row/column semantics; map the same matrix to city connections before deriving groups and disjoint sets.'
save(EP / 'storyboard.json', sb)
print(f"Python card: {card['from']}..{card['from'] + 149}")
