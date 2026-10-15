# EP.18《刚改的昵称，怎么又变回去了？》主从复制（脚本 v0.23.0 定稿）分镜（Miyazaki）。工具链沿用 EP.17 db-lock/gen.py；配音未录时按字数估时长（make_timing.py）
# 比喻：体育直播。赛场 = 主库（唯一写入方 = 场上那名球员），电视转播 = 从库（同一套图层推后播），信号线 + 圆点 = 复制；手机昵称 = 你读到的数据
# 画面无数字 / 比分 / 标志 / 英文；术语标签只用中文（主库 / 从库 / 主从复制 / 读写分离 / 复制延迟 / 异步复制 / 半同步复制）；只有右上「IT小村」水印
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
titles=["变回去了","没丢","看直播","赛场和电视","不挤赛场","邻居先欢呼","信号还没发出去","等一声收到","看赛场本身","回顾"]
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
# ---- EP.18 物件即语义：赛场（stadium 分层 + 球员分层 + 球）= 主库（只有赛场上的这一名球员能改结果 = 唯一写入方）；
# 电视（tv-frame 里放同一套赛场 / 球员 / 球图层，关键帧整体推后）= 从库；信号线 + 移动圆点 = 复制（Knoll 画线和点，节点里标 knollDraw）；
# 手机 + 昵称文字节点 = 你读到的数据。画面无数字、比分、标志、英文；只有右上「IT小村」。
# 从库动画（Nolan/Knoll 2026-10-15）：本期 EP.18 保留现状 —— 电视里的从库图层已按 DLY 帧推后写好关键帧。
# 下一期起：从库节点留空（不写关键帧），只给 replicaOf/delayFrames，由 Knoll 把主库关键帧整体平移。
DLY=24   # 电视转播（从库）比赛场晚的帧数（草稿值；Knoll 按 replicaOf/delayFrames 平移同一套图层）
def stad(p,X,Y,W,tk=None,ball="foot",dark=False,role="main",of=None,d=0):
    """赛场图层组：field/poles/lights-on(+lights-off/dim)/球员 body·stand·ready·kick/球。tk=射门帧（None=不射）；ball=foot|net 初始状态。
    role=main → 主库；role=replica → 电视里的从库，关键帧 = 主库的整体推后 d 帧（meta: replicaOf/delayFrames）。返回 (elements, animations)"""
    k=W/1024;H=W/2;M=dict(layerGroup=p,dbRole=role)
    if role=="replica": M.update(replicaOf=of,delayFrames=d,note="从库：与主库同一套图层，Knoll 把主库关键帧整体推后 delayFrames 帧")
    def L(i,n,x,y,w,h=None): return I(p+i,n,round(x),round(y),round(w),None if h is None else round(h),**M)
    e=[L("fld","stadium-field",X,Y,W,H),L("pol","stadium-poles",X,Y,W,H),L("lon","stadium-lights-on",X,Y,W,H)]
    if dark: e+=[L("loff","stadium-lights-off",X,Y,W,H),L("dim","stadium-dim",X,Y,W,H)]
    px,py,ps=X+330*k,Y+161*k,260*k;FX,FY,FS=X+496*k,Y+374*k,35*k;GX,GY,GS=X+858*k,Y+222*k,30*k
    e+=[L("body","player-body",px,py,ps),L("stand","player-leg-stand",px,py,ps),L("ready","player-leg-ready",px,py,ps),L("kick","player-leg-kick",px,py,ps)]
    e+=[L("ball","ball",FX if ball=="foot" else GX,FY if ball=="foot" else GY,FS if ball=="foot" else GS)]
    a=[]
    if dark: a+=[mv(p+"loff","opacity",0,1,0,0),mv(p+"dim","opacity",0,1,0,0)]
    if ball=="net" or tk is None:   # 用不到的腿姿势不出节点（不再给全程隐藏的图层，appearFrame 不会是 null）
        h=p+("ready" if ball=="net" else "kick");e=[x for x in e if x['id']!=h]
    if ball=="foot" and tk is not None:
        t=tk+d;a+=[out(p+"ready",t,2),F(p+"kick",t,2),mv(p+"ball","x",t+2,t+14,round(FX),round(GX)),mv(p+"ball","y",t+2,t+14,round(FY),round(GY)),
                   mv(p+"ball","w",t+2,t+14,round(FS),round(GS))]
    return e,a
def lightsoff(p,t): return [F(p+"loff",t,6),mv(p+"dim","opacity",t,t+10,0,1),out(p+"lon",t,6)]
def tv(p,X,Y,W,**kw):
    """电视 = 从库：tv-frame + 屏幕里一套推后的赛场图层（屏幕区 512 画框 x64–448、y116–354 → 放 2:1 赛场）"""
    k=W/512;e=[I(p+"tv","tv-frame",X,Y,W,**dict(dbRole="replica",layerGroup=p))]
    se,sa=stad(p+"s",X+64*k,Y+139*k,384*k,role="replica",of=kw.pop("of","m"),d=kw.pop("d",DLY),**kw)
    return e+se,sa
def sig(i,x0,y0,x1,y1,t,dur=40,stop=None,c=None,keep=False):   # keep=True：圆点停在 stop 处不熄（镜头结束时还在半路）
    """信号线 + 移动圆点（复制）。Knoll 画线和点：节点带 knollDraw；圆点节点只作占位，动画全由 signal 参数决定。stop=圆点停在线上的比例（断电时死在半路）"""
    m=dict(knollDraw="signalLine",signal=dict(fromXY=[x0,y0],toXY=[x1,y1],dotStart=t,dotFrames=dur,dotStopAt=stop,dotKeep=keep,note="Knoll：画信号线，圆点从 from 沿线移到 to；dotStopAt≠null 时圆点停在该比例处并熄灭"))
    e=[E(i,"line",x0,y0,x1-x0,y1-y0,c or P['primary'],dashed=True,**m),R(i+"d",x0-12,y0-12,24,24,P['accent'],radius=12,knollDraw="signalDot",signalOf=i)]
    f=stop if stop is not None else 1;te=t+round(dur*f)
    a=[draw(i,0,1)]   # 圆点（signalDot）不带自己的 x/y/opacity 关键帧：只看线上 signal 参数，Knoll 画
    return e,a
def phone(p,X,Y,W,names):
    """手机：昵称框里放文字节点；names=[(文字, 切换帧),…] 依次替换。文字框 = 头像点右侧空白区（512 画框 x232..330，中心 x≈281），居中、≥28px。
    切换帧 f：上一个名字 f-4..f 淡出，新名字 f..f+4 淡入 → 两个名字永不同屏。每个节点只有一条 opacity 关键帧（Knoll 2026-10-15）"""
    k=W/512;e=[I(p,"phone",X,Y,W)];a=[];fs=max(28,round(30*k))
    for j,(t,f) in enumerate(names):
        e.append(T(f"{p}n{j}",round(X+232*k),round(Y+236*k)+round((50*k-fs*1.25)/2),round(98*k),round(50*k),t,fs,P['text'],align="center",nickname=True))
        nxt=names[j+1][1] if j+1<len(names) else None;K=[]
        if f>0: K+=[(f,0),(f+4,1)]
        if nxt is not None: K+=([(nxt-4,1)] if not K or K[-1][0]<nxt-4 else [])+[(nxt,0)]
        if K: a.append(dict(elementId=f"{p}n{j}",property="opacity",keyframes=[dict(frame=x,value=v) for x,v in K],easing="linear"))
    return e,a
def bub(i,x,y,t,c=None): return R(i,x,y,60+40*len(t),80,stroke=c or P['accent'],radius=40,label=t,fontSize=40)
def viewers(p,xs,y,w=130,cheer=False): return [I(f"{p}{j}","viewer-cheer" if cheer else "viewer",x,y,w) for j,x in enumerate(xs)]
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 开场即封面：两行大字 + 大手机（≥480 宽），昵称 旧 → 新 → 旧；大字 0–36 完整、36–45 淡出，字幕 45 帧进
        tB=min(at(0,"又变回"),63);   # Knoll 2026-10-15：新昵称约 21 帧出、约 63 帧换回旧昵称
        tA=max(8,min(tB-20,at(0,"一刷新")-14))
        pe,pa=phone("ph",1180,200,560,[("旧昵称",0),("新昵称",tA),("旧昵称",tB)])
        e=[T("t1",160,190,900,150,"刚改的昵称",120,P['text']),T("t2",160,350,900,150,"又变回去了？",120,P['accent'])]+pe
        return [(e,[out("t1",TOUT,SUB0-TOUT),out("t2",TOUT,SUB0-TOUT)]+pa)]
    if si==1:  # 修改没丢：赛场（主库）上球已进网 + 盾牌；你看到的是慢半拍的转播（电视里球还在脚下 + 钟）
        pe,pa=phone("ph",160,220,480,[("旧昵称",0)])
        me,ma=stad("m",1100,140,620,ball="net");te,ta=tv("v",1220,450,400,ball="foot")
        tk=at(0,"没丢");ts=at(0,"慢半拍")
        e=pe+me+[I("ok","shield",1560,150,130)]+te+[I("clk","clock",1040,560,130)]
        return [(e,pa+ma+ta+[F("ok",tk),pop("ok",tk),F("clk",ts),pop("clk",ts)])]
    if si==2:
        tk=at(0,"电视上看");e1,a1=tv("v",650,110,620,tk=tk,of=None,d=0)
        e1+=viewers("vw",[880],580,280);a1+=[F("vw0",0,8)]
        tk2=at(0,"真正比赛");me,ma=stad("m",100,200,900,tk=tk2);te,ta=tv("v",1260,190,520,tk=tk2,d=DLY)
        se,sa=sig("sg",1000,430,1300,440,tk2+6,DLY)
        return [(e1,a1),(me+te+se,ma+ta+sa)]
    if si==3:  # 主库 / 从库 / 主从复制：同一镜头里依次念到，三个标签依次出（减少章尾停留）
        me,ma=stad("m",410,150,1100)
        s1=(me,ma)
        t2=at(0,"真正改数据");tc=at(0,"原样抄一份")
        me2,ma2=stad("m",100,260,520,tk=t2);te,ta=tv("v",900,140,560,tk=t2);se,sa=sig("sg",620,390,960,400,t2+4,DLY)
        e2=me2+te+se+[term("zk",210,560,300,"主库",fs=56),term("ck",1030,620,300,"从库",fs=56),term("zc",660,760,600,"主从复制")]
        a2=ma2+ta+sa+[F(x,at(0,w)) for x,w in (("zk","主库"),("ck","从库"),("zc","主从复制"))]+[pop(x,at(0,w)) for x,w in (("zk","主库"),("ck","从库"),("zc","主从复制"))]
        return [s1,(e2,a2)]
    if si==4:  # 读写分离：赛场（主库）一直不变；电视（从库）一台变三台，观众越来越多、分到各台前面看
        TX=[240,810,1380]
        def layout(pre):
            me,ma=stad("m",680,90,560,ball="net");E_=me;A_=ma
            for j,x in enumerate(TX):
                te,ta=tv(f"v{j}",x,370,300,ball="net");E_+=te;A_+=ta
            return E_,A_
        e1,a1=layout("");tm=at(0,"看的人太多");tf=at(0,"分到各台从库")
        CX=[700,800,900,1000,1100,1190];DX=[230,340,830,950,1400,1510]
        e1+=viewers("w",CX,600,120);a1+=[F(f"w{j}",tm+j*3,6) for j in range(6)]+[mv(f"w{j}","x",tf+8,tf+24,CX[j],DX[j]) for j in range(6)]
        for j in (0,2):a1+=[F(f"v{j}tv",tf,8)]+[F(f"v{j}s{n}",tf,8) for n in ("fld","pol","lon","body","stand","kick","ball")]
        for j in (0,2):
            se,sa=sig(f"sg{j}",960,370,TX[j]+150,430,tf+6,20);e1+=se;a1+=sa
        e2,a2=stad("m",680,90,560,ball="net",dark=True)   # 观众再多赛场也不挤 → 读写分离 → 备份 / 主库坏了挑一台顶上（同一镜头，标签不用章尾停留）
        for j,x in enumerate(TX):
            te,ta=tv(f"v{j}",x,370,300,ball="net");e2+=te;a2+=ta
        X2=DX+[560,1180,1590];e2+=viewers("w",X2,600,120);tc=at(0,"观众再多")
        a2+=[F(f"w{j}",tc+(j-6)*4,6) for j in range(6,9)]+[F("rw",at(0,"读写分离")),pop("rw",at(0,"读写分离"))]
        tb=at(0,"备份");tx=at(0,"主库要是坏了");tu=at(0,"顶上")
        e2+=[term("rw",660,760,600,"读写分离"),I("bk","shield",1600,330,110),R("up",800,360,320,330,"#00000000",stroke=P['success'],radius=24)]
        a2+=[F("bk",tb),pop("bk",tb)]+lightsoff("m",tx)+[F("up",tu,8),mv("v1tv","scale",tu,tu+10,1,1.08),mv("v1tv","scale",tu+10,tu+20,1.08,1)]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 复制延迟：左邻居窗口欢呼，右你家电视球还在脚下；顶上小赛场发信号，邻居那条已到、你家这条圆点还在半路
        tg=at(1,"欢呼进球")
        ms,msa=stad("m",810,90,300,ball="net")
        nw=[I("nw","neighbor-window",180,200,420),I("ch","viewer-cheer",380,520,300),E("div","line",960,260,0,600,P['muted'])]
        te,ta=tv("v",1120,220,460,ball="foot");you=[I("you","viewer",1250,600,220)]
        s1,sa1=sig("sgn",880,250,520,290,0,12);s2,sa2=sig("sgy",1040,250,1330,330,6,200,stop=None)
        e1=ms+nw+s1+te+you+s2;a1=msa+sa1+ta+sa2+[mv("ch","opacity",0,tg,0,0),F("ch",tg,4),pop("ch",tg)]
        me,ma=stad("m",120,200,640,ball="net");te2,ta2=tv("v",1200,160,520,ball="foot");se,sa=sig("sg",760,360,1260,420,0,L[1]-2,stop=0.55,keep=True)
        e2=me+te2+se+[term("yc",660,740,600,"复制延迟")];a2=ma+ta2+sa+[F("yc",at(0,"复制延迟")),pop("yc",at(0,"复制延迟"))]
        tw=at(0,"刚改完昵称");tr=at(0,"马上去");to=at(0,"看到的就是旧的")
        me3,ma3=stad("m",120,120,520,ball="net");te3,ta3=tv("v",1240,100,440,ball="foot")
        pe,pa=phone("ph",720,320,480,[("新昵称",0),("旧昵称",to)])
        w1,wa1=sig("wr",900,520,500,340,tw,14,c=P['accent']);r1,ra1=sig("rd",1420,380,1060,520,tr,14)
        return [(e1,a1),(e2,a2),(me3+te3+pe+w1+r1,ma3+ta3+pa+wa1+ra1)]
    if si==6:  # 异步复制：主库改完马上说「好了」，不等信号到；断电时圆点死在半路，顶上来的从库没有这个球
        tk=at(2,"主库自己改完");th=at(2,"就说");me,ma=stad("m",120,180,700,tk=tk);te,ta=tv("v",1240,160,480,ball="foot")
        se,sa=sig("sg",820,360,1300,400,th+4,L[0]-th-6,stop=0.8,keep=True)
        e1=me+te+se+[bub("ok",380,96,"好了"),term("yb",660,740,600,"异步复制")];a1=ma+ta+sa+[F("ok",th,4),pop("ok",th),F("yb",at(2,"异步复制")),pop("yb",at(2,"异步复制"))]
        tx=at(0,"突然坏了");tu=at(0,"换上来的从库")
        me2,ma2=stad("m",120,180,700,ball="net",dark=True);te2,ta2=tv("v",1240,160,480,ball="foot");se2,sa2=sig("sg",820,360,1300,400,max(0,tx-30),60,stop=0.5)
        e2=me2+te2+se2+[R("up",1250,180,460,400,"#00000000",stroke=P['accent'],radius=24)];a2=ma2+ta2+sa2+lightsoff("m",tx)+[F("up",tu,8)]
        tb=at(0,"进了球");tc=at(0,"就断了")
        me3,ma3=stad("m",120,180,700,tk=tb);te3,ta3=tv("v",1240,160,480,ball="foot");se3,sa3=sig("sg",820,360,1300,400,tb+14,80,stop=0.45)
        e3=me3+te3+se3+[I("cr","crash",990,300,140)]+viewers("vw",[1380],620,200)
        a3=ma3+ta3+sa3+[mv("cr","opacity",0,tc,0,0),F("cr",tc,4),pop("cr",tc)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==7:  # 半同步复制：主库等至少一台从库回「收到」再说「好了」；等太久退回不等；「收到」≠ 已改好
        base=lambda dark=False,tk=None,ball="net":stad("m",120,180,700,tk=tk,ball=ball,dark=dark)
        tw=at(0,"先等");tr=at(0,"回一句");to=at(0,"再说")
        me,ma=base(tk=0 if False else None,ball="net");te,ta=tv("v",1240,160,480,ball="foot");se,sa=sig("sg",820,360,1300,400,tw,max(8,tr-tw))
        e1=me+te+se+[I("clk","clock",840,150,120),bub("ack",1380,96,"收到",P['success']),bub("ok",380,96,"好了")]
        a1=ma+ta+sa+[F("clk",tw),pop("clk",tw),F("ack",tr,4),pop("ack",tr),out("clk",to-4,4),F("ok",to,4),pop("ok",to)]
        tx=at(1,"突然坏了");th=at(1,"已经有这份改动")
        me2,ma2=base(dark=True);te2,ta2=tv("v",1240,160,480,ball="foot")
        e2=me2+te2+[bub("ack",1380,96,"收到",P['success']),I("has","shield",1600,500,120),term("bt",610,740,700,"半同步复制")]
        a2=ma2+ta2+lightsoff("m",tx)+[F("has",th),pop("has",th),F("bt",at(0,"半同步复制")),pop("bt",at(0,"半同步复制"))]
        tl=at(0,"等太久");tf=at(0,"退回不等")
        me3,ma3=base();te3,ta3=tv("v",1240,160,480,ball="foot");se3,sa3=sig("sg",820,360,1300,400,0,L[2]-2,stop=0.7,keep=True)
        e3=me3+te3+se3+[I("clk","clock",840,150,120),bub("ok",380,96,"好了")]
        a3=ma3+ta3+sa3+[mv("clk","scale",tl,tl+16,1,1.3),out("clk",tf,6),mv("ok","opacity",0,tf,0,0),F("ok",tf,4),pop("ok",tf)]
        tg=at(0,"读到旧数据")
        me4,ma4=stad("m",120,120,520,ball="net");te4,ta4=tv("v",1240,100,440,ball="foot");pe,pa=phone("ph",720,320,480,[("旧昵称",0)])
        r4,ra4=sig("rd",1420,380,1060,520,tg,14)
        e4=me4+te4+[bub("ack",1290,560,"收到",P['success'])]+pe+r4;a4=ma4+ta4+pa+ra4
        return [(e1,a1),(e2,a2),(e3,a3),(e4,a4)]
    if si==8:  # 办法：刚改完那一下，别看转播（电视变暗），直接去主库读 → 手机上是新昵称
        pe,pa=phone("ph",700,230,520,[("旧昵称",0)])
        s1=(pe+[T("q",1260,330,200,200,"？",160,P['accent'],align="center")],pa+[F("q",0,4)])
        tt=at(0,"别看转播");tm=at(0,"直接去主库读")
        me,ma=stad("m",120,200,640,ball="net");te,ta=tv("v",1300,160,440,ball="foot")
        pe2,pa2=phone("ph",740,360,480,[("旧昵称",0),("新昵称",tm+14)])
        r,ra=sig("rd",960,560,560,420,tm,14,c=P['success'])
        dimtv=[mv(i,"opacity",tt,tt+10,1,0.3) for i in [e_['id'] for e_ in te]]
        return [s1,(me+te+pe2+r,ma+ta+dimtv+pa2+ra)]
    if si==9:  # 回顾：读写分离全景；从库照着主库抄、慢一点；想看刚改的就去主库
        TX=[240,810,1380];me,ma=stad("m",680,90,560,ball="net");e1=me;a1=ma
        for j,x in enumerate(TX):
            te,ta=tv(f"v{j}",x,370,300,ball="net");e1+=te;a1+=ta
        e1+=viewers("w",[230,340,830,950,1400,1510],600,120)+[term("rw",660,760,600,"读写分离")];a1+=[F("rw",at(0,"读写分离")),pop("rw",at(0,"读写分离"))]
        tk=at(0,"照着主库抄");tm=at(0,"就去主库看")
        me2,ma2=stad("m",120,120,620,tk=tk);te2,ta2=tv("v",1240,100,440,tk=tk);se2,sa2=sig("sg",740,280,1300,300,tk+4,DLY)
        pe2,pa2=phone("ph",720,330,480,[("旧昵称",0),("新昵称",tm+12)]);r2,ra2=sig("rd",880,560,500,380,tm,12,c=P['success'])
        return [(e1,a1),(me2+te2+se2+pe2+r2,ma2+ta2+sa2+pa2+ra2)]

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
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《刚改的昵称，怎么又变回去了？》",hook="刚改的昵称又变回去了",episode=18,slug="db-replication",release="v0.23.0",draft=True,provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  series=None,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.15）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，按 EP.15 实测语速估，章尾 60 帧）；Knoll timeline 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json（map_timing.py，镜头边界直接按时间轴：章 = 本章首句起 → 下一章首句起，章间 0.6 s 已在音频里；只在全片结尾补 60 帧）。")+"术语标签（7 个，只用中文）念到时淡入（配音到后 words.json 词级对齐，宁晚勿早），完整显示 ≥60 帧；开场第 0 帧即封面画面（大字 + 手机昵称）；赛场 = 主库、电视 = 从库（同一套图层推后 delayFrames 播，Knoll 平移）、信号线与圆点由 Knoll 画（knollDraw）；画面无数字 / 比分 / 标志 / 英文，字幕照念「MySQL 8.4」。素材全部自绘。")
assets=dict(new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png") for n in ("stadium-field","stadium-poles","stadium-lights-on","stadium-lights-off","stadium-dim","player-body","player-leg-stand","player-leg-ready","player-leg-kick","kick-swoosh","ball","goal-net","tv-frame","viewer","viewer-cheer","neighbor-window","phone")],
  reuse=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc="EP.16/17 自绘，复用") for n in ("clock","shield","crash")])
meta["timingSource"]=("/workspace/share/ep18/timeline.json（Knoll）→ map_timing.py → timing.json" if not PROV else "字数估算 4.3 字/秒（make_timing.py → timeline.estimate.json → map_timing.py）；Knoll timeline.json + words.json 到后 sh realign.sh 直接重跑")
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面用 cover/ep18-*.png 定制设计，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])


