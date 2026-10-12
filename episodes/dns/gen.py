import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
src=open('/workspace/sorkin-backup/dns/script.md').read()
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
ids=["phonebook","cache","resolver","iterative","ttl","recap"]
titles=["开场：需要一本电话簿","先翻自己的小本子","请教查号台","一层层往上问","记下来，下次更快","回顾"]
SPLIT={0:[2,2],1:[2,1],2:[2,2],3:[2,2,1],4:[1,1,1],5:[1,1]}
SID={3:["iterative-1a","iterative-1b","iterative-2"]}
def KEY(si,k): return SID[si][k] if si in SID else f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
CARD=dict(stroke=P['secondary'],radius=16,fontSize=36)   # 统一服务器卡片：panel 底、secondary 描边、圆角 16、无窗口圆点、标签 36px
def card(i,x,y,w,h,label,**k): return R(i,x,y,w,h,**{**CARD,"label":label,**k})
def browser(x,y,w=360,h=220): return card("browser",x,y,w,h,"浏览器",reuse=True)
def server(i,x,y,w,h,label): return card(i,x,y,w,h,label,reuse=True,note="统一服务器卡片（同浏览器样式，无窗口圆点，标签 36px）")
TM=json.load(open(HERE/"timing.json"))
def AT(si,k,phrase):
    """镜头内短语起始帧：timing.json 句子 start/dur + 句内字数比例"""
    S=sentences(PARTS[k]); i=next(j for j,s in enumerate(S) if phrase in s); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def AEND(si,k): return TM[KEY(si,k)]["audioFrames"]
IP="203.0.113.10"
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 地址栏 → 服务器头顶号码
        e1=[R("addr",360,140,1200,100,stroke=P['primary'],radius=50,label="example.com",fontSize=44,note="地址栏，charsVisible 逐字敲出"),
            browser(160,400),server("server",1400,360,280,300,"服务器"),
            E("toIP","arrow",560,480,820,60,P['text2'],label="网络只认 IP 地址",direction="r",fontSize=36),
            T("ip",1290,290,500,56,IP,44,P['accent'],align="center"),T("demo",1640,240,120,40,"示意",28,P['text2'],align="center"),
            T("phone",560,720,820,56,"就像打电话只认号码",40,P['primary'],align="center")]
        t=at(0,"可网络上")
        a1=[fade("addr"),mv("addr","charsVisible",8,8+min(36,at(0,"按下回车")),0,11,"linear"),mv("addr","scale",at(0,"按下回车"),at(0,"按下回车")+10,1,1.04,"spring"),
            fade("browser",at(0,"按下回车"),at(0,"按下回车")+12),fade("server",t,t+12),draw("toIP",t+6,20),fade("ip",at(0,"IP 地址"),at(0,"IP 地址")+12),fade("demo",at(0,"IP 地址")+6,at(0,"IP 地址")+18),fade("phone",at(0,"就像打电话"),at(0,"就像打电话")+15)]
        e2=[A("book","phonebook",160,180,600,600),T("hName",880,200,400,56,"名字",44,P['primary'],align="center"),T("hNum",1300,200,460,56,"号码",44,P['accent'],align="center"),
            E("rule","line",880,280,880,0,P['text2']),T("name",880,320,400,56,"example.com",40,P['text'],align="center"),E("map","arrow",1250,330,80,40,P['text2'],direction="r"),
            T("num",1300,320,460,56,IP,40,P['text'],align="center"),T("dns",880,520,880,150,"DNS",120,P['accent'],align="center"),T("dnsSub",880,690,880,50,"帮你查电话簿的系统",40,P['text'],align="center")]
        t=at(1,"所以需要")
        a2=[fade("hName",0,10),fade("hNum",0,10),fade("rule",0,10),fade("book",t,t+12),mv("book","scale",t,t+15,0.9,1,"spring"),fade("name",at(1,"把名字"),at(1,"把名字")+12),draw("map",at(1,"翻译成")),fade("num",at(1,"号码。"),at(1,"号码。")+12),
            mv("dns","scale",at(1,"就叫"),at(1,"就叫")+15,0,1,"spring"),fade("dnsSub",at(1,"帮你查"),at(1,"帮你查")+15)]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 小本子：浏览器 / 操作系统 / hosts，命中短路返回
        base=lambda:[browser(160,140,400,200),card("os",760,140,400,200,"操作系统"),card("outside",1360,140,400,200,"外面的世界",stroke=P['muted'],note="暗色占位，表示还没往外走")]
        e1=base()+[A("nbB",'notebook',280,380,160,160),T("nbBT",160,560,400,44,"最近查过的记录",32,P['text2'],align="center"),
            A("nbS",'notebook',780,380,160,160),A("hosts",'hosts-note',980,380,160,160),T("nbST",760,560,200,44,"系统缓存",32,P['text2'],align="center"),T("hostsT",960,560,200,44,"hosts",36,P['accent'],align="center")]
        a1=[fade("browser",0,10),fade("os",0,10),dict(fade("outside",0,10),keyframes=[dict(frame=0,value=0),dict(frame=10,value=0.5)]),
            mv("nbB","scale",at(0,"先翻"),at(0,"先翻")+15,0,1,"spring"),fade("nbBT",at(0,"浏览器会"),at(0,"浏览器会")+12),
            mv("nbS","scale",at(0,"再问"),at(0,"再问")+15,0,1,"spring"),fade("nbST",at(0,"自己的缓存"),at(0,"自己的缓存")+12),mv("hosts","scale",at(0,"hosts"),at(0,"hosts")+15,0,1,"spring"),fade("hostsT",at(0,"hosts"),at(0,"hosts")+12)]
        e2=base()+[A("nbB",'notebook',280,380,160,160),A("nbS",'notebook',780,380,160,160),A("hosts",'hosts-note',980,380,160,160),
            E("hit","arrow",560,230,200,40,P['success'],direction="l",note="命中闪光：从操作系统一闪回到浏览器（6 帧画完，快）"),
            T("fast",160,640,800,80,"命中：直接返回，很快",56,P['success'],align="center"),
            E("noGo","arrow",1160,230,200,40,P['muted'],direction="r",dash=True),T("noGoT",1160,640,600,50,"一步都不用往外走",40,P['text2'],align="center")]
        t=at(1,"就直接")
        a2=[mv("nbS","scale",at(1,"只要"),at(1,"只要")+10,1,1.12,"spring"),draw("hit",t,6),fade("fast",t+4,t+14),fade("noGo",0,1),dict(out("noGo",at(1,"一步都"),at(1,"一步都")+10,0.2)),fade("noGoT",at(1,"一步都"),at(1,"一步都")+12)]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 查号台
        e1=[browser(160,260),E("call","arrow",560,340,560,60,P['primary'],label="打电话",direction="r",fontSize=36),T("udp",560,420,560,40,"查询通常走 UDP 53 端口",28,P['text2'],align="center"),
            server("resolver",1160,220,600,300,"查号台"),T("resT",1160,540,600,50,"递归解析器",40,P['primary'],align="center"),
            R("isp",1160,640,180,64,stroke=P['text2'],radius=12,label="运营商",fontSize=32),R("pub1",1370,640,180,64,stroke=P['text2'],radius=12,label="1.1.1.1",fontSize=32),R("pub2",1580,640,180,64,stroke=P['text2'],radius=12,label="8.8.8.8",fontSize=32),
            T("pubT",1370,720,390,44,"公共 DNS",32,P['text2'],align="center")]
        t=at(0,"就打给")
        a1=[fade("browser"),draw("call",t,20),fade("udp",t+20,t+32),fade("resolver",at(0,"查号台"),at(0,"查号台")+12),fade("resT",at(0,"递归"),at(0,"递归")+12),
            fade("isp",at(0,"运营商"),at(0,"运营商")+12),fade("pub1",at(0,"1.1.1.1"),at(0,"1.1.1.1")+12),fade("pub2",at(0,"8.8.8.8"),at(0,"8.8.8.8")+12),fade("pubT",at(0,"公共"),at(0,"公共")+12)]
        e2=[browser(160,140),server("resolver",640,140,400,220,"查号台"),R("ask",160,420,880,90,stroke=P['primary'],radius=45,label="example.com 的号码是多少？",fontSize=40,note="对话气泡"),
            card("gRoot",1180,140,560,100,"根服务器",stroke=P['muted']),card("gCom",1180,280,560,100,".com 服务器",stroke=P['muted']),card("gAuth",1180,420,560,100,"权威服务器",stroke=P['muted']),
            E("run","arrow",640,640,1100,60,P['accent'],label="剩下的路，它替你跑",direction="r",fontSize=40,dash=True)]
        t=at(1,"剩下的路")
        a2=[fade("browser",0,8),fade("resolver",0,8),mv("ask","scale",at(1,"你只问"),at(1,"你只问")+15,0,1,"spring")]+[dict(elementId=g,property="opacity",keyframes=[dict(frame=t+5*j,value=0),dict(frame=t+5*j+12,value=0.5)],easing="easeOut") for j,g in enumerate(["gRoot","gCom","gAuth"])]+[draw("run",t,25)]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 时序图：查号台 / 根 / .com / 权威
        cols=[("cRes","查号台",280),("cRoot","根服务器",760),("cCom",".com 服务器",1220),("cAuth","权威服务器",1640)]
        e1=[];a1=[]
        for j,(i,l,cx) in enumerate(cols):
            dy=30 if i=="cAuth" else 0  # 权威服务器卡片下移 30px，避开频道水印留空区（x1700–1840, y80–130）；生命线起点跟着下移、底端仍在 850
            e1+=[dict(server(i,cx-170,110+dy,340,100,l),fontSize=40,note="时序图列标题：统一卡片样式，列标题 40px"),E(i+"Life","line",cx,210+dy,0,640-dy,P['muted'])]
            a1+=[fade(i,j*6,j*6+12),fade(i+"Life",j*6+6,j*6+18)]
        e1+=[A("globe","globe",604,125,70,70)]  # 根服务器卡片旁的地球小图标
        a1+=[fade("globe",at(0,"它先问根"),at(0,"它先问根")+12)]
        rows=[("q1",280,760,"r","example.com 在哪？",P['primary'],"它先问根"),("a1",280,760,"l","去问 .com",P['text'],"只告诉它"),
              ("q2",280,1220,"r","example.com 在哪？",P['primary'],"再去问"),("a2",280,1220,"l","去问权威服务器",P['text'],"它说"),
              ("q3",280,1640,"r","example.com 的号码？",P['primary'],"最后问到"),("a3",280,1640,"l",IP,P['accent'],"才拿到")]
        base=list(e1);abase=[fade(x['id'],0,1) for x in base]  # 1b：列与地球直接在场
        e1b=list(base);a1b=list(abase)
        for j,(i,x0,x1,d,l,c,ph) in enumerate(rows):
            el=E(i,"arrow",x0,290+j*90,x1-x0,50,c,label=l,direction=d,fontSize=32)
            if j<2:
                e1.append(el);a1+=[draw(i,at(0,ph),18)];e1b.append(el)   # 1b：前两支箭头已画好（无动画=满）
            else:
                e1b.append(el);a1b+=[draw(i,at(1,ph),18)]
        a1+=[mv("cRoot","scale",at(0,"从最顶层"),at(0,"从最顶层")+12,1,1.06,"spring")]
        a1b+=[mv("cCom","scale",0,12,1,1.06,"spring"),mv("cAuth","scale",at(1,"才拿到"),at(1,"才拿到")+12,1,1.06,"spring")]
        e2=[A("globe","globe",560,200,640,640),A("dots","anycast-dots",560,200,640,640),T("n13",160,100,1600,70,"根服务器：13 个名字",56,P['accent'],align="center")]
        names=[R(f"r{j}",1300+(j%4)*120,240+(j//4)*120,96,96,stroke=P['accent'],radius=48,label="abcdefghijklm"[j],fontSize=40,note=f"根名字徽章 {'abcdefghijklm'[j]}（对应 {'abcdefghijklm'[j]}.root-servers.net），字母 40px 小写") for j in range(13)]
        e2+=names+[T("many",160,380,380,50,"每个名字背后",40,P['text'],align="center"),T("many2",160,450,380,50,"全世界许多台机器",36,P['primary'],align="center"),T("anyc",160,520,380,44,"（任播）",32,P['text2'],align="center")]
        t=at(2,"但每个")
        a2=[fade("globe",0,10),fade("n13",0,12)]+[mv(f"r{j}","scale",4+j*3,16+j*3,0,1,"spring") for j in range(13)]+[fade("many",t,t+12),fade("dots",at(2,"都是分布"),at(2,"都是分布")+15),fade("many2",at(2,"都是分布"),at(2,"都是分布")+12),fade("anyc",at(2,"许多台"),at(2,"许多台")+12)]
        return [(e1,a1),(e1b,a1b),(e2,a2)]
    if si==4:  # 号码原路返回盖章 / 沙漏 TTL / 旧号码陆续过期
        trio=[("browser","浏览器",160),("os","操作系统",760),("resolver","查号台",1360)]
        e1=[];a1=[]
        for i,l,x in trio: e1.append(server(i,x,200,400,200,l)); a1.append(fade(i,0,10))
        e1+=[R("ipChip",1460,440,300,64,P['panel'],stroke=P['accent'],radius=32,label=IP,fontSize=32,note="号码胶囊：从查号台沿原路向左移动")]
        st=[("sRes",1360,"查号台记一份"),("sOs",760,"系统和浏览器"),("sBr",160,"各记一份")]
        for i,x,ph in st:
            e1+=[R(i,x+100,580,200,70,stroke=P['success'],radius=12,label="已记录",fontSize=36,note="盖章：scale 1.3→1 spring")]
            t=at(0,ph); a1+=[mv(i,"scale",t,t+10,1.3,1,"spring"),fade(i,t,t+6)]
        a1+=[fade("ipChip",0,10),mv("ipChip","x",at(0,"查号台记"),at(0,"下次"),1460,260)]
        e1+=[T("next",160,720,1600,50,"下次：不用再跑一趟",40,P['success'],align="center")];a1+=[fade("next",at(0,"下次"),at(0,"下次")+12)]
        e2=[A("hg","hourglass",200,160,440,440),T("ttl",200,620,440,80,"TTL",64,P['accent'],align="center"),
            R("rec",760,280,1000,120,stroke=P['primary'],radius=16,label=f"example.com → {IP}",fontSize=40),T("valid",760,180,1000,56,"每条记录都带有效期",40,P['text']),
            T("exp",760,460,1000,64,"到期作废，重新查",48,P['danger'])]
        t=at(1,"到期")
        a2=[fade("hg",0,10),fade("rec",0,10),fade("valid",at(1,"每条"),at(1,"每条")+12),fade("ttl",at(1,"TTL"),at(1,"TTL")+12),
            mv("hg","drain",at(1,"有效期"),t+10,0,1,"linear"),mv("rec","opacity",t+10,t+20,1,0.35),mv("rec","strike",t+10,t+20,0,1),fade("exp",t+10,t+22)]
        e3=[];a3=[]
        for j,(i,l,x) in enumerate(trio):
            e3+=[server(i,x,140,400,180,l),A(i+"Nb","notebook",x+140,350,120,120),R(i+"Old",x+50,500,300,64,stroke=P['text2'],radius=12,label="旧号码",fontSize=36),R(i+"New",x+50,500,300,64,stroke=P['success'],radius=12,label="新号码",fontSize=36)]
            t=at(2,"要等")+j*int((at(2,"处处")-at(2,"要等"))/3)
            a3+=[fade(i,0,10),fade(i+"Nb",0,10),fade(i+"Old",0,10),mv(i+"Old","strike",t,t+12,0,1),out(i+"Old",t+12,t+20),fade(i+"New",t+18,t+30)]
        e3+=[T("chg",160,640,1600,56,"网站改了地址",40,P['text'],align="center"),T("eff",160,720,1600,56,"陆续过期后，新地址处处生效",40,P['success'],align="center")]
        a3+=[fade("chg",at(2,"所以网站"),at(2,"所以网站")+12),fade("eff",at(2,"新地址"),at(2,"新地址")+12)]
        return [(e1,a1),(e2,a2),(e3,a3)]
    if si==5:  # 总路线 / 接回第一期
        nodes=[("nNb","小本子","先翻"),("nRes","查号台","打给"),("nRoot","根服务器","从根"),("nCom",".com 服务器","到 .com"),("nAuth","权威服务器","再问到"),("nNum","号码","拿到号码")]
        e1=[];a1=[]
        for j,(i,l,ph) in enumerate(nodes):
            x=100+j*290
            e1.append(card(i,x,300,240,110,l,fontSize=36 if len(l)<6 else 32,stroke=P['accent'] if i=="nNum" else P['secondary']))
            t=at(0,ph); a1+=[fade(i,max(0,t-4),t+8),mv(i,"scale",t,t+10,1.08,1,"spring")]
            if j<5: e1.append(E(f"ar{j}","arrow",x+240,330,50,50,P['primary'],direction="r")); a1.append(draw(f"ar{j}",t+8,8))
        e1+=[A("nbIcon","notebook",160,160,120,120),A("globeIcon","globe",740,160,120,120),
             E("back","arrow",160,520,1600,60,P['success'],label="号码返回，顺手记下来",direction="l",fontSize=40),T("title",160,680,1600,60,"先近后远，一层层问",44,P['text'],align="center")]
        t=at(0,"顺手"); a1+=[fade("nbIcon",at(0,"先翻"),at(0,"先翻")+12),fade("globeIcon",at(0,"从根"),at(0,"从根")+12),draw("back",at(0,"拿到号码"),t-at(0,"拿到号码")+10),fade("title",AEND(5,0)-30,AEND(5,0)-18)]
        EP1=dict(id="ep1Frame",type="image",src="ep01:http-request/connect-1@220",asset=None,placeholder=True,x=1240,y=150,w=520,h=293,color=None,reuse=True,stroke=P['text2'],
            note="【待 Knoll 确认/提供】复用第一期 http-request 的连接镜头 connect-1（storyboard 全局 from=1440，243 帧；s4「建立连接」TCP 三次握手）。建议取镜头内第 200 帧（全局 1640，三支握手箭头都已画完），从 /workspace/video-studio/episodes/http-request/video.mp4 抽帧，或在 remotion 里直接渲染该帧；静帧参考 /workspace/video-studio/episodes/http-request/frames/04-connect.png。16:9 缩放到 520×293，2px text2 描边。")
        e2=[browser(160,180,340,200),server("server",820,180,340,200,"服务器"),R("ipChip",160,420,340,60,stroke=P['accent'],radius=30,label=IP,fontSize=32),
            E("conn","arrow",500,220,320,60,P['primary'],label="建立连接",direction="r",fontSize=36),E("req","arrow",500,330,320,60,P['success'],label="发出请求",direction="r",fontSize=36),
            EP1,T("ep1Cap",1240,460,520,44,"第一期：建立连接",32,P['text2'],align="center"),
            T("ep1",160,560,1600,50,"接第一期：从输入 URL 到页面展示，发生了什么？",36,P['text2'],align="center"),T("title",160,660,1600,80,"输入网址后，怎么找到服务器？",56,P['accent'],align="center")]
        a2=[fade("browser",0,10),fade("ipChip",0,10),fade("server",at(1,"建立连接"),at(1,"建立连接")+10),draw("conn",at(1,"建立连接"),18),draw("req",at(1,"发出请求"),18),
            fade("ep1Frame",at(1,"建立连接"),at(1,"建立连接")+12),fade("ep1Cap",at(1,"建立连接")+6,at(1,"建立连接")+18),fade("ep1",at(1,"也就是"),at(1,"也就是")+12),fade("title",AEND(5,1),AEND(5,1)+15)]
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
EXTRA_HOLD={}  # 暂无；条目自带 extraHold 字段时不叠加
scenes=[];g=0;nshot=0;PARTS=[]
for si,s in enumerate(narr):
    S=sentences(s);parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S) and "".join(parts).replace(' ','')==s.replace(' ','')
    L=[TM[KEY(si,k)]["duration"]+(0 if "extraHold" in TM[KEY(si,k)] else EXTRA_HOLD.get(KEY(si,k),0)) for k in range(len(parts))]
    PARTS[:]=parts;designs=shots_for(si,L);shots=[];f=g
    for k,(p,l) in enumerate(zip(parts,L)):
        els,an=designs[k]
        els=[dict(e) for e in els]+[dict(T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],align="center",role="subtitle"),reuse=True)]
        for a in an:
            for kf in a['keyframes']: kf['frame']=max(0,min(l-1,kf['frame']))
        last=k==len(parts)-1
        shots.append(dict(id=KEY(si,k),**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),shots=shots));g+=D
POSTER=None
meta=dict(title="《输入网址后，怎么找到服务器？》",episode=3,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=False,style="深色背景+蓝青高光扁平2D（沿用前两期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880),
  notes="【暂定时长】尚无配音：timing.json 为估算（第二期 MiMo 冰糖实测句内 4.52 字/秒 + 句间 0.28 秒 + 每镜头 30 帧留白），配音后用实测 timing.json 重跑 gen.py，镜头时长=duration。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/dns/。服务器卡片统一样式（无窗口圆点，标签 36px），时序图列标题卡片同样式。新动画属性：drawProgress（箭头画出）、drain（沙漏 0→1）、strike（删除线 0→1）、charsVisible（地址栏逐字）。203.0.113.10 为 RFC 5737 文档示例地址，画面标注“示意”。根服务器 = 13 个名字 + 任播的许多台机器，13 个根徽章写小写 a–m（对应 a–m.root-servers.net）。iterative-1 在「再去问 .com」拆成 iterative-1a/1b，1b 沿用同一时序图、前两支箭头已画好。recap-2 含第一期 connect-1 画面占位（type image, placeholder:true, src ep01:...），需 Knoll 确认/供素材。时长=MiMo 冰糖实测（timing.mimo.json 映射，scale 1）。")
assets=dict(reuse=[dict(id="browser",desc="浏览器卡片（标签 浏览器 36px）"),dict(id="server",desc="统一服务器卡片（无窗口圆点，标签 36px）"),dict(id="seqDiagram",desc="第二期时序图样式（iterative-1）"),dict(id="routeArrow",desc="第二期路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")],
 new=[dict(id=f.stem,file=f"assets/{f.name}") for f in sorted((HERE/"assets").glob("*.svg"))])
sh2=[x for sc in scenes for x in sc['shots'] if x['id']=="iterative-2"][0]
pl=max(k['frame'] for a in sh2['animations'] for k in a['keyframes'])+6
meta['poster']=dict(shotId="iterative-2",localFrame=pl,frame=sh2['from']+pl,desc="地球+任播点+13 个 a–m 根徽章，标题「根服务器：13 个名字」",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
