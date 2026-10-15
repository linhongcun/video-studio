# EP.18 封面（Miyazaki）：照 EP.17 db-lock/cover/make_cover.py（版式 / 配色 / 字体；16:9 1920×1080，4:3 = 16:9 裁 x240–1680 后整组缩 90% 居中，3:4 单独排 1080×1440）
# 大字「刚改的昵称」白 /「又变回去了？」橙；青底角标「主从复制」；右上「IT小村」；不印系列名。底部 15% 无字；3:4 顶部 144px 无字。主图：手机昵称框里是「旧昵称」+ 旁边电视在转播赛场（慢半拍）+ 信号虚线（自绘 SVG，无数字 / 英文）
# 底部 15% 不放字（16:9/4:3 y>918、3:4 y>1224）；3:4 顶部 144px 内不放字。不出现英文 / 级别名。主图：小人举眼偷看没封箱的大纸箱（自绘 SVG）
import io
from PIL import Image,ImageDraw,ImageFont
import cairosvg
A='/workspace/miyazaki-backup/db-replication/assets/';OUT='/workspace/miyazaki-backup/db-replication/cover/'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FT=lambda s:ImageFont.truetype(FONT,int(s),index=2)
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",accent="#F59E0B",success="#22C55E",danger="#F87171",text="#FFFFFF",text2="#9CA3AF",muted="#6B7280")
TITLE=["刚改的昵称","又变回去了？"];BADGE="主从复制"
def svg(n,w,h):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=A+n+'.svg',output_width=1600))).convert('RGBA');im=im.crop(im.getbbox())
    k=min(w/im.width,h/im.height);return im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
def place(F,im,cx,cy): x,y=int(cx-im.width/2),int(cy-im.height/2);F.alpha_composite(im,(x,y));return (x,y,x+im.width,y+im.height)
def txt(d,xy,t,fs,col,anchor='mm'): d.text(xy,t,font=FT(fs),fill=col,anchor=anchor);return d.textbbox(xy,t,font=FT(fs),anchor=anchor)
def boxwith(F,bs,cx,cy):
    """打开的大纸箱 + 露出的物件（书 / 杯子 / T 恤；物件先画、箱身后画挡住下半截，同视频 boxitems）。返回整组外框"""
    im=svg('box-open',bs,bs);x0,y0=int(cx-im.width/2),int(cy-im.height/2);W=im.width/0.84;R_=[]
    for n,f,o in zip(("book","tshirt","mug"),(0.02,0.46,0.25),(0.12,0.14,0.24)):   # Nolan：物件放大约 2 倍，堆在箱口
        it=svg(n,W*0.50,W*0.50);R_.append(place(F,it,x0-0.08*W+f*W+W*0.28,y0-0.17*W-o*W+W*0.28+0.12*W))
    R_.append(place(F,im,cx,cy))
    return (min(r[0] for r in R_),min(r[1] for r in R_),max(r[2] for r in R_),max(r[3] for r in R_))
def stack(names,w,h):
    im=None
    for n in names:
        a=Image.open(io.BytesIO(cairosvg.svg2png(url=A+n+'.svg',output_width=1024,output_height=512 if n.startswith('stadium') else 1024))).convert('RGBA')
        if im is None: im=Image.new('RGBA',(1024,512),(0,0,0,0))
        if n.startswith('stadium'): im.alpha_composite(a)
        else:   # 球员 / 球：同 gen.py 的赛场坐标（512 画框 → 赛场 1024×512）
            ps=260/512;a=a.resize((round(a.width*ps/2),round(a.height*ps/2)),Image.LANCZOS) if False else a.resize((260,260),Image.LANCZOS)
            im.alpha_composite(a,(330,161))
    b=Image.open(io.BytesIO(cairosvg.svg2png(url=A+'ball.svg',output_width=35,output_height=35))).convert('RGBA');im.alpha_composite(b,(496,374))
    k=min(w/im.width,h/im.height);return im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
def tvwith(F,W,cx,cy):
    tvi=Image.open(io.BytesIO(cairosvg.svg2png(url=A+'tv-frame.svg',output_width=round(W),output_height=round(W)))).convert('RGBA');k=W/512
    x0,y0=int(cx-W/2),int(cy-W/2);F.alpha_composite(tvi,(x0,y0))
    st=stack(["stadium-field","stadium-poles","stadium-lights-on","player-body","player-leg-stand","player-leg-ready"],384*k,192*k);F.alpha_composite(st,(int(x0+64*k),int(y0+139*k)))
    bb=tvi.getbbox();return (x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3])
def phonewith(F,d,W,cx,cy):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=A+'phone.svg',output_width=round(W),output_height=round(W)))).convert('RGBA');k=W/512
    x0,y0=int(cx-W/2),int(cy-W/2);F.alpha_composite(im,(x0,y0))
    d.text((x0+(232+49)*k,y0+(236+25)*k),"旧昵称",font=FT(30*k),fill="#E5E7EB",anchor='mm')
    bb=im.getbbox();return (x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3])
def main(F,d,x,y,w,h,vertical=False):
    """主图：大手机（昵称框里是「旧昵称」）+ 旁边电视在转播赛场 + 赛场 → 电视 → 手机的信号虚线。整组一个外框"""
    G=[]
    if not vertical:
        pw=h*1.25;pb=phonewith(F,d,pw,x+w*0.30,y+h*0.50);tw=h*1.05;tb=tvwith(F,tw,x+w*0.74,y+h*0.50)
    else:
        tw=w*0.55;tb=tvwith(F,tw,x+w*0.66,y+h*0.22);pw=w*0.62;pb=phonewith(F,d,pw,x+w*0.28,y+h*0.70)
    G=[pb,tb];lw=max(8,int(h//60))
    x0,y0=tb[0]+10,(tb[1]+tb[3])/2;x1,y1=pb[2]-10,(pb[1]+pb[3])/2
    n=int(((x1-x0)**2+(y1-y0)**2)**0.5//36)
    for i in range(0,n,2): d.line([(x0+(x1-x0)*i/n,y0+(y1-y0)*i/n),(x0+(x1-x0)*(i+1)/n,y0+(y1-y0)*(i+1)/n)],fill=P['primary'],width=lw)
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
Hd=head(d,280,90,120,150,'left',1170,300,96,56,1640,80)
G,TX=main(F,d,270,470,1380,460)
check('16x9',1920,1080,Hd,G,TX,crop=(240,1680))
F.convert('RGB').save(OUT+'ep18-16x9.png')
# 4:3（Nolan 2026-10-14）：16:9 居中裁 x240–1680 后整组缩到 90%，居中放回 1440×1080 底色画布 → 四边留白 ≥60
C=F.crop((240,0,1680,1080));k=0.9;C=C.resize((round(1440*k),round(1080*k)),Image.LANCZOS)
G4=Image.new('RGBA',(1440,1080),P['bg']);G4.alpha_composite(C,((1440-C.width)//2,(1080-C.height)//2));G4.convert('RGB').save(OUT+'ep18-4x3.png')
F=Image.new('RGBA',(1080,1440),P['bg']);d=ImageDraw.Draw(F)
Hd=head(d,540,214,110,140,'center','c',500,90,56,1000,150)
G,TX=main(F,d,60,620,960,680,vertical=True)
check('3x4',1080,1440,Hd,G,TX,top=144)
F.convert('RGB').save(OUT+'ep18-3x4.png')

# 四边留白实测（按像素：与底色差异 >24 的最外框），4:3 要求四边 ≥60
def margins(p):
    im=Image.open(p).convert('RGB');bg=Image.new('RGB',im.size,P['bg']);from PIL import ImageChops
    df=ImageChops.difference(im,bg).convert('L').point(lambda v:255 if v>24 else 0);x0,y0,x1,y1=df.getbbox()
    return dict(left=x0,top=y0,right=im.width-x1,bottom=im.height-y1)
for n,req in (('16x9',0),('4x3',60),('3x4',0)):
    m=margins(OUT+f'ep18-{n}.png');print(n,'margins',m,('OK' if min(m.values())>=req else 'FAIL(<%d)'%req) if req else '')
