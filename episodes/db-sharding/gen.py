# EP.19《大促一到，下单怎么就卡住了？》分库分表（脚本 v0.24.0 定稿）分镜（Miyazaki）。工具链沿用 EP.18 db-replication/gen.py；配音未到时按字数估时长（make_timing.py）
# 比喻：快递驿站。同款货架 = 同结构的表；彩色贴纸 = 分片键决定去处；每个驿站自己的记账员 = 每个库自己的写入能力。驿站只按颜色区分
# 画面无数字 / 英文 / logo；术语标签只用中文（分表 / 分库 / 分片键 / 按范围 / 按哈希 / 水平拆分 / 垂直拆分 / 跨片查询 / 分布式事务）；只有右上「IT小村」水印
import json,re,math,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','_audit'));import asrcue
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext,narration
narr=narration(); assert len(narr)==13
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
titles=["转圈","写没分出去","驿站扛不住","同款货架","开分站","看颜色","按日子还是打散","另一种拆法","跑遍每个站","转件记账","撞号","先别拆","回顾"]
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
def tag(i,x,y,text,c=None,w=None): return R(i,x,y,max(w or 0,60+44*len(text)),80,stroke=c or P['text2'],radius=40,label=text,fontSize=40)   # 物件上的小标签（≥40px）
def bub(i,x,y,t,c=None): return R(i,x,y,60+40*len(t),80,stroke=c or P['accent'],radius=40,label=t,fontSize=40)
TOUT=36;SUB0=45   # hook-1：封面大字完整显示 0–36 帧，36–45 淡出；第一条字幕从 45 帧进（0–44 空白字幕）
# 术语标签完整显示（Nolan 2026-10-15）：= pop-in 完成（12 帧淡入后）→ 镜头转场淡出开始（fade 12 / crossfade 8）≥63 帧（terms.json 取 66 留余量）；
# 不够的由 _audit/labelfix 在镜头末尾加 hold（label_holds.json；terms.json fullShowExcludesFadeOut=true、holdOnProvisional=true）
# ---- EP.19 物件即语义：驿站（station-色）= 库（一台机器）；同款货架（shelf）= 结构相同的表；包裹 = 一行数据，贴纸颜色 = 分片键算出的去处；
# 记账员（clerk）= 这台库自己的写入能力；收件人（person-色）= 决定颜色的依据；信号虚线 + 圆点 = 包裹 / 请求的去向（沿用 EP.18，Knoll 画，节点标 knollDraw）。
# 驿站只按颜色区分：红 / 蓝 / 绿 / 黄（画面不出数字、英文、logo）；只有右上「IT小村」。
COL=["red","blue","green","yellow"];CX=dict(red=P['danger'],blue=P['secondary'],green=P['success'],yellow=P['accent'])
SIG_DOT=True
def sig(i,x0,y0,x1,y1,t,dur=40,stop=None,c=None,keep=False):   # keep=True：圆点停在 stop 处不熄（镜头结束时还在半路）
    """信号线 + 移动圆点（复制）。Knoll 画线和点：节点带 knollDraw；圆点节点只作占位，动画全由 signal 参数决定。stop=圆点停在线上的比例（断电时死在半路）"""
    m=dict(knollDraw="signalLine",signal=dict(fromXY=[x0,y0],toXY=[x1,y1],dotStart=t,dotFrames=dur,dotStopAt=stop,dotKeep=keep,note="Knoll：画信号线，圆点从 from 沿线移到 to；dotStopAt≠null 时圆点停在该比例处并熄灭"))
    e=[E(i,"line",x0,y0,x1-x0,y1-y0,c or P['primary'],dashed=True,**m),R(i+"d",x0-12,y0-12,24,24,P['accent'],radius=12,knollDraw="signalDot",signalOf=i)]
    f=stop if stop is not None else 1;te=t+round(dur*f)
    a=[draw(i,0,1)]   # 圆点（signalDot）不带自己的 x/y/opacity 关键帧：只看线上 signal 参数，Knoll 画
    return e,a
def par(i,c,x,y,s=110): return I(i,f"parcel-{c}" if c else "parcel",x,y,s)
def moveto(i,a,b,x0,y0,x1,y1,e="easeInOut"): return [mv(i,"x",a,b,x0,x1,e),mv(i,"y",a,b,y0,y1,e)]
def appear(i,t,n=10): return [F(i,t,n),pop(i,t)]
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:   # hook：开场即封面（两行大字 + 手机下单页，按钮在转圈）；第二镜：所有订单挤进一台机器、一张表
        e=[T("t1",160,200,1100,150,"大促一到",120,P['text']),T("t2",160,370,1100,150,"下单怎么就卡住了？",110,P['accent']),
           I("ph","phone-order",1180,170,620),R("btn",1393,556,194,80,P['secondary'],radius=40,label="下单",fontSize=40),I("sp","spinner",1445,644,90)]
        ts=at(0,"转了半天圈")
        a=[out("t1",TOUT,SUB0-TOUT),out("t2",TOUT,SUB0-TOUT),mv("sp","opacity",0,min(ts,30),0,0),F("sp",min(ts,30),6),mv("sp","rotate",min(ts,30),L[0]-1,0,900,"linear"),mv("btn","opacity",min(ts,30),min(ts,30)+8,1,0.5)]
        to=at(0,"所有订单");OX=[120,260,400,180,330,470];OY=[180,330,480,620,700,250]
        e2=[I("db","server",820,160,300),I("tb","table-sheet",1180,220,380)]+[I(f"o{j}","order",x,y,120) for j,(x,y) in enumerate(zip(OX,OY))]
        a2=[F("db",0,8),F("tb",at(0,"一张表"),8),pop("tb",at(0,"一张表"))]
        for j,(x,y) in enumerate(zip(OX,OY)): a2+=[F(f"o{j}",to+j*3,6)]+moveto(f"o{j}",to+8+j*4,to+30+j*4,x,y,1250+(j%3)*80,300+(j//3)*90)
        return [(e,a),(e2,a2)]
    if si==1:   # 接上期：主库（赛场）+ 从库（电视）分走了读；下单是写，还挤进主库
        TX=[1060,1340,1060];TY=[150,150,470]
        e=[I("st","stadium",160,240,640,320),tag("stT",380,580,"主库",P['primary'])]
        a=[]
        for j in range(2):
            e+=[I(f"tv{j}","tv-frame",1080+j*340,180,300),I(f"vw{j}","viewer",1150+j*340,470,160)]
            se,sa=sig(f"sg{j}",800,400,1100+j*340,300,at(0,"加从库")+4+j*4,20);e+=se;a+=sa+[F(f"tv{j}",0,8),F(f"vw{j}",at(0,"分走了读"),8),pop(f"vw{j}",at(0,"分走了读"))]
        e+=[tag("ckT",1240,640,"从库",P['primary'])];a+=[]   # 「从库」小标签和主库一样从第 0 帧就在
        tw=at(0,"下单是写");OX=[1180,1320,1460,1600,1250,1530];OY=[120,140,120,150,700,690]
        e2=[I("st","stadium",160,240,640,320),tag("stT",380,580,"主库",P['primary'])]+[I(f"tv{j}","tv-frame",1080+j*340,300,260) for j in range(2)]
        e2+=[I(f"o{j}","order",x,y,100) for j,(x,y) in enumerate(zip(OX,OY))]+[I("clk","clock",820,150,130)]
        a2=[mv(f"tv{j}","opacity",0,1,0.4,0.4) for j in range(2)]+[F("clk",at(0,"还得挤进"),8),pop("clk",at(0,"还得挤进"))]
        for j,(x,y) in enumerate(zip(OX,OY)): a2+=[F(f"o{j}",tw+j*3,6)]+moveto(f"o{j}",tw+10+j*4,tw+34+j*4,x,y,300+(j%3)*140,300+(j//3)*90)
        return [(e,a),(e2,a2)]
    if si==2:   # 一个快递驿站（青色门头）；大促：包裹堆成山、货架塞满、记账员忙不过来
        e=[I("stn","station",620,140,680)];a=appear("stn",0)
        tp=at(1,"包裹堆成山");tf=at(1,"货架塞满");tc=at(1,"记账员")
        e2=[I("pile","parcel-pile",160,300,440),I("sf","shelf-full",760,220,460),I("ck","clerk-busy",1320,280,440)]
        a2=[F("pile",tp,8),mv("pile","scale",tp,tp+14,0.4,1),F("sf",tf,8),pop("sf",tf),F("ck",tc,8),pop("ck",tc)]
        return [(e,a),(e2,a2)]
    if si==3:   # 分表：站里多摆几排一模一样的货架，包裹按贴纸颜色分到各自的货架上，每个只放一处
        SX=[200,600,1000,1400];tm=at(0,"多摆几排");tc=at(0,"贴纸颜色");td=at(0,"分到不同的货架")
        e=[R("in",120,140,1560,620,"#00000000",stroke=P['muted'],radius=30)]
        for j,c in enumerate(COL): e+=[I(f"sh{j}","shelf",SX[j],300,320),I(f"sc{j}",f"shelf-{c}",SX[j],300,320)]
        PX=[760,880,1000,1120];e+=[par(f"p{j}",c,PX[j],150,100) for j,c in enumerate(COL)]
        a=[F("in",0,8)]+[F(f"sh{j}",tm+j*6,8) for j in range(4)]+[mv(f"sc{j}","opacity",0,td+30,0,0) for j in range(4)]+[F(f"sc{j}",td+30+j*4,8) for j in range(4)]
        for j in range(4): a+=[F(f"p{j}",tc,8)]+moveto(f"p{j}",td+j*4,td+26+j*4,PX[j],150,SX[j]+110,330)+[out(f"p{j}",td+30+j*4,6)]
        e2=[R("db",140,140,1640,560,"#00000000",stroke=P['primary'],radius=30)]
        for j,c in enumerate(COL): e2+=[I(f"tb{j}","table-sheet",210+j*400,220,300),R(f"cb{j}",240+j*400,530,240,24,CX[c],radius=12)]
        e2+=[term("fb",810,740,300,"分表")];tt=at(0,"拆成结构相同")
        a2=[F("db",0,8)]+[F(f"tb{j}",tt+j*4,8) for j in range(4)]+[F(f"cb{j}",tt+j*4,8) for j in range(4)]+[F("fb",at(0,"分表")),pop("fb",at(0,"分表"))]
        return [(e,a),(e2,a2)]
    if si==4:   # 分库：记账员还是只有一个 → 再开几个分站，各有货架、各有记账员 → 分到多台机器，写的压力分开
        e=[I(f"sh{j}",f"shelf-{c}",160+j*300,260,300) for j,c in enumerate(COL)]+[I("ck","clerk-busy",1380,300,400)]
        a=[F("ck",0,8),mv("ck","scale",at(0,"只有一个"),at(0,"只有一个")+12,1,1.08)]
        tn=at(0,"再开几个分站");ts=at(0,"各有货架");tc=at(0,"各有记账员");SX=[150,580,1010,1440]
        e2=[];a2=[]
        for j,c in enumerate(COL):
            e2+=[I(f"st{j}",f"station-{c}",SX[j],160,330),I(f"sh{j}",f"shelf-{c}",SX[j]+10,500,160),I(f"ck{j}","clerk",SX[j]+170,500,160)]
            a2+=[F(f"st{j}",tn+j*5,8),pop(f"st{j}",tn+j*5),F(f"sh{j}",ts+j*3,8),F(f"ck{j}",tc+j*3,8),pop(f"ck{j}",tc+j*3)]
        tm=at(0,"多台机器");tw=at(0,"写的压力");e3=[];a3=[]
        for j,c in enumerate(COL):
            e3+=[I(f"st{j}",f"station-{c}",SX[j],140,320),I(f"sv{j}","server",SX[j]+90,450,150)]
            se,sa=sig(f"sg{j}",960,700,SX[j]+165,600,tw+j*3,16,c=CX[c]);e3+=se;a3+=sa+[F(f"sv{j}",tm+j*3,8),pop(f"sv{j}",tm+j*3)]
        e3+=[I("od","order",900,620,110),term("fk",810,740,300,"分库")];a3+=[F("od",tw-6,6),out("od",tw+18,6),F("fk",at(0,"分库")),pop("fk",at(0,"分库"))]
        return [(e,a),(e2,a2),(e3,a3)]
    if si==5:   # 分片键：去哪个站看贴纸颜色；颜色由收件人决定，同一个人永远去同一个站
        SX=[200,620,1040,1460]
        e=[I(f"st{j}",f"station-{c}",SX[j],150,280) for j,c in enumerate(COL)]+[par("pk","blue",820,470,240),R("ring",828,480,90,80,"#00000000",stroke=P['primary'],radius=16)]
        tc=at(0,"看贴纸颜色");se,sa=sig("sg",940,470,SX[1]+140,420,tc+10,16,c=CX['blue']);e+=se
        a=[F("pk",0,8),mv("ring","opacity",0,tc,0,0),F("ring",tc,6),mv("ring","scale",tc,tc+10,1.3,1)]+sa+[mv(f"st{j}","opacity",tc+10,tc+20,1,0.35) for j in (0,2,3)]
        tp=at(0,"收件人决定");tw=at(0,"同一个人永远")
        e2=[I("pb","person-blue",160,240,300),I("sb","station-blue",1300,160,420)]+[par(f"p{j}","blue",520,420,130) for j in range(3)]
        e2+=[term("fp",760,740,400,"分片键")]
        a2=[F("pb",0,8),pop("pb",tp)]
        for j in range(3): a2+=[F(f"p{j}",tp+6 if j==0 else tw+j*10,6)]+moveto(f"p{j}",tw+j*10,tw+j*10+24,520,420,1330+j*150,600)   # Nolan 2026-10-15：三件在站门口一字排开，不叠
        se2,sa2=sig("sg",480,480,1320,420,tw,40,c=CX['blue']);e2+=se2;a2+=sa2+[F("fp",at(1,"分片键")),pop("fp",at(1,"分片键"))]
        return [(e,a),(e2,a2)]
    if si==6:   # 按范围 vs 按哈希：左边按到货日子 → 今天的全挤进一个站；右边打散算颜色 → 各站差不多
        LX=[120,320,520,720];RX=[1040,1240,1440,1640]
        e=[E("div","line",960,140,0,560,P['muted']),I("cal","calendar",340,120,200),I("shf","shuffle",1260,120,200)]
        e+=[I(f"l{j}",f"station-{c}",LX[j],340,180) for j,c in enumerate(COL)]+[I(f"r{j}",f"station-{c}",RX[j],340,180) for j,c in enumerate(COL)]
        tr=at(0,"按到货日子");tj=at(0,"今天到的");th=at(1,"把收件人打散");te=at(1,"各站忙得")
        e+=[par(f"lp{j}","red",440,330,70) for j in range(6)]+[par(f"rp{j}",COL[j%4],1340,330,70) for j in range(8)]
        e+=[term("fr",230,740,400,"按范围"),term("fh",1290,740,400,"按哈希")]
        a=[F("div",0,8),F("cal",tr,8),pop("cal",tr),mv("shf","opacity",0,th,0,0),F("shf",th,8),pop("shf",th)]+[mv(f"r{j}","opacity",0,th,0.35,0.35) for j in range(4)]+[mv(f"r{j}","opacity",th,th+10,0.35,1) for j in range(4)]
        for j in range(6): a+=[F(f"lp{j}",tj+j*3,6)]+moveto(f"lp{j}",tj+j*3,tj+j*3+20,440,250,LX[0]+20+(j%3)*50,540+(j//3)*60)
        for j in range(8): a+=[F(f"rp{j}",th+12+j*3,6)]+moveto(f"rp{j}",th+12+j*3,th+32+j*3,1340,250,RX[j%4]+30+(j//4)*60,540)
        a+=[F("fr",at(0,"按范围")),pop("fr",at(0,"按范围")),F("fh",at(1,"按哈希")),pop("fh",at(1,"按哈希"))]
        return [(e,a)]
    if si==7:   # 水平拆分（按包裹拆，各站货架一样）vs 垂直拆分（按业务拆：生鲜一个站、大件一个站）
        LX=[120,400,680];tv=at(1,"按业务拆");tf=at(1,"生鲜");tb=at(1,"大件")
        e=[E("div","line",960,140,0,560,P['muted'])]
        for j,c in enumerate(COL[:3]): e+=[I(f"l{j}",f"station-{c}",LX[j],170,240),I(f"ls{j}",f"shelf-{c}",LX[j]+30,440,180)]
        e+=[I("rg","station-green",1060,170,300),I("ry","station-yellow",1460,170,300),I("fr1","parcel-fresh",1100,480,130),I("fr2","parcel-fresh",1230,480,130),I("bg","parcel-big",1470,470,280)]
        e+=[term("sp",210,740,500,"水平拆分"),term("cz",1210,740,500,"垂直拆分")]
        a=[F(f"l{j}",j*4,8) for j in range(3)]+[F(f"ls{j}",at(0,"每站货架")+j*4,8) for j in range(3)]
        a+=[mv(x,"opacity",0,tv,0,0) for x in ("rg","ry")]+[F("rg",tv,8),F("ry",tv+4,8)]+[mv(x,"opacity",0,tf,0,0) for x in ("fr1","fr2")]+[F("fr1",tf,6),pop("fr1",tf),F("fr2",tf+4,6),mv("bg","opacity",0,tb,0,0),F("bg",tb,6),pop("bg",tb)]
        a+=[F("sp",at(0,"水平拆分")),pop("sp",at(0,"水平拆分")),F("cz",at(1,"垂直拆分")),pop("cz",at(1,"垂直拆分"))]
        return [(e,a)]
    if si==8:   # 跨片查询：拆开后麻烦来了；找今天最重的包裹 → 取件员跑遍每个站 → 汇总单
        SX=[160,560,960,1360]
        e=[I(f"st{j}",f"station-{c}",SX[j],200,330) for j,c in enumerate(COL)]+[I("clk","clock",860,560,140)]
        a=[F(f"st{j}",j*4,8) for j in range(4)]+[F("clk",at(0,"麻烦"),8),pop("clk",at(0,"麻烦"))]
        tz=at(0,"最重");tr=at(0,"跑遍");tg=at(0,"再汇总")
        e2=[I(f"st{j}",f"station-{c}",SX[j]+40,150,260) for j,c in enumerate(COL)]+[I("sc","scale",120,450,200),I("rn","runner",380,430,220),I("cb","clipboard",1500,430,230)]
        e2+=[I(f"mk{j}",f"parcel-{c}",SX[j]+130,420,80) for j,c in enumerate(COL)]+[term("kc",710,740,500,"跨片查询")]
        a2=[F("sc",tz,8),pop("sc",tz),mv("rn","opacity",0,tr,0,0),F("rn",tr,6)]
        RX=[x+60 for x in SX];step=max(8,(tg-tr)//4)
        for j in range(4):
            t0=tr+j*step;a2+=[mv("rn","x",t0,t0+step,RX[j-1] if j else 380,RX[j]),mv(f"mk{j}","opacity",0,t0+step,0,0),F(f"mk{j}",t0+step,4)]
        a2+=[out("rn",tg+4,6),mv("cb","opacity",0,tg,0,0),F("cb",tg,8),pop("cb",tg),F("kc",at(0,"跨片查询")),pop("kc",at(0,"跨片查询"))]
        return [(e,a),(e2,a2)]
    if si==9:   # 分布式事务：红站转件给蓝站，两头各记一笔；要么都记、要么都不记；中途断了账对不上
        def base():
            return [I("rs","station-red",160,150,400),I("bs","station-blue",1360,150,400),I("rl","ledger",210,500,300),I("bl","ledger",1410,500,300),
                    I("rk","ledger-ok",210,500,300),I("bk","ledger-ok",1410,500,300)]
        t1=at(0,"转给蓝站");to=at(0,"这头记转出");ti=at(0,"那头记转入")
        se,sa=sig("sg",570,380,1360,380,t1,30,c=CX['red'])
        e=base()+se+[par("pp","red",600,300,110)]
        a=sa+moveto("pp",t1,t1+30,600,300,1240,300)+[mv("rk","opacity",0,to,0,0),F("rk",to,6),pop("rk",to),mv("bk","opacity",0,ti,0,0),F("bk",ti,6),pop("bk",ti)]
        tb=at(0,"都记上");tn=at(0,"都不记");tx=at(0,"中途断了");tu=at(0,"账就对不上");ts=at(0,"又慢又麻烦")
        se2,sa2=sig("sg",570,380,1360,380,max(0,tn+10),40,stop=0.5,c=CX['red'])
        e2=base()+[I("rx","ledger-bad",1410,500,300)]+se2+[par("pp","red",600,300,110),I("cr","crash",900,320,140),I("clk","clock",880,560,140),term("fs",710,740,500,"分布式事务")]
        a2=sa2+[mv("rk","opacity",0,tb,0,0),mv("bk","opacity",0,tb,0,0),F("rk",tb,6),F("bk",tb,6),out("rk",tn,6),out("bk",tn,6)]
        a2+=moveto("pp",tn+10,tx,600,300,860,300)+[mv("cr","opacity",0,tx,0,0),F("cr",tx,4),pop("cr",tx)]
        a2+=[mv("rx","opacity",0,tu,0,0),F("rx",tu,6),pop("rx",tu),mv("clk","opacity",0,ts,0,0),F("clk",ts,6),pop("clk",ts),F("fs",at(1,"分布式事务")),pop("fs",at(1,"分布式事务"))]
        a2[a2.index(mv("rk","opacity",0,tb,0,0))]=mv("rk","opacity",0,tb,0,0)
        # 断了之后：红站这头记了转出（绿勾回来），蓝站那头没记（红叉）→ 账对不上
        a2+=[mv("rk","opacity",tu,tu+6,0,1)]
        return [(e,a),(e2,a2)]
    if si==10:  # 撞号：各站自己给包裹编号（条码签），两张一模一样 → 撞到一起
        tz=at(0,"撞号");tn=at(0,"自己编号")
        e=[I("rs","station-red",160,180,420),I("bs","station-blue",1340,180,420),I("ta","idtag",560,280,240),I("tb","idtag",1120,280,240),I("spk","spark",820,240,280)]
        a=[F("ta",tn,8),pop("ta",tn),F("tb",tn+6,8),pop("tb",tn+6)]+moveto("ta",tz,tz+10,560,280,700,300)+moveto("tb",tz,tz+10,1120,280,980,300)+[mv("spk","opacity",0,tz+8,0,0),F("spk",tz+8,4),pop("spk",tz+8)]
        return [(e,a)]
    if si==11:  # 再开新站 → 不少包裹得搬家（手推车）；单台机器够用就先别拆
        tn=at(0,"再开新站");tm=at(0,"搬家");SX=[160,560,960]
        e=[I(f"st{j}",f"station-{c}",SX[j],180,320) for j,c in enumerate(COL[:3])]+[I("ny","station-yellow",1400,180,320),I("cart","cart",400,500,220)]
        a=[mv("ny","opacity",0,tn,0,0),F("ny",tn,8),pop("ny",tn),mv("cart","opacity",0,tm,0,0),F("cart",tm,6)]+[mv("cart","x",tm,min(tm+40,L[0]-3),400,1300)]
        e2=[I("sv","server",520,180,420),I("stn","station",1000,180,440),I("ck","clerk",1100,520,240)]
        a2=[F("sv",0,8),F("stn",at(0,"就先别拆"),8),F("ck",at(0,"就先别拆")+6,8)]
        return [(e,a),(e2,a2)]
    if si==12:  # 回顾：同一个库里拆表（分表）｜拆到不同机器（分库）｜拆前选好分片键，拆后都有代价
        e=[R("db",120,150,540,500,"#00000000",stroke=P['primary'],radius=30)]+[I(f"tb{j}","table-sheet",150+(j%2)*250,190+(j//2)*220,220) for j in range(4)]
        e+=[I(f"st{j}",f"station-{c}",740+(j%2)*230,160+(j//2)*250,200) for j,c in enumerate(COL)]
        e+=[I("pb","person-blue",1260,180,240),par("pk","blue",1500,240,200),I("cr","crash",1240,470,130),I("clk","clock",1560,470,130)]
        e+=[term("fb",210,740,360,"分表"),term("fk",780,740,360,"分库"),term("fp",1300,740,420,"分片键")]
        tk=at(1,"拆之后都有代价")
        a=[F("fb",at(0,"分表")),pop("fb",at(0,"分表")),F("fk",at(0,"分库")),pop("fk",at(0,"分库")),F("fp",at(1,"分片键")),pop("fp",at(1,"分片键"))]
        a+=[mv(f"st{j}","opacity",0,at(0,"拆到不同机器"),0.3,0.3) for j in range(4)]+[mv(f"st{j}","opacity",at(0,"拆到不同机器"),at(0,"拆到不同机器")+10,0.3,1) for j in range(4)]
        a+=[mv(x,"opacity",0,at(1,"拆之前"),0.3,0.3) for x in ("pb","pk")]+[mv(x,"opacity",at(1,"拆之前"),at(1,"拆之前")+10,0.3,1) for x in ("pb","pk")]
        a+=[mv(x,"opacity",0,tk,0,0) for x in ("cr","clk")]+[F("cr",tk,6),pop("cr",tk),F("clk",tk+4,6),pop("clk",tk+4)]
        return [(e,a)]

def subs(t,L,si,k):
    S=sentences(t);q=TM[KEY(si,k)]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？" and len(m[-1]+c)<=24: m[-1]+=c   # EP.18：合并后不超过 24 字
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
        _ids={x['id'] for x in els};an=[x for x in an if x['elementId'] in _ids]   # 去掉指向已删节点的动画
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
# 静止段轻推镜（村长 2026-10-15）：镜头最后一个画面动作之后还有 ≥75 帧（或全片最后一镜），整镜头从 1.00 缓推到 1.04（Knoll 按 camera.pushIn 做整层 scale，围绕画面中心偏上）
def _lastact(sh):
    K=[k['frame'] for a in sh['animations'] if a['property']!='drawProgress' for k in a['keyframes']]
    return max(K) if K else 0
allsh=[x for sc in scenes for x in sc['shots']]
for sh in allsh:
    la=_lastact(sh);n=sh['durationInFrames']
    if sh['id']=='hook-1': continue
    # 定稿时间复查（2026-10-15）：reshard-2「先别拆」整镜几乎静止 → 从第 0 帧起轻推；station-1 只有 53 帧且全程在淡入 / 介绍，不推
    if n-la>=60 or sh is allsh[-1] or sh['id']=='reshard-2':
        s0=0 if sh is allsh[-1] or sh['id']=='reshard-2' else min(la,n-60)
        sh['camera']=dict(pushIn=dict(fromScale=1.0,toScale=1.04,startFrame=max(0,s0),endFrame=n-1,origin=[960,470],easing="easeInOut"),note="静止段轻推镜：整层（不含字幕 / 水印）缓慢放大")
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《大促一到，下单怎么就卡住了？》",hook="大促一到下单怎么就卡住了",episode=19,slug="db-sharding",release="v0.24.0",draft=True,provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  pendingAudio=PROV,series=None,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.15–18）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾卡（只含全片结尾 60 帧留白）"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，4.3 字/秒估）；Knoll /workspace/share/ep19/timeline.json + words.json 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json（map_timing.py：章 = 本章首句起 → 下一章首句起；只在全片结尾补 60 帧）。")+
    "术语标签（9 个，只用中文）念到时淡入（0..+4 帧，宁晚勿早），完整显示（pop-in 完成 → 转场淡出开始）≥63 帧（按 66 留余量，不够在镜头末尾加 hold）；开场第 0 帧即封面画面（大字 + 手机下单在转圈）；"
    "驿站 = 库（只按颜色区分）、同款货架 = 同结构的表、贴纸颜色 = 分片键、记账员 = 写入能力；信号线与圆点由 Knoll 画（knollDraw）；静止段 camera.pushIn 轻推镜；画面无数字 / 英文 / logo。素材全部自绘。")
NEW=("calendar","cart","clerk","clerk-busy","clipboard","idtag","ledger","ledger-bad","ledger-ok","order","parcel","parcel-big","parcel-blue","parcel-fresh","parcel-green","parcel-pile","parcel-red","parcel-yellow",
     "person-blue","person-green","person-red","person-yellow","phone-order","runner","scale","server","shelf","shelf-blue","shelf-full","shelf-green","shelf-red","shelf-yellow","shuffle","spark","spinner",
     "station","station-blue","station-green","station-red","station-yellow","table-sheet")
assets=dict(new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png") for n in NEW],
  reuse=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc="EP.16–18 自绘，复用") for n in ("clock","crash","stadium","tv-frame","viewer")])
meta["timingSource"]=("/workspace/share/ep19/timeline.json（Knoll）→ map_timing.py → timing.json" if not PROV else "字数估算 4.3 字/秒（make_timing.py → timeline.estimate.json → map_timing.py）；Knoll /workspace/share/ep19/timeline.json + words.json 到后 sh realign.sh 直接重跑")
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面用 cover/ep19-*.png 定制设计，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
