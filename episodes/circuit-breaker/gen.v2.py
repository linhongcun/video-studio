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
titles=["积分稍后到账","雪崩","电闸跳闸","试着合闸","关空调保冰箱","回顾"]
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
    def svc(i,x,y,label,c=None,w=300,fill=P['panel']): return R(i,x,y,w,110,fill,stroke=c or P['secondary'],radius=20,label=label,fontSize=44)
    def red(i,x,y,label,w=300): return R(i,x,y,w,110,"#3F1D24",stroke=P['danger'],radius=20,label=label,fontSize=44)
    def lbl(i,x,y,w,label,c=None,fs=36): return R(i,x,y,w,64,stroke=c or P['text2'],radius=14,label=label,fontSize=fs)
    CX=[160,560,960,1360]; CY=300; NAMES=["下单","库存","支付","积分"]
    def chain(p="c"):  # 一条下单链路：下单 → 库存 → 支付 → 积分
        return [svc(f"{p}{j}",CX[j],CY,n) for j,n in enumerate(NAMES)]+[E(f"{p}a{j}","line",CX[j]+300,CY+55,100,0,P['text2']) for j in range(3)]
    def labels(px,py,w):
        k=w/512; return [lbl(f"l{j}",int(px+k*(101+j*102)-50),py+w+8,100,n,fs=32) for j,n in enumerate(("空调","冰箱","灯","插座"))]
    LATE="积分 · 晚点到"
    if si==0:  # 积分稍后到账
        e1=[I("phone","phone",300,120,460),R("ok",300,600,460,96,stroke=P['success'],radius=48,label="支付成功",fontSize=44),
            R("late",1000,300,600,110,stroke=P['accent'],radius=20,label=LATE,fontSize=48),T("q",1000,520,600,100,"bug？",72,P['danger'],align="center")]
        a1=[F("phone",0),F("ok",at(0,"成功")),pop("ok",at(0,"成功")),F("late",at(1,"小字")),pop("late",at(1,"小字")),F("q",at(2,"这是")),pop("q",at(2,"这是"))]
        e2=[R("late",160,200,600,110,stroke=P['text2'],radius=20,label=LATE,fontSize=44),T("q",160,400,300,90,"bug？",64,P['danger'],align="center"),
            E("strike","line",170,445,280,0,P['danger']),tag("why",500,400,300,"设计如此",P['success'],40),
            R("core",1000,200,760,300,stroke=P['success'],radius=28),R("b1",1050,260,300,96,stroke=P['accent'],radius=48,label="下单",fontSize=44),R("b2",1400,260,300,96,stroke=P['success'],radius=48,label="支付",fontSize=44),
            T("ct",1000,400,760,60,"核心链路",44,P['success'],align="center"),T("ask",1180,600,400,140,"？",120,P['accent'],align="center")]
        a2=[F("late",0),F("q",0),F("strike",at(0,"其实不是")),draw("strike",at(0,"其实不是"),10),F("why",at(0,"其实不是")),pop("why",at(0,"其实不是")),
            F("core",at(1,"保护")),F("b1",at(1,"保护")),F("b2",at(1,"保护")),F("ct",at(1,"保护")),F("ask",at(1,"我们先看看")),pop("ask",at(1,"我们先看看"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 雪崩
        e1=chain()+[red("bad",CX[3],CY,"无响应"),I("tm","timer",CX[3]+80,CY+140,140)]+[I(f"g{j}","guest",160+(j%4)*80,520+(j//4)*100,70) for j in range(8)]+[tag("wait",500,560,360,"排队干等",P['text2'],40)]
        t0=at(0,"库存"); tq=at(1,"越积越多")
        a1=[F("c0",0),F("c1",t0),F("c2",at(0,"支付")),F("c3",at(0,"积分")),F("ca0",t0),F("ca1",at(0,"支付")),F("ca2",at(0,"积分")),F("bad",at(1,"卡住")),pop("bad",at(1,"卡住")),F("tm",at(1,"一直等"))]+[
            F(f"g{j}",at(1,"一直等")+j*5) for j in range(8)]+[F("wait",at(1,"一直等"))]
        e2=chain()+[red("bad",CX[3],CY,"无响应"),red("r2",CX[2],CY,"支付"),red("r1",CX[1],CY,"库存"),red("r0",CX[0],CY,"下单")]+[I(f"g{j}","guest",160+(j%4)*80,520+(j//4)*100,70) for j in range(8)]+[
            term("av",1000,600,440,"雪崩",P['danger'],64)]
        a2=[F("bad",0)]+[F(f"g{j}",0) for j in range(8)]+[F("r0",at(0,"拖垮")),F("r2",at(0,"付款")),F("r1",at(1,"一层层")),F("av",at(1,"一个服务")),pop("av",at(1,"一个服务"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 电闸跳闸
        bx,by,bw=200,140,560
        e1=[I("box","breaker-box",bx,by,bw),I("trip","breaker-tripped",bx,by,bw),I("so","socket",800,440,150),I("sp","spark",860,360,130)]+labels(bx,by,bw)+[
            I("fr","fridge",1080,220,300),I("lp","lamp",1440,300,240),tag("ok",1120,620,560,"其余各路：照常",P['success'],40)]
        tz=at(1,"跳下来")
        a1=[F("box",0),F("so",0)]+[F(f"l{j}",0) for j in range(4)]+[F("sp",at(1,"短路")),pop("sp",at(1,"短路")),F("trip",tz),out("box",tz,tz+8),out("sp",tz+20,tz+30),F("fr",at(1,"冰箱")),F("lp",at(1,"冰箱")),F("ok",at(1,"只断"))]
        e2=[svc("c0",160,300,"下单"),svc("c1",510,300,"库存",w=260),svc("c2",820,300,"支付",w=260),I("son","switch-on",1120,240,120,230),I("soff","switch-off",1120,240,120,230),red("c3",1440,300,"积分"),
            E("ln","line",1260,355,180,0,P['text2']),tag("nowait",160,560,460,"下单：不再干等",P['accent'],40),term("cb",1000,600,420,"熔断",P['danger'],64)]
        tt=at(0,"跳闸")
        a2=[F("c0",0),F("c1",0),F("c2",0),F("c3",0),F("son",0),F("ln",0),F("soff",tt),out("son",tt,tt+8),out("ln",tt,tt+8,0.2),F("nowait",at(0,"快速返回")),F("cb",at(0,"快速返回")),pop("cb",at(0,"快速返回"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 试着合闸
        e1=[I("soff","switch-off",300,220,160,280),I("tm","timer",560,240,200),R("probe",900,330,200,80,stroke=P['primary'],radius=40,label="试探",fontSize=36),
            R("rs",1360,300,300,110,stroke=P['text2'],radius=20,label="积分",fontSize=44),term("ho",900,600,420,"半开",P['primary'],64)]
        tp=at(1,"放一个")
        a1=[F("soff",0),F("rs",0),F("tm",at(0,"跳闸以后")),F("probe",at(1,"过一会儿")),mv("probe","x",tp,tp+30,900,1100),F("ho",at(1,"放一个")),pop("ho",at(1,"放一个"))]
        e2=[R("okc",160,160,700,300,stroke=P['success'],radius=24),I("son","switch-on",200,190,120,220),T("okt",360,250,480,60,"成功：合闸",44,P['success']),
            R("bdc",1000,160,760,300,stroke=P['danger'],radius=24),I("soff","switch-off",1040,190,120,220),T("bdt",1200,220,520,60,"失败：保持断开",44,P['danger']),I("tm","timer",1440,310,120),
            I("hg","hourglass",400,520,160),term("to",640,560,420,"超时",P['accent'],64),tag("give",1120,580,520,"到点就放弃",P['text2'],40)]
        a2=[F("okc",0),F("son",0),F("okt",at(0,"试成功")),F("bdc",0),F("soff",0),F("bdt",at(0,"还是失败")),F("tm",at(0,"还是失败")),
            F("hg",at(1,"另外")),F("to",at(1,"另外")),pop("to",at(1,"另外")),F("give",at(1,"另外"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 关空调保冰箱
        e1=[I("soff","switch-off",200,200,110,200),tag("todo",160,460,360,"订单：待办完",P['text2'],40),
            I("mt","meter",640,160,360),I("ac","aircon",1080,180,320),I("fr","fridge",1460,160,260),tag("act",1060,560,360,"空调：已关",P['text2'],40),tag("frt",1420,560,340,"冰箱：照常",P['success'],40)]
        to_=at(1,"关掉空调")
        a1=[F("soff",0),F("todo",0),F("mt",at(1,"用电紧张")),F("ac",0),F("fr",0),mv("ac","opacity",to_,to_+12,1,0.3),F("act",to_),F("frt",at(1,"用电紧张"))]
        e2=chain()+[I("f1","fridge",CX[1]+110,CY-150,80),I("f2","fridge",CX[2]+110,CY-150,80),I("ac","aircon",CX[3]+70,CY-130,160),
            E("byp","arrow",CX[0]+150,CY+190,700,50,P['success'],direction="r"),R("done",CX[2]+60,CY+260,520,96,stroke=P['success'],radius=48,label="订单已成交",fontSize=44),
            R("late",160,CY+260,560,96,stroke=P['accent'],radius=48,label=LATE,fontSize=44),term("dg",1360,700,380,"降级",P['accent'],64)]
        tk=at(0,"库存和支付")
        a2=[F("c0",0),F("c1",0),F("c2",0),F("c3",0),F("ca0",0),F("ca1",0),F("ca2",0),F("f1",tk),F("f2",tk),F("ac",at(0,"积分是空调")),mv("c3","opacity",at(0,"积分是空调"),at(0,"积分是空调")+12,1,0.35),
            draw("byp",at(1,"跳过"),15),F("late",at(1,"跳过")),F("done",at(1,"跳过")),pop("done",at(1,"跳过")),F("dg",at(1,"跳过")+30),pop("dg",at(1,"跳过")+30)]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=[term("cb",160,160,380,"熔断 · 止损",P['danger'],44),term("dg",600,160,380,"降级 · 兜底",P['accent'],44),
            queue("q",160,380,360),T("lq",160,560,360,50,"消息队列",40,P['primary'],align="center"),I("gate","gate",640,340,220),T("lg",560,580,380,50,"限流",40,P['success'],align="center"),
            I("tk","ticket",1040,350,200),T("lt",960,580,360,50,"幂等",40,P['accent'],align="center"),I("bx","breaker-tripped",1380,340,220),T("lb",1300,580,380,50,"熔断降级",40,P['danger'],align="center"),
            R("title",560,700,800,96,stroke=P['accent'],radius=48,label="四重防线",fontSize=52)]
        a1=[F("cb",0),F("dg",at(0,"降级负责")),mv("q","opacity",0,12,0,0.35),mv("q","opacity",at(1,"消息队列"),at(1,"消息队列")+12,0.35,1),F("lq",at(1,"消息队列")),
            mv("gate","opacity",0,12,0,0.35),mv("gate","opacity",at(1,"限流"),at(1,"限流")+12,0.35,1),F("lg",at(1,"限流")),mv("tk","opacity",0,12,0,0.35),mv("tk","opacity",at(1,"幂等"),at(1,"幂等")+12,0.35,1),F("lt",at(1,"幂等")),
            mv("bx","opacity",0,12,0,0.35),mv("bx","opacity",at(1,"熔断降级"),at(1,"熔断降级")+12,0.35,1),F("lb",at(1,"熔断降级")),F("title",at(1,"熔断降级")),pop("title",at(1,"熔断降级"))]
        e2=[I("phone","phone",300,120,460),R("ok",300,600,460,96,stroke=P['success'],radius=48,label="支付成功",fontSize=44),R("late",1000,360,600,110,stroke=P['accent'],radius=20,label=LATE,fontSize=48)]
        a2=[F("phone",0),F("ok",0),F("late",0),pop("late",0)]
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
   "脚本第 2 版：全片一条下单链路（下单 → 库存 → 支付 → 积分），积分服务卡住；画面不出现「猜你喜欢 / 推荐」。贯穿比喻：家里电闸——某一路短路只跳那一路（熔断），用电紧张先关空调保冰箱（降级：库存、支付 = 冰箱，积分 = 空调）。UI 小字「积分稍后到账」与旁白原话相同，画面写作「积分 · 晚点到」避免重复字幕。旁白术语：雪崩、熔断、降级（主讲），半开、超时（各一句），念到时上屏术语标签。画面不重复字幕句子（validate：术语白名单除外）。不出现具体数字。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/circuit-breaker/。新图标 breaker-box/breaker-tripped/switch-on/switch-off/spark/aircon/lamp/socket/meter 自绘无文字；复用 phone/ticket/server（第十一期）、gate（第十期）、queue/guest（第九期）、fridge（第七期）、timer（第八期）、hourglass（第三期）。branding v1.3.0：只有右上水印 + 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f) for n,f in (("phone","idempotency/assets/phone.svg"),("ticket","idempotency/assets/ticket.svg"),("gate","rate-limit/assets/gate.svg"),("queue","message-queue/assets/queue.svg"),("guest","message-queue/assets/guest.svg"),("fridge","browser-cache/assets/fridge.svg"),("timer","server-cache/assets/timer.svg"),("hourglass","dns/assets/hourglass.svg"))],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("breaker-box","breaker-tripped","switch-on","switch-off","spark","aircon","lamp","socket","meter")])
PS="breaker-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in [s for s in scenes if s['chapterId']=='breaker'][0]['shots']]
pl=sh["durationInFrames"]-30  # 暂定（第 2 版估算 timing）：插座那路已跳闸、冰箱/灯/「其余各路：照常」全显；正式 timing 到后写死
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="家里电闸：插座那一路跳闸，其余各路照常（冰箱、灯亮着）",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
