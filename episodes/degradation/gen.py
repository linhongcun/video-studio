# EP.12《两个价不一样，为什么不是 bug？》（第 4 版：只讲降级）分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts
src=open(SCRIPT).read()
narr=re.findall(r'- 旁白：(.+)',src); assert len(narr)==4
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
titles=["两个价不一样","一个卡住，全都在等","先不算红包","关空调，保冰箱"]
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
    CARDS=("ca","ha","pa","ba","cb_","hb","pb","bb")
    def cards():  # 两张手机价格卡：没有具体金额，只用长短条示意
        return [R("ca",260,120,440,640,P['panel'],stroke=P['secondary'],radius=36),T("ha",260,150,440,56,"搜索页",44,P['text2'],align="center"),
                T("pa",300,260,360,50,"到手价",40,P['text'],align="center"),R("ba",300,340,360,44,P['accent'],radius=22),
                R("cb_",1220,120,440,640,P['panel'],stroke=P['secondary'],radius=36),T("hb",1220,150,440,56,"结算页",44,P['text2'],align="center"),
                T("pb",1260,260,360,50,"到手价",40,P['text'],align="center"),R("bb",1260,340,220,44,P['success'],radius=22),
                R("rb",1260,440,360,72,stroke=P['danger'],radius=16,label="红包抵扣",fontSize=40)]
    if si==0:  # 两个价不一样
        e1=cards()+[E("go","arrow",740,380,440,50,P['text2'],direction="r"),T("q",760,560,400,100,"bug？",72,P['danger'],align="center")]
        tg=at(0,"加购")
        a1=[F(x,0) for x in ("ca","ha","pa","ba")]+[draw("go",tg,20)]+[F(x,tg+10) for x in ("cb_","hb","pb","bb")]+[F("rb",at(0,"红包抵扣")),pop("rb",at(0,"红包抵扣")),F("q",at(0,"这是")),pop("q",at(0,"这是"))]
        e2=[dict(T("q",260,300,400,100,"bug？",72,P['danger'],align="center"),dimmed=True),tag("why",260,480,400,"多半是有意的",P['success'],44),  # 2026-10-14 内容核对：「其实不是，是故意」→「不一定，很可能有意为之」：去掉划线，bug？只变暗不否定；「故意的」→「多半是有意的」
            R("p",1060,300,600,110,P['panel'],stroke=P['secondary'],radius=20,label="到手价计算",fontSize=48),T("ask",1060,460,600,160,"？",120,P['accent'],align="center")]
        tp=at(1,"到手价是怎么")
        a2=[F("q",0),mv("q","opacity",at(0,"不一定"),at(0,"不一定")+12,1,0.5),F("why",at(0,"很可能")),pop("why",at(0,"很可能")),F("p",tp),pop("p",tp),F("ask",tp+6)]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 一个卡住，全都在等
        e1=tree()+[red("r2",KX[2],KY,"红包",KW),I("tm","timer",KX[2]+KW-100,KY-100,90),red("rp",660,130,"到手价计算",600)]+[I(f"g{j}","guest",160+(j%5)*80,690+(j//5)*90,70) for j in range(10)]+[
            red("cart",1080,690,"购物车",260),red("chk",1400,690,"结算页",260)]
        tk=at(1,"卡住")
        a1=[F("p",0),F("ln0",at(0,"同时")),F("lnh",at(0,"同时")),F("lk0",at(0,"商品价格")),F("k0",at(0,"商品价格")),F("lk1",at(0,"优惠券")),F("k1",at(0,"优惠券")),F("lk2",at(0,"红包几个")),F("k2",at(0,"红包几个")),
            F("r2",tk),pop("r2",tk),F("tm",tk)]+[F(f"g{j}",at(1,"一直等着")+j*6) for j in range(10)]+[F("rp",at(2,"很快")),F("cart",at(2,"购物车")),F("chk",at(2,"结算页"))]
        e2=[R("cart",260,360,440,120,P['panel'],stroke=P['primary'],radius=24,label="购物车",fontSize=48),R("chk",1220,360,440,120,P['panel'],stroke=P['primary'],radius=24,label="结算页",fontSize=48),
            R("link",700,410,520,20,P['primary'],radius=10),red("rc",260,365,"购物车",440),red("rk",1220,365,"结算页",440),R("rl",700,410,520,20,P['danger'],radius=10),
            red("r2",1460,140,"红包",200),term("core",660,560,600,"核心链路",P['primary'],64),term("av",760,720,400,"雪崩",P['danger'],64)]
        tc=at(0,"叫核心链路");tr=at(1,"拖垮");ta=at(1,"这就是常说的雪崩")
        a2=[F("cart",0),F("chk",0),F("link",at(0,"购物车到结算")),draw("link",at(0,"购物车到结算"),20),F("core",tc),pop("core",tc),F("r2",at(1,"一个服务")),
            F("rc",tr),F("rl",tr+6),F("rk",tr+12),F("av",ta),pop("av",ta)]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 先不算红包：降级 → 自动降级
        e1=tree()+[R("res",160,700,440,96,stroke=P['success'],radius=48,label="到手价：照算",fontSize=44),R("wal",680,700,380,96,stroke=P['accent'],radius=48,label="红包：还在",fontSize=44)]
        tn=at(1,"先不把红包")
        a1=[F(x,0) for x in TREE]+[mv("k2","opacity",tn,tn+12,1,0.35),mv("lk2","opacity",tn,tn+12,1,0.2),F("res",at(1,"照样")),pop("res",at(1,"照样")),F("wal",at(2,"红包本身")),pop("wal",at(2,"红包本身"))]
        e2=[dict(x,dimmed=True) if x['id']=="k2" else x for x in tree()]+[R("res",160,700,300,96,stroke=P['success'],radius=48,label="到手价",fontSize=44),E("go","arrow",480,700,320,60,P['success'],direction="r"),
            R("chk",820,700,300,96,stroke=P['success'],radius=48,label="结算页",fontSize=44),term("dg",1240,660,300,"降级",P['accent'],64),term("ad",1240,770,440,"自动降级",P['accent'],56)]
        td=at(1,"叫降级");ta=at(2,"叫自动降级")
        a2=[F(x,0) for x in TREE if x not in("k2","lk2")]+[mv("k2","opacity",0,12,0,0.35),mv("lk2","opacity",0,12,0,0.2),F("res",0),draw("go",at(0,"订单能往下走"),20),F("chk",at(0,"订单能往下走")+12),
            F("dg",td),pop("dg",td),F("ad",ta),pop("ad",ta)]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 关空调，保冰箱：主动降级 + 为什么两个价不一样 + 第四招
        e1=[I("mt","meter",200,160,360),I("ac0","aircon",700,200,320),I("fr0","fridge",1200,160,300),tag("act",700,600,360,"空调：已关",P['text2'],40),tag("frt",1170,600,360,"冰箱：照常",P['success'],40)]
        t1=at(1,"先关掉空调")
        a1=[F("mt",at(1,"夏天")),F("ac0",0),F("fr0",0),mv("ac0","opacity",t1,t1+12,1,0.3),F("act",t1),F("frt",t1)]
        e2=[I("f1","fridge",260,220,160),I("f2","fridge",720,220,160),I("ac","aircon",1450,220,160),
            R("cart",160,400,360,110,stroke=P['success'],radius=20,label="购物车",fontSize=44),R("chk",620,400,360,110,stroke=P['success'],radius=20,label="结算页",fontSize=44),
            R("sr",1300,400,460,110,stroke=P['text2'],radius=20,label="搜索推荐页红包",fontSize=44),E("res","arrow",1000,410,280,50,P['success'],direction="l"),
            term("md",660,700,600,"主动降级",P['accent'],64)]
        tg=at(1,"提前关掉它");tm=at(1,"这叫主动降级")
        a2=[F("cart",0),F("chk",0),F("f1",at(0,"就是冰箱")),F("f2",at(0,"就是冰箱")),F("sr",at(0,"搜索推荐")),F("ac",at(0,"就是空调")),
            mv("sr","opacity",tg,tg+12,1,0.35),mv("ac","opacity",tg,tg+12,1,0.35),draw("res",at(1,"资源"),20),F("md",tm),pop("md",tm)]
        e3=cards()+[queue("q",160,300,360),T("lq",160,480,360,50,"消息队列",40,P['primary'],align="center"),I("gate","gate",640,260,220),T("lg",560,500,380,50,"限流",40,P['success'],align="center"),
            I("tk","ticket",1040,270,200),T("lt",960,500,360,50,"幂等",40,P['accent'],align="center"),I("fz","fridge",1440,250,220),term("dg",1340,500,420,"降级",P['accent'],56),
            R("title",560,680,800,96,stroke=P['accent'],radius=48,label="四重防线",fontSize=52)]
        tb=at(1,"扛住高峰");t4=at(1,"第四招")
        a3=[F(x,0) for x in CARDS]+[F("rb",0),mv("rb","scale",at(0,"才算上"),at(0,"才算上")+12,1.15,1,"spring")]+[out(x,tb,tb+10) for x in CARDS+("rb",)]+[
            F("q",tb+10),F("lq",tb+10),F("gate",tb+16),F("lg",tb+16),F("tk",tb+22),F("lt",tb+22),F("fz",t4),F("dg",t4),pop("dg",t4),F("title",t4+20),pop("title",t4+20)]
        return [(e1,a1),(e2,a2),(e3,a3)]
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
meta=dict(title="《搜索页和结算页，为什么两个价不一样？》",episode=12,slug="degradation",release="v0.17.0",series="扛住高峰 04",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  tts=dict(note="Nolan：送 TTS 的旁白把「这是出 bug 了吗？」读成「这是出故障了吗？」；字幕保留「bug」原句。镜头 ttsText = 送 TTS 文字，narration/subtitles = 字幕原文",replace={"这是出 bug 了吗？":"这是出故障了吗？"}),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句间 0.28 秒，每章尾留 60 帧；按 TTS 文字计字）。配音到后：sh run.sh（默认 /workspace/share/ep12-timing.json）→ map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "脚本第 4 版：只讲降级（熔断、半开、超时、电闸跳闸全部拿掉，validate 禁用词）。主线「到手价计算」父方块 → 商品价格 / 优惠券 / 红包（肘形连线），红包卡住拖住购物车 → 结算页（核心链路），雪崩一句带过；自动降级：红包先不算进去，到手价照算，「红包：还在」；主动降级只在第 4 章用比喻「关空调，保冰箱」（购物车、结算页 = 冰箱，「搜索推荐页红包」= 空调，Nolan 批准此标签）。价格卡不写具体金额，只用长短条示意。画面不暗示红包作废 / 失效，不出现积分 / 配送 / 猜你喜欢 / 评价。旁白术语：降级（主讲）、核心链路、自动降级、主动降级，雪崩一次；念到时上屏术语标签（锚在点名的那句 / 分句起点）。画面不重复字幕句子（validate：术语白名单 + LABEL_OK 除外）。不出现具体数字。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/degradation/。新图标 aircon/meter 自绘无文字；复用 ticket（第十一期）、gate（第十期）、queue/guest（第九期）、fridge（第七期）、timer（第八期）。branding v1.3.0：只有右上水印 + 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f) for n,f in (("ticket","idempotency/assets/ticket.svg"),("gate","rate-limit/assets/gate.svg"),("queue","message-queue/assets/queue.svg"),("guest","message-queue/assets/guest.svg"),("fridge","browser-cache/assets/fridge.svg"),("timer","server-cache/assets/timer.svg"))],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("aircon","meter")])
PS="hook-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in scenes[0]['shots']]
pl=300  # 写死（Knoll v4 timing 21:43 + HOLDS）：hook-1 两张卡 186 全显、「红包抵扣」254 弹出完毕、「bug？」314 才开始淡入；hook 从 0 起，全局 = 300
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="两张价格卡并排：搜索页到手价长条 vs 结算页更短长条 +「红包抵扣」行（无具体金额）",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
