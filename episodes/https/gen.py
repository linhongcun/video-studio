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
def browser(x,y,w=360,h=260): return R("browser",x,y,w,h,stroke=P['secondary'],radius=16,label="浏览器",fontSize=36,reuse=True)
def server(x,y): return R("server",x,y,240,300,stroke=P['secondary'],radius=16,label="服务器",fontSize=36,reuse=True,note="服务器卡片：与浏览器同一套样式（panel 底、secondary 描边、圆角 16），无窗口圆点，标签「服务器」36px；Knoll 实现")
LABEL_HOLDS=json.load(open(HERE/"label_holds.json")) if (HERE/"label_holds.json").is_file() else {}
EXTRA_HOLD={"asymmetric-2":40}  # 2026-10-14：handshake-3 +25 已撤回（导演定不加 hold）
#  # 导演决定：ECDHE 金钥匙完整停留 ≥60 帧；timing.json duration + 额外停顿（Knoll 时间线同样加）
TM=json.load(open(HERE/"timing.json")) if (HERE/"timing.json").is_file() else None
def AT(si,k,phrase,L=None):
    """镜头内某短语的起始帧：timing.json 的句子 start/dur + 句内按字数比例；无 timing 时按字数估算"""
    p=PARTS[k]; S=sentences(p); i=next(j for j,s in enumerate(S) if phrase in s); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s))
    if TM:
        q=TM[f"{ids[si]}-{k+1}"]["sentences"]; assert len(q)==len(S),(si,k)
        return round(30*(q[i]["start"]+q[i]["dur"]*off))
    before=cnt("".join(S[:i]))+cnt(s[:s.index(phrase)]); return round(before/RATE*30)
def AEND(si,k):
    if TM: return TM[f"{ids[si]}-{k+1}"]["audioFrames"]
    return round(cnt(PARTS[k])/RATE*30)
def shots_for(si,L):
    if si==0:
        e1=[R("laptop",385,120,1150,640,stroke=P['secondary'],radius=20,note="咖啡店笔记本（复用第一期浏览器窗口，无标签）"),T("wifiTag",430,150,400,50,"公共无线网络",40,P['primary']),
            T("loginT",660,330,600,56,"登录",48,P['text'],align="center"),R("login",660,410,600,110,stroke=P['text2'],radius=12,label="••••••",fontSize=56),
            A("cup","coffee-cup",130,600,140,140),T("cafe",110,760,180,50,"咖啡店",36,P['text2'],align="center"),A("eve","eavesdropper",1580,520,220,220,note="邻座人影，半透明 0.6")]
        a1=[fade("laptop"),fade("wifiTag",10,22),mv("login","charsVisible",30,60,0,6,"linear"),fade("cup",0,12),fade("cafe",4,16),fade("loginT",8,20),mv("eve","opacity",AT(0,0,"同一个网络"),AT(0,0,"同一个网络")+20,0,0.6),mv("eve","x",AT(0,0,"同一个网络"),AEND(0,0),1620,1580)]
        e2=[A("lockOpen","padlock-open",560,240,320,320),A("lockClosed","padlock-closed",560,240,320,320),T("q",1000,300,200,200,"？",160,P['primary'],align="center"),T("six",900,600,700,64,"六步讲清楚",48,P['accent'],align="center")]
        a2=[fade("lockOpen"),out("lockOpen",AT(0,1,"看不到"),AT(0,1,"看不到")+12),fade("lockClosed",AT(0,1,"看不到"),AT(0,1,"看不到")+12),mv("lockClosed","scale",AT(0,1,"看不到")+12,AT(0,1,"看不到")+24,1,1.08,"spring"),mv("q","scale",AT(0,1,"它凭什么"),AT(0,1,"它凭什么")+20,0,1,"spring"),fade("six",AT(0,1,"我们分六步"),AT(0,1,"我们分六步")+15)]
        return [(e1,a1),(e2,a2)]
    if si==1:
        hops=[R(f"hop{k}",660+k*220,440,140,90,stroke=P['muted'],radius=12,label=f"中转站 {k+1}",fontSize=28) for k in range(3)]
        e1=[browser(120,360),server(1560,320),A("postcard","postcard-mini",200,140,480,300)]+hops+[T("httpTag",120,660,360,50,"HTTP = 明信片",36,P['primary'])]
        a1=[fade("browser"),fade("server"),fade("postcard",10,24)]+[fade(f"hop{k}",20+k*8,32+k*8) for k in range(3)]+[mv("postcard","x",40,L[0]-40,200,1240),fade("httpTag",AT(1,0,"它传数据"),AT(1,0,"它传数据")+15)]
        risks=[("eye","窃听","偷看内容"),("pencil","篡改","偷改内容"),("mask","伪装","冒充网站")]
        e2=[A("postcard","postcard",480,80,960,600)]
        a2=[fade("postcard")]
        for k,(i,t,d) in enumerate(risks):
            e2+=[A(i,i,300+k*480,700,100,100),T(i+"L",420+k*480,700,240,56,t,44,P['danger']),T(i+"D",420+k*480,762,240,40,d,30,P['text2'])]
            t0=AT(1,1,["别人可以偷看","可以偷改","还可以冒充"][k]); a2+=[mv(i,"scale",t0,t0+15,0,1,"spring"),fade(i+"L",t0+5,t0+18),fade(i+"D",t0+10,t0+22)]
        a2.append(mv("postcard","glowPlaintext",20,40,0,1))
        return [(e1,a1),(e2,a2)]
    if si==2:
        e1=[A("postcard","postcard-mini",200,320,320,200),A("box","envelope-sealed",800,260,320,320),A("lock","padlock-closed",900,180,120,120),A("keyL","key-symmetric",200,620,200,200),A("keyR","key-symmetric",1520,620,200,200),T("same",700,640,520,56,"同一把钥匙，上锁也开锁",40,P['accent'],align="center"),T("fast",700,720,520,44,"速度很快",34,P['success'],align="center")]
        a1=[fade("postcard"),mv("postcard","x",5,30,200,820),out("postcard",28,36),fade("box",24,36),mv("lock","y",AT(2,0,"对称加密用")-8,AT(2,0,"对称加密用")+8,120,180,"spring"),fade("keyL",AT(2,0,"对称加密用"),AT(2,0,"对称加密用")+10),fade("keyR",AT(2,0,"对称加密用")+5,AT(2,0,"对称加密用")+15),fade("same",AT(2,0,"对称加密用")+15,AT(2,0,"对称加密用")+30),fade("fast",AT(2,0,"速度很快"),AT(2,0,"速度很快")+15)]
        e2=[R("browser",200,220,440,320,stroke=P['secondary'],radius=16,label="浏览器",fontSize=36,reuse=True),dict(server(1340,200),w=300,h=360,fontSize=36),A("keyFly","key-symmetric",740,180,400,400),A("eve","eavesdropper",820,600,260,260),T("q",1150,120,140,140,"？",120,P['danger'],align="center")]
        a2=[fade("browser"),fade("server"),mv("keyFly","x",10,L[1]-50,700,780),fade("eve",20,35),mv("eve","y",AT(2,1,"可路上"),AT(2,1,"可路上")+20,600,560),mv("keyFly","rotate",AT(2,1,"可路上")+15,AT(2,1,"可路上")+35,0,15,"spring"),mv("q","scale",AEND(2,1)-15,AEND(2,1),0,1,"spring")]
        return [(e1,a1),(e2,a2)]
    if si==3:
        e1=[A("pubL","keypair-public",360,260,320,320),A("priL","keypair-private",760,260,320,320),T("pubT",360,620,320,50,"可以公开",36,P['primary'],align="center"),T("priT",760,620,320,50,"只有自己保管",36,P['text2'],align="center"),T("pairT",1180,360,600,64,"一对密钥",56,P['text'])]
        a1=[fade("pairT"),fade("pubL",10,25),fade("pubT",20,32),fade("priL",AT(3,0,"私钥只有"),AT(3,0,"私钥只有")+15),fade("priT",AT(3,0,"私钥只有")+10,AT(3,0,"私钥只有")+22),mv("priL","opacity",L[0]-40,L[0]-20,1,0.7)]
        n=L[1]; st=AT(3,1,"就能算出"); st2=AT(3,1,"偷听的人"); kp=min(st2+12,AEND(3,1)-20)  # 状态切点=实测句内短语起点；金钥匙在状态③开头弹出，停到镜头结束
        e2=[A("ecdheA","ecdhe-step4",226,80,1468,780,fit="contain",state="交换公开值"),A("ecdheB","ecdhe-combine",226,80,1468,780,fit="contain",state="各自把收到的公开值与自己的私有值合成"),
            A("ecdheC","ecdhe-step6",226,80,1468,780,fit="contain",state="得到同一把金色钥匙"),A("keyL","key-symmetric",411,566,160,160),A("keyR","key-symmetric",1347,566,160,160),
            T("stA",660,100,600,50,"① 临时生成，交换公开值",36,P['primary'],align="center"),T("stB",660,100,600,50,"② 各自合成",36,P['primary'],align="center"),T("stC",660,100,600,50,"③ 同一把钥匙",36,P['accent'],align="center"),
            R("sig",160,90,460,64,stroke=P['text2'],radius=32,label="证书私钥 ≠ 会话密钥",fontSize=32)]  # 2026-10-14 内容核对：会话密钥由双方临时密钥算出，证书私钥只签名（不当会话密钥用）
        a2=[fade("ecdheA",0,10),fade("stA",0,10),out("stA",st-6,st),fade("ecdheB",st,st+10),fade("stB",st,st+10),out("stB",st2-6,st2),
            fade("ecdheC",st2,st2+10),fade("stC",st2,st2+10),mv("keyL","scale",kp,kp+15,0,1,"spring"),mv("keyR","scale",kp,kp+15,0,1,"spring"),mv("keyL","rotate",kp+15,n-1,0,8),mv("keyR","rotate",kp+15,n-1,0,8),fade("sig",AT(3,1,"证书里的私钥"),AT(3,1,"证书里的私钥")+12)]
        e3=[A("keyGold","key-symmetric",200,300,260,260),T("hyb1",520,300,1200,56,"非对称方式：协商出会话密钥（慢，只做一次）",40,P['primary']),A("box","envelope-sealed",520,420,240,240),T("hyb2",820,500,900,56,"对称加密：传输真正的数据（快）",40,P['success'])]
        a3=[fade("keyGold"),fade("hyb1",AT(3,2,"先用非对称"),AT(3,2,"先用非对称")+15),fade("box",AT(3,2,"再用它"),AT(3,2,"再用它")+12),fade("hyb2",AT(3,2,"再用它")+10,AT(3,2,"再用它")+25),mv("box","x",AT(3,2,"再用它")+30,L[2]-10,520,1440)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==4:
        e1=[A("pub","keypair-public",400,300,280,280),A("eve","eavesdropper",820,300,300,300),A("fake","keypair-public",1240,300,280,280,tint=P['danger']),T("swap",560,660,800,56,"中间人调包了公钥",44,P['danger'],align="center")]
        a1=[fade("pub"),fade("eve",15,30),mv("pub","x",AT(4,0,"可能被"),AT(4,0,"调了包"),400,820),out("pub",AT(4,0,"调了包"),AT(4,0,"调了包")+8),fade("fake",AT(4,0,"调了包"),AT(4,0,"调了包")+10),fade("swap",AT(4,0,"调了包"),AT(4,0,"调了包")+8)]
        e2=[A("cert","certificate",420,140,720,512),A("ca","ca-badge",1300,200,320,320),T("caT",1240,540,440,56,"CA 签发",44,P['accent'],align="center"),T("certT",420,690,720,50,"证明：这个公钥属于这个网站",38,P['text'],align="center")]
        a2=[fade("cert"),fade("ca",8,20),fade("caT",14,28),mv("ca","x",22,AT(4,1,"证明这个")-2,1300,980),mv("ca","scale",AT(4,1,"证明这个")-2,AT(4,1,"证明这个")+10,1.4,1,"spring"),fade("certT",AT(4,1,"证明这个"),AT(4,1,"证明这个")+15)]
        chain=[("root","根证书（受信任）"),("mid","中间证书"),("leaf","网站证书")]
        e3=[]; a3=[]
        for k,(i,t) in enumerate(chain):
            e3+=[R(i,560,140+k*200,800,130,stroke=P['accent'],radius=16,label=t,fontSize=40),A(i+"Ok","ca-badge",1400,150+k*200,110,110)]
            t0=AT(4,2,"一路校验")+(2-k)*int((AT(4,2,"全部通过")-AT(4,2,"一路校验"))/3); a3+=[fade(i,(2-k)*6,(2-k)*6+12),mv(i+"Ok","drawCheck",t0,t0+20,0,1)]
        e3+=[A("bar","padlock-closed",160,700,140,140),T("barT",320,740,500,56,"地址栏：安全连接",40,P['success'])]
        a3+=[fade("bar",AT(4,2,"才确认"),AT(4,2,"才确认")+15),fade("barT",AT(4,2,"才确认")+10,AT(4,2,"才确认")+25)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==5:
        base=[T("cliL",250,100,400,50,"浏览器",40,align="center"),T("srvL",1270,100,400,50,"服务器",40,align="center"),E("lifeL","line",450,170,0,600,P['secondary']),E("lifeR","line",1470,170,0,600,P['secondary'])]
        h1=E("ch","arrow",450,220,1020,60,P['primary'],label="ClientHello（浏览器问候）",note="支持的算法 + 密钥交换参数",direction="r",fontSize=32)
        h2=E("sh","arrow",450,360,1020,60,P['accent'],label="ServerHello（服务器回应）",note="自己的参数 + 证书 + 签名",direction="l",fontSize=32)
        t1=T("tls13",760,100,400,50,"以 TLS 1.3 为例",36,P["accent"],align="center")
        a1=[fade(i) for i in ["cliL","srvL","lifeL","lifeR"]]+[fade("tls13",AT(5,0,"以 TLS"),AT(5,0,"以 TLS")+12),mv("ch","drawProgress",AT(5,0,"浏览器发出"),AEND(5,0),0,1)]
        a2=[mv("sh","drawProgress",AT(5,1,"服务器回"),AT(5,1,"附上"),0,1),fade("shN",AT(5,1,"附上"),AT(5,1,"附上")+10)]
        shN=T("shN",450,430,1020,48,"+ 参数 + 证书 + 签名",34,P["accent"],align="center")
        e3=base+[h1,h2,A("kL","key-symmetric",310,480,180,180),A("kR","key-symmetric",1380,480,180,180),T("same",660,520,600,56,"各自算出同一把会话密钥",40,P['accent'],align="center"),
            E("data","arrow",450,690,1020,40,P['success'],label="之后全部加密",direction="lr",fontSize=30),R("rtt12",1180,790,600,40,stroke=P['text2'],radius=8,label="完整握手 · TLS 1.2：2 个往返",fontSize=28),R("rtt13",1180,840,600,40,stroke=P['success'],radius=8,label="完整握手 · TLS 1.3：1 个往返",fontSize=28)]
        e3=[e for e in e3]
        for e in e3:
            if e['id'] in("rtt12",): e['y']=770
            if e['id']=="rtt13": e['y']=820
        a3=[mv("kL","scale",10,25,0,1,"spring"),mv("kR","scale",10,25,0,1,"spring"),fade("same",AT(5,2,"各自算出"),AT(5,2,"各自算出")+15),mv("data","drawProgress",AT(5,2,"之后的通信"),AT(5,2,"之后的通信")+30,0,1),fade("rtt12",AT(5,2,"TLS 1.2"),AT(5,2,"TLS 1.2")+15),fade("rtt13",AT(5,2,"1.3 只要"),AT(5,2,"1.3 只要")+15),mv("rtt13","scale",AT(5,2,"1.3 只要")+15,AT(5,2,"1.3 只要")+30,1,1.06,"spring")]
        return [(base+[t1,h1],a1),(base+[t1,h1,h2,shN],a2),(e3+[shN],a3)]
    if si==6:
        e1=[A("box","envelope-sealed",360,220,420,420),A("hash","hash-check",1100,240,380,380),T("tagT",1000,660,600,50,"每条消息带校验标签",38,P['primary'],align="center"),A("pencil","pencil",760,180,120,120),T("alarm",300,700,600,56,"改动一个字节，也会被发现",40,P['danger'],align="center")]
        a1=[fade("box"),mv("box","tamperStrip",AT(6,0,"TLS 1.3 用"),AT(6,0,"TLS 1.3 用")+25,0,1),fade("hash",AT(6,0,"每条消息"),AT(6,0,"每条消息")+15),fade("tagT",AT(6,0,"每条消息")+10,AT(6,0,"每条消息")+25),fade("pencil",AT(6,0,"路上哪怕"),AT(6,0,"路上哪怕")+10),mv("pencil","x",AT(6,0,"路上哪怕")+10,AT(6,0,"也会被发现"),760,560),mv("box","tamperAlarm",AT(6,0,"也会被发现"),AT(6,0,"也会被发现")+10,0,1),mv("hash","badgeDanger",AT(6,0,"也会被发现"),AT(6,0,"也会被发现")+10,0,1),fade("alarm",AT(6,0,"也会被发现")+5,AT(6,0,"也会被发现")+20)]
        e2=[T("scope",360,140,1200,64,"HTTPS 只保护传输过程",52,P['primary'],align="center"),R("c1",260,300,620,320,stroke=P['danger'],radius=20,label="钓鱼网站也能有证书",fontSize=44),R("c2",1040,300,620,320,stroke=P['danger'],radius=20,label="设备中毒，HTTPS 管不了",fontSize=44)]
        a2=[fade("scope"),mv("c1","y",AT(6,1,"它不保证"),AT(6,1,"它不保证")+20,360,300,"spring"),fade("c1",AT(6,1,"它不保证"),AT(6,1,"它不保证")+15),mv("c2","y",AT(6,1,"也不保护"),AT(6,1,"也不保护")+20,360,300,"spring"),fade("c2",AT(6,1,"也不保护"),AT(6,1,"也不保护")+15)]
        return [(e1,a1),(e2,a2)]
    if si==7:
        e1=[A("postcard","postcard",480,80,960,600),A("box","envelope-sealed",760,180,400,400),A("lock","padlock-closed",880,120,160,160),A("stamp","ca-badge",1080,420,140,140),T("back",560,700,800,56,"同一张明信片",40,P['text2'],align="center")]
        t=L[0]; a=AT(7,0,"现在它被锁进"); b=AT(7,0,"盖了邮局"); c=AT(7,0,"还贴上")
        a1=[fade("postcard"),fade("back",5,15),mv("postcard","scale",a,a+20,1,0.4),out("postcard",a+15,a+25),fade("box",a+15,a+30),mv("lock","y",a+30,a+45,60,120,"spring"),fade("lock",a+30,a+40),mv("stamp","scale",b,b+12,1.4,1,"spring"),fade("stamp",b,b+8),mv("box","tamperStrip",c,c+20,0,1)]
        trio=[("lockI","padlock-closed","加密防偷看",P['primary']),("caI","ca-badge","证书防冒充",P['accent']),("hashI","hash-check","完整性校验防篡改",P['success'])]
        e2=[];a2=[];n=L[1]
        for k,(i,a,txt,c) in enumerate(trio):
            e2+=[A(i,a,320+k*500,180,280,280),T(i+"T",220+k*500,490,480,56,txt,40,c,align="center")]
            t0=AT(7,1,["加密防偷看","证书防冒充","完整性校验"][k]); a2+=[mv(i,"scale",t0,t0+15,0,1,"spring"),fade(i+"T",t0+8,t0+20)]
        e2.append(T("title",260,640,1400,96,"HTTPS 为什么安全",72,P['text'],align="center")); a2.append(mv("title","scale",AT(7,1,"这就是"),AT(7,1,"这就是")+20,0,1,"spring"))
        return [(e1,a1),(e2,a2)]
def subs(t,L,si=None,k=None):
    if TM and si is not None: return subs_tm(t,L,si,k)
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
def subs_tm(t,L,si,k):
    S=sentences(t);q=TM[f"{ids[si]}-{k+1}"]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
            else: m.append(c)
        tot=sum(cnt(x) for x in m);acc=0
        for c in m:
            res.append({"text":c.strip().rstrip('，；：。？'),"from":round(30*(qq["start"]+qq["dur"]*acc/tot))});acc+=cnt(c)
    for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    return res
scenes=[];g=0;nshot=0;PARTS=[]
for si,s in enumerate(narr):
    S=sentences(s); parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S),(si,len(S)); assert "".join(parts).replace(' ','')==s.replace(' ','')
    parts=[p if k==0 else ' '*0+p for k,p in enumerate(parts)]
    L=[round(cnt(p)/RATE*30)+PAD for p in parts]
    if si==3: L[1]=round(cnt(parts[1])/RATE*30)+60  # ECDHE：旁白后金钥匙停 2 秒，不加旁白
    if TM: L=[TM[f"{ids[si]}-{k+1}"]["duration"]+(0 if "extraHold" in TM[f"{ids[si]}-{k+1}"] else EXTRA_HOLD.get(f"{ids[si]}-{k+1}",0)) for k in range(len(parts))]
    if TM: L=[x+LABEL_HOLDS.get(f"{ids[si]}-{k+1}",0) for k,x in enumerate(L)]  # 2026-10-14 Nolan：术语标签最短 hold（_audit/labelfix.py → label_holds.json），镜头末尾静音  # 实测配音：镜头时长=timing.json duration（Knoll 缩放比=1）；MiMo 版 timing.json 条目自带 extraHold 字段，duration 已含 40 帧，此时不再叠加 EXTRA_HOLD，避免重复计算
    D=sum(L); est=round((CNT[si]/4.2+2)*30)
    PARTS[:]=parts
    designs=shots_for(si,L); shots=[];f=g
    for k,(p,l) in enumerate(zip(parts,L)):
        els,an=designs[k]
        els=[dict(e) for e in els]+[dict(T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],align="center",role="subtitle"),reuse=True)]
        for a in an:
            for kf in a['keyframes']: kf['frame']=max(0,min(l-1,kf['frame']))
        last=k==len(parts)-1
        shots.append(dict(id=f"{ids[si]}-{k+1}",**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),estimateFormulaFrames=est,shots=shots))
    g+=D
meta=dict(title="《HTTPS 为什么安全？》",episode=2,width=1920,height=1080,fps=30,durationInFrames=g,style="深色背景+蓝青高光扁平2D（沿用第一期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=860),
  notes=f"镜头时长 = 实测配音 timing.json（MiMo「冰糖」，句间停顿 0.28 秒）各镜头 duration，Knoll 缩放比为 1；无 timing.json 时按第一期 +19% 实测 5.53 字/秒估算。动画与字幕按 timing.json 句子 start/dur 定位，句内短语按字数比例插值。from 为全局帧，subtitles 与 keyframes 帧相对镜头；transition 作用于镜头出场。image 元素 asset 路径相对 episodes/https/。密钥交换按 ECDHE：asymmetric-2 三个关键状态 step4 / ecdhe-combine / step6，切点为“就能各自”“偷听的人”的实测起点；两把相同金钥匙 keyL(411,566) / keyR(1347,566) 各 160×160，紧贴 step6 底部两个橙色圆正上方，在状态③开头弹出并慢转 8° 到镜头结束；该镜头 = timing 243 帧（已含 extraHold 40，gen.py 不再重复叠加），旁白音频 183 帧结束后金钥匙完整停留，8° 慢转铺满到镜头结束；总帧 = timing.json 合计 4809。画面文字为中文，英文仅 CA/TLS/HTTP/HTTPS/ClientHello/ServerHello；字幕随旁白保留 Wi-Fi、ECDHE、AEAD 原词。")
assets=dict(reuse=[dict(id="browser",desc="浏览器卡片（标签 浏览器 36px）",usedIn=["plaintext","symmetric"]),dict(id="server",desc="服务器卡片（同浏览器样式，无窗口圆点，标签 服务器 36px）",usedIn=["plaintext","symmetric"]),dict(id="seqDiagram",desc="第一期握手时序图样式",usedIn=["handshake"]),dict(id="subtitle",desc="字幕层")],
 new=[dict(id=f.stem,file=f"assets/{f.name}") for f in sorted((HERE/"assets").glob("*.svg")) if f.stem!="ecdhe-mix"])
import json as _j;from pathlib import Path as _Pc;_CS=_Pc("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=_j.load(open(_CS)).get("https") if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames'],s['estimateFormulaFrames']) for s in scenes])
# 有 timing.json 时 gen.py 已直接按 duration(+EXTRA_HOLD) 生成，不再调用 align.py（它会把额外停顿缩回去）
if not TM: print("no timing.json: 按 5.53 字/秒估算")
