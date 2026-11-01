from pathlib import Path
import json,hashlib,subprocess,math,re,ast
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent.parent
Q=D/'qa-independent';O=Q/'clip-review'
assert not O.exists(),'Preserve previous attempt'
O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identities={n:sha(D/n) for n in ['remotion/src/Main.tsx','model.json','storyboard.json','voice.wav','script.md','article.mdx','plan.json']}
assert identities['remotion/src/Main.tsx']=='50a4a92d5234b3f1eba6c168158c8e794be649c166d6b92c138a88f002ceb037'
owner=json.loads((D/'qa-own/actual-clips-and-captions.json').read_text())
assert all(sha(D/n)==h for n,h in owner['sourceHashes'].items())
clips=[{**c,'path':D/c['file'],'provenance':'author-same-exact-source-muted'} for c in owner['clips']]
extra=Q/'reset-window';er=json.loads((extra/'report.json').read_text());assert er['pass'] and er['sourceUnchanged']
assert all(sha(D/n)==h for n,h in er['sourceHashes'].items())
clips.append({'name':'success-to-exhausted-and-permanent-resets','start':2676,'end':3455,'path':extra/'success-to-exhausted-and-permanent-resets.mp4','sha256':er['videoSHA256'],'provenance':'independent-fresh-source-with-real-voice'})
b=json.loads((D/'storyboard.json').read_text());shots=[s for c in b['scenes'] for s in c['shots']];plan={p['id']:p for p in json.loads((D/'plan.json').read_text())};src=(D/'remotion/src/Main.tsx').read_text();block=re.search(r'const anchors:Record<string,\[number,number\]\[\]>=\{(.*?)\};',src,re.S)[1];anchors={n:ast.literal_eval(v) for n,v in re.findall(r"'(\d+)':(\[\[.*?\]\])",block)}
def model_at(f):
 for s in shots:
  if s['from']<=f<s['from']+s['durationInFrames']:
   gs=[0]+[s['voice'][i]['localStart']+(s['voice'][i]['localEnd']-s['voice'][i]['localStart'])*p for i,p in anchors.get(s['id'],[])];idx=max(i for i,g in enumerate(gs) if f-s['from']>=g);return plan[s['id']]['modelStages'][idx]
 raise AssertionError(f)
def balanced(xs):
 if len(xs)==1:return xs[0]
 k=len(xs)//2;return '('+balanced(xs[:k])+'+'+balanced(xs[k:])+')'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'kind':'independent-full-decode-and-integer-samples-of-source-clips','sourceHashes':identities,'clips':[],'pass':False,'visualReviewed':False,'scope':'Six muted author clips reused only after full source/output SHA checks, plus one fresh independent actual-voice window; no formal-final MP4 or semantic audio-listening claim.'}
reportpath=O/'report.json'
def save():reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
save()
try:
 for c in clips:
  assert sha(c['path'])==c['sha256'];dest=O/c['name'];dest.mkdir();n=c['end']-c['start']+1
  probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(c['path'])],capture_output=True,text=True,check=True)
  meta=json.loads(probe.stdout);(dest/'ffprobe.json').write_text(probe.stdout);v=[s for s in meta['streams'] if s['codec_type']=='video'][0];audio=[s for s in meta['streams'] if s['codec_type']=='audio'];assert int(v['nb_frames'])==n and v['r_frame_rate']=='30/1';assert v['width']==960 and v['height']==540
  assert bool(audio)==(c['provenance']=='independent-fresh-source-with-real-voice')
  ns=sorted(set(range(0,n,15))|{n-1});expr="select='"+balanced(['eq(n,'+str(i)+')' for i in ns])+"'"
  cmd=['ffmpeg','-v','error','-xerror','-i',str(c['path']),'-map','0:v:0','-vf',expr,'-fps_mode','vfr','-start_number','0',str(dest/'n%04d.png'),'-map','0:v:0','-map','0:a?','-f','null','-']
  run=subprocess.run(cmd,capture_output=True,text=True);(dest/'decode.stderr.txt').write_text(run.stderr);(dest/'command.json').write_text(json.dumps(cmd,indent=2)+'\n');assert run.returncode==0,run.stderr
  files=sorted(dest.glob('n*.png'));assert len(files)==len(ns)
  frames=[{'localN':local,'globalN':c['start']+local,'expectedModelState':model_at(c['start']+local),'file':str(p.relative_to(D)),'sha256':sha(p)} for local,p in zip(ns,files)]
  contacts=[]
  for j in range(0,len(frames),6):
   chunk=frames[j:j+6];contact=Image.new('RGB',(1280,392*math.ceil(len(chunk)/2)),(18,18,18));draw=ImageDraw.Draw(contact)
   for k,f in enumerate(chunk):
    x=(k%2)*640;y=(k//2)*392
    with Image.open(D/f['file']) as im:contact.paste(im.convert('RGB').resize((640,360)),(x,y+32))
    draw.text((x+7,y+7),'n='+str(f['localN'])+' global='+str(f['globalN'])+' '+f['expectedModelState'],font=font,fill=(255,236,211))
   out=dest/('contact-'+str(j//6+1).zfill(2)+'.jpg');contact.save(out,quality=92);contacts.append({'file':str(out.relative_to(D)),'sha256':sha(out),'frames':chunk})
  report['clips'].append({'name':c['name'],'path':str(c['path'].relative_to(D)),'sha256':c['sha256'],'provenance':c['provenance'],'globalRange':[c['start'],c['end']],'frames':n,'seconds':n/30,'videoCodec':v['codec_name'],'audioStreams':len(audio),'fullXerrorDecodeExit':run.returncode,'decodeStderr':run.stderr,'samples':frames,'contacts':contacts});save()
 report['sourceUnchanged']=all(sha(D/n)==h for n,h in identities.items());report['pass']=report['sourceUnchanged'] and len(report['clips'])==7;report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();save();print(json.dumps({'pass':report['pass'],'clips':len(report['clips']),'frames':sum(c['frames'] for c in report['clips']),'samples':sum(len(c['samples']) for c in report['clips'])}))
except Exception as e:
 report['failure']={'type':type(e).__name__,'message':str(e)};save();raise
