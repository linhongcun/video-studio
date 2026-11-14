import hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
EP=Path(__file__).resolve().parent
ROOT=next(p for p in EP.parents if (p/'AGENTS.md').exists())
plan_items=json.loads((EP/'plan.json').read_text())
plan={int(x['id']):x['visual'] for x in plan_items}
voice_words=json.loads((EP/'words.json').read_text())
shared_cues=json.loads((EP/'voice/cues.json').read_text())
words_by_number={int(re.match(r'\d+',shot['id']).group()):shot for shot in voice_words['shots']}
for item in plan_items:
 word_shot=words_by_number[int(item['id'])]
 for action in item['actions']:
  sentence=word_shot['sentences'][action['sentence']]
  if sentence['text'].startswith(action['cue']):continue
  if not any(c['shot']==word_shot['id'] and c['sentence']==sentence['id'] and c['cue']==action['cue'] for c in shared_cues):
   raise ValueError(f"{item['id']}: internal action cue {action['cue']!r} needs an exact shared voice/cues.json onset; no sentence-start fallback")
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
 for f in ['shot_frames.json']:
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
   sentence=shot['subtitles'][action['sentence']]['text']
   if sentence.startswith(action['cue']):
    labels[action['cue']]=shot['cueFrames']['sentences'][action['sentence']]
   else:
    word_shot=words_by_number[int(shot['id'])]
    sentence_id=word_shot['sentences'][action['sentence']]['id']
    cue=next(c for c in shared_cues if c['shot']==word_shot['id'] and c['sentence']==sentence_id and c['cue']==action['cue'])
    labels[action['cue']]=cue['onsetFrame']-shot['from']
   if action.get('endCue') and action['endCue'] not in labels:
    end_sentence=next((i for i,s in enumerate(shot['subtitles']) if s['text'].startswith(action['endCue'])),None)
    if end_sentence is not None:
     labels[action['endCue']]=shot['cueFrames']['sentences'][end_sentence]
    else:
     word_shot=words_by_number[int(shot['id'])]
     matches=[c for c in shared_cues if c['shot']==word_shot['id'] and c['cue']==action['endCue']]
     if len(matches)!=1:raise ValueError(f"{shot['id']}: end cue {action['endCue']!r} needs one exact shared onset")
     labels[action['endCue']]=matches[0]['onsetFrame']-shot['from']
story['meta']['timingSource']='voice.wav '+hashlib.sha256((EP/'voice.wav').read_bytes()).hexdigest()+' + words.json '+hashlib.sha256((EP/'words.json').read_bytes()).hexdigest()+' + script.md '+sha
(EP/'storyboard.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n')
print('Shared assembly complete; original reviewed script SHA retained.')
