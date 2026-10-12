# EP.05《网站离你那么远，为什么还这么快？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
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
titles=["为什么秒开","都去总仓又远又挤","各地开门店","DNS 指到最近的店","门店没货就回源","回顾"]
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
def store(i,x,y,s=200,empty=False,**k): return A(i,"store-empty" if empty else "store",x,y,s,s,**k)
def wh(i,x,y,s=360,**k): return A(i,"warehouse",x,y,s,s,**k)
def dot(i,x,y,c=P['primary'],s=32): return R(i,x,y,s,s,c,radius=s//2,note="地图上的城市点")
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 为什么秒开：片名卡 → 地图上海 ↔ 美国西海岸 → 140 ms → 好多趟 → 秒开？
        MAP=lambda:A("map","map",160,260,1600,560)
        e1=[T("brand",160,150,1600,60,"我是 IT小村",48,P['primary'],align="center"),
            T("title",160,150,1600,80,"网站离你那么远，为什么还这么快？",60,P['text'],align="center"),
            MAP(),dot("sh",420,470),T("shT",300,520,280,50,"上海（你）",40,P['primary'],align="center"),
            dot("us",1500,470,P['accent']),server("srv",1380,600,280,140,"服务器"),T("usT",1360,400,320,50,"美国西海岸",40,P['accent'],align="center")]
        a1=[F("brand",0),out("brand",at(0,"你在上海")-14,at(0,"你在上海")),F("title",at(0,"你在上海")),F("map",at(0,"你在上海")),F("sh",at(0,"上海")),F("shT",at(0,"上海")),
            F("us",at(0,"服务器")),F("usT",at(0,"美国")),F("srv",at(0,"服务器")),pop("srv",at(0,"服务器"))]
        e2=[A("map","map",160,140,1600,460),dot("sh",420,340),T("shT",300,430,280,50,"上海",40,P['primary'],align="center"),
            dot("us",1500,340,P['accent']),T("usT",1360,430,320,50,"美国西海岸",40,P['accent'],align="center"),
            E("go","arrow",460,300,1030,50,P['primary'],label="光纤",direction="r",fontSize=36),E("back","arrow",460,360,1030,50,P['primary'],direction="l"),
            R("rtt",710,460,500,90,stroke=P['accent'],radius=45,label="来回一趟 约 140 ms",fontSize=44),
            browser(160,640,360,220),T("trips",560,650,600,50,"打开一个网页，要来回好多趟",36,P['text'],align="center")]
        a2=[F("map",0),F("sh",0),F("shT",0),F("us",0),F("usT",0),draw("go",at(0,"光在光纤"),20),draw("back",at(0,"光在光纤")+20,20),F("rtt",at(0,"大约 140")),pop("rtt",at(0,"大约 140")),
            F("browser",at(0,"而打开")),F("trips",at(0,"而打开"))]
        t=at(0,"要来回")
        for j in range(3):
            y=720+j*50; e2.append(E(f"t{j}","arrow",600,y,520,36,P['secondary'],direction="r" if j%2==0 else "l")); a2.append(draw(f"t{j}",t+j*8,10))
        e2+=[T("fast",1240,640,520,90,"秒开？",80,P['accent'],align="center")]
        a2+=[F("fast",at(1,"秒开")),pop("fast",at(1,"秒开"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 都去总仓：一个总仓，四面八方订单 → 大促堵死；总仓 = 源站，挤垮
        e1=[wh("wh",760,180,400),T("whT",760,600,400,56,"总仓",44,P['primary'],align="center"),
            T("shop",160,180,560,56,"只有一个总仓的网店",40,P['text'],align="center"),
            R("promo",1220,180,540,80,stroke=P['danger'],radius=40,label="大促：订单暴增",fontSize=40)]
        a1=[F("shop",0),F("wh",0),F("whT",0)]
        t=at(0,"所有人下单")
        for j,(x,d,y) in enumerate([(160,"r",300),(160,"r",420),(160,"r",540),(1180,"l",300),(1180,"l",420),(1180,"l",540)]):
            far=j in (0,5); e1.append(E(f"o{j}","arrow",x,y,580,40,P['text2'] if far else P['primary'],direction=d)); a1.append(draw(f"o{j}",t+j*5,40 if far else 14))
        e1+=[T("far",160,680,560,50,"离得远，等得久",40,P['text2'],align="center"),T("jam",760,680,400,64,"堵死了",52,P['danger'],align="center")]
        a1+=[F("far",at(0,"离得远")),F("promo",at(0,"大促")),pop("promo",at(0,"大促")),F("jam",at(0,"堵死")),mv("wh","x",at(0,"堵死"),at(0,"堵死")+6,760,770,"linear")]
        e2=[wh("wh",160,200,360),T("whT",160,580,360,56,"总仓",44,P['primary'],align="center"),T("eq",540,330,120,80,"=",64,P['text'],align="center"),
            server("origin",680,240,440,240,"源站"),T("originT",680,500,440,50,"网站自己的服务器",36,P['text2'],align="center")]
        a2=[F("wh",0),F("whT",0),F("eq",at(0,"网站也一样")),F("origin",at(1,"源站")),pop("origin",at(1,"源站")),F("originT",at(1,"网站自己"))]
        t=at(1,"所有人都去")
        for j in range(4):
            y=250+j*60; e2.append(E(f"r{j}","arrow",1160,y,600,40,P['danger'] if j==3 else P['primary'],direction="l")); a2.append(draw(f"r{j}",t+j*6,14))
        e2+=[R("crash",1160,600,600,90,stroke=P['danger'],radius=16,label="人一多，源站可能被挤垮",fontSize=36),T("slow",160,720,960,50,"远的人慢",40,P['text2'],align="center")]
        a2+=[F("slow",at(1,"远的人慢")),F("crash",at(1,"人一多")),pop("crash",at(1,"人一多"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 各地开门店
        e1=[A("map","map",160,220,1600,500),wh("wh",1480,260,200),T("whT",1460,470,240,50,"总仓",40,P['primary'],align="center")]
        a1=[F("map",0),F("wh",0),F("whT",0)]
        t=at(0,"在各地开了")
        for j,(x,y) in enumerate([(300,280),(560,470),(840,300),(1100,480)]):
            e1.append(store(f"s{j}",x,y,150)); a1+=[F(f"s{j}",t+j*8),pop(f"s{j}",t+j*8)]
        e1+=[T("chain",160,140,700,56,"办法：开连锁店",44,P['text'],align="center"),
             R("cdn",160,740,760,100,stroke=P['secondary'],radius=16,label="CDN：内容分发网络",fontSize=44),
             T("edgeT",980,760,780,60,"门店 = 边缘节点",48,P['primary'],align="center")]
        a1+=[F("chain",0),F("cdn",at(1,"CDN")),pop("cdn",at(1,"CDN")),F("edgeT",at(1,"边缘节点"))]
        e2=[store("store",160,200,340),T("storeT",160,560,340,50,"门店",40,P['primary'],align="center"),
            wh("wh",1420,200,340),T("whT",1420,560,340,50,"总仓",40,P['primary'],align="center"),
            A("truck","truck",1240,150,120,120),E("stock","arrow",540,240,860,50,P['accent'],label="提前备货",direction="l",fontSize=40)]
        a2=[F("store",0),F("storeT",0),F("wh",0),F("whT",0),draw("stock",at(0,"提前放到"),30),F("truck",at(0,"图片")),mv("truck","x",at(0,"提前放到"),at(0,"提前放到")+30,1240,560)]
        for j,g in enumerate(["图片","视频","脚本","样式"]):
            e2.append(R(f"g{j}",580+j*200,330,180,70,stroke=P['accent'],radius=12,label=g,fontSize=36)); a2+=[F(f"g{j}",at(0,g)),pop(f"g{j}",at(0,g))]
        e2+=[T("still",580,420,780,44,"不常变的东西",36,P['text2'],align="center"),
             R("you",900,620,160,80,stroke=P['primary'],radius=40,label="你",fontSize=40),E("near","arrow",520,635,370,50,P['success'],label="家门口",direction="l",fontSize=36),
             T("noWh",1420,620,340,50,"不用跑去总仓",36,P['text2'],align="center"),
             R("ms",900,760,560,90,stroke=P['success'],radius=45,label="来回一趟只要几 ms",fontSize=44)]
        a2+=[F("still",at(0,"不常变")),F("you",at(1,"你要的")),draw("near",at(1,"家门口"),15),F("noWh",at(1,"就不用")),F("ms",at(2,"几毫秒")),pop("ms",at(2,"几毫秒"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # DNS：沿用第三期查号台画法（浏览器卡片 → 打电话箭头 → 查号台服务器卡片 + 电话簿）
        e1=[browser(160,260),E("call","arrow",560,340,560,60,P['primary'],label="打电话",direction="r",fontSize=36),
            server("resolver",1160,220,600,300,"查号台"),T("resT",1160,540,600,50,"DNS",40,P['primary'],align="center"),
            A("book","phonebook",740,440,240,240),R("ask",160,140,880,80,stroke=P['primary'],radius=40,label="该去哪家店？",fontSize=40,note="对话气泡（同第三期）"),
            T("ep3",160,740,1600,60,"还记得第三期的 DNS 吗？",48,P['accent'],align="center")]
        a1=[F("browser",0),mv("ask","scale",0,15,0,1,"spring"),F("ask",0),draw("call",at(1,"还记得"),20),F("resolver",at(1,"还记得")),F("book",at(1,"第三期")),F("ep3",at(1,"第三期")),F("resT",at(1,"DNS"))]
        e2=[server("resolver",160,140,400,220,"查号台"),R("ask",160,390,400,80,stroke=P['primary'],radius=40,label="这个网站在哪？",fontSize=36),
            A("map","map",640,140,1120,392),
            store("sBusy",1500,190,140),R("busy",1500,340,140,60,stroke=P['danger'],radius=30,label="忙",fontSize=36),
            store("sFar",860,400,110),store("sNear",860,200,140),
            R("ring",840,180,180,180,"#0B1020",stroke=P['success'],radius=90,note="圈出最近的门店（描边环，画在门店下层）"),
            R("you",690,300,120,64,stroke=P['primary'],radius=32,label="你",fontSize=36),
            R("addr",160,520,400,80,stroke=P['success'],radius=16,label="答：附近门店的地址",fontSize=32),
            E("go","arrow",640,600,1120,50,P['success'],label="被带到附近的店",direction="r",fontSize=36),
            T("skip",640,680,1120,50,"正忙的店会被跳过",36,P['text2'],align="center"),
            T("auto",160,770,1600,60,"你什么都不用做",48,P['text'],align="center")]
        e2=e2[:3]+[e2[7]]+e2[3:7]+e2[8:]  # ring 在门店下层
        a2=[F("resolver",0),F("ask",0),F("map",at(0,"用了 CDN")),F("sFar",at(0,"用了 CDN")),F("sBusy",at(0,"用了 CDN")),F("sNear",at(0,"用了 CDN")),F("you",at(0,"你的位置")),
            F("ring",at(0,"离你近")),pop("ring",at(0,"离你近")),F("addr",at(0,"门店地址")),F("busy",at(0,"避开")),F("skip",at(0,"避开")),mv("sBusy","opacity",at(0,"正忙")+10,at(0,"正忙")+22,1,0.35),
            draw("go",at(1,"就被带到"),18),F("auto",at(1,"你什么"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 回源 / 缓存命中 / 保质期
        e1=[store("store",160,180,340,empty=True),T("storeT",160,530,340,50,"门店",40,P['primary'],align="center"),
            R("shelf",160,600,340,80,stroke=P['danger'],radius=16,label="货架：空",fontSize=40),
            wh("wh",1420,180,340),T("whT",1420,530,340,50,"总仓",40,P['primary'],align="center"),
            E("fetch","arrow",540,260,840,50,P['accent'],label="回总仓取一份",direction="r",fontSize=36),E("back","arrow",540,360,840,50,P['accent'],direction="l"),
            R("give",580,440,360,80,stroke=P['primary'],radius=16,label="一份交给你",fontSize=36),R("keep",980,440,400,80,stroke=P['success'],radius=16,label="一份放上货架",fontSize=36),
            R("origin",660,700,600,100,stroke=P['accent'],radius=50,label="这叫：回源",fontSize=52)]
        a1=[F("store",0),F("storeT",0),F("shelf",at(0,"没货")),F("wh",0),F("whT",0),draw("fetch",at(1,"去总仓"),20),draw("back",at(1,"交给你"),20),
            F("give",at(1,"交给你")),F("keep",at(1,"自己也留")),F("origin",at(1,"这叫回源")),pop("origin",at(1,"这叫回源"))]
        e2=[store("store",160,180,400),T("storeT",160,590,400,50,"门店",40,P['primary'],align="center"),
            R("shelf",160,660,400,80,stroke=P['success'],radius=16,label="货架：有货",fontSize=40),
            R("you",1360,330,240,80,stroke=P['primary'],radius=40,label="下一位",fontSize=40),
            E("take","arrow",600,345,720,50,P['success'],label="直接拿到",direction="l",fontSize=40),
            R("hit",760,560,720,120,stroke=P['success'],radius=60,label="缓存命中",fontSize=60)]
        a2=[F("store",0),F("storeT",0),F("shelf",0),F("you",0),draw("take",at(0,"直接拿到"),18),F("hit",at(0,"缓存命中")),pop("hit",at(0,"缓存命中"))]
        e3=[store("store",160,180,340),T("storeT",160,530,340,50,"门店",40,P['primary'],align="center"),
            R("goods",580,200,440,90,stroke=P['accent'],radius=16,label="保质期：能放多久",fontSize=40),
            R("exp",580,320,440,80,stroke=P['text2'],radius=16,label="到期变灰",fontSize=36),
            wh("wh",1420,180,340),T("whT",1420,530,340,50,"总仓",40,P['primary'],align="center"),
            E("renew","arrow",1040,240,360,50,P['primary'],label="换新的",direction="r",fontSize=36),
            E("notice","arrow",540,460,860,50,P['accent'],label="网站更新：通知门店",direction="l",fontSize=36),
            R("off",580,560,440,80,stroke=P['danger'],radius=16,label="旧货提前下架",fontSize=36),
            T("rule",160,720,1600,60,"过期就回总仓换新，更新可以提前下架",44,P['text'],align="center")]
        a3=[F("store",0),F("storeT",0),F("wh",0),F("whT",0),F("goods",at(0,"保质期")),pop("goods",at(0,"保质期")),F("exp",at(0,"过期了")),
            mv("goods","opacity",at(0,"过期了")+12,at(0,"过期了")+24,1,0.35),draw("renew",at(0,"回总仓"),15),
            draw("notice",at(1,"通知门店"),20),F("off",at(1,"下架")),pop("off",at(1,"下架")),F("rule",at(1,"网站更新"))]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==5:  # 回顾
        nodes=[("n1","DNS 指路","DNS 把你"),("n2","最近的门店","最近的门店"),("n3","有货：直接给","有货就"),("n4","没货：回源","没货就")]
        e1=[];a1=[]
        for j,(i,l,ph) in enumerate(nodes):
            x=160+j*427; e1.append(card(i,x,240,320,110,l,fontSize=36,stroke=P['accent'] if j==3 else P['secondary']))
            t=at(0,ph); a1+=[F(i,max(0,t-4)),mv(i,"scale",t,t+10,1.08,1,"spring")]
            if j<3: e1.append(E(f"ar{j}","arrow",x+320,265,107,60,P['primary'],direction="r")); a1.append(draw(f"ar{j}",t+8,8))
        e1+=[store("store",260,440,240),wh("wh",1420,440,240),E("road","arrow",540,540,840,50,P['success'],label="路近了",direction="l",fontSize=40),
             T("light",160,760,1600,60,"路近了，总仓也轻松了",48,P['success'],align="center")]
        a1+=[F("store",0),F("wh",0),draw("road",at(1,"路近了"),15),F("light",at(1,"总仓也轻松"))]
        e2=[store("store",160,180,300),wh("wh",1460,180,300),
            R("dyn",520,160,880,90,stroke=P['danger'],radius=16,label="订单 / 余额：每个人都不一样",fontSize=40),
            E("direct","arrow",480,330,960,50,P['accent'],label="门店里没有，回总仓拿",direction="r",fontSize=36),
            T("final",160,560,1600,70,"网站离你再远，也能很快打开",56,P['primary'],align="center"),
            T("sign",160,680,1600,64,"我是 IT小村，下期见",48,P['accent'],align="center")]
        te=AEND(5,1)
        a2=[F("store",0),F("wh",0),F("dyn",at(0,"订单")),pop("dyn",at(0,"订单")),draw("direct",at(0,"还是要回"),20),F("final",at(1,"所以")),F("sign",at(2,"我是"))]
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
meta=dict(title="《网站离你那么远，为什么还这么快？》",episode=5,slug="cdn",release="v0.9.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.2.0",endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准 557 字/3937 帧，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）。配音到后：Knoll 的 cdn timing（键 why-1…recap-1）存为 timing.mimo.json → map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+"extraHold：miss-2 末尾 +30 帧纯画面停留（配音不动，后续镜头顺延；common_split.HOLDS，暂定与实测 timing 都自动加上）。"+
   "from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/cdn/。第四章沿用第三期「查号台」画法（浏览器卡片+打电话箭头+查号台服务器卡片+电话簿 phonebook.svg 复用自 dns/assets）。新图标 warehouse/store/store-empty/map/truck 自绘无文字。英文白名单：CDN、DNS、IT、ms。片尾卡与两种水印由全局组件处理。")
assets=dict(reuse=[dict(id="browser",desc="浏览器卡片"),dict(id="server",desc="统一服务器卡片（查号台、源站）"),dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层"),
  dict(id="phonebook",file="assets/phonebook.svg",from_="dns/assets/phonebook.svg"),dict(id="globe",file="assets/globe.svg",from_="dns/assets/globe.svg",used=False)],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("warehouse","store","store-empty","map","truck")])
PS="why-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
pl=349  # Nolan 定：why-2 局部 349（全局 533）
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="上海↔美国西海岸光纤来回 + 「来回一趟 约 140 ms」+ 「秒开？」",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
