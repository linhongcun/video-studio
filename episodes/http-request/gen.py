import json,re
src=open('/workspace/sorkin-backup/http-request-v2/script.md').read()
narr=re.findall(r'- 旁白：(.+)',src)
assert len(narr)==10
CNT=[int(x) for x in re.findall(r'- 字数：(\d+)',src)]
def cnt(s): return len(re.findall(r'[\u4e00-\u9fff A-Za-z0-9]',s.replace(' ','')))
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",text="#E5E7EB",muted="#6B7280",success="#22C55E",accent="#F59E0B",danger="#EF4444")
def R(i,x,y,w,h,c=P['panel'],reuse=False,**k): return dict(id=i,type="rect",x=x,y=y,w=w,h=h,color=c,reuse=reuse,**k)
def T(i,x,y,w,h,t,fs=40,c=P['text'],reuse=False,**k): return dict(id=i,type="text",x=x,y=y,w=w,h=h,text=t,fontSize=fs,color=c,reuse=reuse,**k)
def E(i,ty,x,y,w,h,c,reuse=False,**k): return dict(id=i,type=ty,x=x,y=y,w=w,h=h,color=c,reuse=reuse,**k)
BROWSER=lambda x=120,y=200,w=640,h=420: R("browser",x,y,w,h,P['panel'],True,stroke=P['secondary'],radius=16,label="浏览器窗口（第一期）")
SERVER=lambda x=1400,y=260: E("server","icon",x,y,300,380,P['secondary'],True,label="服务器（第一期）")
ids=["intro","url","cache","dns","connect","request","server","response","render","recap"]
titles=["开场","URL 解析","缓存检查","DNS 解析","建立连接","发送请求","服务器处理","返回响应","浏览器渲染","最后，串起来看一遍"]
steps=["URL 解析","缓存检查","DNS 解析","TCP/TLS 握手","发送请求","服务器处理","返回响应","浏览器渲染"]
def fade(i,a=0,b=12): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=0),dict(frame=b,value=1)],easing="easeOut")
def mv(i,prop,a,b,va,vb,e="easeInOut"): return dict(elementId=i,property=prop,keyframes=[dict(frame=a,value=va),dict(frame=b,value=vb)],easing=e)
def stepbar(vertical=False):
    els=[]
    for k,s in enumerate(steps):
        if vertical: els.append(R(f"step{k+1}",120,110+k*92,560,76,P['panel'],False,stroke=P['muted'],radius=12,label=f"{k+1} {s}"))
        else: els.append(R(f"step{k+1}",83+k*220,560,214,110,P['panel'],False,stroke=P['secondary'],radius=12,label=f"{k+1}\n{s}",fontSize=33))
    return els
# split points: list of sentence-index groups per scene (by '。')
def sentences(s): return [x for x in re.findall(r'[^。？]+[。？]',s)]
# shot designs: scene -> list of (elements, animations builder)
def shots_for(si,L):
    # returns list of (elements,anims) per shot; L = shot lengths
    if si==0:
        q=T("question",900,300,120,200,"?",180,P['primary'],True,align="center")
        return [([BROWSER(560,180,800,500),T("url",620,220,680,44,"https://example.com",32,reuse=True,font="monospace"),q],
                 [fade("browser"),mv("url","charsVisible",8,40,0,19,"linear"),mv("question","scale",40,60,0,1,"spring")]),
                ([T("tag",700,140,520,64,"8 步看懂一次访问",40,P['accent'],align="center",stroke=P['accent'],radius=32),q]+stepbar(),
                 [fade("tag",0,10),mv("question","opacity",0,15,1,0)]+[mv(f"step{k+1}","opacity",10+k*6,20+k*6,0,1) for k in range(8)])]
    if si==1:
        parts=[("https",P['primary'],"协议"),("example.com",P['secondary'],"域名"),(":443",P['accent'],"端口"),("/index.html",P['success'],"路径")]
        els=[T("urlFull",260,200,1400,80,"https://example.com:443/index.html",56,font="monospace",align="center")]
        x=200;an=[fade("urlFull",0,10)]
        for k,(t,c,l) in enumerate(parts):
            w=[260,480,220,420][k]
            els+= [R(f"seg{k}",x,340,w,90,P['panel'],stroke=c,radius=10,label=t,font="monospace",fontSize=40),T(f"segL{k}",x,450,w,50,l,32,c,align="center")]
            an+=[mv(f"seg{k}","y",20+k*10,32+k*10,200,340,"spring"),fade(f"seg{k}",20+k*10,30+k*10),fade(f"segL{k}",30+k*10,40+k*10)]; x+=w+40
        els.append(T("search",200,600,1520,50,"不是网址 → 交给搜索引擎",34,P['muted'],align="center"))
        an.append(fade("search",L[0]-80,L[0]-60))
        e2=[T("httpWord",560,320,300,90,"http://",64,P['danger'],font="monospace"),E("hsts","icon",900,260,220,240,P['success'],label="HSTS 盾牌"),T("httpsWord",1160,320,340,90,"https://",64,P['success'],font="monospace"),T("hstsNote",360,620,1200,50,"命中 HSTS 名单：HTTP 直接升级为 HTTPS（不发明文请求）",34,P['text'],align="center")]
        a2=[fade("httpWord"),fade("hsts",15,30),mv("httpWord","x",30,60,560,900),mv("httpWord","opacity",50,60,1,0),fade("httpsWord",55,70),fade("hstsNote",70,90)]
        return [(els,an),(e2,a2)]
    if si==2:
        els=[BROWSER(),E("drawer","icon",900,300,420,300,P['secondary'],label="缓存抽屉（新）"),E("cacheFile","icon",1000,200,220,160,P['text'],label="index.html",timer="max-age 倒计时"),
             E("check","icon",1300,180,120,120,P['success'],label="✓"),T("hitLabel",800,680,800,60,"强缓存命中，不发请求",44,P['success'],align="center"),T("ccTag",1000,140,400,44,"Cache-Control: max-age=3600",28,P['accent'],font="monospace")]
        an=[fade("browser"),fade("drawer",10,25),mv("cacheFile","y",30,60,360,200,"spring"),fade("ccTag",60,75),mv("check","scale",L[0]//2,L[0]//2+15,0,1,"spring"),fade("hitLabel",L[0]//2+10,L[0]//2+25)]
        return [(els,an)]
    if si==3:
        loc=[R(f"local{k}",120,200+k*130,520,100,P['panel'],stroke=P['muted'],radius=12,label=l) for k,l in enumerate(["浏览器缓存","系统缓存","hosts 文件"])]
        miss=[T(f"miss{k}",660,225+k*130,200,50,"未命中",32,P['danger']) for k in range(3)]
        an=[]
        for k in range(3): an+=[fade(f"local{k}",10+k*40,20+k*40),fade(f"miss{k}",30+k*40,40+k*40)]
        e1=loc+miss
        res=R("resolver",120,620,520,100,P['panel'],stroke=P['primary'],radius=12,label="递归解析器")
        e1.append(res);an.append(fade("resolver",L[0]-40,L[0]-20))
        tree=[R("root",1180,120,320,90,P['panel'],stroke=P['primary'],radius=45,label="根 .",font="monospace"),
              R("tld",1180,330,320,90,P['panel'],stroke=P['secondary'],radius=45,label="com（顶级域）",font="monospace"),
              R("auth",1120,540,440,90,P['panel'],stroke=P['success'],radius=45,label="example.com（权威）",font="monospace"),
              E("edge1","line",1340,210,0,120,P['muted']),E("edge2","line",1340,420,0,120,P['muted'])]
        q=[E(f"ask{k}","arrow",640,670,480,0,P['primary'],label=l) for k,l in enumerate(["问根","问 .com","问权威"])]
        ip=[T("ip",120,750,800,64,"example.com → 203.0.113.10",44,P['success'],font="monospace"),T("ipNote",120,816,800,36,"示例 IP：RFC 5737 文档专用地址，非真实服务器",28,P['muted'])]
        e2=[res]+tree+q+ip
        a2=[fade("root",0,10),fade("edge1",10,15),fade("tld",15,25),fade("edge2",25,30),fade("auth",30,40)]
        for k,yy in enumerate([165,375,585]): a2+=[mv(f"ask{k}","y",45+k*45,60+k*45,670,yy),fade(f"ask{k}",45+k*45,55+k*45),mv(f"ask{k}","opacity",80+k*45,90+k*45,1,0)]
        a2+=[fade("ip",190,205),fade("ipNote",205,220)]
        return [(e1,an),(e2,a2)]
    if si==4:
        base=[T("cliL",300,110,300,50,"浏览器",36,align="center"),T("srvL",1320,110,300,50,"服务器",36,align="center"),E("lifeL","line",450,170,0,660,P['secondary']),E("lifeR","line",1470,170,0,660,P['secondary'])]
        arr=[]
        for k,(l,d) in enumerate([("SYN","r"),("SYN+ACK","l"),("ACK","r")]):
            arr.append(E(f"tcp{k}","arrow",450,220+k*90,1020,60,P['primary'],label=l,direction=d))
        a1=[fade(i) for i in ["cliL","srvL","lifeL","lifeR"]]+[mv(f"tcp{k}","drawProgress",30+k*int((L[0]-60)/3),30+(k+1)*int((L[0]-60)/3)-5,0,1) for k in range(3)]
        tls=[E(f"tls{k}","arrow",450,500+k*70,1020,50,P['accent'],label=l,direction=d) for k,(l,d) in enumerate([("ClientHello","r"),("ServerHello + 证书","l"),("密钥交换 / Finished","r")])]
        lock=[E("lock","icon",880,730,160,100,P['success'],label="🔒"),T("lockNote",1060,750,400,50,"证书校验、密钥协商",32,P['success'])]
        q=T("quic",1300,830,540,40,"HTTP/3 = QUIC over UDP",28,P['muted'],font="monospace")
        tls13=T("tls13note",990,688,460,40,"TLS 1.3 只需 1 个往返（1-RTT）",28,"#9CA3AF")
        a2=[mv(f"tls{k}","drawProgress",10+k*35,40+k*35,0,1) for k in range(3)]+[mv("lock","scale",120,140,0,1,"spring"),fade("lockNote",135,150),fade("quic",L[1]-90,L[1]-70),fade("tls13note",200,220)]
        # keep base & tcp visible
        return [(base+arr,a1),(base+arr+tls+lock+[q,tls13],a2)]
    if si==5:
        env=E("packet","packet",500,300,560,340,P['secondary'],True,label="信封数据包（第一期）")
        lines=[T(f"hdr{k}",540,330+k*70,500,52,t,30,c,font="monospace") for k,(t,c) in enumerate([("GET /index.html HTTP/1.1",P['primary']),("Host: example.com",P['text']),("Cookie: sid=abc123",P['accent']),('If-None-Match: "v1"',P['success'])])]
        a1=[fade("browser"),fade("packet",10,25),fade("hdr0",30,45)]
        a2=[fade(f"hdr{k}",10+(k-1)*40,25+(k-1)*40) for k in (1,2,3)]+[mv("packet","x",L[1]-60,L[1]-10,500,1000,"easeIn")]
        return [([BROWSER(80,300,380,300),env,lines[0]],a1),([BROWSER(80,300,380,300),SERVER(1500,260),env]+lines,a2)]
    if si==6:
        edge=E("cdn","icon",760,180,320,200,P['primary'],label="CDN 边缘节点（新）",note="DNS 阶段经 CNAME 指向")
        cname=T("cname",640,100,700,44,"example.com CNAME → edge.cdn.example.net",28,P['muted'],font="monospace")
        env=E("packet","packet",200,240,200,130,P['secondary'],True,label="信封")
        hit=T("hit",760,400,320,44,"命中 → 直接返回",32,P['success'],align="center")
        a1=[fade("cdn"),fade("cname",15,30),mv("packet","x",30,70,200,700),mv("packet","x",80,120,700,200),fade("hit",75,90)]
        e1=[BROWSER(120,200,0+300,200),edge,cname,env,hit]
        e1[0]=BROWSER(100,200,300,200)
        lb=R("lb",560,520,240,110,P['panel'],stroke=P['accent'],radius=12,label="负载均衡（新）");rp=R("rp",880,520,240,110,P['panel'],stroke=P['accent'],radius=12,label="反向代理（新）")
        origin=SERVER(1380,420);origin['h']=320;origin['label']="源站服务器（第一期）"
        fo=E("folder","icon",1440,780,80,70,P['accent'],True,label="静态文件");ge=E("gear","icon",1560,780,80,70,P['primary'],True,label="动态生成")
        miss=T("missT",560,440,560,44,"未命中 → 回源",32,P['danger'],align="center")
        env2=dict(env);env2['y']=520
        a2=[fade("missT"),fade("lb",10,20),fade("rp",20,30),mv("packet","x",20,140,700,1380),fade("folder",150,165),fade("gear",165,180),mv("gear","rotate",165,L[1]-1,0,360,"linear")]
        return [(e1,a1),([edge,miss,lb,rp,origin,env2,fo,ge],a2)]
    if si==7:
        cards=[R(f"code{c}",200+k*400,220,340,200,P['panel'],stroke=col,radius=16,label=f"{c}\n{l}",fontSize=56) for k,(c,col,l) in enumerate([("200",P['success'],"成功"),("301",P['secondary'],"永久重定向"),("404",P['accent'],"找不到"),("500",P['danger'],"服务器出错")])]
        a1=[mv(f"code{c}","rotateY",10+k*int(L[0]/4.5),25+k*int(L[0]/4.5),90,0,"easeOut") for k,c in enumerate(["200","301","404","500"])]
        c304=R("code304",660,180,600,300,P['panel'],stroke=P['primary'],radius=20,label="304 Not Modified",fontSize=64)
        dr=E("drawer","icon",160,520,360,240,P['secondary'],label="缓存抽屉");ar=E("back","arrow",660,480,0,140,P['primary'],label="用本地缓存",curve=-0.4)
        et=T("etag",700,560,1080,100,'If-None-Match: "v1"  ⇄  ETag: "v1" → 协商缓存',36,P['accent'],font="monospace")
        a2=[mv("code304","scale",0,20,0,1,"spring"),fade("drawer",20,35),mv("back","drawProgress",35,60,0,1),fade("etag",60,80)]
        hd=[T(f"rh{k}",360,260+k*120,1200,80,t,48,P['text'],font="monospace") for k,t in enumerate(["Content-Type: text/html","Cache-Control: max-age=3600","Set-Cookie: sid=abc123"])]
        rp=E("respPacket","packet",160,240,160,340,P['success'],True,label="响应包（第一期）")
        a3=[fade("respPacket")]+[fade(f"rh{k}",10+k*25,25+k*25) for k in range(3)]
        return [(cards,a1),([c304,dr,ar,et],a2),([rp]+hd,a3)]
    if si==8:
        nm=["DOM","CSSOM","渲染树","布局","绘制/合成"]
        pipe=[R(f"pipe{k}",120+k*344,240,312,140,P['panel'],stroke=P['muted'],radius=14,label=n,fontSize=40) for k,n in enumerate(nm)]
        a1=[mv(f"pipe{k}","strokeColor",15+k*int((L[0]-40)/5),25+k*int((L[0]-40)/5),P['muted'],P['primary']) for k in range(5)]
        src=[T("htmlSrc",120,440,600,50,"HTML → DOM",32,P['secondary']),T("cssSrc",800,440,600,50,"CSS → CSSOM",32,P['accent'])]
        a1+=[fade("htmlSrc",10,20),fade("cssSrc",30,40)]
        sc=R("script",560,220,300,180,P['danger'],label="<script>",font="monospace");df=T("defer",560,420,300,50,"defer / async",34,P['success'],align="center")
        a2=[mv("script","scale",0,15,0,1,"spring"),fade("defer",50,65),mv("script","y",70,100,220,520)]
        sub=T("sub",120,620,1680,50,"子资源再发请求 · keep-alive 复用连接",32,P['muted'],align="center")
        fin=[E(f"fin{k}","arrow",560,700+k*36,800,30,P['muted'],label=l,direction=d) for k,(l,d) in enumerate([("FIN","r"),("ACK","l"),("FIN","l"),("ACK","r")])]
        # 2026-10-14 内容核对：「空闲一段时间后才四次挥手」——先亮「连接空闲中」，四次挥手推后到镜头后段（旧版：念到即挥手）
        idle=R("idle",760,470,400,56,P['bg'],stroke=P['muted'],radius=28,label="连接空闲中",fontSize=32)
        n3=L[2]; ti=int(n3*0.5); tf=int(n3*0.66)
        a3=[fade("sub"),fade("idle",ti,ti+10)]+[mv(f"fin{k}","drawProgress",tf+k*int(n3*0.05),tf+k*int(n3*0.05)+int(n3*0.07),0,1) for k in range(4)]
        return [(pipe+src,a1),(pipe+[sc,df],a2),(pipe+[sub,idle]+fin,a3)]
    if si==9:
        bar=stepbar(True)
        title=T("finalTitle",760,380,1080,140,"一次访问，八步完成",96,P['success'],align="center")
        n=len(L);out=[]
        bounds=[[0,1],[2],[3],[4,5,6],[7]]
        for j in range(n):
            an=[]
            for k in bounds[j]:
                t=10+bounds[j].index(k)*int(L[j]/len(bounds[j]))
                an.append(mv(f"step{k+1}","strokeColor",t,t+10,P['muted'],P['primary']))
            els=list(bar)
            if j==n-1:
                an+= [mv(f"step{k+1}","fillColor",L[j]-80,L[j]-60,P['panel'],P['success']) for k in range(8)]+[mv("finalTitle","scale",L[j]-60,L[j]-40,0,1,"spring")]
                els.append(title)
            out.append((els,an))
        return out
# shot narration splits: groups of sentences (or clause splits for recap)
def split_narr(si,s):
    if si==9:
        return ["最后，串起来看一遍：浏览器解析网址、检查缓存；","未命中就做 DNS 解析拿到 IP；","TCP 三次握手，HTTPS 再做 TLS 握手；","然后发送 HTTP 请求，服务器处理后返回 200 或 304 等响应；","浏览器再构建 DOM 和 CSSOM，经过布局、绘制、合成，展示页面。"]
    S=sentences(s)
    g={0:[2,1],1:[1,1],2:[2],3:[2,1],4:[2,2],5:[1,1],6:[1,1],7:[2,1,1],8:[2,1,1]}[si]
    out=[];i=0
    for n in g: out.append("".join(S[i:i+n]));i+=n
    assert i==len(S),(si,len(S))
    return out
def subs(t,L):
    cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',t) if x.strip()]
    # merge tiny clauses
    m=[]
    for c in cl:
        if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
        else: m.append(c)
    talk=int(L*sum(cnt(x) for x in m)/max(1,cnt(t)))
    tot=sum(cnt(x) for x in m);res=[];f=0
    speak=L-15
    for k,c in enumerate(m):
        d=round(speak*cnt(c)/tot); e=min(L-1,f+d-1) if k<len(m)-1 else L-1
        res.append(dict(text=c.rstrip('，；：。？'),from_=f,to=e));f=e+1
    return [dict(text=r['text'],**{"from":r['from_'],"to":r['to']}) for r in res]
scenes=[];g=0;nshot=0
for si,s in enumerate(narr):
    D=round((CNT[si]/4.2+2)*30)
    parts=split_narr(si,s); assert "".join(parts)==s
    tot=cnt(s); speak=D-60
    L=[round(speak*cnt(p)/tot) for p in parts]; L[-1]=D-sum(L[:-1])
    for k in range(len(L)-1): L[k]+=0
    # distribute pause: 30 to first? keep 60 in last; add 0
    L=[round((speak)*cnt(p)/tot)+ (60//len(parts)) for p in parts]; L[-1]=D-sum(L[:-1])
    designs=shots_for(si,L)
    shots=[];f=g
    for k,(p,l) in enumerate(zip(parts,L)):
        els,an=designs[k]
        els=[dict(e) for e in els]+[T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],True,align="center",role="subtitle")]
        for a in an:
            for kf in a['keyframes']: kf['frame']=max(0,min(l-1,kf['frame']))
        last=(k==len(parts)-1)
        shots.append(dict(id=f"{ids[si]}-{k+1}",**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l),elements=els,animations=an,
            transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),shots=shots))
    g+=D
meta=dict(title="《从输入 URL 到页面展示，发生了什么？》（完整版）",width=1920,height=1080,fps=30,durationInFrames=g,style="深色背景+蓝青高光扁平2D（沿用第一期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=860),
  notes="帧数按脚本估算：每段 round((字数/4.2+2)×30)，段内按镜头旁白字数分配，每段约 2 秒停顿平均摊到各镜头；以配音实测 timing.json 为准，届时按段等比缩放镜头与相对帧。from 为全局帧，subtitles 与 keyframes 帧相对镜头；transition 作用于镜头出场。章节 chapterId 与 article.mdx 锚点一致（intro/recap 为自定）。示例 IP 203.0.113.10 为 RFC 5737 文档地址。")
assets=dict(reuse=[dict(id="browser",desc="第一期浏览器窗口（rect，panel 底 + secondary 描边，圆角 16）",usedIn=["intro","cache","request","server"]),
 dict(id="url/addressbar",desc="第一期地址栏打字机文本",usedIn=["intro"]),dict(id="question",desc="第一期开场大问号",usedIn=["intro"]),
 dict(id="server",desc="第一期服务器图标（含源站）",usedIn=["request","server"]),dict(id="packet",desc="第一期信封数据包（请求）",usedIn=["request","server"]),
 dict(id="respPacket",desc="第一期响应包",usedIn=["response"]),dict(id="folder/gear",desc="第一期文件夹、齿轮图标",usedIn=["server"]),dict(id="subtitle",desc="字幕层")],
 new=[dict(id="stepbar",desc="1–8 步骤条（横排用于开场，竖排用于结尾总结，可逐格点亮/变绿）"),
 dict(id="urlSegments",desc="URL 四段切分块（协议/域名/端口/路径，各自配色+下方标签）"),dict(id="hsts",desc="HSTS 盾牌图标，http→https 翻转"),
 dict(id="drawer",desc="缓存抽屉 + 带 max-age 倒计时的文件 + 绿色对勾（第 2、7 章共用）"),
 dict(id="dnsLocal",desc="三层本地缓存条（浏览器缓存/系统缓存/hosts）+ 未命中标签"),dict(id="dnsTree",desc="DNS 树：根 . → com → example.com 权威，递归解析器问询箭头，结果 203.0.113.10 + RFC 5737 注释"),
 dict(id="seqDiagram",desc="握手时序图：两条竖线 + 带标签箭头（SYN/SYN+ACK/ACK，TLS ClientHello 等，第 8 章复用做四次挥手）"),dict(id="lock",desc="TLS 锁图标"),
 dict(id="cdn",desc="CDN 边缘节点图标 + CNAME 文本 + 命中折返路径"),dict(id="lb/rp",desc="负载均衡、反向代理两道门"),
 dict(id="statusCards",desc="状态码翻牌卡 200/301/404/500 + 放大 304"),dict(id="pipeline",desc="渲染流水线五格 DOM→CSSOM→渲染树→布局→绘制/合成"),dict(id="scriptBlock",desc="<script> 阻塞方块 + defer/async 标签")])
import json as _j;from pathlib import Path as _Pc;_CS=_Pc("/workspace/miyazaki-backup/covers/cover-spec.json");_cov=_j.load(open(_CS)).get("http-request-v2") if _CS.exists() else None  # 专用封面规格（covers/make_covers.py）
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open("storyboard.json","w"),ensure_ascii=False,indent=1)
print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames'],s['narrationChars']) for s in scenes])

# --- align to measured timing
# After estimated frames, align to measured voiceover if timing.json is present.
# Re-run: python3 gen.py && python3 align.py
# Or: TIMING_JSON=/path/to/timing.json python3 gen.py
import os
from pathlib import Path as _P
_timing = os.environ.get("TIMING_JSON") or str(_P(__file__).resolve().parent / "timing.json")
if _P(_timing).is_file():
    from align import align as _align
    _r = _align(_P(_timing), _P(__file__).resolve().parent / "storyboard.json")
    print("aligned", _r["total"], _r["scenes"])
else:
    print("skip align: no timing.json at", _timing)
