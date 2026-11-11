#!/usr/bin/env python3
"""Export frozen Figure frames from actual limited-BT.709 final media."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent
R=next(p for p in D.parents if (p/'AGENTS.md').is_file())
source=D/'video.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(source)]))['streams'][0]
assert probe['color_range']=='tv' and probe['color_space']=='bt709'
article=(D/'article.mdx').read_text()
figures=re.findall(r'<Figure\s+src="/video-studio/episodes/prisoners-light/article/([^"/]+)"[^>]*seekTo=\{([0-9.]+)\}',article)
assert len(figures)==2
out=D/'article';out.mkdir(parents=True,exist_ok=True)
(D/'qa').mkdir(parents=True,exist_ok=True)
rows=[]
for filename,seconds in figures:
 frame=Fraction(seconds)*30
 assert frame.denominator==1 and 0<=frame<int(probe['nb_frames'])
 target=out/filename
 filt=f'select=eq(n\\,{int(frame)}),scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vf',filt,'-frames:v','1','-q:v','2',str(target)],check=True)
 assert target.is_file() and target.stat().st_size>1000
 previous=R/'episodes/puzzles/prisoners-light/publication/article'/filename
 rows.append({'previousPublicationSHA256':hashlib.sha256(previous.read_bytes()).hexdigest() if previous.is_file() else None,'filename':filename,'timeSeconds':seconds,'frame':int(frame),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size})
report={'passed':True,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'articleSHA256':hashlib.sha256((D/'article.mdx').read_bytes()).hexdigest(),'frameSelection':'Decode from frame zero and select exact integer n; no approximate seek.','colorOperation':'Actual limited BT.709 to full-range BT.601 JPEG pixel conversion, not relabeling.','figures':rows,'visualReviewSeparate':True}
(D/'qa/article-image-export.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
