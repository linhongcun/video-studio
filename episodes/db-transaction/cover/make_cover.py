# EP.15 封面设计稿（Miyazaki）：照 EP.14 db-index/cover/make_cover.py（版式 / 配色 / 字体；16:9 主稿 1920×1080，4:3 = 16:9 居中裁 x240–1680，3:4 单独排 1080×1440）
# 定制设计，不取视频帧。标题以 script.md 为准：《扣了钱，对方没到账？》→「扣了钱，」白 /「对方没到账？」橙；青底角标「数据库事务」；右上「IT小村」；不印系列名。
# Nolan 规格：三种尺寸底部 15% 不放字（16:9/4:3 y>918、3:4 y>1224）；3:4 顶部 144px 内不放字（含水印）。不出现 COMMIT/ROLLBACK/ACID。
# 主图（本期自绘 SVG）：你的余额框 500→400（标「示例」）—硬币沿虚线飞出—闪电截断—朋友 200 框变红 +「？」
import io
from PIL import Image,ImageDraw,ImageFont
import cairosvg
A='/workspace/miyazaki-backup/db-transaction/assets/';OUT='/workspace/miyazaki-backup/db-transaction/cover/'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FT=lambda s:ImageFont.truetype(FONT,int(s),index=2)
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",accent="#F59E0B",success="#22C55E",danger="#F87171",text="#FFFFFF",text2="#9CA3AF",muted="#6B7280")
TITLE=["扣了钱，","对方没到账？"];BADGE="数据库事务"
def svg(n,w,h):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=A+n+'.svg',output_width=1600))).convert('RGBA');im=im.crop(im.getbbox())
    k=min(w/im.width,h/im.height);return im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
def place(F,im,cx,cy): x,y=int(cx-im.width/2),int(cy-im.height/2);F.alpha_composite(im,(x,y));return (x,y,x+im.width,y+im.height)
def txt(d,xy,t,fs,col,anchor='mm'): d.text(xy,t,font=FT(fs),fill=col,anchor=anchor);return d.textbbox(xy,t,font=FT(fs),anchor=anchor)
def main(F,d,x,y,w,h):
    """主图，返回 (组框列表, 文字框列表)；组内的字（框里的数字）算组的一部分"""
    G=[];TX=[];bw=int(w*0.29);bh=int(min(h*0.62,bw*1.2));by=y;r=int(bh*0.12);lw=max(6,h//70)
    # 你的余额框：500 划掉 → 400
    nf=min(bh*0.45,bw/1.85);L=(x,by,x+bw,by+bh);d.rounded_rectangle(L,r,fill=P['panel'],outline=P['secondary'],width=lw)
    o=txt(d,(x+bw/2,by+bh*0.26),"500",nf*0.45,P['muted']);d.line([(o[0]-6,(o[1]+o[3])/2),(o[2]+6,(o[1]+o[3])/2)],fill=P['danger'],width=max(4,lw))
    txt(d,(x+bw/2,by+bh*0.64),"400",nf,P['text']);G.append(L)
    # 朋友的余额框：200，红框
    R_=(x+w-bw,by,x+w,by+bh);d.rounded_rectangle(R_,r,fill=P['panel'],outline=P['danger'],width=lw);txt(d,(x+w-bw/2,by+bh*0.55),"200",nf,P['text']);G.append(R_)
    # 框下：名字 + 示例
    fs=min(h*0.085,60);TX.append(txt(d,(x+bw/2,by+bh+fs*0.9),"你",fs,P['text2']));TX.append(txt(d,(x+w-bw/2,by+bh+fs*0.9),"朋友",fs,P['text2']))
    TX.append(txt(d,(x+w/2,by+bh+fs*0.9),"（余额为示例）",min(h*0.065,44),P['text2']))
    # 中间：虚线（只画到闪电）、硬币、闪电、问号
    m0,m1=x+bw,x+w-bw;mw=m1-m0;py=by+bh*0.58;bx=m0+mw*0.62
    X=m0+mw*0.06
    while X<bx-mw*0.08: d.line([(X,py),(min(X+mw*0.05,bx-mw*0.08),py)],fill=P['accent'],width=lw);X+=mw*0.085
    cs=min(h*0.22,mw*0.30);G.append(place(F,svg('coin',cs,cs),m0+mw*0.30,py))
    fb=place(F,svg('fault',min(h*0.30,mw*0.30),min(h*0.44,mw*0.44)),bx-mw*0.04,py);G.append(fb)
    qs=min(h*0.26,(m1-fb[2])*1.1);TX.append(txt(d,((fb[2]+m1)/2,fb[1]+qs*0.1),"？",qs,P['accent']))
    return G,TX
def main_v(F,d,x,y,w,h):
    """3:4 主图：上排两个余额框（框内写名字），下排硬币沿虚线飞向右框、被闪电截断 +「？」"""
    G=[];TX=[];gap=60;bw=(w-gap)//2;bh=int(h*0.50);r=36;lw=8;nf=min(bh*0.42,bw/1.85)
    L=(x,y,x+bw,y+bh);d.rounded_rectangle(L,r,fill=P['panel'],outline=P['secondary'],width=lw)
    txt(d,(x+30,y+24),"你",52,P['text2'],'la');o=txt(d,(x+bw-30,y+24),"500",nf*0.42,P['muted'],'ra')
    d.line([(o[0]-6,(o[1]+o[3])/2),(o[2]+6,(o[1]+o[3])/2)],fill=P['danger'],width=8);txt(d,(x+bw/2,y+bh*0.64),"400",nf,P['text']);G.append(L)
    rx=x+bw+gap;R_=(rx,y,rx+bw,y+bh);d.rounded_rectangle(R_,r,fill=P['panel'],outline=P['danger'],width=lw)
    txt(d,(rx+30,y+24),"朋友",52,P['text2'],'la');txt(d,(rx+bw/2,y+bh*0.64),"200",nf,P['text']);G.append(R_)
    # 下排：从左框底部引出的虚线 → 硬币 → 闪电（截断）→「？」（在右框正下方）
    py=y+bh+(h-bh)*0.42;x0=x+bw*0.5;d.line([(x0,y+bh),(x0,py)],fill=P['accent'],width=lw)
    bxc=x+w*0.56;X=x0
    while X<bxc-80: d.line([(X,py),(min(X+40,bxc-80),py)],fill=P['accent'],width=lw);X+=70
    cs=(h-bh)*0.42;G.append(place(F,svg('coin',cs,cs),x+w*0.30,py))
    fb=place(F,svg('fault',(h-bh)*0.5,(h-bh)*0.66),bxc,py);G.append(fb)
    TX.append(txt(d,(rx+bw/2,py),"？",(h-bh)*0.55,P['accent']))
    TX.append(txt(d,(x+w/2,y+h-40),"（余额为示例）",44,P['text2']))
    return G,TX
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
# 16:9：标题左上 fs130，角标右上区；主图下半横跨 4:3 安全区 x270–1650，字 ≤918
F=Image.new('RGBA',(1920,1080),P['bg']);d=ImageDraw.Draw(F)
Hd=head(d,280,90,130,160,'left',1180,140,100,60,1640,80)
G,TX=main(F,d,270,450,1380,580)
check('16x9',1920,1080,Hd,G,TX,crop=(240,1680))
F.convert('RGB').save(OUT+'ep15-16x9.png');F.convert('RGB').crop((240,0,1680,1080)).save(OUT+'ep15-4x3.png')
# 3:4：水印 y160（顶部 144 内无字），标题居中 fs130，角标居中；主图 x60–1020，字 ≤1224
F=Image.new('RGBA',(1080,1440),P['bg']);d=ImageDraw.Draw(F)
Hd=head(d,540,170,120,148,'center','c',476,90,56,1000,160)
G,TX=main_v(F,d,60,606,960,616)
check('3x4',1080,1440,Hd,G,TX,top=144)
F.convert('RGB').save(OUT+'ep15-3x4.png')
