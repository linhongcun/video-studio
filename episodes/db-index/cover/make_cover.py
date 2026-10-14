# EP.14 封面设计稿（Miyazaki）：沿用 covers/make_covers.py 的版式 / 配色 / 字体（EP.12 做法：16:9 主稿，4:3 = 16:9 居中裁 x240–1680，3:4 单独排）
# 主图用本期自绘 SVG（book / toc / person）重新排：上一行「翻书」= 书 + 小人 + 页码计数；下一行「查目录」= 目录 → 书 ✓。无系列名（未定）
import io
from PIL import Image,ImageDraw,ImageFont
import cairosvg
A='/workspace/miyazaki-backup/db-index/assets/';OUT='/workspace/miyazaki-backup/db-index/cover/'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FT=lambda s:ImageFont.truetype(FONT,int(s),index=2)
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",accent="#F59E0B",success="#22C55E",text="#FFFFFF",text2="#9CA3AF",line="#374151")
TITLE=["加个索引","为啥就快了"];BADGE="索引"
def svg(n,w,h):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=A+n+'.svg',output_width=1600))).convert('RGBA');im=im.crop(im.getbbox())
    k=min(w/im.width,h/im.height);return im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
def pill(d,x,y,text,fs,col,fill=None):
    w=int(d.textlength(text,font=FT(fs)))+fs;h=int(fs*1.5)
    d.rounded_rectangle([x,y,x+w,y+h],h//2,fill=fill or P['panel'],outline=col,width=max(4,fs//12));d.text((x+w/2,y+h/2),text,font=FT(fs),fill=P['text'],anchor='mm');return (x,y,x+w,y+h)
def tick(d,x,y,s):
    d.line([(x,y+s*0.5),(x+s*0.38,y+s*0.88),(x+s,y)],fill=P['success'],width=max(8,int(s*0.14)),joint='curve')
def arrow(d,x0,x1,y,s):
    d.line([(x0,y),(x1-s,y)],fill=P['accent'],width=max(6,s//4));d.polygon([(x1-s*1.2,y-s*0.7),(x1,y),(x1-s*1.2,y+s*0.7)],fill=P['accent'])
def place(F,im,x,y): F.alpha_composite(im,(int(x),int(y)));return (int(x),int(y),int(x)+im.width,int(y)+im.height)
def rows(F,d,x,y,w,h,tagfs,cntfs,tagleft):
    """两行对比，返回所有占用框（查重叠）"""
    R=[];rh=(h-40)//2
    for r in range(2):
        ry=y+r*(rh+40);label=("翻书",P['text2']) if r==0 else ("查目录",P['primary'])
        tw=int(d.textlength("查目录",font=FT(tagfs)))+tagfs   # 两个标签同宽对齐
        if tagleft:
            th=int(tagfs*1.5);tb=pill(d,x,ry+(rh-th)//2,label[0],tagfs,label[1]);cx=x+tw+40;cy=ry;cw=w-tw-40;ch=rh
        else:
            tb=pill(d,x,ry,label[0],tagfs,label[1]);cx=x;cy=tb[3]+20;cw=w;ch=rh-(tb[3]-ry)-20
        R.append(tb)
        if r==0:   # 书 + 小人 + 计数
            bh=ch-(int(cntfs*1.4) if tagleft else 0);b=svg('book',cw*0.55,bh);R.append(place(F,b,cx,cy))
            p=svg('person',cw*0.36,bh*0.78);R.append(place(F,p,cx+b.width+cw*0.06,cy+bh-p.height))
            t="第 1、2、3……页"
            if tagleft: tbx=d.textbbox((cx,cy+bh+6),t,font=FT(cntfs));d.text((cx,cy+bh+6),t,font=FT(cntfs),fill=P['accent'])
            else: tbx=d.textbbox((tb[2]+30,tb[1]+(tb[3]-tb[1])/2),t,font=FT(cntfs),anchor='lm');d.text((tb[2]+30,tb[1]+(tb[3]-tb[1])/2),t,font=FT(cntfs),fill=P['accent'],anchor='lm')
            R.append(tbx)
        else:      # 目录 → 书 ✓
            tc=svg('toc',cw*0.36,ch);R.append(place(F,tc,cx,cy+(ch-tc.height)/2))
            bk=svg('book',cw*0.4,ch);bx=cx+cw-bk.width-ch*0.12;R.append(place(F,bk,bx,cy+(ch-bk.height)/2))
            arrow(d,cx+tc.width+cw*0.04,bx-cw*0.04,cy+ch/2,max(30,int(ch*0.1)))
            s=int(ch*0.3);tx_=bx+bk.width-s*1.05;ty_=cy+(ch+bk.height)/2-s*1.1;tick(d,tx_,ty_,s);R.append((int(tx_),int(ty_),int(tx_+s),int(ty_+s)))
    return R
def head(d,W,tx,ty,tfs,tlh,align,bx,by,bh,bfs,wx,wy):
    R=[]
    for i,l in enumerate(TITLE):
        a='la' if align=='left' else 'ma';d.text((tx,ty+i*tlh),l,font=FT(tfs),fill=P['text'] if i==0 else P['accent'],anchor=a,stroke_width=4,stroke_fill=P['bg']);R.append(d.textbbox((tx,ty+i*tlh),l,font=FT(tfs),anchor=a))
    bw=int(d.textlength(BADGE,font=FT(bfs)))+bh;d.rounded_rectangle([bx,by,bx+bw,by+bh],bh//2,fill=P['primary']);d.text((bx+bw/2,by+bh/2),BADGE,font=FT(bfs),fill=P['bg'],anchor='mm');R.append((bx,by,bx+bw,by+bh))
    d.text((wx,wy),"IT小村",font=FT(40),fill="#E5E7EB",anchor='ra');R.append(d.textbbox((wx,wy),"IT小村",font=FT(40),anchor='ra'));return R
def overl(R):
    return [(a,b) for i,a in enumerate(R) for b in R[i+1:] if a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]]
# 16:9（同 make_covers L["16x9"]：标题 x280 y120 fs130 lh165，徽标 x360 y480 h110 fs72，水印 x1640 y80；内容在 4:3 区 x240–1680 内，y≤900 无字）
F=Image.new('RGBA',(1920,1080),P['bg']);d=ImageDraw.Draw(F)
H=head(d,1920,280,120,130,165,'left',360,480,110,72,1640,80)
S=rows(F,d,990,170,650,710,56,44,False)
print('16x9 overlaps',overl(H+S),'subject box',min(r[0] for r in S),min(r[1] for r in S),max(r[2] for r in S),max(r[3] for r in S))
F.convert('RGB').save(OUT+'ep14-16x9.png');F.convert('RGB').crop((240,0,1680,1080)).save(OUT+'ep14-4x3.png')
# 3:4（标题居中 y190 fs140 lh170，徽标 x90 y560 h100 fs64，水印 x1000 y144；文字 y≤1224）
F=Image.new('RGBA',(1080,1440),P['bg']);d=ImageDraw.Draw(F)
H=head(d,1080,540,190,140,170,'center',90,560,100,64,1000,144)
S=rows(F,d,90,700,900,620,64,48,True)
print('3x4 overlaps',overl(H+S),'subject box',min(r[0] for r in S),min(r[1] for r in S),max(r[2] for r in S),max(r[3] for r in S))
F.convert('RGB').save(OUT+'ep14-3x4.png')
