# EP.08《数据库明明有数据，为什么还要再存一份？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
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
titles=["明明都有","每单都跑仓库","备菜台","放多久","菜单变了","回顾"]
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
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 明明都有：冰箱 → 门店 → 柜台 → 后厨 → 大仓库
        e1=[I("fridge","fridge",160,300,180,250),I("store","store",400,290,240),I("counter","counter-idle",700,310,220),I("chef","chef",980,300,240),
            T("kT",940,560,320,50,"后厨",40,P['accent'],align="center"),I("wh","warehouse",1320,220,420),I("db","db",1620,520,120),T("dbT",1320,680,420,50,"大仓库 = 数据库",40,P['primary'],align="center")]
        t=at(0,"走进店里")
        a1=[F("fridge",0),out("fridge",t,t+12,0.35),F("store",t),out("store",t+20,t+32,0.35),F("counter",t+20),out("counter",t+40,t+52,0.35),F("chef",t+40),F("kT",t+40),
            F("wh",at(0,"网站的数据")),F("db",at(0,"网站的数据")),F("dbT",at(0,"要什么都有"))]
        e2=[prep("prep",160,380,640),R("copy",160,220,640,90,stroke=P['accent'],radius=16,label="常用：另备一份",fontSize=40),
            I("wh","warehouse",1300,220,440),I("db","db",1620,520,120),E("back","arrow",820,460,460,50,P['text2'],direction="l",dash=True),
            T("q",820,600,460,140,"？",110,P['accent'],align="center")]
        a2=[F("wh",0),F("db",0),F("prep",at(0,"再存一份")),F("copy",at(0,"再存一份")),draw("back",at(0,"再存一份"),15),F("q",at(1,"为什么")),pop("q",at(1,"为什么"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 每单都跑仓库
        e1=[I("counter","counter-idle",160,240,240),I("chef","chef",780,300,220),I("wh","warehouse",1340,200,420),
            R("steps",160,660,1600,90,stroke=P['text2'],radius=16,label="每单：跑一趟仓库",fontSize=40)]
        t=at(0,"每来一个点单")
        a1=[F("counter",0),F("chef",0),F("wh",0)]
        for j in range(3):
            e1.append(I(f"tk{j}","ticket",420,260,90)); s0=t+j*12; a1+=[F(f"tk{j}",s0,6),mv(f"tk{j}","x",s0,s0+20,420,680-j*30),mv(f"tk{j}","y",s0,s0+20,260,260+j*90)]
        a1+=[mv("chef","x",at(0,"跑去"),at(0,"跑去")+30,780,1130),F("steps",at(0,"找到食材"))]
        e2=[R("few",160,200,460,80,stroke=P['success'],radius=16,label="客人少：还行",fontSize=40),R("rush",160,310,460,80,stroke=P['accent'],radius=16,label="饭点",fontSize=40),
            I("wh","warehouse",1340,200,420),A("spin","spinner",1490,330,120,120),I("db","db",1620,520,120)]+[I(f"c{j}","chef",640+j*170,380,150) for j in range(4)]+[
            R("slow",160,700,760,90,stroke=P['danger'],radius=16,label="数据库：慢",fontSize=44)]
        a2=[F("wh",0),F("db",0),F("few",at(0,"客人少")),F("rush",at(0,"饭点"))]+[F(f"c{j}",at(0,"挤满")+j*6) for j in range(4)]+[F("spin",at(1,"人一多")),F("slow",at(1,"压慢")),pop("slow",at(1,"压慢"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 备菜台：命中 / 没命中
        e1=[I("chef","chef",160,300,240),prep("prep",520,330,720),R("lbl",520,700,720,80,stroke=P['accent'],radius=16,label="备菜台",fontSize=44),
            I("wh","warehouse",1440,280,300),T("noRun",1400,600,380,50,"不用跑这里",36,P['text2'],align="center"),I("dish","dish-green",820,330,160),T("grab",160,600,320,50,"伸手就拿",40,P['success'],align="center")]
        tg=at(1,"伸手就拿")
        a1=[F("chef",0),F("prep",at(0,"备菜台")),F("lbl",at(0,"备菜台")),F("wh",0),mv("wh","opacity",0,1,0.35,0.35,"linear"),F("dish",at(1,"热门")),
            mv("dish","x",tg,tg+20,820,380),F("grab",tg),F("noRun",at(1,"不用跑"))]
        # hit-miss-2（v0.12.1 拆分）：第 1 句——服务端缓存 + Redis，画面用备菜台
        e2=[prep("prep",460,220,1000),R("cacheL",460,640,1000,90,stroke=P['accent'],radius=16,label="服务端缓存",fontSize=48),
            T("redis",460,750,1000,50,"Redis：放内存",40,P['primary'],align="center")]
        a2=[F("prep",0),F("cacheL",at(0,"服务端缓存")),pop("cacheL",at(0,"服务端缓存")),F("redis",at(0,"Redis"))]
        # hit-miss-3（新）：第 2 句——缓存命中 / 缓存没命中对比 + 跑仓库箭头
        e3=[prep("prep",160,240,560),T("tag",160,560,560,50,"服务端缓存",40,P['accent'],align="center"),
            R("hit",800,200,960,100,stroke=P['success'],radius=16,label="台上有 → 缓存命中（Cache Hit）",fontSize=40),
            R("miss",800,340,960,100,stroke=P['accent'],radius=16,label="台上没有 → 缓存没命中（Cache Miss）",fontSize=40),
            E("fetch","arrow",800,520,960,50,P['accent'],label="跑一次仓库，回来摆上台",direction="r",fontSize=36),
            R("next",800,640,960,90,stroke=P['success'],radius=16,label="第二单：秒拿",fontSize=40)]
        a3=[F("prep",0),F("tag",0),F("hit",at(0,"缓存命中")),pop("hit",at(0,"缓存命中")),F("miss",at(0,"台上没有")),draw("fetch",at(0,"去仓库拿"),18),F("next",at(0,"下一单"))]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==3:  # 放多久
        e1=[prep("prep",160,300,760),R("hot",1000,260,760,90,stroke=P['success'],radius=16,label="热门菜：上台",fontSize=40),R("cold",1000,400,760,90,stroke=P['text2'],radius=16,label="冷门菜：不上台",fontSize=40),
            T("small",160,700,760,50,"台面有限",40,P['text2'],align="center")]
        a1=[F("prep",0),F("small",at(0,"不大")),F("hot",at(0,"最热门")),F("cold",at(0,"最热门")+10)]
        e2=[];a2=[]
        for j,(lab,c) in enumerate([("还剩 60 秒","green"),("还剩 20 秒","green"),("到点：撤掉","amber")]):
            x=200+j*520; e2+=[I(f"d{j}",f"dish-{c}",x,200,220),I(f"tm{j}","timer",x+230,230,110),R(f"tl{j}",x,440,360,80,stroke=P['accent'] if j==2 else P['success'],radius=16,label=lab,fontSize=36)]
            a2+=[F(f"d{j}",0),F(f"tm{j}",at(0,"过期时间")+j*6),F(f"tl{j}",at(0,"过期时间")+j*6)]
        a2+=[out("d2",at(0,"撤掉"),at(0,"撤掉")+12,0.25)]
        e2+=[R("ttl",160,580,900,90,stroke=P['secondary'],radius=16,label="TTL = 过期时间",fontSize=44),R("exp",1100,580,660,90,stroke=P['secondary'],radius=16,label="EXPIRE：到点自动撤",fontSize=40)]
        a2+=[F("ttl",at(0,"过期时间")),F("exp",at(0,"时间一到"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 菜单变了：更新数据 → 删缓存
        e1=[prep("prep",160,260,640),I("old","dish-amber",330,180,160),I("wh","warehouse",1300,200,420),
            R("p0",1300,640,420,80,stroke=P['text2'],radius=16,label="价格：38",fontSize=40),R("p1",1300,640,420,80,stroke=P['accent'],radius=16,label="价格：42",fontSize=40),
            R("rule",160,640,900,90,stroke=P['accent'],radius=16,label="更新数据 → 删缓存",fontSize=44),T("x",290,130,240,50,"过时了",40,P['danger'],align="center")]
        tc=at(0,"价格调了"); tr=at(1,"马上撤掉")
        a1=[F("prep",0),F("old",0),F("wh",0),F("p0",0),out("p0",tc,tc+12),F("p1",tc+6),F("x",at(1,"不对了")),F("rule",tr),pop("rule",tr),
            out("old",tr,tr+12),out("x",tr,tr+12)]
        e2=[prep("prep",160,320,600),R("miss",160,180,760,90,stroke=P['accent'],radius=16,label="没命中 → 取新货",fontSize=40),I("new","dish-green",380,240,160),
            R("page",1000,200,760,280,stroke=P['danger'],radius=16,label="网页：价格 38",fontSize=48),T("x",1000,500,760,60,"旧价",44,P['danger'],align="center"),
            R("forgot",1000,640,760,90,stroke=P['danger'],radius=16,label="没撤：上错菜",fontSize=40)]
        a2=[F("prep",0),F("miss",at(0,"台上没有")),F("new",at(0,"再摆上来")),pop("new",at(0,"再摆上来")),
            F("forgot",at(1,"要是忘了")),F("page",at(1,"网页上")),F("x",at(1,"旧数据"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾：由近到远 冰箱 → 门店 → 柜台 → 备菜台 → 仓库
        row=lambda:[I("fridge","fridge",190,300,180,250),I("store","store",410,290,260),I("counter","counter-idle",700,310,240),prep("prep",980,340,360),I("wh","warehouse",1420,270,300)]
        labs=[("l0",120,"浏览器缓存",P['primary']),("l1",400,"CDN",P['accent']),("l2",680,"负载均衡",P['text2']),("l3",980,"服务端缓存",P['success']),("l4",1420,"数据库",P['text2'])]
        LB=lambda:[T(i,x,600,300 if i!="l3" else 360,50,t,36,c,align="center") for i,x,t,c in labs]
        # recap-1：只留三层缓存（由近到远），不画柜台/仓库，无底部标签
        e1=[I("fridge","fridge",330,300,200,280),I("store","store",760,290,300),prep("prep",1240,360,440),
            T("l0",280,640,300,50,"浏览器缓存",40,P['primary'],align="center"),T("l1",760,640,300,50,"CDN",40,P['accent'],align="center"),T("l3",1240,640,440,50,"服务端缓存",40,P['success'],align="center")]
        # 开头不空：三组先以 35% 亮度出现，念到「冰箱」「门店」「备菜台」时逐个点亮
        a1=[]
        for ids_,ph in ((("fridge","l0"),"冰箱"),(("store","l1"),"门店"),(("prep","l3"),"备菜台")):
            c=at(0,ph)
            for i in ids_: a1+=[mv(i,"opacity",0,12,0,0.35,"easeOut"),mv(i,"opacity",c,c+12,0.35,1,"easeOut")]
        e2=[R("stack",160,160,1600,80,stroke=P['secondary'],radius=16,label="缓存 + 柜台",fontSize=44)]+row()+LB()+[R("fast",660,720,600,90,stroke=P['success'],radius=45,label="网页秒开",fontSize=48)]
        a2=[F("stack",0)]+[F(i,0) for i in ("fridge","store","prep","wh","l0","l1","l3","l4")]+[F("counter",at(0,"柜台")),F("l2",at(0,"柜台")),pop("counter",at(0,"柜台")),F("fast",at(1,"下次")),pop("fast",at(1,"下次"))]
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
meta=dict(title="《数据库明明有数据，为什么还要再存一份？》",episode=8,slug="server-cache",release="v0.12.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）。配音到后：Knoll 的 ep8 timing 存为 timing.mimo.json → map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "贯穿比喻：店里的后厨。大仓库 = 数据库，备菜台 = 服务端缓存；接第七期冰箱（浏览器缓存）、第五期门店（CDN）、第六期柜台（负载均衡）。英文 Redis / Cache Hit / Cache Miss / TTL / EXPIRE 只上屏不进旁白。画面不重复字幕句子（validate 检查）。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/server-cache/。新图标 chef/prep-table/dish-green/dish-amber/ticket/timer/db 自绘无文字；复用 warehouse/store（第五期）、counter-idle（第六期）、fridge/spinner（第七期）。branding v1.3.0：只有右上水印（留空区 x1700–1840 y80–130）+ 60 帧片尾卡（全局组件），无中央水印，全片无「我是 IT小村」。")
assets=dict(reuse=[dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层"),
  dict(id="warehouse",file="assets/warehouse.svg",from_="cdn/assets/warehouse.svg"),dict(id="store",file="assets/store.svg",from_="cdn/assets/store.svg"),
  dict(id="counter-idle",file="assets/counter-idle.svg",from_="load-balancing/assets/counter-idle.svg"),dict(id="fridge",file="assets/fridge.svg",from_="browser-cache/assets/fridge.svg"),dict(id="spinner",file="assets/spinner.svg",from_="browser-cache/assets/spinner.svg")],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("chef","prep-table","dish-green","dish-amber","ticket","timer","db")])
PS="hit-miss-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
TG=[a for a in sh["animations"] if a["elementId"]=="dish" and a["property"]=="x"][0]["keyframes"]
pl=227  # 写死：hit-miss-1 局部 227（v0.12.1 正式 timing，全局 1505；菜到手边、「伸手就拿」完整）
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="备菜台上伸手就拿：菜盘从台上滑到厨师手边，「备菜台」「伸手就拿」",file="poster.jpg")
import json as _j;from pathlib import Path as _Pc;_CS=_Pc("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=_j.load(open(_CS)).get("server-cache") if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
