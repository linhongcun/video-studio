from pathlib import Path
import subprocess,json,datetime
root=Path.cwd();w=root/'work/leetcode-video-style';slug='daily-temperatures';marker=w/'render-complete'/f'{slug}.json';rev=root/f'episodes-codex/{slug}/revisions/leetcode-style'
assert not marker.exists() and not (rev/'video.mp4').exists()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();print('Additional frozen independent episode worker started:',slug,start,flush=True)
with (w/f'{slug}-render.log').open('w') as log:r=subprocess.run(['python3','episodes-codex/_shared/leetcode-video/render.py',slug,'--render'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
row={'slug':slug,'exitCode':r.returncode,'startedAtUTC':start,'finishedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'extraWorker':True}
if r.returncode:
 (w/'render-failed.json').write_text(json.dumps(row)+'\n');raise SystemExit(r.returncode)
d=json.loads((rev/'render-result.json').read_text());assert d['visualRevision']=='leetcode-style-v1';row.update(status='render-complete',sha256=d['sha256'],frames=d['frames']);temp=marker.with_suffix('.tmp');temp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');temp.replace(marker);print(json.dumps(row),flush=True)
