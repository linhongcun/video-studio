from pathlib import Path
import subprocess,json,collections,hashlib
from PIL import Image
R=Path('/workspace/video-studio');D=R/'episodes-codex/kafka-message-backlog';Q=D/'qa-final-independent';rows=[]
def rgb(p,n,extra=None):
 vf=f'select=eq(n\\,{n}),'+(extra+',' if extra else '')+'format=rgb24'
 a=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf',vf,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']);return Image.frombytes('RGB',(1920,1080),a)
def yuv(p):
 pinfo=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=color_space,color_range,color_transfer,color_primaries,pix_fmt','-of','json',str(p)]))['streams'][0]
 fmt='yuvj420p' if pinfo['color_range']=='pc' else 'yuv420p';a=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-frames:v','1','-f','rawvideo','-pix_fmt',fmt,'-']);x=y=10;l=1920*1080;index=(y//2)*960+x//2
 return pinfo,[a[y*1920+x],a[l+index],a[l+l//4+index]]
for slug in ['kafka-message-backlog','kafka-message-ordering']:
 d=R/'episodes-codex'/slug
 for rel in ['remotion/out/voice.mp4','remotion/out/voice-bt709.mp4','remotion/out/body.mp4','video.mp4']:
  p=d/rel
  if p.exists():
   im=rgb(p,0);info,vals=yuv(p);rows.append({'episode':slug,'file':rel,'stream':info,'backgroundYUV':vals,'backgroundRGB':im.getpixel((10,10)),'panelRGB':im.getpixel((500,500))})
raw=D/'remotion/out/voice.mp4'
# Probe the conversion itself without any new lossy encode; terminal RGB conversion is explicit 709.
filters='scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,scale=in_range=tv:out_range=pc:in_color_matrix=bt709,format=rgb24'
im=rgb(raw,0,filters);losslessProbe={'backgroundRGB':im.getpixel((10,10)),'panelRGB':im.getpixel((500,500)),'operation':'Same normalize pixel conversion directly decoded to RGB without x264 re-encode','filter':filters}
patches=[]
for n,xy,label in [(1905,(497,440),'blue-circle-fill'),(2034,(555,435),'orange-circle-fill'),(2250,(10,10),'background')]:
 src=Image.open(D/'qa-independent/cross-v1'/f'frame-{n:05}.png').convert('RGB');row={'frame':n,'point':xy,'label':label,'sourcePNG':src.getpixel(xy),'stages':{}}
 for rel in ['remotion/out/voice.mp4','remotion/out/voice-bt709.mp4','video.mp4']:
  im=rgb(D/rel,n);c=im.getpixel(xy);bright=[c for c in im.crop((100,140,1750,200)).getdata() if c[0]>220 and c[1]>200 and c[2]>180];row['stages'][rel]={'pointRGB':c,'modalBrightTitleTextRGB':collections.Counter(bright).most_common(1)}
 patches.append(row)
out={'purpose':'Read-only stage attribution; no production input/output changed. Full and limited pixel conversions inspected, not inferred only from tags.','sourceTargetBG':[33,29,27],'chain':rows,'withoutLossyEncodeProbe':losslessProbe,'colorPatches':patches};(Q/'color-chain-probe.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
