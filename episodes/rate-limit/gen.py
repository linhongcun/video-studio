# EP.10《抢票那一刻，为什么总提示系统繁忙？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
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
titles=["系统繁忙","不限流会怎样","限流","令牌桶","熔断和降级","回顾"]
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
    if si==0:  # 系统繁忙
        e1=[I("phone","phone-busy",660,120,600),R("buy",820,560,280,80,stroke=P['success'],radius=40,label="购买",fontSize=40),
            R("busy",700,300,520,120,stroke=P['danger'],radius=20,label="系统繁忙",fontSize=48),
            T("q",160,320,420,80,"崩了？",56,P['text2'],align="center"),R("block",1340,320,420,96,stroke=P['accent'],radius=48,label="有意为之",fontSize=44)]
        tb=at(0,"弹出")
        a1=[F("phone",0),F("buy",0),pop("buy",at(0,"点下购买")),out("buy",tb,tb+10),F("busy",tb),pop("busy",tb),F("q",at(1,"坏了")),
            mv("q","opacity",at(2,"没坏")+8,at(2,"没坏")+20,1,0.35),F("block",at(2,"故意拦")),pop("block",at(2,"故意拦"))]
        e2=crowd("g",160,520,6,3,110,90)+[I("gate","gate",640,180,520),queue("q",1220,440,560),T("ask",160,260,400,120,"？",110,P['accent'],align="center")]
        a2=[F("gate",0)]+[F(f"g{j}",j*6) for j in range(6)]+[F("ask",0),pop("ask",0),F("q",at(1,"景区门口")),mv("q","x",at(1,"景区门口"),at(1,"景区门口")+24,1300,1220)]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 不限流会怎样
        e1=[R("park",960,160,800,560,stroke=P['success'],radius=24),T("cap",960,180,800,50,"容量：一千人（示意）",40,P['success'],align="center"),
            I("gate","gate-open",640,300,320),T("out",160,180,460,50,"门外：一万人（示意）",36,P['danger'])]+crowd("g",160,260,12,4,110,90)+[tag("jam",1160,740,400,"寸步难行",P['danger'],44)]
        to=at(1,"大门敞开")
        a1=[F("park",0),F("cap",at(0,"一千人")),F("gate",0)]+[F(f"g{j}",j*3) for j in range(12)]+[F("out",at(0,"一万人"))]
        for j in range(12): a1+=[mv(f"g{j}","x",to+j*3,to+j*3+30,160+(j%4)*110,1000+(j%6)*110),mv(f"g{j}","y",to+j*3,to+j*3+30,260+(j//4)*120,260+(j//6)*140+(j%2)*40)]
        a1+=[mv("park","opacity",at(1,"挤满"),at(1,"挤满")+12,1,1),F("jam",at(1,"路被堵死"))]
        e2=[I("srv","server",760,180,400),I("down","server-down",760,180,400)]+[I(f"r{j}","slip",160+(j%3)*110,220+(j//3)*150,100) for j in range(9)]+[
            tag("crash",760,640,400,"服务器：挤垮",P['danger'],44),I("phone","phone-busy",1400,220,300),tag("no",1340,580,420,"抢票失败",P['danger'],44)]
        tf=at(0,"请求")
        a2=[F("srv",0)]+[F(f"r{j}",tf+j*4,6) for j in range(9)]+[mv(f"r{j}","x",tf+12+j*4,tf+36+j*4,160+(j%3)*110,860) for j in range(9)]+[
            F("down",at(0,"挤垮")),out("srv",at(0,"挤垮"),at(0,"挤垮")+12),F("crash",at(0,"挤垮")),F("phone",at(0,"连原本")),F("no",at(0,"买不到"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 限流
        e1=crowd("w",160,300,6,3,110,90)+[I("gate","gate",640,200,440),R("park",1180,200,580,460,stroke=P['success'],radius=24)]+[I(f"in{j}","guest",1220+(j%3)*170,260+(j//3)*170,120) for j in range(6)]+[
            tag("wait",160,560,420,"门外：候场",P['accent'],40),term("rl",640,700,440,"限流",P['primary'],56)]
        tp=at(0,"限量放人")
        a1=[F("gate",0),F("park",0)]+[F(f"w{j}",0) for j in range(6)]+[F(f"in{j}",tp+j*14) for j in range(6)]+[F("wait",at(1,"外面等")),F("rl",at(2,"限流")),pop("rl",at(2,"限流"))]
        e2=[I("gate","gate",160,220,420),term("rl",160,700,420,"限流",P['primary'],48),R("qps",700,220,1060,110,stroke=P['secondary'],radius=20,label="QPS = 每秒请求数",fontSize=48),
            I("phone","phone-busy",860,400,360),R("busy",1260,500,500,96,stroke=P['danger'],radius=20,label="系统繁忙",fontSize=44),E("say","arrow",1260,700,500,50,P['accent'],label="门口：请稍等",direction="l",fontSize=36)]
        a2=[F("gate",0),F("rl",0),F("qps",at(0,"QPS")),pop("qps",at(0,"QPS")),F("phone",at(1,"系统繁忙")),F("busy",at(1,"系统繁忙")),draw("say",at(1,"门口在说"),15)]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 令牌桶
        e1=[I("bucket","bucket",260,240,480),term("tb",260,740,480,"令牌桶",P['accent'],52),T("ask",960,200,400,120,"？",110,P['accent'])]+[I(f"t{j}","token",400,100,120) for j in range(4)]+[
            T("tl",1000,420,300,50,"令牌",44,P['accent']),tag("rate",1000,520,560,"匀速发票",P['primary'],40),I("tm","timer",1360,240,140)]
        a1=[F("ask",0),pop("ask",0),out("ask",at(1,"令牌桶"),at(1,"令牌桶")+10),F("bucket",at(1,"令牌桶")),F("tb",at(1,"令牌桶")),pop("tb",at(1,"令牌桶")),F("tm",at(2,"固定的速度")),F("rate",at(2,"固定的速度")),F("tl",at(2,"门票"))]
        t0=at(2,"按固定")
        for j in range(4): s=t0+j*20; a1+=[F(f"t{j}",s,6),mv(f"t{j}","y",s,s+18,100,330),out(f"t{j}",s+18,s+22)]
        e2=[I("bucket","bucket",160,220,360),I("empty","bucket-empty",160,220,360),I("full","bucket-full",160,220,360),I("gate","gate",820,220,380),I("tk","token",520,380,110),
            I("g0","guest",620,400,110),tag("none",160,620,420,"没票：不放行",P['danger'],40)]+[I(f"b{j}","guest",620,330+j*0,110) for j in range(3)]+[
            R("burst",160,740,1000,90,stroke=P['success'],radius=16,label="攒票 → 放一小波",fontSize=40)]
        tt=at(0,"拿走一张"); te=at(0,"桶空了"); tw=at(1,"没人来"); tbst=at(1,"一小波")
        a2=[F("bucket",0),F("gate",0),F("g0",0),F("tk",tt),mv("tk","x",tt,tt+16,520,640),mv("g0","x",at(0,"才能进"),at(0,"才能进")+24,620,1260),out("tk",at(0,"才能进"),at(0,"才能进")+8),
            F("empty",te),out("bucket",te,te+10),F("none",te),out("none",tw,tw+10),F("full",tw),out("empty",tw,tw+10)]
        for j in range(3): a2+=[F(f"b{j}",tbst-10),mv(f"b{j}","x",tbst+j*4,tbst+24+j*4,620,1260+j*130)]
        a2+=[out("full",tbst+20,tbst+32,0.6),F("burst",tbst)]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 熔断和降级
        # 2026-10-14 内容核对：熔断改成「导游不往那边带人、举『暂停开放』牌，大门照常放人；过一会先带少量游客试，没问题再恢复」（旧版：路上『暂停』牌 +『定时重试』+ 派人看看）
        e1=[I("gate","gate-open",160,240,360),T("rlT",160,180,360,50,"限流",40,P['primary'],align="center"),tag("gateT",160,600,360,"大门：照常",P['success'],40),
            E("path","arrow",560,420,620,50,P['text2'],direction="r"),I("spot","spot",1240,200,400),I("smoke","smoke",1400,120,220),
            I("guide","guide",600,250,170),R("stop",790,250,300,110,P['bg'],stroke=P['danger'],radius=16,label="暂停开放",fontSize=44),
            I("tm","timer",800,520,120),tag("few",940,540,320,"少量游客",P['accent'],40),I("t0","guest",660,345,80),I("t1","guest",720,345,80),
            R("ok",1240,620,400,84,P['bg'],stroke=P['success'],radius=16,label="恢复",fontSize=40),
            term("cb",160,700,440,"熔断",P['danger'],52),I("fuse","fuse",620,700,100)]
        tp=at(1,"暂停开放"); tt=at(1,"带几个人"); tk=at(1,"没问题")
        a1=[F("gate",0),F("rlT",at(0,"限流")),F("gateT",at(0,"限流")),F("spot",0),F("path",0),F("smoke",at(1,"故障")),F("guide",at(1,"导游")),pop("guide",at(1,"导游")),F("stop",tp),pop("stop",tp),
            F("tm",at(1,"过一会")),F("few",tt),F("t0",tt),F("t1",tt+4),mv("t0","x",tt+6,tt+40,660,1330),mv("t1","x",tt+10,tt+44,720,1410),
            out("smoke",tk,tk+12),out("stop",tk,tk+12),F("ok",tk),pop("ok",tk),F("cb",at(1,"熔断")),pop("cb",at(1,"熔断")),F("fuse",at(1,"熔断"))]
        e2=[I("main","spot",160,180,400),tag("mainT",160,600,400,"主路：照常",P['success'],40),I("cam","camera",900,220,300),tag("camT",860,600,380,"打卡：先关",P['text2'],40),
            term("dg",1300,700,440,"降级",P['accent'],52),I("dgi","downgrade",1300,560,120)]
        a2=[F("main",0),F("cam",0),F("mainT",at(0,"保住")),F("camT",at(0,"关掉")),mv("cam","opacity",at(0,"关掉"),at(0,"关掉")+12,1,0.25),F("dgi",at(0,"降级")),F("dg",at(0,"降级")),pop("dg",at(0,"降级"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=[R("title",460,140,1000,96,stroke=P['accent'],radius=48,label="两招：排队 + 限流",fontSize=48),queue("q",160,320,700),T("lq",160,620,700,50,"消息队列：排好队",40,P['primary'],align="center"),
            I("gate","gate",1240,260,340),T("lg",1060,620,700,50,"限流：分批进门",40,P['success'],align="center"),T("plus",880,380,140,80,"+",80,P['text'],align="center")]
        a1=[mv("q","opacity",0,12,0,0.35),mv("q","opacity",at(0,"消息队列"),at(0,"消息队列")+12,0.35,1),F("lq",at(0,"消息队列")),
            mv("gate","opacity",0,12,0,0.35),mv("gate","opacity",at(0,"限流"),at(0,"限流")+12,0.35,1),F("lg",at(0,"限流")),F("plus",at(1,"合起来")),F("title",at(1,"两招")),pop("title",at(1,"两招"))]
        # recap-2（导演）：「先别急」忙碌手机停一拍 → 翻成「购买成功」；「守住那扇门」回到闸门，客人按顺序一个个进
        e2=[I("phone","phone-busy",160,140,480),I("ok","phone",160,140,480),R("busy",180,290,440,110,stroke=P['danger'],radius=20,label="系统繁忙",fontSize=44),
            R("done",180,600,440,96,stroke=P['success'],radius=48,label="购买成功",fontSize=44),I("gate","gate",1000,200,420),R("park",1440,220,320,420,stroke=P['success'],radius=24)]+[
            I(f"w{j}","guest",900-j*80,540,80) for j in range(4)]
        tf=max(at(0,"先别急"),68)+24; tg=at(0,"守住")  # 正式 timing：「先别急」局部 68（Knoll 实测），忙碌手机停 24 帧 → 92 翻「购买成功」
        a2=[F("phone",0),F("busy",0),F("ok",tf),out("phone",tf,tf+10),out("busy",tf,tf+10),F("done",tf),pop("done",tf),F("gate",0),F("park",0)]
        for j in range(4):
            s=tg+j*8; a2+=[F(f"w{j}",0),mv(f"w{j}","x",s,s+14,900-j*80,1480+(j%2)*130),mv(f"w{j}","y",s,s+14,540,280+(j//2)*150)]
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
meta=dict(title="《抢票那一刻，为什么总提示系统繁忙？》",episode=10,slug="rate-limit",release="v0.14.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）。配音到后：Knoll 的 ep10 timing 存为 timing.mimo.json → map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "贯穿比喻：景区门口限量放人，接第九期叫号队伍（门口先限量，进来的人再排队）。旁白点出术语：限流、令牌桶（主讲）、熔断、降级（各一句，配小图标）、QPS（一次），念到时上屏术语标签；一千人/一万人为示意数字，画面标「示意」。画面不重复字幕句子（validate：术语白名单除外）。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/rate-limit/。新图标 gate/gate-open/bucket/bucket-empty/bucket-full/token/server/server-down/spot/smoke/camera/fuse/downgrade 自绘无文字；复用 phone/guest/queue/slip/spinner（第九期）、timer（第八期）。branding v1.3.0：只有右上水印（留空区 x1700–1840 y80–130）+ 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f"message-queue/assets/{n}.svg") for n in ("phone","guest","queue","slip")]+[dict(id="timer",file="assets/timer.svg",from_="server-cache/assets/timer.svg")],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("phone-busy","gate","gate-open","guide","bucket","bucket-empty","bucket-full","token","server","server-down","spot","smoke","camera","fuse","downgrade")])
PS="token-bucket-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
pl=195  # 写死：token-bucket-1 局部 195（ep10 正式 timing，全局 2082）——「令牌桶」「匀速发票」已全显、第二张令牌正落进桶
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="令牌桶：门口的桶按固定速度掉进令牌，「令牌桶」「令牌」「固定速度」",file="poster.jpg")
_CS=Path("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=json.load(open(_CS)).get(meta["slug"]) if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
