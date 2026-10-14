# EP.11《手一抖点了两次支付，为什么只扣一次钱？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT
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
titles=["手一抖","为什么会重复","取餐号","唯一 ID","重试和幂等","回顾"]
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
    if si==0:  # 手一抖
        e1=[I("phone","phone-pending",660,120,560),I("busy","phone-busy",660,120,560),R("ok",760,590,360,80,stroke=P['accent'],radius=40,label="待支付",fontSize=40),
            R("pay",800,700,280,84,stroke=P['accent'],radius=42,label="支付",fontSize=44),I("tap1","tap",1240,520,200),I("tap2","tap",1400,420,200),
            T("q",160,320,420,80,"重复扣款？",56,P['danger'],align="center")]
        tp=at(0,"点下支付"); tz=at(0,"转圈"); t2=at(1,"又点")
        a1=[F("phone",0),F("ok",0),pop("ok",0),out("ok",tp,tp+10),F("pay",tp),F("tap1",tp),out("tap1",tp+20,tp+30),F("busy",tz),out("phone",tz,tz+10),
            F("tap2",t2),pop("tap2",t2),F("q",at(2,"会不会")),pop("q",at(2,"会不会"))]
        e2=[I("phone","phone-busy",160,160,420),I("coin","coin",700,260,200),tag("once",620,500,360,"扣款：仅一笔",P['success'],40),
            I("win","window",1180,200,520),I("tk","ticket",1080,520,180)]
        a2=[F("phone",0),F("coin",at(0,"只会扣")),pop("coin",at(0,"只会扣")),F("once",at(0,"只会扣")),F("win",at(1,"取餐窗口")),F("tk",at(1,"取餐窗口")),mv("tk","x",at(1,"取餐窗口"),at(1,"取餐窗口")+24,1080,1350)]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 为什么会重复
        e1=[I("tap","tap",220,200,260),tag("t1",160,520,380,"原因一：手滑",P['text2'],40),I("sig","signal",820,200,260),tag("t2",740,520,420,"原因二：网卡",P['text2'],40),
            I("r1","request",1260,240,160),I("r2","request",1260,420,160),term("rt",1280,620,420,"重试",P['accent'],52)]
        tr=at(2,"重试")
        a1=[F("tap",at(1,"手一抖")),F("t1",at(1,"手一抖")),F("sig",at(2,"网络卡")),F("t2",at(2,"网络卡"))]+fly("r1",at(2,"发出去"),1100,1500)+fly("r2",at(2,"自己再发"),1100,1500)+[F("rt",tr),pop("rt",tr)]
        e2=[I(f"r{j}","request",160,180+j*190,150) for j in range(3)]+[I("srv","server",1300,180,360),tag("same",160,760,520,"内容完全相同",P['text2'],40),
            R("sign",1180,600,600,96,stroke=P['danger'],radius=20,label="不算新单",fontSize=48)]
        a2=[F("same",at(0,"同一个请求"))]+sum([fly(f"r{j}",at(0,"两次")+j*10,160,820) for j in range(3)],[])+[F("srv",0),F("sign",at(1,"新的一笔")),pop("sign",at(1,"新的一笔"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 取餐号
        e1=[I("g","guest",160,360,200),I("tk","ticket",400,380,160),I("win","window",1100,160,560),I("meal","meal",1260,560,200),tag("first",1100,780-0,520,"第一次：出餐",P['success'],40)]
        e1[-1]["y"]=700
        a1=[F("g",0),F("tk",at(0,"取餐号")),pop("tk",at(0,"取餐号")),F("win",0),mv("g","x",at(1,"第一次"),at(1,"第一次")+30,160,860),mv("tk","x",at(1,"第一次"),at(1,"第一次")+30,400,1000),
            F("meal",at(1,"领到了")),pop("meal",at(1,"领到了")),F("first",at(1,"领到了"))]
        e2=[I("g","guest",860,360,200),I("tk","ticket",1000,380,160),I("win","window",1100,160,560),R("done",1180,370,400,110,stroke=P['accent'],radius=20,label="已领取",fontSize=52),
            term("mi",160,300,440,"幂等",P['primary'],64),tag("same",160,460,440,"结果不变",P['text2'],44)]
        a2=[F("g",0),F("tk",0),F("win",0),F("done",at(0,"已经领过")),pop("done",at(0,"已经领过")),F("mi",at(1,"幂等")),pop("mi",at(1,"幂等")),F("same",at(1,"结果"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 唯一 ID
        e1=[I("srv","server",1340,200,360),T("ask",1380,600,280,120,"？",110,P['accent'],align="center")]+[I(f"r{j}","request",160,180+j*220,170) for j in range(3)]+[
            I(f"k{j}","ticket",340,200+j*220,110) for j in range(3)]+[term("id",640,400,520,"唯一 ID",P['accent'],56),tag("same",640,560,520,"重发：号不变",P['text2'],40)]  # 2026-10-14 内容核对：加「重发：号不变」
        tk=at(1,"编号"); ti=at(2,"唯一")
        a1=[F("srv",0),F("ask",0),pop("ask",0),out("ask",at(1,"每笔"),at(1,"每笔")+10)]+[F(f"r{j}",at(1,"每笔")+j*6) for j in range(3)]+[x for j in range(3) for x in (F(f"k{j}",tk+j*8),pop(f"k{j}",tk+j*8))]+[F("id",ti),pop("id",ti),F("same",at(2,"重发")),pop("same",at(2,"重发"))]
        e2=[I("r","request",160,300,200),I("k","ticket",300,280,110),I("led","ledger",760,200,360),tag("look",700,600,480,"号先登记",P['text2'],40),
            R("new",1260,200,500,96,stroke=P['success'],radius=20,label="首次登记 → 扣款",fontSize=40),R("old",1260,420,500,96,stroke=P['accent'],radius=20,label="登记过：回「已支付」",fontSize=40),
            I("coin","coin",1450,640,140)]
        a2=[F("r",0),F("k",0),F("led",at(0,"登记")),F("look",at(0,"登记")),F("new",at(1,"登记成功")),F("coin",at(1,"扣钱")),pop("coin",at(1,"扣钱")),out("coin",at(1,"登记过了"),at(1,"登记过了")+10),F("old",at(1,"登记过了")),pop("old",at(1,"登记过了"))]  # 2026-10-14 内容核对：先查再办 → 先登记、登记成功才扣（旧版：翻账本对号 / 新号：扣款并登记）
        return [(e1,a1),(e2,a2)]
    if si==4:  # 重试和幂等
        e1=[term("mi",160,200,420,"幂等",P['primary'],56),T("plus",620,200,120,96,"+",72,P['text'],align="center"),term("rt",780,200,420,"重试",P['accent'],56),I("sig","signal",160,440,200)]+[
            I(f"r{j}","request",420,440+j*0,150) for j in range(3)]+[I("led","ledger",1300,360,300),tag("one",1260,700,400,"账上：仅一笔",P['success'],40)]
        t0=at(1,"大胆再发")
        a1=[F("mi",0),F("rt",at(0,"重试")),pop("rt",at(0,"重试")),F("plus",at(0,"重试")),F("sig",at(1,"网络")),F("led",0)]+sum([fly(f"r{j}",t0+j*12,420,1140) for j in range(3)],[])+[x for j in range(3) for x in (out(f"r{j}",t0+j*12+24,t0+j*12+30),)]+[F("one",at(1,"只扣"))]
        e2=[I("phone","phone",160,140,420),R("btn",250,560,240,80,stroke=P['accent'],radius=40,label="支付",fontSize=40),R("gray",250,560,240,80,"#374151",stroke=P["muted"],radius=40,label="支付",fontSize=40),
            term("fc",640,180,500,"防重复提交",P['accent'],48),T("gate1",640,300,500,50,"第一道门",40,P['text2'],align="center"),I("r","request",640,560,140),E("byp","arrow",800,500,500,50,P['danger'],direction="r",label="绕过按钮",fontSize=36),
            I("led","ledger",1380,300,300),term("bd",1340,700,420,"兜底：幂等",P['primary'],44)]
        tg=at(0,"变灰"); tb=at(1,"挡不住")
        a2=[F("phone",0),F("btn",0),F("gray",tg),out("btn",tg,tg+8),F("fc",at(0,"防重复提交")),pop("fc",at(0,"防重复提交")),F("gate1",at(0,"第一道门")),F("led",0),
            F("r",tb),draw("byp",tb,15),mv("r","x",tb+15,tb+40,640,1200),F("bd",at(1,"兜底")),pop("bd",at(1,"兜底"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=[queue("q",160,300,480),T("lq",160,540,480,50,"消息队列",44,P['primary'],align="center"),I("gate","gate",820,240,300),T("lg",720,580,500,50,"限流",44,P['success'],align="center"),
            I("tk","ticket",1400,250,280),T("lt",1300,580,480,50,"幂等",44,P['accent'],align="center"),R("title",560,700,800,96,stroke=P['accent'],radius=48,label="三重防线",fontSize=52)]
        a1=[mv("q","opacity",0,12,0,0.35),mv("q","opacity",at(0,"消息队列"),at(0,"消息队列")+12,0.35,1),F("lq",at(0,"消息队列")),
            mv("gate","opacity",0,12,0,0.35),mv("gate","opacity",at(0,"限流"),at(0,"限流")+12,0.35,1),F("lg",at(0,"限流")),
            mv("tk","opacity",0,12,0,0.35),mv("tk","opacity",at(0,"幂等"),at(0,"幂等")+12,0.35,1),F("lt",at(0,"幂等")),F("title",at(1,"合起来")),pop("title",at(1,"合起来"))]
        e2=[I("busy","phone-busy",160,140,480),I("ok","phone",160,140,480),R("done",140,600,560,96,stroke=P['success'],radius=48,label="支付成功 · 只扣一次",fontSize=40),
            I("led","ledger",1000,200,360),I("tk","ticket",1380,240,200)]
        tf=at(0,"先别慌")+24
        a2=[F("busy",0),F("ok",tf),out("busy",tf,tf+10),F("done",tf),pop("done",tf),F("led",at(0,"后台")),F("tk",at(0,"那张号")),pop("tk",at(0,"那张号"))]
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
        shots.append(dict(id=KEY(si,k),chapterId=ids[si],**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),shots=shots));g+=D
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《手一抖点了两次支付，为什么只扣一次钱？》",episode=11,slug="idempotency",release="v0.15.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句间 0.28 秒，每章尾留 60 帧）。配音到后：sh run.sh（默认 /workspace/share/ep11-timing.json）→ map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "贯穿比喻：取餐号，同一张号只能领一次餐，再来只亮「已领取」。旁白术语：重试、幂等、唯一 ID（主讲）、防重复提交（一句），念到时上屏术语标签。画面不重复字幕句子（validate：术语白名单除外）。不出现具体数字。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/idempotency/。新图标 phone-pending/ticket/window/meal/tap/signal/request/ledger/coin 自绘无文字；复用 phone/phone-busy/server/gate（第十期）、queue/guest（第九期），hook-1「待支付」→ 点支付后转圈，recap-2 翻牌「支付成功 · 只扣一次」沿用第十期样式。branding v1.3.0：只有右上水印 + 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f"rate-limit/assets/{n}.svg") for n in ("phone","phone-busy","server","gate","queue","guest")],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("ticket","window","meal","tap","signal","request","ledger","coin","phone-pending")])
PS="ticket-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in [s for s in scenes if s['chapterId']=='ticket'][0]['shots']]
pl=416  # 写死：ticket-2 局部 416（ep11 正式 timing，ticket-2 起点 1366 → 全局 1782）——「已领取」已亮、「幂等」398–410 弹出后已全显
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="取餐号：同一张号再来窗口亮「已领取」，旁边「幂等」",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
