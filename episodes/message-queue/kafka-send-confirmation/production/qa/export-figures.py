"""Export preplanned integer frames from final limited-BT709 media; outputs only."""
from pathlib import Path
import hashlib,json,subprocess,datetime
D=Path(__file__).resolve().parents[1]
video=D/'video.mp4'
plan=json.loads((D/'article-figure-plan.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=color_range,color_space,color_transfer,color_primaries,nb_frames','-of','json',str(video)],text=True))['streams'][0]
assert [probe[k] for k in ['color_range','color_space','color_transfer','color_primaries']]==['tv','bt709','bt709','bt709'],probe
out=D/'article';out.mkdir(exist_ok=True)
rows=[]
for row in plan['figures']:
 n=row['frame'];assert 0<=n<int(probe['nb_frames'])
 name=Path(row['path']).name;target=out/name
 vf='select=eq(n\\,'+str(n)+'),scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',vf,'-frames:v','1','-q:v','2',str(target)],check=True)
 assert target.is_file() and target.stat().st_size>10000
 rows.append({'frame':n,'seconds':n/30,'file':'article/'+name,'sha256':sha(target),'bytes':target.stat().st_size,'visualReviewed':False})
r={'checkedAtBeijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'videoSha256':sha(video),'articleSha256':sha(D/'article.mdx'),'planSha256':sha(D/'article-figure-plan.json'),'method':'Integer-frame select of final MP4 with actual limited BT709 to full BT601 JPEG pixel conversion; no label-only conversion.','status':'extracted-awaiting-actual-visual-review','figures':rows}
(D/'qa/article-figures.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':r['status'],'frames':[x['frame']for x in rows]},ensure_ascii=False))
