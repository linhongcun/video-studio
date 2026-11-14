import json,shutil,subprocess,sys
from pathlib import Path
EP=Path(__file__).resolve().parent
b=json.loads((EP/'voice/build.json').read_text());c=json.loads((EP/'episode-config.json').read_text())
card=c['unvoicedEndCard'];card['durationInFrames']=round(card['durationSeconds']*30);card['from']=b['summary']['frames']-card['durationInFrames']
assert card['from']>=0
(EP/'episode-config.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(EP/'scripts/build_code_card.py')],check=True)
shutil.copy2(EP/'voice.wav',EP/'remotion/public/audio/voice.wav')
subprocess.run([sys.executable,str(EP/'assemble.py')],check=True)
s=json.loads((EP/'storyboard.json').read_text());last=s['scenes'][-1]['shots'][-1]
last['codeCardFrom']=card['from']-last['from'];s['meta']['unvoicedEndCard']=card
assert last['from']+last['durationInFrames']==b['summary']['frames']
if last.get('subtitles'):last['subtitles'][-1]['to']=last['codeCardFrom']-1
(EP/'storyboard.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('Code-card start derived from the real voice build.')
