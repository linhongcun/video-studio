# EP.19 封面（Miyazaki）：照 EP.18 db-replication/cover/make_cover.py（版式 / 配色 / 字体；16:9 1920×1080，4:3 = 16:9 裁 x240–1680 后整组缩 90% 居中，3:4 单独排 1080×1440）
# 大字「大促一到」白 /「下单怎么就卡住了？」橙；青底角标「分库分表」；右上「IT小村」。底部 15% 无字；3:4 顶部 144px 无字。主图：手机下单在转圈 + 红 / 蓝 / 绿三个驿站 + 彩色虚线（自绘，无数字 / 英文）
import io
from PIL import Image,ImageDraw,ImageFont
import cairosvg
A='/workspace/miyazaki-backup/global-id/assets/';OUT='/workspace/miyazaki-backup/global-id/cover/'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FT=lambda s:ImageFont.truetype(FONT,int(s),index=2)
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",accent="#F59E0B",success="#22C55E",danger="#F87171",text="#FFFFFF",text2="#9CA3AF",muted="#6B7280")
TITLE=["两个订单","怎么撞成同一个号了？"];BADGE="全局唯一 ID"
def svg(n,w,h):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=A+n+'.svg',output_width=1600))).convert('RGBA');im=im.crop(im.getbbox())
    k=min(w/im.width,h/im.height);return im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
def place(F,im,cx,cy): x,y=int(cx-im.width/2),int(cy-im.height/2);F.alpha_composite(im,(x,y));return (x,y,x+im.width,y+im.height)
def txt(d,xy,t,fs,col,anchor='mm'): d.text(xy,t,font=FT(fs),fill=col,anchor=anchor);return d.textbbox(xy,t,font=FT(fs),anchor=anchor)
def main(F,d,x,y,w,h,vertical=False):
    """主图：红站 + 蓝站各吐出一张一模一样的条码，中间火花（撞号）。无数字 / 英文。"""
    G=[]
    if not vertical:
        rs=place(F,svg('station-red',h*0.70,h*0.70),x+w*0.22,y+h*0.32)
        bs=place(F,svg('station-blue',h*0.70,h*0.70),x+w*0.78,y+h*0.32)
        br=place(F,svg('barcode-same',h*0.42,h*0.42),x+w*0.28,y+h*0.78)
        bb=place(F,svg('barcode-same',h*0.42,h*0.42),x+w*0.72,y+h*0.78)
        sp=place(F,svg('spark',h*0.45,h*0.45),x+w*0.50,y+h*0.62)
    else:
        rs=place(F,svg('station-red',w*0.36,w*0.36),x+w*0.22,y+h*0.18)
        bs=place(F,svg('station-blue',w*0.36,w*0.36),x+w*0.78,y+h*0.18)
        br=place(F,svg('barcode-same',w*0.28,w*0.28),x+w*0.25,y+h*0.48)
        bb=place(F,svg('barcode-same',w*0.28,w*0.28),x+w*0.75,y+h*0.48)
        sp=place(F,svg('spark',w*0.32,w*0.32),x+w*0.50,y+h*0.72)
    G=[rs,bs,br,bb,sp]
    return [(min(b[0] for b in G),min(b[1] for b in G),max(b[2] for b in G),max(b[3] for b in G))],[]
def head(d,tx,ty,tfs,tlh,align,bx,by,bh,bfs,wx,wy):
    R=[]
    for i,l in enumerate(TITLE):
        a='la' if align=='left' else 'ma';d.text((tx,ty+i*tlh),l,font=FT(tfs),fill=P['text'] if i==0 else P['accent'],anchor=a,stroke_width=4,stroke_fill=P['bg']);R.append(d.textbbox((tx,ty+i*tlh),l,font=FT(tfs),anchor=a))
    bw=int(d.textlength(BADGE,font=FT(bfs)))+bh
    if bx=='c': bx=int(tx-bw/2)
    d.rounded_rectangle([bx,by,bx+bw,by+bh],bh//2,fill=P['primary']);d.text((bx+bw/2,by+bh/2),BADGE,font=FT(bfs),fill=P['bg'],anchor='mm');R.append((bx,by,bx+bw,by+bh))
    R.append(txt(d,(wx,wy),"IT小村",40,"#E5E7EB",'ra'));return R
def overl(R): return [(a,b) for i,a in enumerate(R) for b in R[i+1:] if a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]]
def check(tag,W,H,Hd,G,TX,top=0,crop=None):
    T=Hd+TX;bot=int(H*0.85)
    err=overl(Hd+G+TX)+[('bottom15%',t) for t in T if t[3]>bot]+[('top',t) for t in T if t[1]<top]+[('edge',b) for b in Hd+G+TX if b[0]<0 or b[1]<0 or b[2]>W or b[3]>H]
    if crop: err+=[('4:3 crop',b) for b in Hd+G+TX if b[0]<crop[0] or b[2]>crop[1]]
    print(tag,'ERR' if err else 'OK',err,'subject',min(b[0] for b in G),min(b[1] for b in G),max(b[2] for b in G),max(b[3] for b in G))
F=Image.new('RGBA',(1920,1080),P['bg']);d=ImageDraw.Draw(F)
Hd=head(d,280,70,96,120,'left',280,340,80,44,1640,70)
G,TX=main(F,d,200,430,1520,520)
check('16x9',1920,1080,Hd,G,TX,crop=(240,1680))
F.convert('RGB').save(OUT+'ep20-16x9.png')
C=F.crop((240,0,1680,1080));k=0.9;C=C.resize((round(1440*k),round(1080*k)),Image.LANCZOS)
G4=Image.new('RGBA',(1440,1080),P['bg']);G4.alpha_composite(C,((1440-C.width)//2,(1080-C.height)//2));G4.convert('RGB').save(OUT+'ep20-4x3.png')
F=Image.new('RGBA',(1080,1440),P['bg']);d=ImageDraw.Draw(F)
Hd=head(d,540,180,90,110,'center','c',450,80,44,1000,140)
G,TX=main(F,d,60,620,960,680,vertical=True)
check('3x4',1080,1440,Hd,G,TX,top=144)
F.convert('RGB').save(OUT+'ep20-3x4.png')

def margins(p):
    im=Image.open(p).convert('RGB');bg=Image.new('RGB',im.size,P['bg']);from PIL import ImageChops
    df=ImageChops.difference(im,bg).convert('L').point(lambda v:255 if v>24 else 0);x0,y0,x1,y1=df.getbbox()
    return dict(left=x0,top=y0,right=im.width-x1,bottom=im.height-y1)
for n,req in (('16x9',0),('4x3',60),('3x4',0)):
    m=margins(OUT+f'ep20-{n}.png');print(n,'margins',m,('OK' if min(m.values())>=req else 'FAIL(<%d)'%req) if req else '')
