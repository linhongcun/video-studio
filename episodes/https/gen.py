import json,re,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
src=open('/workspace/sorkin-backup/https/script.md').read()
narr=re.findall(r'- 旁白：(.+)',src); assert len(narr)==8
CNT=[int(x) for x in re.findall(r'- 字数：(\d+)',src)]
def cnt(s): return len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",success="#22C55E",accent="#F59E0B",danger="#F87171")
# 校准：第一期 +19% 实测 5.53 字/秒（24 镜头 timing.json），每镜头 audio 外留 30 帧
RATE=5.53; PAD=30
def R(i,x,y,w,h,c=P['panel'],**k): return dict(id=i,type="rect",x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def T(i,x,y,w,h,t,fs=40,c=P['text'],**k): return dict(id=i,type="text",x=x,y=y,w=w,h=h,text=t,fontSize=fs,**{"color":c,"reuse":False,**k})
def A(i,name,x,y,w,h,**k): return dict(id=i,type="image",asset=f"assets/{name}.svg",x=x,y=y,w=w,h=h,**{"color":None,"reuse":False,**k})
def E(i,ty,x,y,w,h,c,**k): return dict(id=i,type=ty,x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def fade(i,a=0,b=12): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=0),dict(frame=b,value=1)],easing="easeOut")
def out(i,a,b): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=1),dict(frame=b,value=0)],easing="easeIn")
def mv(i,p,a,b,va,vb,e="easeInOut"): return dict(elementId=i,property=p,keyframes=[dict(frame=a,value=va),dict(frame=b,value=vb)],easing=e)
ids=["intro","plaintext","symmetric","asymmetric","certificate","handshake","integrity","recap"]
titles=["开场","明文的风险","对称加密","非对称加密","证书与 CA","TLS 1.3 握手","完整性与误区","回到那张明信片"]
SPLIT={0:[2,3],1:[2,2],2:[2,1],3:[1,1,1],4:[2,1,1],5:[2,1,2],6:[2,1],7:[1,1]}
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
def browser(x,y,w=360,h=260): return R("browser",x,y,w,h,stroke=P['secondary'],radius=16,label="浏览器",reuse=True)
def server(x,y): return E("server","icon",x,y,240,300,P['secondary'],label="服务器（第一期）",reuse=True)
def shots_for(si,L):
    if si==0:
        e1=[R("laptop",560,200,800,480,stroke=P['secondary'],radius=16,label="咖啡店笔记本（复用第一期浏览器窗口）"),T("wifiTag",600,230,300,44,"公共无线网络",32,P['primary']),
            R("login",760,380,400,80,stroke=P['text2'],radius=10,label="••••••",fontSize=40),A("eve","eavesdropper",1440,300,320,320)]
        a1=[fade("laptop"),fade("wifiTag",10,22),mv("login","charsVisible",30,60,0,6,"linear"),fade("eve",L[0]//2,L[0]//2+20),mv("eve","x",L[0]//2,L[0]-30,1500,1440)]
        e2=[A("lockOpen","padlock-open",560,240,320,320),A("lockClosed","padlock-closed",560,240,320,320),T("q",1000,300,200,200,"？",160,P['primary'],align="center"),T("six",900,600,700,64,"六步讲清楚",48,P['accent'],align="center")]
        a2=[fade("lockOpen"),out("lockOpen",L[1]//3,L[1]//3+12),fade("lockClosed",L[1]//3,L[1]//3+12),mv("lockClosed","scale",L[1]//3+12,L[1]//3+24,1,1.08,"spring"),mv("q","scale",L[1]//2,L[1]//2+20,0,1,"spring"),fade("six",L[1]-90,L[1]-70)]
        return [(e1,a1),(e2,a2)]
    if si==1:
        hops=[R(f"hop{k}",660+k*220,440,140,90,stroke=P['muted'],radius=12,label=f"中转站 {k+1}",fontSize=28) for k in range(3)]
        e1=[browser(120,360),server(1560,320),A("postcard","postcard",200,140,480,300)]+hops+[T("httpTag",120,660,360,50,"HTTP = 明信片",36,P['primary'])]
        a1=[fade("browser"),fade("server"),fade("postcard",10,24)]+[fade(f"hop{k}",20+k*8,32+k*8) for k in range(3)]+[mv("postcard","x",40,L[0]-40,200,1240),fade("httpTag",30,45)]
        risks=[("eye","窃听","偷看内容"),("pencil","篡改","偷改内容"),("mask","伪装","冒充网站")]
        e2=[A("postcard","postcard",660,120,600,375)]
        a2=[fade("postcard")]
        for k,(i,t,d) in enumerate(risks):
            e2+=[E(i,"icon",340+k*440,540,160,160,P['danger'],label=t+"图标"),T(i+"L",280+k*440,710,280,56,t,44,P['danger'],align="center"),T(i+"D",280+k*440,776,280,40,d,30,P['text2'],align="center")]
            t0=20+k*int((L[1]-60)/3); a2+=[mv(i,"scale",t0,t0+15,0,1,"spring"),fade(i+"L",t0+5,t0+18),fade(i+"D",t0+10,t0+22)]
        a2.append(mv("postcard","glowPlaintext",20,40,0,1))
        return [(e1,a1),(e2,a2)]
    if si==2:
        e1=[A("postcard","postcard",200,320,320,200),A("box","envelope-sealed",800,260,320,320),A("lock","padlock-closed",900,180,120,120),A("keyL","key-symmetric",200,620,200,200),A("keyR","key-symmetric",1520,620,200,200),T("same",700,640,520,56,"同一把钥匙，上锁也开锁",40,P['accent'],align="center"),T("fast",700,720,520,44,"速度很快",34,P['success'],align="center")]
        a1=[fade("postcard"),mv("postcard","x",20,60,200,820),out("postcard",55,65),fade("box",50,65),mv("lock","y",70,90,120,180,"spring"),fade("keyL",90,100),fade("keyR",95,105),fade("same",105,120),fade("fast",L[0]-60,L[0]-45)]
        e2=[browser(120,320),server(1560,300),A("keyFly","key-symmetric",560,380,160,160),A("eve","eavesdropper",820,560,280,280),T("q",880,160,160,160,"？",140,P['danger'],align="center")]
        a2=[fade("browser"),fade("server"),mv("keyFly","x",10,L[1]-50,560,880),fade("eve",20,35),mv("eve","y",L[1]-70,L[1]-50,560,480),mv("keyFly","rotate",L[1]-55,L[1]-35,0,15,"spring"),mv("q","scale",L[1]-40,L[1]-25,0,1,"spring")]
        return [(e1,a1),(e2,a2)]
    if si==3:
        e1=[A("pubL","keypair-public",360,260,320,320),A("priL","keypair-private",760,260,320,320),T("pubT",360,620,320,50,"可以公开",36,P['primary'],align="center"),T("priT",760,620,320,50,"只有自己保管",36,P['text2'],align="center"),T("pairT",1180,360,600,64,"一对密钥",56,P['text'])]
        a1=[fade("pairT"),fade("pubL",10,25),fade("pubT",20,32),fade("priL",L[0]//2,L[0]//2+15),fade("priT",L[0]//2+10,L[0]//2+22),mv("priL","opacity",L[0]-40,L[0]-20,1,0.7)]
        n=L[1]; sp=n-60; _s=subs(PARTS[1],n); st=_s[1]["from"]; st2=_s[2]["from"]  # 状态切点=字幕分句起点；旁白后金钥匙停 60 帧
        e2=[A("ecdheA","ecdhe-step4",226,80,1468,780,fit="contain",state="交换公开值"),A("ecdheB","ecdhe-combine",226,80,1468,780,fit="contain",state="各自把收到的公开值与自己的私有值合成"),
            A("ecdheC","ecdhe-step6",226,80,1468,780,fit="contain",state="得到同一把金色钥匙"),A("keyL","key-symmetric",411,566,160,160),A("keyR","key-symmetric",1347,566,160,160),
            T("stA",660,100,600,50,"① 交换公开值",36,P['primary'],align="center"),T("stB",660,100,600,50,"② 各自合成",36,P['primary'],align="center"),T("stC",660,100,600,50,"③ 同一把钥匙",36,P['accent'],align="center")]
        a2=[fade("ecdheA",0,10),fade("stA",0,10),out("stA",st-6,st),fade("ecdheB",st,st+10),fade("stB",st,st+10),out("stB",st2-6,st2),
            fade("ecdheC",st2,st2+10),fade("stC",st2,st2+10),mv("keyL","scale",sp-20,sp,0,1,"spring"),mv("keyR","scale",sp-20,sp,0,1,"spring"),mv("keyL","rotate",sp,n-1,0,8),mv("keyR","rotate",sp,n-1,0,8)]
        e3=[A("keyGold","key-symmetric",200,300,260,260),T("hyb1",520,300,1200,56,"非对称方式：协商出会话密钥（慢，只做一次）",40,P['primary']),A("box","envelope-sealed",520,420,240,240),T("hyb2",820,500,900,56,"对称加密：传输真正的数据（快）",40,P['success'])]
        a3=[fade("keyGold"),fade("hyb1",L[2]//4,L[2]//4+15),fade("box",L[2]//2,L[2]//2+12),fade("hyb2",L[2]//2+10,L[2]//2+25),mv("box","x",L[2]//2+30,L[2]-30,520,1440)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==4:
        e1=[A("pub","keypair-public",400,300,280,280),A("eve","eavesdropper",820,300,300,300),A("fake","keypair-public",1240,300,280,280,tint=P['danger']),T("swap",560,660,800,56,"中间人调包了公钥",44,P['danger'],align="center")]
        a1=[fade("pub"),fade("eve",15,30),mv("pub","x",40,L[0]//2,400,820),out("pub",L[0]//2,L[0]//2+8),fade("fake",L[0]//2,L[0]//2+10),fade("swap",L[0]//2+10,L[0]//2+25)]
        e2=[A("cert","certificate",420,140,720,512),A("ca","ca-badge",1300,200,320,320),T("caT",1240,540,440,56,"CA 签发",44,P['accent'],align="center"),T("certT",420,690,720,50,"证明：这个公钥属于这个网站",38,P['text'],align="center")]
        a2=[fade("cert"),fade("ca",L[1]//4,L[1]//4+15),mv("ca","x",L[1]//4+20,L[1]//2,1300,980),mv("ca","scale",L[1]//2,L[1]//2+12,1.4,1,"spring"),fade("caT",L[1]//4+10,L[1]//4+25),fade("certT",L[1]//2+10,L[1]//2+25)]
        chain=[("root","根证书（系统内置）"),("mid","中间证书"),("leaf","网站证书")]
        e3=[]; a3=[]
        for k,(i,t) in enumerate(chain):
            e3+=[R(i,560,140+k*200,800,130,stroke=P['accent'],radius=16,label=t,fontSize=40),A(i+"Ok","ca-badge",1400,150+k*200,110,110)]
            t0=30+(2-k)*int((L[2]-120)/3); a3+=[fade(i,(2-k)*6,(2-k)*6+12),mv(i+"Ok","drawCheck",t0,t0+20,0,1)]
        e3+=[A("bar","padlock-closed",160,700,140,140),T("barT",320,740,500,56,"地址栏：安全连接",40,P['success'])]
        a3+=[fade("bar",L[2]-70,L[2]-55),fade("barT",L[2]-60,L[2]-45)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==5:
        base=[T("cliL",250,100,400,50,"浏览器",40,align="center"),T("srvL",1270,100,400,50,"服务器",40,align="center"),E("lifeL","line",450,170,0,600,P['secondary']),E("lifeR","line",1470,170,0,600,P['secondary'])]
        h1=E("ch","arrow",450,220,1020,60,P['primary'],label="ClientHello（浏览器问候）",note="支持的算法 + 密钥交换参数",direction="r",fontSize=32)
        h2=E("sh","arrow",450,360,1020,60,P['accent'],label="ServerHello（服务器回应）",note="自己的参数 + 证书 + 签名",direction="l",fontSize=32)
        t1=T("tls13",760,100,400,50,"以 TLS 1.3 为例",36,P["accent"],align="center")
        a1=[fade(i) for i in ["cliL","srvL","lifeL","lifeR"]]+[fade("tls13",10,22),mv("ch","drawProgress",L[0]//2,L[0]-20,0,1)]
        a2=[mv("sh","drawProgress",10,L[1]-30,0,1)]
        e3=base+[h1,h2,A("kL","key-symmetric",310,480,180,180),A("kR","key-symmetric",1380,480,180,180),T("same",660,520,600,56,"各自算出同一把会话密钥",40,P['accent'],align="center"),
            E("data","arrow",450,690,1020,40,P['success'],label="之后全部加密",direction="lr",fontSize=30),R("rtt12",1180,790,600,40,stroke=P['text2'],radius=8,label="TLS 1.2：2 个往返",fontSize=28),R("rtt13",1180,840,600,40,stroke=P['success'],radius=8,label="TLS 1.3：1 个往返",fontSize=28)]
        e3=[e for e in e3]
        for e in e3:
            if e['id'] in("rtt12",): e['y']=770
            if e['id']=="rtt13": e['y']=820
        a3=[mv("kL","scale",10,25,0,1,"spring"),mv("kR","scale",10,25,0,1,"spring"),fade("same",25,40),mv("data","drawProgress",L[2]//3,L[2]//3+30,0,1),fade("rtt12",L[2]-120,L[2]-105),fade("rtt13",L[2]-100,L[2]-85),mv("rtt13","scale",L[2]-80,L[2]-65,1,1.06,"spring")]
        return [(base+[t1,h1],a1),(base+[t1,h1,h2],a2),(e3,a3)]
    if si==6:
        e1=[A("box","envelope-sealed",360,220,420,420),A("hash","hash-check",1100,240,380,380),T("tagT",1000,660,600,50,"每条消息带校验标签",38,P['primary'],align="center"),E("pencil","icon",760,180,120,120,P['danger'],label="铅笔"),T("alarm",300,700,600,56,"改动一个字节，也会被发现",40,P['danger'],align="center")]
        a1=[fade("box"),mv("box","tamperStrip",15,40,0,1),fade("hash",30,45),fade("tagT",40,55),fade("pencil",L[0]//2,L[0]//2+10),mv("pencil","x",L[0]//2+10,L[0]//2+40,760,560),mv("box","tamperAlarm",L[0]//2+40,L[0]//2+50,0,1),mv("hash","badgeDanger",L[0]//2+40,L[0]//2+50,0,1),fade("alarm",L[0]//2+45,L[0]//2+60)]
        e2=[T("scope",360,140,1200,64,"HTTPS 只保护传输过程",52,P['primary'],align="center"),R("c1",260,300,620,320,stroke=P['danger'],radius=20,label="钓鱼网站也能有证书",fontSize=44),R("c2",1040,300,620,320,stroke=P['danger'],radius=20,label="设备中毒，HTTPS 管不了",fontSize=44)]
        a2=[fade("scope"),mv("c1","y",L[1]//3,L[1]//3+20,360,300,"spring"),fade("c1",L[1]//3,L[1]//3+15),mv("c2","y",2*L[1]//3-30,2*L[1]//3-10,360,300,"spring"),fade("c2",2*L[1]//3-30,2*L[1]//3-15)]
        return [(e1,a1),(e2,a2)]
    if si==7:
        e1=[A("postcard","postcard",660,200,600,375),A("box","envelope-sealed",760,180,400,400),A("lock","padlock-closed",880,120,160,160),A("stamp","ca-badge",1080,420,140,140),T("back",560,640,800,56,"同一张明信片",40,P['text2'],align="center")]
        t=L[0]
        a1=[fade("postcard"),fade("back",5,15),mv("postcard","scale",t//5,t//5+20,1,0.4),out("postcard",t//5+15,t//5+25),fade("box",t//5+15,t//5+30),mv("lock","y",t//5+30,t//5+45,60,120,"spring"),fade("lock",t//5+30,t//5+40),mv("stamp","scale",t//2,t//2+12,1.4,1,"spring"),fade("stamp",t//2,t//2+8),mv("box","tamperStrip",3*t//4,3*t//4+20,0,1)]
        trio=[("lockI","padlock-closed","加密防偷看",P['primary']),("caI","ca-badge","证书防冒充",P['accent']),("hashI","hash-check","完整性校验防篡改",P['success'])]
        e2=[];a2=[];n=L[1]
        for k,(i,a,txt,c) in enumerate(trio):
            e2+=[A(i,a,320+k*500,180,280,280),T(i+"T",220+k*500,490,480,56,txt,40,c,align="center")]
            t0=10+k*int((n-120)/3); a2+=[mv(i,"scale",t0,t0+15,0,1,"spring"),fade(i+"T",t0+8,t0+20)]
        e2.append(T("title",260,640,1400,96,"HTTPS 为什么安全",72,P['text'],align="center")); a2.append(mv("title","scale",n-70,n-50,0,1,"spring"))
        return [(e1,a1),(e2,a2)]
def subs(t,L):
    cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',t) if x.strip()]
    m=[]
    for c in cl:
        if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
        else: m.append(c)
    tot=sum(cnt(x) for x in m);res=[];f=0;speak=L-PAD
    for k,c in enumerate(m):
        d=round(speak*cnt(c)/tot); e=min(L-1,f+d-1) if k<len(m)-1 else L-1
        res.append({"text":c.strip().rstrip('，；：。？'),"from":f,"to":e});f=e+1
    return res
scenes=[];g=0;nshot=0;PARTS=[]
for si,s in enumerate(narr):
    S=sentences(s); parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S),(si,len(S)); assert "".join(parts).replace(' ','')==s.replace(' ','')
    parts=[p if k==0 else ' '*0+p for k,p in enumerate(parts)]
    L=[round(cnt(p)/RATE*30)+PAD for p in parts]
    if si==3: L[1]=round(cnt(parts[1])/RATE*30)+60  # ECDHE：旁白后金钥匙停 2 秒，不加旁白
    D=sum(L); est=round((CNT[si]/4.2+2)*30)
    PARTS[:]=parts
    designs=shots_for(si,L); shots=[];f=g
    for k,(p,l) in enumerate(zip(parts,L)):
        els,an=designs[k]
        els=[dict(e) for e in els]+[dict(T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],align="center",role="subtitle"),reuse=True)]
        for a in an:
            for kf in a['keyframes']: kf['frame']=max(0,min(l-1,kf['frame']))
        last=k==len(parts)-1
        shots.append(dict(id=f"{ids[si]}-{k+1}",**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),estimateFormulaFrames=est,shots=shots))
    g+=D
meta=dict(title="《HTTPS 为什么安全？》",episode=2,width=1920,height=1080,fps=30,durationInFrames=g,style="深色背景+蓝青高光扁平2D（沿用第一期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=860),
  notes=f"帧数已按第一期 +19% 实测校准：timing.json 24 镜头合计 5.53 字/秒（公式 字数/4.2 的估算在 +19% 下偏长约 30%），每镜头 = round(字数/5.53×30)+30 帧停顿；scene.estimateFormulaFrames 保留原公式值供对照。配音实测后用 align.py 对齐。from 为全局帧，subtitles 与 keyframes 帧相对镜头；transition 作用于镜头出场。image 元素 asset 路径相对 episodes/https/。密钥交换按 ECDHE（ECDHE 镜头合并为 3 个关键状态 step4 / ecdhe-combine / step6，状态切点跟随字幕分句（约 76/70/88 帧），旁白后金钥匙停 60 帧；两把相同金钥匙 keyL(411,566) / keyR(1347,566) 各 160×160，紧贴 step6 底部两个橙色圆正上方（金色钥匙放进同色圆内看不清），呼应“= 同一把会话密钥 =”，含 8° 慢转不压文字；step1–6 文件保留），双方交换公开参数各自算出会话密钥。画面文字为中文，英文仅 CA/TLS/HTTP/HTTPS；字幕随旁白保留 Wi-Fi、ClientHello、ServerHello、ECDHE、AEAD 原词。")
assets=dict(reuse=[dict(id="browser",desc="第一期浏览器窗口",usedIn=["plaintext","symmetric"]),dict(id="server",desc="第一期服务器图标",usedIn=["plaintext","symmetric"]),dict(id="seqDiagram",desc="第一期握手时序图样式",usedIn=["handshake"]),dict(id="subtitle",desc="字幕层")],
 new=[dict(id=f.stem,file=f"assets/{f.name}") for f in sorted((HERE/"assets").glob("*.svg")) if f.stem!="ecdhe-mix"])
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames'],s['estimateFormulaFrames']) for s in scenes])
_t=os.environ.get("TIMING_JSON") or str(HERE/"timing.json")
if Path(_t).is_file():
    from align import align as _al; print("aligned",_al(Path(_t),HERE/"storyboard.json")["total"])
else: print("skip align: no timing.json (配音实测后放入本目录再运行)")
