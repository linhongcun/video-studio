# EP.09《双十一下单那么多，为什么不丢单？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
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
titles=["双十一零点","不排队会怎样","取号叫号","削峰","生产者和消费者","回顾"]
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
def prep(i,x,y,w=720,**k): return A(i,"prep-table",x,y,w,w//2,**k)
def queue(i,x,y,w=1000,**k): return A(i,"queue",x,y,w,round(w*0.38),**k)
def ctr(i,x,y,w=280,**k): return A(i,"counter-idle",x,y,w,round(w*0.75),**k)
def term(i,x,y,w,label,c=None,fs=48): return R(i,x,y,w,96,stroke=c or P['primary'],radius=48,label=label,fontSize=fs)
def tag(i,x,y,w,label,c=None,fs=40): return R(i,x,y,w,84,stroke=c or P['text2'],radius=16,label=label,fontSize=fs)
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 双十一零点
        e1=[prep("prep",160,330,560),I("chef","chef",780,300,220),I("clock","clock",1360,180,280),T("t0",1360,480,280,64,"00:00",56,P['accent'],align="center"),
            tag("busy",700,620,380,"后厨：超负荷",P['danger'])]+[I(f"tk{j}","ticket",1500,560,100) for j in range(6)]
        t=at(0,"双十一零点"); tf=at(0,"同时下单")
        a1=[F("prep",0),F("chef",0),F("clock",t),F("t0",t),pop("t0",t)]
        for j in range(6):
            s=tf+j*8; a1+=[F(f"tk{j}",s,6),mv(f"tk{j}","x",s,s+24,1500,1040+(j%3)*90),mv(f"tk{j}","y",s,s+24,560,240+(j//3)*150+(j%3)*20)]
        a1+=[F("busy",at(0,"做不过来"))]
        e2=[R("site",160,200,440,240,stroke=P['secondary'],radius=16,label="网站：没崩",fontSize=44),I("phone","phone",760,170,300),T("ok",700,480,420,50,"订单：一张不少",40,P['success'],align="center"),
            queue("q",530,520,860)]
        a2=[F("site",0),F("phone",at(0,"订单")),F("ok",at(0,"订单")),F("q",at(1,"排好的队")),mv("q","x",at(1,"排好的队"),at(1,"排好的队")+24,630,530)]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 不排队会怎样
        e1=[ctr("counter",160,300,320),I("g0","guest",220,560,140),I("chef","chef",1400,280,240),I("tk","ticket",380,300,90),
            E("wait","arrow",520,400,820,50,P['text2'],direction="r",dash=True),A("spin","spinner",260,180,110,110),term("sync",700,620,480,"同步",P['accent'],56)]
        tw=at(1,"站在那里等")
        a1=[F("counter",0),F("g0",0),F("chef",0),F("tk",at(1,"每收一单")),mv("tk","x",tw,tw+30,380,1300),draw("wait",tw,20),F("spin",tw),F("sync",at(2,"同步")),pop("sync",at(2,"同步"))]
        e2=[ctr("counter",160,240,280)]+[I(f"g{j}","guest",160+j*120,520,110) for j in range(6)]+[I("chef","chef",1100,220,220),
            I("f0","slip-fallen",1340,420,130),I("f1","slip-fallen",1480,320,110),tag("lost",1300,600,420,"丢单",P['danger'],44),
            R("site",1360,160,360,140,stroke=P['secondary'],radius=16,label="网站",fontSize=40),A("spin","spinner",1490,320,100,100)]
        a2=[F("counter",0),F("chef",0)]+[F(f"g{j}",j*10) for j in range(6)]+[mv("chef","x",at(0,"手忙脚乱"),at(0,"手忙脚乱")+20,1100,1060),
            F("f0",at(0,"弄丢了")),F("f1",at(0,"弄丢了")+8),F("lost",at(0,"弄丢了")),out("f0",at(1,"网站"),at(1,"网站")+12),out("f1",at(1,"网站"),at(1,"网站")+12),out("lost",at(1,"网站"),at(1,"网站")+12),
            F("site",at(1,"网站")),F("spin",at(1,"卡住"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 取号叫号
        e1=[term("title",160,140,440,"取号叫号",P['accent'],48),ctr("counter",160,300,320),queue("q",560,300,860),I("chef","chef",1500,300,220),
            I("slip","slip",420,300,90),I("g0","guest",180,600,130),I("phone","phone",340,580,180),T("got",540,640,300,56,"已收到",44,P['success'])]
        tp=at(1,"放进")
        a1=[F("title",0),F("counter",0),F("q",0),F("chef",0),F("g0",0),F("slip",at(1,"号单")),mv("slip","x",tp,tp+24,420,1400),mv("slip","y",tp,tp+24,300,440),
            F("phone",at(1,"已收到")),F("got",at(1,"已收到")),pop("got",at(1,"已收到"))]
        e2=[ctr("counter",160,200,280)]+[I(f"g{j}","guest",160+j*130,470,110) for j in range(3)]+[
            R("syncR",160,640,620,84,stroke=P['muted'],radius=16,label="同步：站着等",fontSize=40),R("asyncR",160,750,620,84,stroke=P['success'],radius=16,label="异步：先回「已收到」",fontSize=40),
            queue("q",880,240,880),term("mq",880,600,880,"消息队列（MQ）",P['primary'],48),T("mqen",880,720,880,50,"Message Queue",36,P['text2'],align="center")]
        a2=[F("counter",0),F("q",0)]+[F(f"g{j}",j*14) for j in range(3)]+[out("g0",at(0,"接下一位"),at(0,"接下一位")+12),F("syncR",at(0,"异步")),F("asyncR",at(0,"异步")),pop("asyncR",at(0,"异步")),
            F("mq",at(1,"消息队列")),pop("mq",at(1,"消息队列")),F("mqen",at(1,"MQ"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 削峰
        e1=[I("peak","peak-curve",160,200,900,428),T("in",160,660,900,50,"涌入：一万单/分钟（示意）",40,P['danger']),T("cap",160,730,900,50,"处理：一千单/分钟（示意）",40,P['success']),
            I("chef","chef",1360,220,240),I("f0","slip-fallen",1300,480,140),I("f1","slip-fallen",1480,500,140),tag("noq",1240,680,520,"没队列：冲垮",P['danger'],44)]
        a1=[F("peak",0),F("chef",0),F("in",at(1,"一万单")),F("cap",at(1,"一千单")),F("noq",at(2,"没有队列")),F("f0",at(2,"当场")),F("f1",at(2,"当场")+6)]
        e2=[I("flat","flat-curve",160,200,900,428),T("leg",160,660,900,50,"虚线：原来的尖峰",36,P['text2']),queue("q",1180,220,580),I("chef","chef",1380,470,200),
            term("cut",160,740,480,"削峰",P['primary'],56)]
        a2=[F("flat",0),F("leg",0),F("q",0),F("chef",0),F("cut",at(1,"这就叫")),pop("cut",at(1,"这就叫"))]  # 「削峰」在句尾：提前到「这就叫」弹出，留够停留
        return [(e1,a1),(e2,a2)]
    if si==4:  # 生产者和消费者
        e1=[ctr("counter",160,280,300),term("prod",160,560,300,"生产者",P['accent'],44),queue("q",520,260,860),I("chef","chef",1480,260,220),term("cons",1440,560,300,"消费者",P['success'],44),
            I("dish","dish-green",1520,460,140),R("done",560,700,800,90,stroke=P['primary'],radius=16,label="做完 → 才划掉",fontSize=44),
            R("ring",1166,444,97,131,None,stroke=P['accent'],radius=12),E("strike","arrow",1150,486,128,24,P['danger'],headless=True,note="划线：无箭头的线段，drawProgress"),
            R("gone",1172,452,85,115,P['bg'])]  # 队首号单（queue.svg 第 5 张）：高亮框 → 红线划过 → 盖掉移除
        tc=at(1,"划掉")
        a1=[F("counter",0),F("q",0),F("chef",0),F("prod",at(0,"生产者")),pop("prod",at(0,"生产者")),F("cons",at(0,"消费者")),pop("cons",at(0,"消费者")),
            F("dish",at(1,"做完")),F("done",tc),pop("done",tc),
            F("ring",at(1,"做完")),draw("strike",tc,10),mv("gone","opacity",0,1,0,0,"linear"),F("gone",tc+14),out("ring",tc+14,tc+26),out("strike",tc+14,tc+26)]
        e2=[queue("q",160,240,760),I("c1","chef",1000,240,200),tag("err",960,520,280,"出错",P['danger'],44),I("c2","chef",1460,240,200),I("pot","pot",1170,300,110),
            R("gone",738,410,72,101,P['bg']),R("ring",730,402,89,117,None,stroke=P['accent'],radius=12),I("slip","slip",714,400,120),R("still",160,560,560,84,stroke=P['accent'],radius=16,label="号单：还在",fontSize=40),R("safe",960,640,780,90,stroke=P['success'],radius=45,label="接手重做 → 不丢",fontSize=40),
            R("kafka",160,700,240,80,stroke=P['text2'],radius=40,label="Kafka",fontSize=40),R("rabbit",440,700,320,80,stroke=P['text2'],radius=40,label="RabbitMQ",fontSize=40)]
        te=at(0,"出了错"); th=at(0,"换个厨师")
        # 对比 producer-1：厨师 1 出错（锅掉下），队首号单不划掉、保持高亮，厨师 2 再把它取走
        a2=[F("q",0),F("c1",0),F("pot",0),F("err",te),pop("err",te),mv("pot","y",te,te+18,300,430,"easeIn"),mv("c1","opacity",te+12,te+24,1,0.35),
            F("slip",te),F("ring",te),pop("ring",te),F("still",at(0,"号单还在")),
            F("c2",th),mv("slip","x",th,th+24,714,1660),mv("slip","y",th,th+24,400,300),out("ring",th,th+12),mv("gone","opacity",0,1,0,0,"linear"),F("gone",th),F("safe",at(0,"不会丢")),F("kafka",at(1,"Kafka")),pop("kafka",at(1,"Kafka")),F("rabbit",at(1,"RabbitMQ")),pop("rabbit",at(1,"RabbitMQ"))]  # 各在念到时单独弹出
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        row=[I("fridge","fridge",170,300,160,230),I("store","store",440,290,240),ctr("counter",780,330,240),prep("prep",1110,350,300),queue("q",1480,340,300)]
        labs=[("l0",120,"浏览器缓存",P['primary']),("l1",420,"CDN",P['accent']),("l2",760,"负载均衡",P['text']),("l3",1090,"服务端缓存",P['success']),("l4",1450,"消息队列",P['primary'])]
        LB=[T(i,x,600,340 if i!="l4" else 360,50,t,36,c,align="center") for i,x,t,c in labs]
        e1=row+LB
        a1=[]
        for ids_,ph in ((("fridge","l0","prep","l3"),"缓存"),(("q","l4"),"消息队列"),(("store","l1"),"门店"),(("counter","l2"),"柜台")):
            c=at(0,ph)
            for i in ids_: a1+=[mv(i,"opacity",0,12,0,0.35,"easeOut"),mv(i,"opacity",c,c+12,0.35,1,"easeOut")]
        e2=[I("phone","phone",200,140,520),T("sub",200,680,520,56,"订单已提交",44,P['success'],align="center"),E("go","arrow",760,400,320,50,P['text2'],direction="r"),
            queue("q",1100,300,640)]
        a2=[F("phone",0),F("sub",at(0,"订单已提交")),pop("sub",at(0,"订单已提交")),draw("go",at(0,"后面"),18),F("q",at(0,"后面")+10),mv("q","x",at(0,"后面")+10,at(0,"后面")+40,1180,1100)]
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
meta=dict(title="《双十一下单那么多，为什么不丢单？》",episode=9,slug="message-queue",release="v0.13.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）。配音到后：Knoll 的 ep9 timing 存为 timing.mimo.json → map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "贯穿比喻：接第八期后厨——前台发号、号单排进叫号队伍（消息队列）、后厨按自己的节奏做。旁白点出术语：同步、异步、消息队列（MQ）、削峰、生产者、消费者、Kafka、RabbitMQ（各一次），念到时上屏术语标签；一万单/一千单为示意数字，画面标「示意」。画面不重复字幕句子（validate：术语白名单除外）。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/message-queue/。新图标 clock/phone/queue/peak-curve/flat-curve/slip/slip-fallen/guest 自绘无文字；复用 chef/prep-table/ticket/dish-green（第八期）、counter-idle（第六期）、store（第五期）、fridge/spinner（第七期）。branding v1.3.0：只有右上水印（留空区 x1700–1840 y80–130）+ 60 帧片尾卡（全局组件），无中央水印，无自我介绍。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层"),
  dict(id="store",file="assets/store.svg",from_="cdn/assets/store.svg"),dict(id="counter-idle",file="assets/counter-idle.svg",from_="load-balancing/assets/counter-idle.svg"),
  dict(id="fridge",file="assets/fridge.svg",from_="browser-cache/assets/fridge.svg"),dict(id="spinner",file="assets/spinner.svg",from_="browser-cache/assets/spinner.svg")]+
  [dict(id=n,file=f"assets/{n}.svg",from_=f"server-cache/assets/{n}.svg") for n in ("chef","prep-table","ticket","dish-green")],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("clock","phone","queue","peak-curve","flat-curve","slip","slip-fallen","guest","pot")])
PS="peak-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
pl=330  # 写死：peak-2 局部 330（ep9 正式 timing，全局 2612）——「削峰」刚弹出（312–324）、平缓曲线 + 队列 + 后厨都在
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="削峰：虚线尖峰被队列压成平缓曲线，「削峰」标签、叫号队列与后厨",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
