# EP.16 封面设计稿（Miyazaki）：照 EP.15 db-transaction/cover/make_cover.py（版式 / 配色 / 字体；16:9 主稿 1920×1080，4:3 = 16:9 居中裁 x240–1680，3:4 单独排 1080×1440）
# 定制设计，不取视频帧。标题以 script.md 为准：「没封箱的包裹」白 /「别人看得见吗？」橙；青底角标「事务隔离级别」；右上「IT小村」；不印系列名。
# 底部 15% 不放字（16:9/4:3 y>918、3:4 y>1224）；3:4 顶部 144px 内不放字。不出现英文 / 级别名。主图：小人举眼偷看没封箱的大纸箱（自绘 SVG）
import io
from PIL import Image,ImageDraw,ImageFont
import cairosvg
A='/workspace/miyazaki-backup/db-isolation/assets/';OUT='/workspace/miyazaki-backup/db-isolation/cover/'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FT=lambda s:ImageFont.truetype(FONT,int(s),index=2)
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",accent="#F59E0B",success="#22C55E",danger="#F87171",text="#FFFFFF",text2="#9CA3AF",muted="#6B7280")
TITLE=["没封箱的包裹","别人看得见吗？"];BADGE="事务隔离级别"
def svg(n,w,h):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=A+n+'.svg',output_width=1600))).convert('RGBA');im=im.crop(im.getbbox())
    k=min(w/im.width,h/im.height);return im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
def place(F,im,cx,cy): x,y=int(cx-im.width/2),int(cy-im.height/2);F.alpha_composite(im,(x,y));return (x,y,x+im.width,y+im.height)
def txt(d,xy,t,fs,col,anchor='mm'): d.text(xy,t,font=FT(fs),fill=col,anchor=anchor);return d.textbbox(xy,t,font=FT(fs),anchor=anchor)
def main(F,d,x,y,w,h,vertical=False):
    """主图：小人举着眼睛偷看一个没封箱的大纸箱（虚线 = 视线）。返回 (图形框, 文字框)"""
    G=[];lw=max(8,h//60)
    if not vertical:
        ph=h*0.80;p=svg('person',ph*0.75,ph);G.append(place(F,p,x+p.width/2,y+h-p.height/2))
        es=h*0.30;eb=place(F,svg('eye',es*1.6,es),x+p.width+es*1.05,y+h*0.30);G.append(eb)
        bs=min(h*1.0,w*0.42);bx=place(F,svg('box-open',bs,bs),x+w-bs/2,y+h-bs/2);G.append(bx)
    else:
        bs=min(w*0.70,h*0.78);bx=place(F,svg('box-open',bs,bs),x+w-bs/2,y+h*0.52);G.append(bx)
        ph=h*0.50;p=svg('person',ph*0.75,ph);pb=place(F,p,x+p.width/2,y+h-p.height/2);G.append(pb)
        es=h*0.17;eb=place(F,svg('eye',es*1.6,es),pb[0]+p.width*0.55,pb[1]-es*0.75);G.append(eb)
    # 视线：从眼睛到箱口的虚线
    x0,y0=eb[2]+10,(eb[1]+eb[3])/2;x1,y1=bx[0]+bs*0.25,bx[1]+bs*0.30;n=int(((x1-x0)**2+(y1-y0)**2)**0.5//36)
    for i in range(0,n,2): d.line([(x0+(x1-x0)*i/n,y0+(y1-y0)*i/n),(x0+(x1-x0)*(i+1)/n,y0+(y1-y0)*(i+1)/n)],fill=P['primary'],width=lw)
    return G,[]
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
Hd=head(d,280,90,120,150,'left',1170,300,96,56,1640,80)
G,TX=main(F,d,270,420,1380,460)
check('16x9',1920,1080,Hd,G,TX,crop=(240,1680))
F.convert('RGB').save(OUT+'ep16-16x9.png')
# 4:3（Nolan 2026-10-14）：16:9 居中裁 x240–1680 后整组缩到 90%，居中放回 1440×1080 底色画布 → 四边留白 ≥60
C=F.crop((240,0,1680,1080));k=0.9;C=C.resize((round(1440*k),round(1080*k)),Image.LANCZOS)
G4=Image.new('RGBA',(1440,1080),P['bg']);G4.alpha_composite(C,((1440-C.width)//2,(1080-C.height)//2));G4.convert('RGB').save(OUT+'ep16-4x3.png')
F=Image.new('RGBA',(1080,1440),P['bg']);d=ImageDraw.Draw(F)
Hd=head(d,540,214,110,140,'center','c',500,90,56,1000,150)
G,TX=main(F,d,60,620,960,680,vertical=True)
check('3x4',1080,1440,Hd,G,TX,top=144)
F.convert('RGB').save(OUT+'ep16-3x4.png')

# 四边留白实测（按像素：与底色差异 >24 的最外框），4:3 要求四边 ≥60
def margins(p):
    im=Image.open(p).convert('RGB');bg=Image.new('RGB',im.size,P['bg']);from PIL import ImageChops
    df=ImageChops.difference(im,bg).convert('L').point(lambda v:255 if v>24 else 0);x0,y0,x1,y1=df.getbbox()
    return dict(left=x0,top=y0,right=im.width-x1,bottom=im.height-y1)
for n,req in (('16x9',0),('4x3',60),('3x4',0)):
    m=margins(OUT+f'ep16-{n}.png');print(n,'margins',m,('OK' if min(m.values())>=req else 'FAIL(<%d)'%req) if req else '')
