"""Use the shared sentence assembler, then declare the unvoiced Python appendix."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

EP = Path(__file__).resolve().parent
ROOT = EP.parents[1]
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/assemble_sentence_episode.py'), str(EP)], check=True)
config = json.loads((EP / 'episode-config.json').read_text())
card = dict(config['unvoicedEndCard'])
sb = json.loads((EP / 'storyboard.json').read_text())
last = sb['scenes'][-1]['shots'][-1]
assert card['from'] + card['durationInFrames'] == sb['meta']['durationInFrames']
assert card['from'] > max(v['wavEnd'] for sc in sb['scenes'] for sh in sc['shots'] for v in sh['voice'])
last['codeCardFrom'] = card['from'] - last['from']
last['subtitles'][-1]['to'] = last['codeCardFrom'] - 1
last['subtitles'][-1]['duration'] = last['subtitles'][-1]['to'] - last['subtitles'][-1]['from'] + 1
last['timing']['holdReason'] = 'Original closing retained; final15 seconds show a complete static Python solution without narration/captions.'
for field in ['codeSource', 'displaySource']:
    card[field + 'Sha256'] = hashlib.sha256((EP / card[field]).read_bytes()).hexdigest()
sb['meta']['unvoicedEndCard'] = card
sb['meta']['revisionNote'] = 'Append complete Python solution for pause-to-read closure; previous6544 visual frames and spoken sentences preserved.'
(EP / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False, indent=2) + '\n')
print(f"Python card: frame{card['from']}..{card['from'] + card['durationInFrames'] - 1}")
