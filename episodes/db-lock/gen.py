# EP.17《两个人抢同一件货，听谁的？》数据库锁（脚本 v0.22.0 待定稿）分镜草稿（Miyazaki，provisional）。工具链沿用 EP.16 db-isolation/gen.py
# 物件即语义：两只手=两个人；T 恤=一条数据；吊牌=版本；锁=写锁；玻璃罩=读锁；货架=一张表。
# 画面不加数字标签、不出现英文；术语标签只用中文（丢失更新 / 写锁 / 读锁 / 行锁 / 表锁 / 死锁 / 悲观锁 / 乐观锁）；只有右上「IT小村」水印
import json,re,math,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','_audit'));import asrcue
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext,narration
narr=narration(); assert len(narr)==10
def cnt(s): return len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",success="#22C55E",accent="#F59E0B",danger="#F87171")
def R(i,x,y,w,h,c=P['panel'],**k): return dict(id=i,type="rect",x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def T(i,x,y,w,h,t,fs=40,c=P['text'],**k): return dict(id=i,type="text",x=x,y=y,w=w,h=h,text=t,fontSize=fs,**{"color":c,"reuse":False,**k})
def E(i,ty,x,y,w,h,c,**k): return dict(id=i,type=ty,x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def I(i,name,x,y,w,h=None,**k): return dict(id=i,type="image",asset=f"assets/{name}.svg",x=x,y=y,w=w,h=w if h is None else h,**{"color":None,"reuse":False,**k})
def fade(i,a=0,b=12): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=0),dict(frame=b,value=1)],easing="easeOut")
def mv(i,p,a,b,va,vb,e="easeInOut"): return dict(elementId=i,property=p,keyframes=[dict(frame=a,value=va),dict(frame=b,value=vb)],easing=e)
def draw(i,a,n=15): return mv(i,"drawProgress",a,a+n,0,1,"easeOut")
def F(i,a,n=12): return fade(i,a,a+n)
def out(i,a,n=10): return mv(i,"opacity",a,a+n,1,0)
def pop(i,a): return mv(i,"scale",a,a+12,0,1,"spring")
def hl(i,a,c=P['success'],c0=P['secondary']): return mv(i,"strokeColor",a,a+10,c0,c)
titles=["抢同一件","后来的盖掉先来的","挂一把锁","围着看","锁一件还是锁一架","互相等","整单重来","先挂锁再动手","放回去时看一眼","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
TM=json.load(open(HERE/"timing.json"))
ASR=json.load(open(HERE/"asr_words.json")) if (HERE/"asr_words.json").exists() else {}
PARTS=[]
def AT(si,_k,phrase):   # 非术语画面动作的时刻：按字数插值（术语标签另由 labelfix 按词级 ASR 对齐）
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def term(i,x,y,w,label,c=None,fs=64): return R(i,x,y,w,110,stroke=c or P['primary'],radius=55,label=label,fontSize=fs)
def ex(i,x,y,w=300): return T(i,x,y,w,46,"（示例）",32,P['text2'],align="center")   # Nolan：32px
def itag(i,x,y,text,c=None,w=None):   # 物件上的小标签（价钱等，32px）
    return R(i,x,y,max(w or 0,60+28*len(text.replace(' ',''))),80,stroke=c or P['accent'],radius=40,label=text,fontSize=40)   # Nolan：数字标签成片 40px；框高 80（= 2×字号）留足余量，避免渲染器按框高压字号
def rowtag(i,x,y,num):   # 一行数据的青色行号角标（28px）
    return R(i,x,y,max(72,40+32*len(num.replace(" ",""))),60,"#083344",stroke=P['primary'],radius=14,label=num,fontSize=32)   # Nolan：角标 ≥32px，框高 60
def boxitems(p,bx,by,bw,names=("book","mug","tshirt")):   # 打开的大纸箱（事务）里露出的物件：放在纸箱元素之前，箱身挡住下半截
    s=round(bw*0.62);return [I(f"{p}{n}",n,round(bx+bw*f),round(by-bw*o),s) for n,f,o in zip(names,(-0.02,0.20,0.40),(0.16,0.10,0.18))]   # Nolan：物件放大约 2 倍，堆在箱口
def item(p,name,x,y,s,num=None):   # 一行数据 = 一件具体物件 + 青色行号角标
    return [I(p,name,x,y,s)]+([rowtag(p+"n",x+s-max(72,40+32*len(num.replace(" ","")))+10,y-22,num)] if num else [])
def stairs(p,x,y0,w,gap,hs,hi=None):   # 几档规矩：不写级别名，只画由低到高的台阶
    return [R(f"{p}{j}",x+j*(w+gap),y0-h,w,h,stroke=(P['accent'] if j==hi else P['primary']),radius=12) for j,h in enumerate(hs)]
TOUT=36;SUB0=45   # hook-1（Nolan 2026-10-14）：封面大字完整显示 0–36 帧，36–45 淡出；第一条字幕从 45 帧进（0–44 空白字幕）
# EP.17 数据库锁：各章镜头设计（draft，provisional）。物件即语义：两只手=两个人（蓝袖浅肤 / 橙袖深肤）；T 恤=一条数据；吊牌=这条数据当前的版本；
# 锁（关/开）=写锁；玻璃罩=读锁（大家能看、手伸不进去）；货架=一张表。画面不加数字标签；写锁时旁人的眼睛照样能看（普通查询不加锁）。
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    def hand(i,side,x,y,w=440): return I(i,"hand-a" if side=="a" else "hand-b",x,y,w)
    def sight(i,x,y,w,h): return E(i,"line",x,y,w,h,P['primary'],dashed=True)
    if si==0:  # 开场即封面：第 0 帧满屏——两只手从两侧伸向同一件 T 恤 + 两行大字；0–36 大字完整，36–45 淡出，字幕 45 帧进
        e=[T("t1",160,90,900,150,"两人抢一件货",120,P['text']),T("t2",160,240,900,150,"听谁的？",120,P['accent']),
           I("shirt","tshirt",760,400,400),hand("ha","a",340,370,460),hand("hb","b",1120,370,460)]
        tg=at(0,"同时伸手");td=at(0,"同时要改同一条数据")
        a=[out("t1",TOUT,SUB0-TOUT),out("t2",TOUT,SUB0-TOUT),mv("ha","x",tg,tg+8,340,370),mv("hb","x",tg,tg+8,1120,1090),
           mv("ha","x",tg+8,tg+16,370,350),mv("hb","x",tg+8,tg+16,1090,1110),mv("shirt","scale",td,td+8,1,1.06),mv("shirt","scale",td+8,td+16,1.06,1)]
        return [(e,a)]
    if si==1:  # 丢失更新（Nolan）：只有两张不同颜色的吊牌——蓝手先贴蓝吊牌 tag，橙手后贴绿吊牌 tag-green 正好盖在同一位置，蓝的就看不见了（后来的盖掉先来的）；不画叉
        base=[I("shirt","tshirt",760,240,400),hand("ha","a",220,440,440),hand("hb","b",1260,440,440)]
        TX,TY,TS=1080,200,200
        tl=at(0,"看了一眼吊牌");te=at(0,"各自改了价钱");tb=at(0,"再贴回去");tc=at(0,"后贴的那张")
        e1=base+[I("tga","tag",560,520,TS),I("tgb","tag-green",1180,520,TS)]
        a1=[F("tga",tl),pop("tga",tl),F("tgb",tl+4),pop("tgb",tl+4),
            mv("tga","x",tb,tb+14,560,TX),mv("tga","y",tb,tb+14,520,TY),
            mv("tgb","x",tc,tc+14,1180,TX),mv("tgb","y",tc,tc+14,520,TY),mv("tga","opacity",tc+12,tc+14,1,0)]   # 绿的落位后蓝的完全被盖住
        e2=base+[I("tgb","tag-green",TX,TY,TS),term("lu",660,740,600,"丢失更新")]
        a2=[F("lu",at(0,"丢失更新")),pop("lu",at(0,"丢失更新"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 写锁：先到的（蓝袖）挂锁；橙袖伸手被挡、在旁边等；旁边的眼睛照样能看（不画成连看都不让看）
        base=[I("shirt","tshirt",760,240,400),I("eye","eye",300,140,150),sight("sight",460,215,330,120),hand("ha","a",300,430,440)]
        tk=at(0,"挂一把锁");tw=at(0,"别人想改它");tq=at(0,"只能等");to=at(0,"把锁打开")
        e1=base+[I("lk","lock-closed",880,540,160),I("lo","lock-open",880,540,160),hand("hb","b",1300,430,440),I("clk","clock",1420,250,130)]
        a1=[F("lk",tk,6),pop("lk",tk),mv("lo","opacity",0,to,0,0),mv("hb","x",tw,tw+10,1400,1240),mv("hb","x",tw+10,tw+18,1240,1300),F("clk",tq),pop("clk",tq),
            out("lk",to,8),F("lo",to,8),out("clk",to+4,8)]
        e2=base+[I("lk","lock-closed",880,540,160),hand("hb","b",1300,430,440),I("clk","clock",1420,250,130),term("xl",760,740,400,"写锁")]
        a2=[F("xl",at(0,"写锁")),pop("xl",at(0,"写锁"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 读锁：玻璃罩罩住 T 恤，几个人一起围着看；手伸过来被罩子挡回
        base=[I("shirt","tshirt",770,300,380),I("p1","person",130,500,220),I("p2","person",380,540,190),I("e1","eye",190,340,120),I("e2","eye",420,400,110),I("e3","eye",895,90,130),hand("hb","b",1300,420,440)]
        tv=at(0,"只是想看");tg=at(0,"一起围着看");tn=at(0,"谁也不能拿走")
        e1=base+[I("dome","glass-dome",700,210,520)]
        a1=[F("p1",tv),F("p2",tv+4),F("e1",tg),F("e2",tg+4),F("e3",tg+8),F("dome",tg),mv("hb","x",tn,tn+8,1400,1220),mv("hb","x",tn+8,tn+16,1220,1320)]
        e2=base+[I("dome","glass-dome",700,210,520),term("sl",760,770,400,"读锁")]
        a2=[F("sl",at(0,"读锁")),pop("sl",at(0,"读锁"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 锁一件 vs 锁一架：货架 = 一张表，架上每件 T 恤 = 一行
        X=[520,820,1120];YU,YD=213,470;s=180
        goods=[I(f"u{j}",n,X[j],YU,s) for j,n in enumerate(("tshirt","tshirt-orange","tshirt"))]+[I(f"d{j}",n,X[j],YD,s) for j,n in enumerate(("tshirt-orange","tshirt","tshirt-orange"))]
        base=[I("shelf","shelf",410,150,1100,550)]+goods
        tr=at(1,"只锁这一件");tp=at(1,"旁边的货大家照样拿")
        e1=base+[I("lk1","lock-closed",880,320,90),hand("hb","b",1296,113,380)]
        a1=[F("shelf",0,8)]+[F(e['id'],4,8) for e in goods]+[F("lk1",tr,6),pop("lk1",tr),F("hb",tp-10,8),mv("u2","y",tp,tp+12,YU,YU-40),mv("hb","y",tp,tp+12,113,73)]
        e2=base+[R("frame",390,130,1140,570,"#00000000",stroke=P['accent'],radius=24,dashed=True),I("lkT","lock-closed",860,290,200),hand("hb","b",1290,370,380),I("clk","clock",1560,330,110),term("tl",760,740,400,"表锁")]
        tt=at(0,"整个货架都锁上");tw=at(0,"一起等")
        a2=[F("frame",tt),F("lkT",tt,6),pop("lkT",tt),F("hb",tt+10),F("clk",tw),pop("clk",tw),F("tl",at(0,"表锁")),pop("tl",at(0,"表锁"))]
        e1=e1+[term("rl",760,740,400,"行锁")];a1=a1+[F("rl",at(1,"行锁")),pop("rl",at(1,"行锁"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 等太久只放弃这一步（手缩回，自己那一单的箱子还在）；死锁：各攥一件、都要对方那件
        e1=[I("shirt","tshirt",700,240,400),I("lk","lock-closed",820,540,160),hand("ha","a",240,430,440),
            I("bo_s","tshirt-orange",1330,470,200),I("bo","box-open",1290,560,280),hand("hb","b",1180,330,400),I("clk","clock",1450,200,120)]
        tq=at(0,"排队等");tg=at(0,"等得太久");tb=at(0,"先放弃这一步")
        a1=[F("clk",tq),pop("clk",tq),mv("clk","scale",tg,tg+12,1,1.15),mv("hb","x",tb,tb+14,1180,1440),mv("hb","opacity",tb,tb+14,1,0.35),out("clk",tb,10)]
        base=[I("sa","tshirt",380,260,340),I("la","lock-closed",500,500,110),hand("ha","a",80,330,340),
              I("sb","tshirt-orange",1200,260,340),I("lb","lock-closed",1320,500,110),hand("hb","b",1500,330,340)]
        arr=[E("arA","line",720,380,480,-60,P['secondary'],dashed=True),E("arB","line",1200,470,-480,60,P['accent'],dashed=True),I("clk","clock",900,540,120)]
        tc=at(0,"各攥着一件");tr=at(0,"伸手要对方那件");tf=at(0,"永远等下去")
        e2=base+arr+[term("dl",760,740,400,"死锁")]
        a2=[F("la",tc,6),F("lb",tc+4,6),draw("arA",tr),draw("arB",tr+4),F("clk",tf),mv("clk","rotation",tf,tf+40,0,360),F("dl",at(1,"死锁")),pop("dl",at(1,"死锁"))]
        return [(e1,a1),(e2,a2)]
    if si==6:  # 整单撤回（Nolan）：橙虚线框 + 倒放标出「被撤回的是橙手这一单」；橙手把橙 T 恤整件放回原位、松手退出，它的锁变开锁后消失；然后蓝手拿到这件
        base=[I("sa","tshirt",380,260,340),I("la","lock-closed",500,500,110),hand("ha","a",80,330,340),I("sb","tshirt-orange",1200,260,340),hand("hb","b",1500,330,340)]
        e=base+[I("lb","lock-closed",1320,500,110),I("lbo","lock-open",1320,540,110),E("arA","line",720,380,480,-60,P['secondary'],dashed=True),
                R("ord",1150,230,690,500,"#00000000",stroke=P['accent'],radius=30,dashed=True),I("rw","rewind",1560,150,110)]
        tf=at(0,"发现这种僵局");tr=at(0,"整单撤回");tn=max(at(0,"重新来一次"),tr+96)
        a=[mv("lbo","opacity",0,tr+30,0,0),mv("arA","opacity",tf,tf+8,0.4,1),F("ord",tr,8),F("rw",tr),pop("rw",tr),
           mv("sb","y",tr+12,tr+28,260,300),mv("lb","y",tr+12,tr+28,500,540),                       # 橙手把 T 恤整件放回去
           mv("hb","x",tr+20,tr+40,1500,1760),mv("hb","opacity",tr+20,tr+40,1,0),out("ord",tr+34,8),  # 松手退出这一单
           out("lb",tr+30,8),F("lbo",tr+30,8),mv("lbo","opacity",tr+50,tr+58,1,0),                 # 锁 → 开锁 → 消失
           mv("sb","x",tr+62,tr+82,1200,740),mv("sb","y",tr+62,tr+82,300,260),mv("ha","x",tr+62,tr+82,80,110),out("arA",tr+62,8),   # 蓝手拿到这件
           out("rw",tn-8,8),mv("hb","x",tn,tn+16,1760,1500),mv("hb","opacity",tn,tn+16,0,1)]   # 程序重新来一次：橙手再伸回来
        return [(e,a)]
    if si==7:  # 悲观锁：先挂锁，再伸手；另一只手只能等着；盾牌 = 先保证安全
        e=[I("shirt","tshirt",760,260,400),I("lk","lock-closed",880,560,160),hand("ha","a",120,430,440),hand("hb","b",1320,430,440),I("clk","clock",1440,280,120),I("sh","shield",1250,130,170),term("pl",760,770,400,"悲观锁")]
        tk=at(0,"先挂锁");th=at(0,"再动手");tw=at(0,"少几个人同时干");ts=at(0,"先保证安全")
        a=[mv("ha","opacity",0,th,0,0),F("lk",tk,6),pop("lk",tk),F("ha",th,6),mv("ha","x",th,th+14,120,300),F("hb",tw-6,6),F("clk",tw),pop("clk",tw),F("sh",ts),pop("sh",ts),F("pl",at(1,"悲观锁")),pop("pl",at(1,"悲观锁"))]
        return [(e,a)]
    if si==8:  # 乐观锁：不挂锁直接拿；放回时对一眼吊牌（右侧小卡 = 拿走时记下的吊牌）；被换过 → 重新拿
        memo=[R("memo",1400,200,300,340,stroke=P['text2'],radius=20),I("tm","tag",1450,230,200),I("ey","eye",1330,100,100)]
        e1=[I("shirt","tshirt",760,260,400),I("tg0","tag",1060,220,200),I("tg1","tag-swapped",1060,220,200),hand("ha","a",320,430,440)]+memo+[
            T("ne",1270,520,120,120,"≠",100,P['danger'],align="center")]
        tt=at(0,"直接拿去改");tp=at(1,"放回去的时候");tl=at(1,"看一眼吊牌");tc=at(1,"被别人换过");tr=at(1,"重新拿一次")
        a1=[F("memo",tt),F("tm",tt),mv("tg1","opacity",0,tc-30,0,0)]+[mv(i,"x",tt,tt+14,x0,x0-260) for i,x0 in (("shirt",760),("tg0",1060),("tg1",1060),("ha",320))]+[
            mv(i,"x",tp,tp+14,x0-260,x0) for i,x0 in (("shirt",760),("tg0",1060),("tg1",1060),("ha",320))]+[F("tg1",tc-30,10),F("ey",tl,6),pop("ey",tl),F("ne",tc),
            mv("shirt","x",tr,tr+12,760,560),mv("shirt","x",tr+12,tr+24,560,760)]
        e2=[I("shirt","tshirt",760,260,400),I("tg1","tag-swapped",1060,220,200),hand("ha","a",320,430,440),R("memo",1400,200,300,340,stroke=P['success'],radius=20),I("tm","tag-swapped",1450,230,200),I("ey","eye",1330,100,100),term("ol",760,770,400,"乐观锁")]
        a2=[F("ol",at(0,"乐观锁")),pop("ol",at(0,"乐观锁"))]
        return [(e1,a1),(e2,a2)]
    if si==9:  # 回顾：六张小卡（写锁 / 读锁 / 锁一件 / 锁一架 / 先挂锁 / 放回再对吊牌）；最后两只手按同一顺序拿货
        CX=[120,690,1260];CY=[120,470];cw,ch=440,320   # 右上卡不进水印区（x<1700）
        cards=[R(f"c{j}",CX[j%3],CY[j//3],cw,ch,stroke=P['text2'],radius=20) for j in range(6)]
        x0,y0=CX[0],CY[0];x1,y1=CX[1],CY[0];x2,y2=CX[2],CY[0];x3,y3=CX[0],CY[1];x4,y4=CX[1],CY[1];x5,y5=CX[2],CY[1]
        ic=[I("i0","tshirt",x0+40,y0+30,180),I("i0l","lock-closed",x0+150,y0+140,70),term("w0",x0+240,y0+110,200,"写锁",fs=56),
            I("i1d","glass-dome",x1+20,y1+20,220),I("i1","tshirt",x1+75,y1+80,110),term("w1",x1+260,y1+110,200,"读锁",fs=56),
            I("i2s","shelf",x2+40,y2+70,400,200),I("i2","tshirt",x2+170,y2+60,80),I("i2l","lock-closed",x2+205,y2+120,46),
            I("i3s","shelf",x3+40,y3+70,400,200),R("i3f",x3+30,y3+60,420,220,"#00000000",stroke=P['accent'],radius=14,dashed=True),I("i3l","lock-closed",x3+190,y3+110,100),
            I("i4l","lock-closed",x4+90,y4+130,110),hand("i4h","a",x4+230,y4+90,220),
            I("i5t","tag",x5+90,y5+60,190),I("i5e","eye",x5+270,y5+110,130)]
        tw=at(0,"写锁");tr=at(0,"读锁");t2=at(0,"只锁一行");t3=at(0,"锁整张表");t4=at(0,"先挂锁是悲观");t5=at(0,"放回时再检查")
        G={0:tw,1:tr,2:t2,3:t3,4:t4,5:t5}
        e1=cards+ic
        a1=[F(f"c{j}",max(0,G[j]-6),6) for j in range(6)]+[F(e['id'],G[int(e['id'][1])]) for e in ic if e['id'][0]=='i']+[F("w0",tw),F("w1",tr)]
        # 同一顺序拿货：上排蓝袖、下排橙袖，都先拿蓝 T 恤（挂锁）再拿橙 T 恤
        e2=[hand("ha","a",80,120,320),I("ua","tshirt",520,150,220),I("ub","tshirt-orange",900,150,220),I("la","lock-closed",590,330,80),I("lb","lock-closed",970,330,80),
            hand("hb","b",1520,470,320),I("da","tshirt",1180,500,220),I("db","tshirt-orange",800,500,220),I("lc","lock-closed",1250,680,80),I("ld","lock-closed",870,680,80),
            E("pa","line",400,260,520,0,P['secondary'],dashed=True),E("pb","line",1520,610,-520,0,P['accent'],dashed=True)]
        to=at(0,"同一个顺序")
        a2=[draw("pa",to,20),draw("pb",to,20),F("la",to+8,6),F("lc",to+8,6),pop("la",to+8),pop("lc",to+8),F("lb",to+28,6),F("ld",to+28,6),pop("lb",to+28),pop("ld",to+28)]
        return [(e1,a1),(e2,a2)]

def subs(t,L,si,k):
    S=sentences(t);q=TM[KEY(si,k)]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
            else: m.append(c)
        tot=sum(cnt(x) for x in m);acc=0;ct=None;pos=0
        aw=ASR.get(qq.get("src"))
        if aw: ct=asrcue.char_times(aw,s)   # 词级：按位置对齐到脚本字序（同音错字不影响）
        g0=sum(TM[x]["duration"] for x in list(TM)[:list(TM).index(KEY(si,k))])
        for c in m:
            if ct: f_=math.floor(30*(ct[pos]-ASR.get("_bias",0.1))-g0)   # 字幕不晚于配音：去掉宁晚偏置，向下取整
            else: f_=round(30*(qq["start"]+qq["dur"]*acc/tot))
            res.append({"text":subtext(c.strip().rstrip('，；：。？')),"from":max(0,f_),"src":qq.get("src"),"voiceFrom":max(0,f_)});acc+=cnt(c);pos+=len(asrcue.P(c))
    for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    res[0]["from"]=0
    if (si,k)==(0,0):   # 开场大字期间不出字幕：前置空白字幕到 SUB0-1，之后的字幕不早于 SUB0（起点相撞的往后顺延）
        for r in res: r["from"]=max(r["from"],SUB0)
        for a_,b_ in zip(res,res[1:]):
            if b_["from"]<a_["from"]+30: b_["from"]=a_["from"]+30   # 被大字推后的字幕至少留 30 帧可读；其余按配音起点不动
        res.insert(0,{"text":"","from":0,"blank":True,"note":"开场封面大字期间不出字幕"})
        for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    return res
scenes=[];g=0;nshot=0;CLAMP=[]
for si,s in enumerate(narr):
    S=sentences(s);parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S)
    L=[TM[KEY(si,k)]["duration"] for k in range(len(parts))]
    PARTS[:]=parts;designs=shots_for(si,L);shots=[];f=g
    for k,(p,l) in enumerate(zip(parts,L)):
        els,an=designs[k]
        els=[dict(e) for e in els]+[dict(T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],align="center",role="subtitle"),reuse=True)]
        for a in an:
            for kf in a['keyframes']:
                if not 0<=kf['frame']<=l-1: CLAMP.append((KEY(si,k),a['elementId'],a['property'],kf['frame'],l))
                kf['frame']=max(0,min(l-1,kf['frame']))
        last=k==len(parts)-1
        shots.append(dict(id=KEY(si,k),chapterId=ids[si],**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationCharsRecount=cnt(s),shots=shots));g+=D
# 图片节点（Knoll 2026-10-15：渲染器照图片节点加图片元素）：每个 image 元素补 appearFrame / disappearFrame（镜头内帧，按 opacity 关键帧算；null=到镜头末尾）、z（叠放顺序，越大越上）、tagText（贴在该物件上的小标签文字）
TAGS={}   # 本期不贴任何小标签文字
def _op(sh,eid,f):
    v=1.0;K=[k for a in sh['animations'] if a['elementId']==eid and a['property']=='opacity' for k in a['keyframes']]
    if not K: return 1.0
    K=sorted(K,key=lambda k:k['frame'])
    if f<=K[0]['frame']: return K[0]['value']
    for a_,b_ in zip(K,K[1:]):
        if a_['frame']<=f<=b_['frame']: return a_['value']+(b_['value']-a_['value'])*(f-a_['frame'])/max(1,b_['frame']-a_['frame'])
    return K[-1]['value']
for sc in scenes:
    for sh in sc['shots']:
        for z,e in enumerate(sh['elements']):
            if e['type']!='image': continue
            vis=[f for f in range(sh['durationInFrames']) if _op(sh,e['id'],f)>0.01]
            e['appearFrame']=vis[0] if vis else None
            e['disappearFrame']=(vis[-1]+1) if vis and vis[-1]<sh['durationInFrames']-1 else None
            e['z']=z
            if e['id'] in TAGS: e['tagText']=TAGS[e['id']]
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《两个人抢同一件货，听谁的？》",hook="两人抢一件货听谁的",episode=17,slug="db-lock",release="v0.22.0",draft=True,provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  series=None,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.15）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，按 EP.15 实测语速估，章尾 60 帧）；Knoll timeline 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json（map_timing.py，镜头边界直接按时间轴：章 = 本章首句起 → 下一章首句起，章间 0.6 s 已在音频里；只在全片结尾补 60 帧）。")+"草稿：术语标签（8 个，只用中文）暂按字数插值放在念到处，配音 words.json 到后走 asrcue/labelfix 对齐；开场第 0 帧即封面画面（两只手抢同一件 T 恤）；画面无数字标签、无英文。素材全部自绘。")
assets=dict(reuse=[dict(id=n,file=f"assets/{n}.svg",desc="EP.16 自绘，复用") for n in ("tshirt","tshirt-orange","person","box-open","eye","clock","rewind","shield")],
  new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc=d) for n,d in (("hand-a","手：蓝袖浅肤（先到的人）"),("hand-b","手：橙袖深肤（后到的人）"),("lock-closed","锁（关）=写锁"),("lock-open","锁（开）"),("tag","吊牌·原版"),("tag-swapped","吊牌·换过（橙）"),("tag-green","吊牌·另一人改的（绿）"),("glass-dome","玻璃罩=读锁"),("shelf","货架=一张表"))])
meta["timingSource"]="/workspace/share/ep17/timeline.json（Knoll 配音草稿，只读）→ map_timing.py → timing.json"
meta["pendingRegen"]=[dict(sentence="ch3-1",shot="xlock-1",text="办法是：先到的人，在 T 恤上挂一把锁。",take="c",note="Knoll 将重新生成，时长会变；到时重跑 map_timing+gen"),dict(sentence="ch5-1",shot="scope-1",text="锁也分大小。",take="c",note="同上")]
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面用 cover/ep17-*.png 定制设计，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])

