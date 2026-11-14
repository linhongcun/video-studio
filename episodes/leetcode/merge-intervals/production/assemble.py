import hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
EP=Path(__file__).resolve().parent
ROOT=next(p for p in EP.parents if (p/'AGENTS.md').exists())
plan={int(x['id']):x['visual'] for x in json.loads((EP/'plan.json').read_text())}
script=(EP/'script.md').read_text()
sections=re.split(r'(?m)(?=^### )',script)
for i,section in enumerate(sections):
 m=re.match(r'###\s+(\d+)',section)
 if m:
  number=int(m.group(1))
  if '画面：' not in section:
   sections[i]=re.sub(r'(?m)^(旁白：.*)$',r'\1\n画面：'+plan[number],section)
with tempfile.TemporaryDirectory(prefix='lc56-assemble-') as temp:
 d=Path(temp);(d/'voice').mkdir()
 (d/'script.md').write_text(''.join(sections))
 for f in ['plan.json','episode-config.json','covers.json']:shutil.copy2(EP/f,d/f)
 for f in ['build.json']:shutil.copy2(EP/'voice'/f,d/'voice'/f)
 shutil.copy2(EP/'voice.wav',d/'voice.wav')
 subprocess.run([sys.executable,str(ROOT/'episodes/_shared/assemble_sentence_episode.py'),str(d)],check=True)
 for f in ['storyboard.json','words.json','captions.srt','shot_frames.json']:
  if (d/f).exists():shutil.copy2(d/f,EP/f)
 for f in ['cues.json','cue_tests.json','shot_frames.json']:
  if (d/'voice'/f).exists():shutil.copy2(d/'voice'/f,EP/'voice'/f)
sha=hashlib.sha256((EP/'script.md').read_bytes()).hexdigest()
words=json.loads((EP/'words.json').read_text());words['scriptSha256']=sha;words['script']='script.md'
(EP/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2)+'\n')
story=json.loads((EP/'storyboard.json').read_text())
by_number={int(item['id']):item for item in json.loads((EP/'plan.json').read_text())}
for scene in story['scenes']:
 for shot in scene['shots']:
  actions=by_number[int(shot['id'])]['actions']
  shot['actionCues']=actions
  labels=shot['cueFrames'].setdefault('labels',{})
  for action in actions:
   labels[action['cue']]=shot['cueFrames']['sentences'][action['sentence']]
story['meta']['timingSource']='voice.wav '+hashlib.sha256((EP/'voice.wav').read_bytes()).hexdigest()+' + words.json '+hashlib.sha256((EP/'words.json').read_bytes()).hexdigest()+' + script.md '+sha
(EP/'storyboard.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n')
print('Shared assembly complete; original reviewed script SHA retained.')
