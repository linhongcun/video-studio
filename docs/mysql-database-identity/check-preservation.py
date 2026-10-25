"""Check original narration/timeline, frozen inputs, copies and unrelated movies."""
from pathlib import Path
import argparse,hashlib,json,subprocess
P=argparse.ArgumentParser();P.add_argument('--encoded',action='store_true');P.add_argument('--upstream');P.add_argument('--report',required=True);A=P.parse_args()
R=Path(__file__).resolve().parents[2];I=json.loads((Path(__file__).parent/'index.json').read_text());BASE=I['baselineCommit'];sha=lambda b:hashlib.sha256(b).hexdigest()
def blob(path,ref=BASE):return subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=R)
rows=[]
for slug in I['selected']:
 d=R/'episodes-codex'/slug;rel=d.relative_to(R)
 for name in ['storyboard.json','script.md','words.json','voice.wav','covers.json','cover-16x9.jpg']:
  assert (d/name).read_bytes()==blob(rel/name),(slug,name)
 if (d/'remotion/src/branch-map.ts').exists():assert (d/'remotion/src/branch-map.ts').read_bytes()==blob(rel/'remotion/src/branch-map.ts'),slug
 m=json.loads((d/'source-sha256.json').read_text())
 for path,h in m.items():assert sha((d/path).read_bytes())==h,(slug,path)
 row={'slug':slug,'narrationSubtitlesTimelineAndPosterPreserved':True,'frozenInputs':len(m)}
 if A.encoded:
  v=(d/'video.mp4').read_bytes();old=next(x for x in I['originalMovies'] if x['slug']==slug);e=json.loads((d/'render-result.json').read_text())
  assert sha(v)!=old['sha256'] and sha(v)==e['sha256'] and v==(R/'episodes'/slug/'video.mp4').read_bytes(),slug
  probe=['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=start_time,duration,time_base,start_pts,duration_ts','-of','json']
  before=json.loads(subprocess.check_output(probe+['-i','pipe:0'],input=blob(f'episodes/{slug}/video.mp4')))['streams'][0]
  after=json.loads(subprocess.check_output(probe+[str(d/'video.mp4')]))['streams'][0]
  assert before==after,(slug,'audio container timing',before,after)
  row.update({'sha256':e['sha256'],'frames':e['frames'],'siteCopyMatched':True,'audioContainerTimingPreserved':True,'audioTiming':after})
 rows.append(row)
untouched=[]
for p in sorted((R/'episodes').glob('*/meta.json')):
 slug=p.parent.name
 if slug in I['selected'] or not (p.parent/'video.mp4').exists():continue
 expected=blob(f'episodes/{slug}/video.mp4',A.upstream or BASE)
 assert sha((p.parent/'video.mp4').read_bytes())==sha(expected),slug
 untouched.append(slug)
shared=R/'episodes-codex/_shared/branch-map/index.ts';assert shared.read_bytes()==blob(shared.relative_to(R))
result={'status':'passed','baselineCommit':BASE,'integratedUpstream':A.upstream,'encoded':A.encoded,'episodes':rows,'totalFrozenInputs':sum(x['frozenInputs'] for x in rows),'unrelatedMovieCopiesPreserved':untouched,'sharedCameraUnchanged':True}
Path(A.report).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Protected',len(rows),'episodes,',len(untouched),'other movies;',result['totalFrozenInputs'],'frozen inputs verified')
