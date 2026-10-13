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
titles=["两个价不一样","雪崩","电闸跳闸","试着合闸","关空调保冰箱","回顾"]
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
    def red(i,x,y,label,w=300): return R(i,x,y,w,110,"#3F1D24",stroke=P['danger'],radius=20,label=label,fontSize=44)
    # 主线：「到手价计算」父方块 → 三个子服务（商品价格 / 优惠券 / 红包），肘形连线
    KX=[160,770,1380]; KW=380; KY=520; KN=["商品价格","优惠券","红包"]
    def tree(c=None):
        c=c or P['secondary']
        return [R("p",660,130,600,110,P['panel'],stroke=c,radius=20,label="到手价计算",fontSize=48),
                E("ln0","line",960,240,0,90,P['text2']),E("lnh","line",350,330,1220,0,P['text2'])]+[
                E(f"lk{j}","line",KX[j]+KW//2,330,0,190,P['text2']) for j in range(3)]+[
                R(f"k{j}",KX[j],KY,KW,110,P['panel'],stroke=c,radius=20,label=n,fontSize=44) for j,n in enumerate(KN)]
    TREE=["p","ln0","lnh","lk0","lk1","lk2","k0","k1","k2"]
    def cards(dim=False):  # 两张手机价格卡：没有具体金额，只用长短条示意
        return [R("ca",260,120,440,640,P['panel'],stroke=P['secondary'],radius=36),T("ha",260,150,440,56,"搜索页",44,P['text2'],align="center"),
                T("pa",300,260,360,50,"到手价",40,P['text'],align="center"),R("ba",300,340,360,44,P['accent'],radius=22),
                R("cb_",1220,120,440,640,P['panel'],stroke=P['secondary'],radius=36),T("hb",1220,150,440,56,"结算页",44,P['text2'],align="center"),
                T("pb",1260,260,360,50,"到手价",40,P['text'],align="center"),R("bb",1260,340,220,44,P['success'],radius=22),
                R("rb",1260,440,360,72,stroke=P['danger'],radius=16,label="红包抵扣",fontSize=40)]
    def labels(px,py,w):
        k=w/512; return [R(f"l{j}",int(px+k*(101+j*102)-50),py+w+8,100,64,stroke=P['text2'],radius=14,label=n,fontSize=32) for j,n in enumerate(("空调","冰箱","灯","插座"))]
    if si==0:  # 两个价不一样
        e1=cards()+[E("go","arrow",740,380,440,50,P['text2'],direction="r"),T("q",760,560,400,100,"bug？",72,P['danger'],align="center")]
        tg=at(0,"加购")
        a1=[F(x,0) for x in ("ca","ha","pa","ba")]+[draw("go",tg,20)]+[F(x,tg+10) for x in ("cb_","hb","pb","bb")]+[F("rb",at(0,"红包抵扣")),pop("rb",at(0,"红包抵扣")),F("q",at(0,"这是")),pop("q",at(0,"这是"))]
        e2=[T("q",360,300,400,100,"bug？",72,P['danger'],align="center"),E("strike","line",380,350,360,0,P['danger']),tag("why",360,480,400,"故意的",P['success'],44),
            T("ask",1180,300,400,200,"？",140,P['accent'],align="center")]
        a2=[F("q",0),F("strike",at(0,"其实不是")),draw("strike",at(0,"其实不是"),10),F("why",at(0,"故意")),pop("why",at(0,"故意")),F("ask",at(1,"我们先看看")),pop("ask",at(1,"我们先看看"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 雪崩
        e1=tree()
        a1=[F("p",0),F("ln0",at(0,"同时")),F("lnh",at(0,"同时")),F("lk0",at(0,"商品价格")),F("k0",at(0,"商品价格")),F("lk1",at(0,"优惠券")),F("k1",at(0,"优惠券")),F("lk2",at(0,"红包")),F("k2",at(0,"红包")),pop("k2",at(0,"红包"))]
        e2=tree()+[red("r2",KX[2],KY,"红包",KW),I("tm","timer",KX[2]+KW-100,KY-100,90),red("rp",660,130,"到手价计算",600)]+[I(f"g{j}","guest",160+(j%5)*80,690+(j//5)*90,70) for j in range(10)]+[
            red("cart",1080,690,"购物车",260),red("chk",1400,690,"结算页",260),term("av",620,760,360,"雪崩",P['danger'],64)]
        tk=at(0,"卡住");tq=at(0,"越积越多")
        a2=[F(x,0) for x in TREE]+[F("r2",tk),pop("r2",tk),F("tm",tk)]+[F(f"g{j}",at(0,"一直等着")+j*6) for j in range(10)]+[
            F("rp",at(0,"拖垮")),F("cart",at(0,"购物车")),F("chk",at(0,"结算页")),F("av",at(1,"这就叫雪崩")),pop("av",at(1,"这就叫雪崩"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 电闸跳闸
        bx,by,bw=200,140,560
        e1=[I("box","breaker-box",bx,by,bw),I("trip","breaker-tripped",bx,by,bw),I("so","socket",800,440,150),I("sp","spark",860,360,130)]+labels(bx,by,bw)+[
            I("fr","fridge",1080,220,300),I("lp","lamp",1440,300,240),tag("ok",1120,620,560,"其余各路：照常",P['success'],40)]
        tz=at(1,"跳下来")
        a1=[F("box",0),F("so",0)]+[F(f"l{j}",0) for j in range(4)]+[F("sp",at(1,"短路")),pop("sp",at(1,"短路")),F("trip",tz),out("box",tz,tz+8),out("sp",tz+20,tz+30),F("fr",at(1,"冰箱")),F("lp",at(1,"冰箱")),F("ok",at(1,"只断"))]
        e2=[x for x in tree() if x['id']!="lk2"]+[E("lk2a","line",1570,330,0,190,P['text2']),I("son","switch-on",1600,330,90,170),I("soff","switch-off",1600,330,90,170),
            tag("fast",160,700,320,"直接出价",P['accent'],40),term("cb",760,700,400,"熔断",P['danger'],64)]
        for x in e2:
            if x['id'] in("k0","k1"): x['stroke']=P['success']
        tt=at(0,"跳闸");tc=at(0,"这就叫熔断")
        a2=[F(x,0) for x in TREE if x!="lk2"]+[F("lk2a",0),F("son",0),F("soff",tt),out("son",tt,tt+8),out("lk2a",tt,tt+8,0.2),mv("k2","opacity",tt,tt+12,1,0.35),
            F("fast",at(0,"也不再等它")),F("cb",tc),pop("cb",tc)]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 试着合闸
        e1=[I("soff","switch-off",300,220,160,280),I("tm","timer",560,240,200),R("probe",900,330,200,80,stroke=P['primary'],radius=40,label="试探",fontSize=36),
            R("rs",1360,300,300,110,stroke=P['text2'],radius=20,label="红包",fontSize=44),term("ho",900,600,420,"半开",P['primary'],64)]
        tp=at(1,"放一个");th=at(1,"这个状态叫半开")
        a1=[F("soff",0),F("rs",0),F("tm",at(0,"跳闸以后")),F("probe",at(1,"过一会儿")),mv("probe","x",tp,tp+30,900,1100),F("ho",th),pop("ho",th)]
        e2=[R("okc",160,160,700,300,stroke=P['success'],radius=24),I("son","switch-on",200,190,120,220),T("okt",360,250,480,60,"成功：合闸",44,P['success']),
            R("bdc",1000,160,760,300,stroke=P['danger'],radius=24),I("soff","switch-off",1040,190,120,220),T("bdt",1200,220,520,60,"失败：保持断开",44,P['danger']),I("tm","timer",1440,310,120),
            I("hg","hourglass",400,520,160),term("to",640,560,420,"超时",P['accent'],64),tag("give",1120,580,520,"到点就放弃",P['text2'],40)]
        tt=at(1,"叫超时")
        a2=[F("okc",0),F("son",0),F("okt",at(0,"试成功")),F("bdc",0),F("soff",0),F("bdt",at(0,"还是失败")),F("tm",at(0,"还是失败")),
            F("hg",at(1,"另外")),F("give",at(1,"另外")),F("to",tt),pop("to",tt)]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 关空调保冰箱：自动降级 + 主动降级
        e1=tree()+[R("res",160,700,440,96,stroke=P['success'],radius=48,label="到手价：照算",fontSize=44),R("wal",680,700,380,96,stroke=P['accent'],radius=48,label="红包：还在",fontSize=44),
            term("ad",1240,700,520,"自动降级",P['accent'],64)]
        tn=at(1,"先不把红包");ta=at(1,"这叫自动降级")
        a1=[F(x,0) for x in TREE]+[mv("k2","opacity",tn,tn+12,1,0.35),mv("lk2","opacity",tn,tn+12,1,0.2),F("res",at(1,"照样")),pop("res",at(1,"照样")),F("wal",at(1,"红包本身")),F("ad",ta),pop("ad",ta)]
        e2=[I("mt","meter",200,160,360),I("ac0","aircon",700,200,320),I("fr0","fridge",1200,160,300),
            I("f1","fridge",260,220,160),I("f2","fridge",720,220,160),I("ac","aircon",1450,220,160),
            R("cart",160,400,360,110,stroke=P['success'],radius=20,label="购物车",fontSize=44),R("chk",620,400,360,110,stroke=P['success'],radius=20,label="结算页",fontSize=44),
            R("sr",1300,400,460,110,stroke=P['text2'],radius=20,label="搜索推荐页红包",fontSize=44),E("res","arrow",1000,410,280,50,P['success'],direction="l"),
            term("md",760,700,520,"主动降级",P['accent'],64)]
        tb=at(1,"大促时");tg=at(1,"先关掉它");tm=at(2,"这叫主动降级");t1=at(0,"关空调")
        a2=[F("mt",0),F("ac0",0),F("fr0",0),mv("ac0","opacity",t1,t1+12,1,0.3),out("mt",tb,tb+8),out("ac0",tb,tb+8),out("fr0",tb,tb+8),
            F("cart",tb+8),F("chk",tb+8),F("f1",at(1,"是冰箱")),F("f2",at(1,"是冰箱")),F("sr",at(1,"搜索推荐")),F("ac",at(1,"是空调")),
            mv("sr","opacity",tg,tg+12,1,0.35),mv("ac","opacity",tg,tg+12,1,0.35),draw("res",at(1,"资源"),20),F("md",tm),pop("md",tm)]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=[term("cb",160,160,380,"熔断 · 止损",P['danger'],44),term("dg",600,160,380,"降级 · 兜底",P['accent'],44),
            queue("q",160,380,360),T("lq",160,560,360,50,"消息队列",40,P['primary'],align="center"),I("gate","gate",640,340,220),T("lg",560,580,380,50,"限流",40,P['success'],align="center"),
            I("tk","ticket",1040,350,200),T("lt",960,580,360,50,"幂等",40,P['accent'],align="center"),I("bx","breaker-tripped",1380,340,220),T("lb",1300,580,380,50,"熔断降级",40,P['danger'],align="center"),
            R("title",560,700,800,96,stroke=P['accent'],radius=48,label="四重防线",fontSize=52)]
        a1=[F("cb",0),F("dg",at(0,"降级负责"))]
        for i_,l_,w_ in (("q","lq","消息队列"),("gate","lg","限流"),("tk","lt","幂等"),("bx","lb","熔断降级")):
            a1+=[mv(i_,"opacity",0,12,0,0.35),mv(i_,"opacity",at(1,w_),at(1,w_)+12,0.35,1),F(l_,at(1,w_))]
        a1+=[F("title",at(1,"熔断降级")),pop("title",at(1,"熔断降级"))]
        e2=cards()
        a2=[F(x,0) for x in ("ca","ha","pa","ba","cb_","hb","pb","bb")]+[F("rb",0),pop("rb",0)]
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
   "脚本第 3 版：主线「到手价计算」父方块 → 商品价格 / 优惠券 / 红包三个子服务（肘形连线），雪崩、熔断、半开、超时都落在红包上；降级分自动（红包先不算进去，到手价照算，「红包：还在」）和主动（大促：购物车、结算页 = 冰箱；搜推页红包计算 = 空调，关掉，资源流向结算页）。价格卡不写具体金额，只用长短条示意。画面不暗示红包作废 / 失效，不出现积分 / 配送 / 猜你喜欢 / 评价 / 推荐（validate 禁用词）。贯穿比喻：家里电闸。旁白术语：雪崩、熔断、降级（主讲，含自动降级 / 主动降级），半开、超时（各一句），念到时上屏术语标签。画面不重复字幕句子（validate：术语白名单除外）。不出现具体数字。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/circuit-breaker/。新图标 breaker-box/breaker-tripped/switch-on/switch-off/spark/aircon/lamp/socket/meter 自绘无文字；复用 ticket/server（第十一期）、gate（第十期）、queue/guest（第九期）、fridge（第七期）、timer（第八期）、hourglass（第三期）。branding v1.3.0：只有右上水印 + 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f) for n,f in (("ticket","idempotency/assets/ticket.svg"),("gate","rate-limit/assets/gate.svg"),("queue","message-queue/assets/queue.svg"),("guest","message-queue/assets/guest.svg"),("fridge","browser-cache/assets/fridge.svg"),("timer","server-cache/assets/timer.svg"),("hourglass","dns/assets/hourglass.svg"))],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("breaker-box","breaker-tripped","switch-on","switch-off","spark","aircon","lamp","socket","meter")])
PS="breaker-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in [s for s in scenes if s['chapterId']=='breaker'][0]['shots']]
pl=239  # 写死（Knoll v3 timing 20:25 + HOLDS）：breaker-1 动画全部在 228 结束——插座那路已跳闸、火花消失、冰箱/灯/「其余各路：照常」全显；全局 1398+239=1637
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="家里电闸：插座那一路跳闸，其余各路照常（冰箱、灯亮着）",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
