# EP.07《同一张图，为什么第二次打开不用再下？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
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
titles=["第二次为什么快","第一次去店里买","第二次直接开冰箱","保质期","过期了先问一句","回顾"]
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
def store(i,x,y,s=200,**k): return A(i,"store",x,y,s,s,**k)
def ctr(i,x,y,s=200,**k): return A(i,"counter-idle",x,y,s,s,**k)
def fridge(i,x,y,w=300,h=420,opened=False,**k): return A(i,"fridge-open" if opened else "fridge",x,y,w,h,**k)
def bx(i,c,x,y,s=100,**k): return A(i,f"box-{c}",x,y,s,s,**k)
def tiles(pre,x0,y0,w=340,h=210,gx=20,gy=20): return [A(f"{pre}{j}","photo",x0+(j%2)*(w+gx),y0+(j//2)*(h+gy),w,h) for j in range(4)]
BROWSER=lambda x,y,w=360,h=220: card("browser",x,y,w,h,"浏览器",reuse=True)
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 第二次为什么快：同一网页左右对比
        e1=[T("aT",160,140,760,50,"第一次",40,P['text2'],align="center"),T("bT",1000,140,760,50,"第二次",40,P['primary'],align="center"),
            R("pageA",160,200,760,520,stroke=P['text2'],radius=16),R("pageB",1000,200,760,520,stroke=P['primary'],radius=16)]+tiles("a",190,240)+tiles("b",1030,240)+[
            A("spin","spinner",490,400,100,100)]
        t=at(0,"第一次打开"); t2=at(0,"关掉再打开")
        a1=[F("aT",0),F("pageA",0),F("spin",t),F("bT",t2),F("pageB",t2)]+[F(f"a{j}",t+20+j*28) for j in range(4)]+[out("spin",t+20+3*28,t+20+3*28+10)]+[F(f"b{j}",at(0,"几乎一下"),6) for j in range(4)]
        e2=[R("same1",160,180,560,80,stroke=P['text2'],radius=16,label="网络：一样",fontSize=40),R("same2",160,290,560,80,stroke=P['text2'],radius=16,label="网站：一样",fontSize=40),
            T("q",160,420,560,130,"？",110,P['accent'],align="center"),
            A("laptop","laptop",800,180,520,520),fridge("fridge",1400,280,260,360),T("fridgeT",1340,660,380,50,"小冰箱",40,P['primary'],align="center")]
        a2=[F("same1",at(0,"网络没变")),F("same2",at(0,"网站也没变")),F("q",at(0,"为什么")),pop("q",at(0,"为什么")),
            F("laptop",at(1,"答案")),F("fridge",at(1,"小冰箱")),pop("fridge",at(1,"小冰箱")),F("fridgeT",at(1,"小冰箱"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 第一次去店里买
        e1=[BROWSER(160,300),A("cart","cart",560,320,180,180),store("store",1000,220,320),T("storeT",1000,560,320,50,"门店（第五期）",36,P['text2'],align="center"),
            ctr("counter",1420,260,320),T("ctrT",1420,600,320,50,"柜台（第六期）",36,P['text2'],align="center")]
        t=at(0,"跑一趟")
        a1=[F("browser",0),F("cart",t),mv("cart","x",t,t+40,560,800),F("store",at(0,"门店")),F("storeT",at(0,"门店")),F("counter",at(0,"柜台")),F("ctrT",at(0,"柜台"))]
        for j,(c,lab,ph) in enumerate([("cyan","图片","图片"),("blue","脚本","脚本"),("green","样式","样式")]):
            e1+=[bx(f"p{j}",c,1060+j*240,680,90),T(f"pT{j}",1160+j*240,700,120,50,lab,36,P['text'])]
            a1+=[F(f"p{j}",at(0,ph)),F(f"pT{j}",at(0,ph))]
        e2=[BROWSER(160,260),fridge("fridge",1300,180,380,520,opened=True),R("cacheL",1260,720,460,90,stroke=P['accent'],radius=16,label="浏览器缓存",fontSize=48),
            T("disk",160,620,1000,56,"本质：浏览器在本机保存的资源副本",44,P['text'],align="center"),T("disk2",160,686,1000,46,"（可能在内存，也可能在硬盘）",36,P['text2'],align="center",note="stock-qa 2026-10-16：第二行小一号")]
        t=at(0,"顺手放进")
        a2=[F("browser",0),F("fridge",t-10),F("cacheL",at(0,"就叫浏览器缓存")),pop("cacheL",at(0,"就叫浏览器缓存")),F("disk",at(1,"它其实")),F("disk2",at(1,"它其实")+6)]
        for j,c in enumerate(["cyan","blue","green"]):
            e2.append(bx(f"p{j}",c,560,300+j*0,90)); s0=t+j*12; a2+=[F(f"p{j}",max(0,s0-10)),mv(f"p{j}","x",s0,s0+30,560+j*110,1390),mv(f"p{j}","y",s0,s0+30,300,280+j*125)]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 第二次直接开冰箱
        e1=[BROWSER(160,300),fridge("fridgeC",640,200,360,500),fridge("fridge",640,200,360,500,opened=True),R("page",1200,200,560,440,stroke=P['primary'],radius=16)]+tiles("t",1230,230,240,180,20,20)+[
            R("noOut",160,600,360,80,stroke=P['success'],radius=40,label="不出门",fontSize=40),R("noQ",160,700,360,80,stroke=P['success'],radius=40,label="不排队",fontSize=40)]
        t=at(0,"先看看冰箱"); tg=at(0,"直接拿出来")
        a1=[F("browser",0),F("fridgeC",0),F("page",0),out("fridgeC",t,t+8),F("fridge",t,8)]+[F(f"t{j}",tg,6) for j in range(4)]+[F("noOut",at(0,"连门")),F("noQ",at(0,"排队"))]
        for j,c in enumerate(["cyan","blue","green"]):
            e1.append(bx(f"p{j}",c,720,260+j*140,80)); a1+=[F(f"p{j}",t),mv(f"p{j}","x",tg,tg+18,720,1240+j*170),mv(f"p{j}","opacity",tg+18,tg+24,1,0)]
        e2=[T("cdnH",160,160,760,56,"CDN：附近门店",44,P['text2'],align="center"),store("store",420,280,240),
            E("trip","arrow",200,600,680,50,P['text2'],label="还得出门",direction="r",fontSize=36,dash=True),R("near",160,700,760,80,stroke=P['text2'],radius=16,label="距离：近",fontSize=40),
            T("cacheH",1000,160,760,56,"浏览器缓存：自家冰箱",44,P['primary'],align="center"),fridge("fridge",1250,250,260,380),
            R("zero",1000,700,760,80,stroke=P['success'],radius=16,label="距离：就在家里",fontSize=40)]
        a2=[F("cdnH",at(0,"CDN")),F("store",at(0,"CDN")),draw("trip",at(0,"离你近")),F("near",at(0,"离你近")),F("cacheH",at(0,"家里的冰箱")),F("fridge",at(0,"家里的冰箱")),
            F("zero",at(1,"门店再近")),pop("zero",at(1,"门店再近"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 保质期
        e1=[fridge("fridge",160,200,360,500,opened=True),R("no",160,740,360,80,stroke=P['danger'],radius=40,label="不行",fontSize=44),
            R("code",640,220,1120,110,stroke=P['secondary'],radius=16,label="Cache-Control: max-age=3600",fontSize=48),
            T("zh",640,360,1120,56,"能放多久：3600 秒",44,P['primary'],align="center")]
        a1=[F("fridge",0),F("no",at(0,"不行")),pop("no",at(0,"不行"))]
        for j,c in enumerate(["cyan","blue","green"]):
            e1+=[bx(f"p{j}",c,700+j*360,470,150),A(f"tag{j}","tag",820+j*360,560,130,86)]; a1+=[F(f"p{j}",0),F(f"tag{j}",at(0,"保质期标签")+j*6),pop(f"tag{j}",at(0,"保质期标签")+j*6)]
        a1+=[F("code",at(0,"写着")),F("zh",at(0,"能放多少秒"))]
        e2=[R("track",160,220,1600,40,P['panel'],stroke=P['text2'],radius=20),R("ok",160,220,960,40,P['success'],radius=20),R("late",1120,220,640,40,P['accent'],radius=20),
            R("okL",160,300,760,90,stroke=P['success'],radius=16,label="没过期 → 强缓存",fontSize=40),R("lateL",1000,300,760,90,stroke=P['accent'],radius=16,label="过期了：要先问",fontSize=40),
            R("short",160,560,760,100,stroke=P['text2'],radius=16,label="常换：短",fontSize=40),R("long",1000,560,760,100,stroke=P['text2'],radius=16,label="图标：很久",fontSize=40)]
        t=at(0,"没过保质期"); t2=at(0,"过了保质期")
        a2=[F("track",0),F("ok",t),F("okL",t),F("late",t2),F("lateL",t2),F("short",at(1,"常换")),F("long",at(1,"几乎不变"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 过期了先问一句（v0.12.2：拆 3 镜头）
        # revalidate-1：过期不一定重买 + 带 ETag 去问
        e1=[BROWSER(160,240),bx("old","amber",260,500,120),R("etag",160,660,420,80,stroke=P['accent'],radius=16,label="ETag：编号 37",fontSize=40),
            ctr("counter",1360,220,360),E("ask","arrow",580,320,760,50,P['primary'],label="这份还新鲜吗？",direction="r",fontSize=36),
            R("exp",640,620,620,90,stroke=P['accent'],radius=16,label="过期 ≠ 重新买",fontSize=40)]
        a1=[F("browser",0),F("old",0),F("counter",0),F("exp",at(0,"不一定")),F("etag",at(0,"ETag")),pop("etag",at(0,"ETag")),draw("ask",at(0,"去问店里"),18)]
        # revalidate-2：304 没变 + 一问一答 = 协商缓存
        e2=[BROWSER(160,240),bx("old","amber",260,500,120),bx("fresh","green",260,500,120),R("etag",160,660,420,80,stroke=P['accent'],radius=16,label="ETag：编号 37",fontSize=40),
            ctr("counter",1360,220,360),E("ask","arrow",580,320,760,50,P['primary'],label="这份还新鲜吗？",direction="r",fontSize=36),
            E("reply","arrow",580,460,760,50,P['success'],label="304 Not Modified",direction="l",fontSize=40),R("same",1360,620,360,90,stroke=P['success'],radius=45,label="没变",fontSize=48),
            R("neg",640,640,640,90,stroke=P['secondary'],radius=16,label="一问一答 = 协商缓存",fontSize=40)]
        tr=at(0,"店里只回")
        a2=[F("browser",0),F("old",0),F("etag",0),F("counter",0),F("ask",0),draw("reply",tr,18),F("same",tr+10),pop("same",tr+10),
            mv("fresh","opacity",0,tr+20,0,0,"linear"),F("fresh",tr+20),out("old",tr+20,tr+32),F("neg",at(0,"这一问一答")),pop("neg",at(0,"这一问一答"))]  # 句首即出：句子短，给标签留足时间
        # revalidate-3：变了才重新下载 + 换文件名（画面不写「旧货」）
        e3=[fridge("fridge",160,200,360,500,opened=True),ctr("counter",1400,200,320),
            E("newA","arrow",560,300,820,50,P['accent'],label="变了：给新货",direction="l",fontSize=36),bx("newBox","cyan",1240,380,110),
            R("old",600,500,460,90,stroke=P['text2'],radius=16,label="logo.v1.png",fontSize=40),R("new",1100,500,520,90,stroke=P['accent'],radius=16,label="logo.v2.png",fontSize=40),
            T("rename",560,640,1200,56,"改名 = 新货",44,P['text'],align="center")]
        tn=at(0,"要是变了"); tf=at(0,"文件名")
        a3=[F("fridge",0),F("counter",0),draw("newA",tn,18),F("newBox",tn+6),mv("newBox","x",tn+6,tn+36,1240,600),F("old",tf),F("new",tf+10),pop("new",tf+10),
            mv("old","opacity",tf+24,tf+36,1,0.35),F("rename",tf+24)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==5:  # 回顾：冰箱 → 门店 → 柜台 三层
        e1=[fridge("fridge",200,240,260,360),T("l1",160,640,400,50,"浏览器缓存：最近",36,P['primary'],align="center"),
            E("a1","arrow",500,400,240,50,P['text2'],direction="r"),store("store",780,260,320),T("l2",740,640,400,50,"CDN：离你近",36,P['accent'],align="center"),
            E("a2","arrow",1120,400,200,50,P['text2'],direction="r")]+[ctr(f"c{j}",1340+j*140,330,130) for j in range(3)]+[T("l3",1320,640,440,50,"负载均衡：抗高峰",36,P['success'],align="center")]
        a1=[F("fridge",at(0,"浏览器缓存")),F("l1",at(0,"浏览器缓存")),draw("a1",at(0,"CDN"),12),F("store",at(0,"CDN")),F("l2",at(0,"CDN")),draw("a2",at(0,"负载均衡"),12)]+[F(f"c{j}",at(0,"负载均衡")+4*j) for j in range(3)]+[F("l3",at(0,"负载均衡"))]
        e2=[R("stack",160,160,1600,90,stroke=P['secondary'],radius=16,label="冰箱 + 门店 + 柜台",fontSize=44),fridge("fridge",200,320,260,360),
            R("page",640,300,1120,500,stroke=P['primary'],radius=16)]+tiles("t",680,340,500,200,20,20)+[R("instant",160,720,400,80,stroke=P['success'],radius=40,label="秒出图",fontSize=44)]
        t=at(1,"下次网页")
        a2=[F("stack",0),F("fridge",0),F("page",at(1,"下次")),F("instant",at(1,"秒出图")),pop("instant",at(1,"秒出图"))]+[F(f"t{j}",at(1,"秒出图"),6) for j in range(4)]
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
meta=dict(title="《同一张图，为什么第二次打开不用再下？》",episode=7,slug="browser-cache",release="v0.11.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）。配音到后：Knoll 的 ep7 timing 存为 timing.mimo.json → map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+
   "贯穿比喻：自家冰箱 = 浏览器缓存；门店 = CDN（第五期）；柜台 = 负载均衡后的服务器（第六期）。英文术语 Cache-Control / max-age / ETag / 304 Not Modified 只上屏不进旁白。画面不重复字幕句子（validate 检查）。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/browser-cache/。新图标 fridge/fridge-open/photo/box-*/tag/spinner/laptop/cart 自绘无文字；复用 store/counter-idle（第五、六期）。branding v1.3.0：只有右上水印（留空区 x1700–1840 y80–130）+ 60 帧片尾卡（全局组件），无中央水印，全片无「我是 IT小村」。")
assets=dict(reuse=[dict(id="browser",desc="浏览器卡片"),dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层"),
  dict(id="store",file="assets/store.svg",from_="cdn/assets/store.svg"),dict(id="counter-idle",file="assets/counter-idle.svg",from_="load-balancing/assets/counter-idle.svg")],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("fridge","fridge-open","photo","box-cyan","box-blue","box-green","box-amber","tag","spinner","laptop","cart")])
PS="second-1"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
AT_TG=[a for a in sh["animations"] if a["elementId"]=="t0"][0]["keyframes"][0]["frame"]
pl=152  # 定稿：second-1 局部 152（冰箱打开、货包飞向页面、图片瞬间全出）
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="冰箱打开那一刻：三个货包飞向页面，图片瞬间全出",file="poster.jpg")
import json as _j;from pathlib import Path as _Pc;_CS=_Pc("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=_j.load(open(_CS)).get("browser-cache") if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
