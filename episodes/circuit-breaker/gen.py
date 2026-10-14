# EP.13《一个服务出故障，为什么整个网站没跟着崩？》（熔断）分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts
src=open(SCRIPT).read()
narr=re.findall(r'- 旁白：(.+)',src); assert len(narr)==6
CNT=[int(x) for x in re.findall(r'- 字数：(\d+)',src)]
def cnt(s): return len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",success="#22C55E",accent="#F59E0B",danger="#F87171")
def R(i,x,y,w,h,c=P['panel'],**k): return dict(id=i,type="rect",x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def T(i,x,y,w,h,t,fs=40,c=P['text'],**k): return dict(id=i,type="text",x=x,y=y,w=w,h=h,text=t,fontSize=fs,**{"color":c,"reuse":False,**k})
def A(i,name,x,y,w,h,**k): return dict(id=i,type="image",asset=f"assets/{name}.svg",x=x,y=y,w=w,h=h,**{"color":None,"reuse":False,**k})
def E(i,ty,x,y,w,h,c,**k): return dict(id=i,type=ty,x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def fade(i,a=0,b=12): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=0),dict(frame=b,value=1)],easing="easeOut")
def out(i,a,b,v=0): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=1),dict(frame=b,value=v)],easing="easeIn")
def mv(i,p,a,b,va,vb,e="easeInOut"): return dict(elementId=i,property=p,keyframes=[dict(frame=a,value=va),dict(frame=b,value=vb)],easing=e)
def draw(i,a,n=15): return mv(i,"drawProgress",a,a+n,0,1,"easeOut")
def F(i,a,n=12): return fade(i,a,a+n)
def pop(i,a): return mv(i,"scale",a,a+12,0,1,"spring")
titles=["没跟着崩","雪崩","电闸跳闸","关闭是通，打开是断","试着合闸","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
CARD=dict(stroke=P['secondary'],radius=16,fontSize=36)
def card(i,x,y,w,h,label,**k): return R(i,x,y,w,h,**{**CARD,"label":label,**k})
def browser(x,y,w=360,h=220): return card("browser",x,y,w,h,"浏览器",reuse=True)
def server(i,x,y,w,h,label): return card(i,x,y,w,h,label,reuse=True,note="统一服务器卡片（同浏览器样式，无窗口圆点，标签 36px）")
TM=json.load(open(HERE/"timing.json"))
PARTS=[]
def AT(si,_k,phrase):
    # 自动定位短语所在的镜头（本章内唯一），返回该镜头内的相对帧
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def AEND(si,k): return TM[KEY(si,k)]["audioFrames"]
def I(i,name,x,y,w,h=None,**k): return A(i,name,x,y,w,w if h is None else h,**k)
def queue(i,x,y,w=1000,**k): return A(i,"queue",x,y,w,round(w*0.38),**k)
def term(i,x,y,w,label,c=None,fs=48): return R(i,x,y,w,96,stroke=c or P['primary'],radius=48,label=label,fontSize=fs)
def tag(i,x,y,w,label,c=None,fs=40): return R(i,x,y,w,84,stroke=c or P['text2'],radius=16,label=label,fontSize=fs)
def crowd(p,x,y,n,cols,step=100,s=90): return [I(f"{p}{j}","guest",x+(j%cols)*step,y+(j//cols)*(step+10),s) for j in range(n)]
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    def red(i,x,y,label,w=340,h=120,fs=44): return R(i,x,y,w,h,"#3F1D24",stroke=P['danger'],radius=20,label=label,fontSize=fs)
    def svc(i,x,y,label,w=340,h=120,c=None,fs=44): return R(i,x,y,w,h,P['panel'],stroke=c or P['success'],radius=20,label=label,fontSize=fs)
    GX=[1000,1400];GY=[200,380];GN=[["商品服务","订单服务"],["运费险服务","支付服务"]]
    def grid(): return [svc(f"s{r}{c}",GX[c],GY[r],GN[r][c],360) for r in range(2) for c in range(2)]
    GRID=["s00","s01","s10","s11"]
    def labels(px,py,w):
        k=w/512; return [R(f"l{j}",int(px+k*(101+j*102)-50),py+w+8,100,64,stroke=P['text2'],radius=14,label=n,fontSize=32) for j,n in enumerate(("客厅","卧室","厨房","插座"))]
    def checkout(x,y,w=560,h=620,p="co"):  # 结算页：商品 / 运费险 / 「提交订单」按钮（无金额）
        return [R(p,x,y,w,h,P['panel'],stroke=P['secondary'],radius=36),T(p+"h",x,y+30,w,56,"结算页",44,P['text2'],align="center"),
                R(p+"r1",x+50,y+120,w-100,96,stroke=P['text2'],radius=18,label="商品",fontSize=40),R(p+"fx",x+50,y+240,w-100,96,stroke=P['accent'],radius=18,label="运费险",fontSize=40),
                R(p+"btn",x+50,y+h-150,w-100,100,"#14532D",stroke=P['success'],radius=50,label="提交订单",fontSize=44)]
    def CO(p="co"): return [p,p+"h",p+"r1",p+"fx",p+"btn"]
    def gap(x,y,w=560,p="co"):  # 运费险一行消失后的灰色虚线空框（同位置同尺寸，无文字），提示「这里原来有一项」
        return R(p+"gap",x+50,y+240,w-100,96,P['panel'],stroke=P['muted'],radius=18,dash=True,note="dashed outline, no text")
    if si==0:  # 没跟着崩
        e1=checkout(200,140)+[gap(200,140)]+grid()+[red("bad",GX[0],GY[1],"运费险服务",360),I("sp","spark",GX[0]+300,GY[1]+70,90),
            tag("ok",1000,600,760,"其余服务：照常",P['success'],40)]
        tb=at(0,"出了故障")
        tk=at(1,"照样能下单")
        a1=[F(x,0) for x in CO()]+[F(x,at(0,"运费险服务")) for x in GRID]+[
            F("bad",tb),pop("bad",tb),F("sp",tb),out("cofx",tk,tk+12),F("cogap",tk,12),mv("cobtn","scale",tk+6,tk+18,1.12,1,"spring"),F("ok",tk)]
        e2=grid()+[red("bad",GX[0],GY[1],"运费险服务",360),T("why",160,300,760,120,"为什么没崩？",80,P['accent'],align="center"),T("ask",1180,620,400,140,"？",120,P['accent'],align="center")]
        a2=[F(x,0) for x in GRID]+[F("bad",0),F("why",0),pop("why",0),F("ask",at(1,"什么都不做")),pop("ask",at(1,"什么都不做"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 雪崩 / 级联故障
        e1=[svc("od",200,300,"结算页",400,130,P['secondary'],48),E("ln","line",600,365,560,0,P['text2']),svc("iv",1160,300,"运费险服务",400,130,P['secondary'],48),
            R("bub",680,170,360,90,stroke=P['text2'],radius=45,label="加运费险吗？",fontSize=44),red("ivr",1160,300,"运费险服务",400,130,48),I("tm","timer",420,500,140)]
        a1=[F("od",0),F("ln",at(0,"顺带去问")),F("iv",at(0,"顺带去问")),F("bub",at(0,"这一单")),pop("bub",at(0,"这一单")),F("ivr",at(1,"出了故障")),out("bub",at(1,"迟迟"),at(1,"迟迟")+10),F("tm",at(1,"一直等"))]
        e2=[red("iv",1160,140,"运费险服务",400,120),svc("od",640,140,"订单服务",400,120,P['secondary']),svc("pay",640,400,"支付服务",400,120,P['secondary']),red("odr",640,140,"订单服务",400,120),red("payr",640,400,"支付服务",400,120)]+[
            I(f"g{j}","guest",160+(j%4)*90,160+(j//4)*100,76) for j in range(12)]+[term("av",1160,600,400,"雪崩",P['danger'],64),term("cf",1160,730,400,"级联故障",P['danger'],48)]
        tq=at(0,"越积越多");ta=at(1,"这就叫雪崩");tc=at(1,"也叫级联故障")
        a2=[F("iv",0),F("od",0),F("pay",0)]+[F(f"g{j}",j*8) for j in range(12)]+[F("odr",at(0,"拖垮")),F("payr",at(0,"支付")),F("av",ta),pop("av",ta),F("cf",tc),pop("cf",tc)]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 超时 → 电闸 → 熔断
        e1=[I(f"g{j}","guest",220+j*200,380,110) for j in range(4)]+[I(f"h{j}","hourglass",235+j*200,240,80) for j in range(4)]+[
            red("iv",1300,380,"运费险服务",400,120),term("to",220,620,360,"超时",P['accent'],64),tag("wait",660,630,360,"仍要等满",P['text2'],40)]
        tt=at(0,"这叫超时")
        a1=[F(f"g{j}",0) for j in range(4)]+[F("iv",0)]+[F(f"h{j}",at(0,"等待上限")+j*6) for j in range(4)]+[F("to",tt),pop("to",tt),F("wait",at(1,"超时要有"))]
        bx,by,bw=200,140,560
        e2=[I("box","breaker-box",bx,by,bw),I("trip","breaker-tripped",bx,by,bw),I("so","socket",800,440,150),I("sp","spark",860,360,130)]+labels(bx,by,bw)+[
            I("fr","tv",1060,200,320),I("lp","lamp",1440,300,240),tag("ok",1120,620,560,"其余各路：照常",P['success'],40)]
        tz=at(0,"跳下来")
        a2=[F("box",0),F("so",0)]+[F(f"l{j}",0) for j in range(4)]+[F("fr",0),F("lp",0),F("sp",at(0,"短路")),pop("sp",at(0,"短路")),F("trip",tz),out("box",tz,tz+8),out("sp",tz+8,tz+16),F("ok",at(0,"短路"))]
        e3=[svc("od",160,240,"结算页",360,120,P['secondary']),E("lna","line",520,300,120,0,P['text2']),I("son","switch-on",640,190,100,190),I("soff","switch-off",640,190,100,190),
            E("lnb","line",740,300,140,0,P['text2']),red("iv",880,240,"运费险服务",360,120),
            R("cnt",1300,200,460,200,stroke=P['accent'],radius=20),T("c1",1300,225,460,60,"最近 100 次（示例）",40,P['text'],align="center"),T("c2",1300,305,460,60,"失败 50%（示例）",40,P['danger'],align="center"),
            E("back","arrow",520,430,360,50,P['accent'],direction="l"),R("ret",160,500,300,96,stroke=P['accent'],radius=48,label="马上返回",fontSize=40),R("btn",480,500,300,96,"#14532D",stroke=P['success'],radius=48,label="提交订单",fontSize=40),
            term("cb",880,520,360,"熔断",P['danger'],64),R("both",500,720,920,100,stroke=P['primary'],radius=50,label="熔断不能代替超时",fontSize=52)]
        tj=at(0,"就跳闸");tr=at(0,"直接返回");tc=at(1,"这叫熔断");tm=at(2,"熔断不能代替超时")
        a3=[F("od",0),F("lna",0),F("son",0),F("lnb",0),F("iv",0),F("cnt",at(0,"最近")),F("c1",at(0,"最近")),F("c2",at(0,"一半")),
            F("soff",tj),out("son",tj,tj+8),out("lnb",tj,tj+8,0.2),draw("back",tr,15),F("ret",tr+8),pop("ret",tr+8),F("btn",tr+20),pop("btn",tr+20),F("cb",tc),pop("cb",tc),F("both",tm),pop("both",tm)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==3:  # 关闭是通，打开是断
        e=[T("hd",160,120,1600,80,"熔断器 · 反直觉",60,P['accent'],align="center"),
           R("c0",160,230,500,420,stroke=P['success'],radius=28),I("son","switch-on",230,280,120,230),I("lp1","lamp",420,300,200),
           R("c1",710,230,500,420,stroke=P['danger'],radius=28),I("soff","switch-off",780,280,120,230),I("lp2","lamp",970,300,200),
           R("c2",1260,230,500,420,stroke=P['muted'],radius=28),T("q3",1260,360,500,160,"？",120,P['text2'],align="center"),
           term("t0",160,690,500,"关闭 · 正常调用",P['success'],44),term("t1",710,690,500,"打开 · 拒绝请求",P['danger'],44)]
        t0=at(2,"「关闭」");t1=at(2,"「打开」")
        a=[F("hd",0),pop("hd",0),F("c0",at(1,"三种状态")),F("c1",at(1,"三种状态")),F("c2",at(1,"三种状态")),F("q3",at(1,"三种状态")),F("son",at(1,"电闸合上")),F("lp1",at(1,"才通电")),
           F("soff",t1),F("lp2",t1),mv("lp2","opacity",t1,t1+12,0,0.3),F("t0",t0),pop("t0",t0),F("t1",t1),pop("t1",t1)]
        a=[x for x in a if not(x['elementId']=="lp2" and x['keyframes'][-1]['value']==1)]
        return [(e,a)]
    if si==4:  # 半开
        e1=[I("soff","switch-off",200,200,130,250),I("tm","timer",420,220,200),T("ts",380,440,300,60,"30 秒（示例）",40,P['accent'],align="center"),
            red("iv",1360,260,"运费险服务",360,120)]+[R(f"pr{j}",760,250+j*50,90,36,P['primary'],radius=18) for j in range(2)]+[term("ho",760,620,520,"半开 · 少量试探",P['primary'],48)]
        tp=at(1,"再放少量");th=at(1,"这个状态叫半开")
        a1=[F("soff",0),F("iv",0),F("tm",at(1,"断开三十秒")),F("ts",at(1,"断开三十秒"))]+[x for j in range(2) for x in (F(f"pr{j}",tp+j*10),mv(f"pr{j}","x",tp+j*10,tp+j*10+40,760,1240))]+[F("ho",th),pop("ho",th)]
        e2=[R("okc",160,160,760,420,stroke=P['success'],radius=24),I("son","switch-on",220,220,130,250),T("okt",400,300,500,60,"成功：回到关闭",44,P['success']),
            R("bdc",1000,160,760,420,stroke=P['danger'],radius=24),I("soff","switch-off",1060,220,130,250),T("bdt",1240,260,500,60,"失败：回到打开",44,P['danger']),I("tm","timer",1420,360,140),
            term("ho",660,660,600,"半开 · 两种结果",P['primary'],44)]
        a2=[F("ho",0),F("okc",0),F("son",at(0,"试成功")),F("okt",at(0,"试成功")),F("bdc",at(0,"还是失败")),F("soff",at(0,"还是失败")),F("bdt",at(0,"还是失败")),F("tm",at(0,"过一阵"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=checkout(200,140)+[gap(200,140),I("soff","switch-off",1000,200,120,230),red("iv",1200,250,"运费险服务",400,120),
            term("st",1000,480,600,"熔断：暂停调用",P['danger'],44),R("dgl",1000,620,600,96,stroke=P['accent'],radius=48,label="降级 · 上期",fontSize=44)]
        tl=at(0,"少显示");tp=at(0,"下单付款照常")
        a1=[F(x,0) for x in CO()]+[F("soff",0),F("iv",0),F("st",0),pop("st",0),out("cofx",tl,tl+12),F("cogap",tl,12),F("dgl",at(0,"上期讲的降级")),pop("dgl",at(0,"上期讲的降级")),mv("cobtn","scale",tp,tp+12,1.12,1,"spring")]
        e2=[term("k0",160,140,500,"限流：管流量",P['success'],44),term("k1",710,140,500,"熔断：隔离故障",P['danger'],44),term("k2",1260,140,500,"降级：保核心",P['accent'],44),
            queue("q",160,340,300),T("lq",160,500,300,50,"消息队列",40,P['primary'],align="center"),I("gate","gate",540,300,200),T("lg",500,520,280,50,"限流",40,P['success'],align="center"),
            I("tk","ticket",880,310,180),T("lt",830,520,280,50,"幂等",40,P['accent'],align="center"),I("fz","shield",1200,300,200),T("lf",1160,520,280,50,"降级",40,P['accent'],align="center"),
            I("bx","breaker-tripped",1500,300,200),T("lb",1460,520,280,50,"熔断",40,P['danger'],align="center"),R("five",560,640,800,96,stroke=P['accent'],radius=48,label="第五招：熔断",fontSize=52)]+grid()+[red("bad",GX[0],GY[1],"运费险服务",360),I("cut","switch-off",880,330,90,170)]
        t2=at(1,"一个服务挂了")
        PH=["k0","k1","k2","q","lq","gate","lg","tk","lt","fz","lf","bx","lb","five"]
        a2=[F("k0",at(0,"限流管")),F("k1",at(0,"限流管")+8),F("k2",at(0,"限流管")+16)]+[F(x,at(0,"第五招")) for x in ("q","lq","gate","lg","tk","lt","fz","lf")]+[F("bx",at(0,"第五招")+10),F("lb",at(0,"第五招")+10),F("five",at(0,"第五招")+10),pop("five",at(0,"第五招")+10)]+[
            out(x,t2,t2+10) for x in PH]+[F(x,t2+10) for x in GRID]+[F("bad",t2+10),F("cut",t2+10)]
        return [(e1,a1),(e2,a2)]
def subs(t,L,si,k):
    S=sentences(t);q=TM[KEY(si,k)]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
            else: m.append(c)
        tot=sum(cnt(x) for x in m);acc=0
        for c in m: res.append({"text":c.strip().rstrip('，；：。？'),"from":round(30*(qq["start"]+qq["dur"]*acc/tot))});acc+=cnt(c)
    for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    return res
scenes=[];g=0;nshot=0;CLAMP=[]
for si,s in enumerate(narr):
    S=sentences(s);parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S) and "".join(parts).replace(' ','')==s.replace(' ','')
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
        shots.append(dict(id=KEY(si,k),chapterId=ids[si],**{"from":f},durationInFrames=l,narration=p,**({"ttsText":tts(p)} if tts(p)!=p else {}),subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),shots=shots));g+=D
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《一个服务出故障，为什么整个网站没跟着崩？》",episode=13,slug="circuit-breaker",release="v0.18.0",series="扛住高峰 05",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  tts=dict(note="第十三期：送 TTS 文字 = 字幕原文（读音表无替换）",replace={}),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句间 0.28 秒，每章尾留 60 帧；按 TTS 文字计字）。配音到后：sh run.sh（默认 /workspace/share/ep13-timing.json）→ map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "第十三期（熔断，v0.18.0，脚本 v2 运费险）：主线 结算页同步调用运费险服务（弱依赖），运费险服务持续故障；结算页卡片：商品 / 运费险 /「提交订单」，熔断后「运费险」一行消失、「提交订单」照常（上期降级一句带过）。画面禁用词见 validate BAN（上期主线词、旧稿快速失败提示语、旧稿服务名）。⚠ timing 为估算（按 Knoll EP.13 旧稿实测校准），Knoll 新配音到后必须 sh run.sh <新 timing> 重对、重算停留和封面帧。雪崩（级联故障）→ 超时（仍要等满）→ 家里电闸跳闸 → 熔断（示例：最近 100 次失败 50% 跳闸，快速失败：马上返回，结算页「提交订单」照常）+「熔断不能代替超时」→ 三种状态（关闭 = 电闸合上通电 = 正常调用；打开 = 跳闸 = 拒绝请求；反直觉）→ 半开（示例：断开 30 秒，放少量试探；成功回到关闭 / 失败回到打开）→ 回顾（熔断后结算页少显示「运费险」一项 = 上期降级，下单付款照常；限流管流量 / 熔断隔离故障 / 降级保核心；第五招）。示例参数上屏都标「示例」。旁白术语：雪崩、级联故障、超时、熔断、关闭、打开、半开，念到时上屏术语标签（锚在点名的那句）。画面不重复字幕句子（validate：术语白名单 + LABEL_OK 除外）。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/circuit-breaker/。复用 EP.12 第 3 版电闸箱 / 跳闸 / 开关 / 火花 / 灯 / 插座 / 计时器；新图标 tv / shield 自绘无文字（第十三期家里电闸各路标 客厅 / 卧室 / 厨房 / 插座，电器用台灯和电视）；复用 phone/ticket（第十一期）、gate（第十期）、queue/guest（第九期）、hourglass（第三期）。branding v1.3.0：只有右上水印 + 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f) for n,f in (("ticket","idempotency/assets/ticket.svg"),("gate","rate-limit/assets/gate.svg"),("queue","message-queue/assets/queue.svg"),("guest","message-queue/assets/guest.svg"),("timer","server-cache/assets/timer.svg"),("hourglass","dns/assets/hourglass.svg"))+tuple((n,"circuit-breaker/ep12-old（EP.12 第 3 版）") for n in ("breaker-box","breaker-tripped","switch-on","switch-off","spark","lamp","socket"))],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("tv","shield")])
PS="breaker-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in scenes[2]['shots']]
pl=196  # 写死（Knoll EP13 新稿 timing 08:0x + HOLDS）：breaker-2 共 204 帧，跳闸 176–188、火花 192 消失，之后插座那路已跳、其余各路 / 电视 / 台灯 /「其余各路：照常」（129 起全显）都在；全局 1541+196=1737
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="家里电闸：插座那一路跳闸，其余各路照常（电视、台灯照常亮）",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
