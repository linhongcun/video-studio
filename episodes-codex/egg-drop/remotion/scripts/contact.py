import json,os,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
D=Path(sys.argv[1]);data=json.loads((D/'samples.json').read_text());font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
groups=json.loads(os.environ.get('CONTACT_GROUPS','{}'))
if not groups:
 groups={'rules':['01','02'],'bad-choices':['03','04','05'],'budget':['06','07','08'],'actual-first':['09'],'actual-linear':['10'],'answer':['11','12']}
for name,ids in groups.items():
 samples=[]
 for id in ids:
  ss=[s for s in data['samples']if str(s['shot'])[:2]==id]
  if len(ss)>6:ss=[ss[round((len(ss)-1)*p)]for p in [0,.2,.4,.6,.8,1]]
  samples+=ss
 if not samples:continue
 w,h=480,298;image=Image.new('RGB',(w*3,h*((len(samples)+2)//3)),(15,23,42));draw=ImageDraw.Draw(image)
 for i,s in enumerate(samples):
  x=i%3*w;y=i//3*h;im=Image.open(s['file']).convert('RGB');im.thumbnail((480,270));image.paste(im,(x,y+26));draw.text((x+8,y+2),f"{s['shot']} / local {s['local']} / f{s['frame']}",font=font,fill=(229,231,235))
 image.save(D/(name+'-contact.jpg'),quality=94);print(D/(name+'-contact.jpg'))
