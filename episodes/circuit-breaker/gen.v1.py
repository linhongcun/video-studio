# EP.12《一个服务挂了，为什么整个 App 没崩？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
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
titles=["双十一的空白","雪崩","电闸跳闸","试着合闸","主动关空调","回顾"]
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
    def fly(i,a,x0,x1,n=24): return [F(i,a,6),mv(i,"x",a,a+n,x0,x1)]
    def svc(i,x,y,label,c=None,w=420): return R(i,x,y,w,110,stroke=c or P['secondary'],radius=20,label=label,fontSize=44)
    def lbl(i,x,y,w,label,c=None,fs=36): return R(i,x,y,w,64,stroke=c or P['text2'],radius=14,label=label,fontSize=fs)
    def labels(px,py,w):  # 电闸箱下方 4 路标签（与 breaker-box.svg 开关列对齐）
        k=w/512; return [lbl(f"l{j}",int(px+k*(101+j*102)-50),py+w+8,100,n,fs=32) for j,n in enumerate(("空调","冰箱","灯","插座"))]
    if si==0:  # 双十一的空白
        e1=[R("page",160,140,760,700,stroke=P['secondary'],radius=24),T("pt",200,170,680,50,"商品页",40,P['text2']),R("item",200,240,680,170,"#1F2937",stroke=P['muted'],radius=16),
            R("rec",200,440,680,230,"#111827",stroke=P['muted'],radius=16,label="猜你喜欢",fontSize=36),R("buy",200,700,680,96,stroke=P['accent'],radius=48,label="下单",fontSize=44),
            I("phone","phone",1180,140,440),R("ok",1180,600,440,96,stroke=P['success'],radius=48,label="支付成功",fontSize=44),T("q",1100,740,300,80,"bug？",60,P['danger'],align="center")]
        a1=[F("page",0),F("pt",0),F("item",0),F("rec",0),mv("rec","opacity",at(0,"一片空白"),at(0,"一片空白")+12,1,0.6),F("buy",at(1,"照样下单")),pop("buy",at(1,"照样下单")),
            F("phone",at(1,"付款")),F("ok",at(1,"成功")),pop("ok",at(1,"成功")),F("q",at(2,"bug")),pop("q",at(2,"bug"))]
        e2=[R("rec",160,200,620,230,"#111827",stroke=P['muted'],radius=16,label="猜你喜欢",fontSize=36),T("q",160,470,300,80,"bug？",60,P['danger'],align="center"),
            E("strike","line",170,510,280,0,P['danger']),tag("why",500,470,280,"设计如此",P['success'],40),
            R("core",1000,200,760,300,stroke=P['success'],radius=28),R("b1",1050,260,300,96,stroke=P['accent'],radius=48,label="下单",fontSize=44),R("b2",1400,260,300,96,stroke=P['success'],radius=48,label="支付",fontSize=44),
            T("ct",1000,400,760,60,"核心链路",44,P['success'],align="center"),T("ask",1180,600,400,140,"？",120,P['accent'],align="center")]
        a2=[F("rec",0),F("q",0),F("strike",at(0,"其实不是")),draw("strike",at(0,"其实不是"),10),F("why",at(0,"故意")),pop("why",at(0,"故意")),
            F("core",at(1,"保护")),F("b1",at(1,"保护")),F("b2",at(1,"保护")),F("ct",at(1,"最要紧")),F("ask",at(1,"会发生什么")),pop("ask",at(1,"会发生什么"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 雪崩
        e1=[svc("s3",700,200,"下单"),svc("s2",700,420,"商品页"),svc("s1",700,640,"推荐服务"),E("ar1","arrow",1140,450,300,50,P['text2'],direction="r",label="去问",fontSize=36),
            R("bad",700,640,420,110,"#3F1D24",stroke=P['danger'],radius=20,label="无响应",fontSize=44),I("tm","timer",1180,600,140)]
        a1=[F("s3",0),F("s2",0),F("s1",at(0,"推荐服务")),draw("ar1",at(0,"去问"),15),F("bad",at(1,"卡住")),pop("bad",at(1,"卡住")),F("tm",at(1,"一直等"))]
        e2=[svc("s3",700,200,"下单"),svc("s2",700,420,"商品页"),R("s1",700,640,420,110,"#3F1D24",stroke=P['danger'],radius=20,label="无响应",fontSize=44),
            R("r2",700,420,420,110,"#3F1D24",stroke=P['danger'],radius=20,label="商品页",fontSize=44),R("r3",700,200,420,110,"#3F1D24",stroke=P['danger'],radius=20,label="下单",fontSize=44)]+[
            I(f"g{j}","guest",160+(j%4)*110,330+(j//4)*120,90) for j in range(8)]+[term("av",1260,420,440,"雪崩",P['danger'],64)]
        tw=at(0,"越积越多")
        a2=[F("s3",0),F("s2",0),F("s1",0)]+[F(f"g{j}",tw+j*6) for j in range(8)]+[F("r2",at(0,"跟着卡住")),F("r3",at(0,"拖慢")),F("av",at(1,"雪崩")),pop("av",at(1,"雪崩"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 电闸跳闸
        bx,by,bw=200,140,560
        e1=[I("box","breaker-box",bx,by,bw),I("trip","breaker-tripped",bx,by,bw),I("so","socket",800,440,150),I("sp","spark",860,360,130)]+labels(bx,by,bw)+[
            I("fr","fridge",1080,220,300),I("lp","lamp",1440,300,240),tag("ok",1120,620,560,"其余各路：照常",P['success'],40)]
        tz=at(1,"跳下来")
        a1=[F("box",0),F("so",0)]+[F(f"l{j}",0) for j in range(4)]+[F("sp",at(1,"短路")),pop("sp",at(1,"短路")),F("trip",tz),out("box",tz,tz+8),out("sp",tz+20,tz+30),F("fr",at(1,"冰箱")),F("lp",at(1,"冰箱")),F("ok",at(1,"照常"))]
        e2=[svc("pg",160,300,"商品页",w=380),I("son","switch-on",700,250,140,240),I("soff","switch-off",700,250,140,240),R("rs",1000,300,420,110,"#3F1D24",stroke=P['danger'],radius=20,label="推荐服务",fontSize=44),
            E("ln1","line",540,355,160,0,P['text2']),E("ln2","line",840,355,160,0,P['text2']),R("def",160,520,380,90,stroke=P['accent'],radius=20,label="默认推荐",fontSize=40),
            term("cb",1000,560,420,"熔断",P['danger'],64)]
        tt=at(0,"跳闸")
        a2=[F("pg",0),F("son",0),F("rs",0),F("ln1",0),F("ln2",0),F("soff",tt),out("son",tt,tt+8),out("ln2",tt,tt+8,0.2),F("def",at(0,"默认结果")),pop("def",at(0,"默认结果")),F("cb",at(1,"熔断")),pop("cb",at(1,"熔断"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 试着合闸
        e1=[I("soff","switch-off",300,220,160,280),I("tm","timer",560,240,200),R("probe",900,330,200,80,stroke=P['primary'],radius=40,label="试探",fontSize=36),
            R("rs",1340,300,420,110,stroke=P['text2'],radius=20,label="推荐服务",fontSize=44),term("ho",900,600,420,"半开",P['primary'],64)]
        tp=at(1,"放一个")
        a1=[F("soff",0),F("rs",0),F("tm",at(1,"过一会儿")),F("probe",tp),mv("probe","x",tp,tp+30,900,1100),F("ho",at(1,"这个状态")),pop("ho",at(1,"这个状态"))]
        e2=[R("okc",160,160,700,300,stroke=P['success'],radius=24),I("son","switch-on",200,190,120,220),T("okt",360,250,480,60,"成功：合闸",44,P['success']),
            R("bdc",1000,160,760,300,stroke=P['danger'],radius=24),I("soff","switch-off",1040,190,120,220),T("bdt",1200,220,520,60,"失败：保持断开",44,P['danger']),I("tm","timer",1440,310,120),
            I("hg","hourglass",400,520,160),term("to",640,560,420,"超时",P['accent'],64),tag("give",1120,580,520,"到点就放弃",P['text2'],40)]
        a2=[F("okc",0),F("son",at(0,"试成功")),F("okt",at(0,"合上闸")),F("bdc",at(0,"还是失败")),F("soff",at(0,"还是失败")),F("bdt",at(0,"继续断开")),F("tm",at(0,"再试")),
            F("hg",at(1,"等待上限")),F("to",at(1,"超时")),pop("to",at(1,"超时")),F("give",at(1,"死等"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 主动关空调
        e1=[term("cb",160,180,360,"熔断",P['danger'],52),I("soff","switch-off",200,320,110,200),T("p1",160,560,360,50,"出事后才断",40,P['text2'],align="center"),
            I("mt","meter",640,160,360),I("ac","aircon",1080,180,320),I("fr","fridge",1460,160,260),tag("act",1060,560,360,"空调：已关",P['text2'],40),tag("frt",1420,560,340,"冰箱：照常",P['success'],40)]
        to_=at(1,"关掉空调")
        a1=[F("cb",0),F("soff",0),F("p1",at(0,"出了问题")),F("mt",at(1,"用电紧张")),F("ac",0),F("fr",0),mv("ac","opacity",to_,to_+12,1,0.3),F("act",to_),F("frt",at(1,"保住冰箱"))]
        e2=[R("page",160,140,700,700,stroke=P['secondary'],radius=24),R("rec",200,200,300,90,stroke=P['muted'],radius=16,label="推荐",fontSize=40),R("cm",520,200,300,90,stroke=P['muted'],radius=16,label="评论",fontSize=40),
            R("hot",200,320,620,260,"#111827",stroke=P['accent'],radius=16,label="热销榜（固定）",fontSize=40),R("o1",1100,240,560,110,stroke=P['success'],radius=20,label="下单",fontSize=48),R("o2",1100,420,560,110,stroke=P['success'],radius=20,label="支付",fontSize=48),
            E("res","arrow",860,380,240,50,P['success'],direction="r"),term("dg",1100,640,420,"降级",P['accent'],64)]
        toff=at(0,"关掉")
        a2=[F("page",0),F("rec",0),F("cm",0),mv("rec","opacity",toff,toff+12,1,0.3),mv("cm","opacity",toff,toff+12,1,0.3),F("hot",at(0,"固定榜单")),F("o1",0),F("o2",0),draw("res",at(0,"力气"),15),F("dg",at(1,"降级")),pop("dg",at(1,"降级"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=[term("cb",160,160,380,"熔断 · 被动",P['danger'],44),term("dg",600,160,380,"降级 · 主动",P['accent'],44),
            queue("q",160,380,360),T("lq",160,560,360,50,"消息队列",40,P['primary'],align="center"),I("gate","gate",640,340,220),T("lg",560,580,380,50,"限流",40,P['success'],align="center"),
            I("tk","ticket",1040,350,200),T("lt",960,580,360,50,"幂等",40,P['accent'],align="center"),I("bx","breaker-tripped",1380,340,220),T("lb",1300,580,380,50,"熔断降级",40,P['danger'],align="center"),
            R("title",560,700,800,96,stroke=P['accent'],radius=48,label="四重防线",fontSize=52)]
        a1=[F("cb",at(0,"熔断")),F("dg",at(0,"降级")),mv("q","opacity",0,12,0,0.35),mv("q","opacity",at(1,"消息队列"),at(1,"消息队列")+12,0.35,1),F("lq",at(1,"消息队列")),
            mv("gate","opacity",0,12,0,0.35),mv("gate","opacity",at(1,"限流"),at(1,"限流")+12,0.35,1),F("lg",at(1,"限流")),mv("tk","opacity",0,12,0,0.35),mv("tk","opacity",at(1,"幂等"),at(1,"幂等")+12,0.35,1),F("lt",at(1,"幂等")),
            mv("bx","opacity",0,12,0,0.35),mv("bx","opacity",at(1,"熔断降级"),at(1,"熔断降级")+12,0.35,1),F("lb",at(1,"熔断降级")),F("title",at(1,"全站都崩")),pop("title",at(1,"全站都崩"))]
        e2=[R("page",160,140,700,700,stroke=P['secondary'],radius=24),R("rec",200,200,620,230,"#111827",stroke=P['muted'],radius=16,label="推荐位：空",fontSize=40),R("buy",200,480,620,96,stroke=P['accent'],radius=48,label="下单",fontSize=44),
            I("phone","phone",1180,140,440),R("ok",1180,600,440,96,stroke=P['success'],radius=48,label="支付成功",fontSize=44)]
        a2=[F("page",0),F("rec",0),F("buy",0),F("phone",at(0,"就知道")),F("ok",at(0,"就知道")),pop("ok",at(0,"就知道"))]
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
meta=dict(title="《一个服务挂了，为什么整个 App 没崩？》",episode=12,slug="circuit-breaker",release="v0.17.0",series="扛住高峰 04",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  tts=dict(note="Nolan：送 TTS 的旁白把「这是出 bug 了吗？」读成「这是出故障了吗？」；字幕保留「bug」原句。镜头 ttsText = 送 TTS 文字，narration/subtitles = 字幕原文",replace={"这是出 bug 了吗？":"这是出故障了吗？"}),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句间 0.28 秒，每章尾留 60 帧；按 TTS 文字计字）。配音到后：sh run.sh（默认 /workspace/share/ep12-timing.json）→ map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "贯穿比喻：家里电闸——某一路短路只跳那一路（熔断），用电紧张先关空调保冰箱（降级）。旁白术语：雪崩、熔断、降级（主讲），半开、超时（各一句），念到时上屏术语标签。画面不重复字幕句子（validate：术语白名单除外）。不出现具体数字。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/circuit-breaker/。新图标 breaker-box/breaker-tripped/switch-on/switch-off/spark/aircon/lamp/socket/meter 自绘无文字；复用 phone/ticket/server（第十一期）、gate（第十期）、queue/guest（第九期）、fridge（第七期）、timer（第八期）、hourglass（第三期）。branding v1.3.0：只有右上水印 + 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f) for n,f in (("phone","idempotency/assets/phone.svg"),("ticket","idempotency/assets/ticket.svg"),("gate","rate-limit/assets/gate.svg"),("queue","message-queue/assets/queue.svg"),("guest","message-queue/assets/guest.svg"),("fridge","browser-cache/assets/fridge.svg"),("timer","server-cache/assets/timer.svg"),("hourglass","dns/assets/hourglass.svg"))],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("breaker-box","breaker-tripped","switch-on","switch-off","spark","aircon","lamp","socket","meter")])
PS="breaker-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in [s for s in scenes if s['chapterId']=='breaker'][0]['shots']]
pl=252  # 写死：breaker-1 局部 252（ep12 正式 timing，breaker-1 起点 1298（hook-1 +40、avalanche-2 +47 停留后）→ 全局 1550）——插座那路已跳闸、冰箱/灯/「其余各路：照常」全显
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="家里电闸：插座那一路跳闸，其余各路照常（冰箱、灯亮着）",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
