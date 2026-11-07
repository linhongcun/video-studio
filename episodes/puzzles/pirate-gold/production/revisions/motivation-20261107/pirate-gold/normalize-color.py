#!/usr/bin/env python3
"""Convert new Remotion full-range BT.601 pixels once to limited BT.709."""
from pathlib import Path
import subprocess,json,hashlib,argparse
D=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(__doc__)
parser.add_argument('--input',type=Path,default=D/'remotion/out/voice.mp4')
parser.add_argument('--output',type=Path,default=D/'remotion/out/voice-bt709.mp4')
parser.add_argument('--report',type=Path,default=D/'remotion/out/color-encoding-check.json')
args=parser.parse_args()
source=args.input;output=args.output
def probe(p):
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(p)]))
 return data['streams'][0]
def first(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-read_intervals','%+#1','-show_frames','-show_entries','frame=pix_fmt,color_range,color_space,color_transfer,color_primaries','-of','json',str(p)]))['frames'][0]
raw=probe(source)
assert raw['color_range']=='pc' and raw['color_space'] in ['smpte170m','bt470bg'],raw
command=['ffmpeg','-v','error','-y','-i',str(source),'-map','0:v:0','-map','0:a:0','-vf','scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-fps_mode','passthrough','-video_track_timescale','90000','-c:a','copy','-map_metadata','-1','-movflags','+faststart',str(output)]
subprocess.run(command,check=True)
expected={'pix_fmt':'yuv420p','color_range':'tv','color_space':'bt709','color_transfer':'bt709','color_primaries':'bt709'}
actual=probe(output);decoded=first(output)
assert all(actual.get(k)==v and decoded.get(k)==v for k,v in expected.items())
assert raw['nb_frames']==actual['nb_frames']
report={'passed':True,'operation':'pixel conversion full-range BT.601 to limited BT.709, not relabeling','command':command,'input':{k:raw.get(k) for k in expected},'output':{k:actual.get(k) for k in expected},'decodedFirstFrameColor':decoded,'frames':int(actual['nb_frames']),'outputSHA256':hashlib.sha256(output.read_bytes()).hexdigest()}
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
