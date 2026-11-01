"""Build labeled contact sheets from an existing QA manifest; does not render."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

directory=Path(sys.argv[1])
data=json.loads((directory/'samples.json').read_text())
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
groups={'overview':[f'{n:02d}' for n in range(1,30)]}
for name,ids in groups.items():
 chosen=[]
 for shot in ids:
  samples=[s for s in data['samples'] if str(s['shot']).startswith(shot)]
  if len(samples)>6:
   samples=[samples[round((len(samples)-1)*p)] for p in [0,.2,.4,.6,.8,1]]
  chosen+=samples
 width,height,columns=480,298,3
 canvas=Image.new('RGB',(width*columns,height*((len(chosen)+columns-1)//columns)),(15,23,42));draw=ImageDraw.Draw(canvas)
 for i,sample in enumerate(chosen):
  x=i%columns*width;y=i//columns*height
  image=Image.open(sample['file']).convert('RGB');image.thumbnail((480,270));canvas.paste(image,(x,y+26))
  draw.text((x+8,y+2),f"{sample['shot']} / local {sample['local']} / global {sample['frame']}",font=font,fill=(229,231,235))
 canvas.save(directory/(name+'-contact.jpg'),quality=94)
 print(directory/(name+'-contact.jpg'))
