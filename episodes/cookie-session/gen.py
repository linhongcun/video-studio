import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
src=open('/workspace/sorkin-backup/cookie-session/script.md').read()
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

from common_split import ids,SPLIT as _SP
titles=["HTTP 记不住人","登录后发手牌","每次都带上","柜台里存什么","手牌被偷怎么办","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
SID={}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
CARD=dict(stroke=P['secondary'],radius=16,fontSize=36)   # 统一卡片：panel 底、secondary 描边、圆角 16、无窗口圆点、标签 36px
def card(i,x,y,w,h,label,**k): return R(i,x,y,w,h,**{**CARD,"label":label,**k})
def browser(x,y,w=400,h=240): return card("browser",x,y,w,h,"浏览器",reuse=True)
def server(i,x,y,w,h,label): return card(i,x,y,w,h,label,reuse=True,note="统一服务器卡片（同浏览器样式，无窗口圆点，标签 36px）")
TM=json.load(open(HERE/"timing.json"))
def AT(si,k,phrase):
    S=sentences(PARTS[k]); i=next(j for j,s in enumerate(S) if phrase in s); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def AEND(si,k): return TM[KEY(si,k)]["audioFrames"]
NUM="会话 ID：0417"
def tag(i,x,y,s=120,**k): return A(i,"tag",x,y,s,s,**k)
def ride(i,a,b,x0,x1): return mv(i,"x",a,b,x0,x1,"easeInOut")
def pop(i,a): return mv(i,"scale",a,a+12,0,1,"spring")
def F(i,a,n=12): return fade(i,a,a+n)
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 记不住人：登录 → 每次请求服务器头顶都是问号
        e1=[browser(160,320),T("login",160,580,400,50,"已登录 ✓",40,P['success'],align="center"),server("server",1360,320,400,240,"服务器")]
        a1=[F("browser",0),F("server",0),F("login",at(0,"你刚登录"))]
        for j,ph in enumerate(["点开下一页","每一次请求","像第一次见面"]):
            y=260+j*130
            e1+=[E(f"req{j}","arrow",560,y,800,50,P['primary'],label="请求",direction="r",fontSize=32),T(f"q{j}",1360+j*140,180,120,90,"？",72,P['accent'],align="center")]
            t=at(0,ph); a1+=[draw(f"req{j}",t,15),F(f"q{j}",t+12)]
        e1+=[T("http",560,140,800,56,"HTTP：无状态",44,P['primary'],align="center"),T("who",1360,600,400,50,"你是谁？",40,P['accent'],align="center"),
             T("first",160,700,1600,56,"每次请求，都像第一次见面",44,P['text'],align="center"),T("pw",160,790,1600,56,"每点一页都输一次密码？",40,P['danger'],align="center")]
        a1+=[F("http",at(0,"可 HTTP")),F("who",at(0,"像第一次见面")+12),F("first",at(0,"像第一次见面")),F("pw",at(0,"要是"))]
        e2=[T("ask",160,160,1600,80,"网站是怎么认出你的？",64,P['text'],align="center"),A("locker","locker",710,300,500,500),T("ans",1260,500,500,60,"答案：存包处",48,P['accent'],align="center")]
        a2=[mv("ask","scale",0,12,0.9,1,"spring"),F("ask",0),F("locker",at(1,"答案")),pop("locker",at(1,"答案")),F("ans",at(1,"存包处"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 发手牌（合并镜头：存包处发手牌 → 登录 Set-Cookie → 手牌飞进浏览器框内）
        tA=at(0,"柜台会给你"); t2=at(0,"登录也一样"); t=at(0,"在响应里")
        e1=[A("locker","locker",1160,200,500,500),T("counter",1160,720,500,56,"柜台",44,P['primary'],align="center"),
            tag("tagA",1340,380,140),T("tagT",260,640,520,56,"手牌",48,P['accent'],align="center"),
            browser(160,200),server("server",1360,200,400,240,"服务器"),
            E("login","arrow",560,260,800,50,P['primary'],label="登录：账号 + 密码",direction="r",fontSize=32),
            T("ok",1360,460,400,50,"密码正确 ✓",40,P['success'],align="center"),
            E("resp","arrow",560,380,800,50,P['accent'],label="响应：Set-Cookie",direction="l",fontSize=36),
            tag("tag",1240,470,100),R("num",660,620,600,90,stroke=P['accent'],radius=16,label=NUM,fontSize=40,note="手牌特写：只有一串编号（示意）"),
            T("cookie",320,340,220,56,"Cookie",44,P['accent'],align="center",note="标在浏览器框内（框 160–560 × 200–440）")]
        a1=[F("locker",0),F("counter",0),F("tagA",tA),ride("tagA",tA,tA+30,1340,450),F("tagT",tA+20),
            out("locker",t2-14,t2),out("counter",t2-14,t2),out("tagA",t2-14,t2),out("tagT",t2-14,t2),
            F("browser",t2),F("server",t2),draw("login",t2+6,15),F("ok",at(0,"验证通过")),draw("resp",t,20),
            F("tag",t),ride("tag",t,t+40,1240,190),mv("tag","y",t,t+40,470,300,"easeInOut"),
            F("num",at(0,"一串编号")),pop("num",at(0,"一串编号")),F("cookie",at(0,"这就是"))]
        return [(e1,a1)]
    if si==2:  # 每次都带上
        e1=[browser(160,300),server("server",1360,300,400,240,"example.com"),T("auto",160,160,1600,56,"浏览器自动带上，不用你动手",44,P['primary'],align="center"),
            T("hi",1360,580,400,50,"认出你了 ✓",40,P['success'],align="center")]
        a1=[F("browser",0),F("server",0),F("auto",at(0,"自动"))]
        t0=at(0,"每个请求")
        for j in range(3):
            y=300+j*90; t=t0+j*35
            e1+=[E(f"req{j}","arrow",560,y,800,50,P['primary'],direction="r"),tag(f"t{j}",560,y-30,72)]
            a1+=[draw(f"req{j}",t,20),F(f"t{j}",t,6),ride(f"t{j}",t,t+20,560,1270)]
        a1+=[F("hi",at(0,"就知道"))]
        e2=[browser(160,300),tag("mine",300,560,120),server("server",1360,140,400,200,"example.com"),server("other",1360,520,400,200,"别的网站"),
            E("ok","arrow",560,220,800,50,P['success'],label="照样认得你",direction="r",fontSize=32),tag("tOk",580,180,72),
            E("no","arrow",560,600,800,50,P['text2'],label="不会带过去",direction="r",fontSize=32,dash=True),T("x",860,660,200,56,"拿不到",40,P["danger"],align="center"),
            T("back",160,760,1600,56,"关掉再回来：手牌还在、没过期，就还认得",40,P['text'],align="center"),
            T("only",1360,740,400,50,"只交给发它的网站",32,P['text2'],align="center")]
        t=at(1,"只要手牌")
        a2=[F("browser",0),F("server",0),F("other",0),F("mine",0),F("back",at(1,"关掉页面")),draw("ok",t,18),F("tOk",t,6),ride("tOk",t,t+20,580,1270),
            draw("no",at(1,"手牌只会"),18),F("x",at(1,"别的网站拿")),F("only",at(1,"手牌只会"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 柜台里存什么
        e1=[A("locker","locker",160,200,480,480),T("lockT",160,700,480,56,"柜台 = 服务器",40,P['primary'],align="center"),
            server("sess",760,200,1000,480,""),T("sessT",800,230,920,64,"Session（存在服务器那边）",48,P['accent'],align="center"),
            R("row",820,340,880,80,stroke=P['accent'],radius=12,label="编号：0417",fontSize=40),
            T("who",860,460,800,56,"用户：小明",44,P['text']),T("till",860,540,800,56,"登录到：今晚 12 点",44,P['text'])]
        a1=[F("locker",0),F("lockT",0),F("sess",at(0,"Session")-10),F("sessT",at(0,"Session")),F("row",at(0,"按编号")),F("who",at(0,"这是谁")),F("till",at(0,"登录到"))]
        e2=[tag("tag",200,180,300),T("num",160,500,380,50,NUM,36,P['accent'],align="center"),T("nopw",160,570,380,56,"没有密码",44,P['success'],align="center"),
            A("thief","thief",700,300,300,300),tag("tTh",960,330,100),E("use","arrow",1020,420,340,50,P['danger'],direction="r"),
            server("server",1360,300,400,240,"柜台"),T("pass",1360,560,400,50,"只认手牌 ✓",40,P['success'],align="center"),
            T("anyone",160,760,1600,60,"谁拿着手牌，谁就能冒充你",48,P['danger'],align="center")]
        t=at(1,"可柜台")
        a2=[F("tag",0),F("num",at(1,"一串编号")),F("nopw",at(1,"不装")),F("server",t),F("thief",t),F("tTh",t),draw("use",at(1,"谁拿着"),15),F("pass",at(1,"谁拿着")+12),F("anyone",at(1,"谁就能"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 手牌被偷怎么办
        shields=[("sH","HttpOnly：网页脚本读不到","加上 HttpOnly"),("sS","Secure：只走 HTTPS","加上 Secure"),("sM","SameSite：限制别的网站带上它","SameSite")]
        base=[A("thief","thief",160,260,300,300),tag("tag",520,260,300),E("grab","arrow",420,380,120,50,P['danger'],direction="r")]
        rects=[R(i,900,160+j*130,860,100,stroke=P['success'],radius=16,label=l,fontSize=36,note="护盾标签：scale 弹出") for j,(i,l,_) in enumerate(shields)]
        e1=base+rects+[T("guard",160,620,700,56,"护好手牌",44,P['accent'],align="center")]
        a1=[F("thief",0),F("tag",0),draw("grab",at(0,"所以"),15),F("guard",at(0,"护好"))]
        for i,_,ph in shields: t=at(0,ph); a1+=[F(i,t),pop(i,t)]
        a1+=[out("grab",at(0,"SameSite"),at(0,"SameSite")+10,0.2)]
        e2=base+rects+[R("sE",900,550,860,100,stroke=P['success'],radius=16,label="过期：到点作废",fontSize=36),
            R("void",520,600,300,90,stroke=P['danger'],radius=12,label="已作废",fontSize=40,note="盖章：scale 1.3→1 spring"),
            T("logout",160,740,1600,56,"退出登录：柜台作废这个编号，偷到的手牌也没用了",40,P['text'],align="center")]
        a2=[out("grab",0,1,0.2),F("sE",at(1,"有效期")),pop("sE",at(1,"有效期")),F("logout",at(1,"退出登录")),
            mv("void","scale",at(1,"作废"),at(1,"作废")+10,1.3,1,"spring"),F("void",at(1,"作废"),6),mv("tag","opacity",at(1,"偷到"),at(1,"偷到")+12,1,0.35)]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        nodes=[("n1","登录成功","登录成功"),("n2","Set-Cookie 发手牌","发一张"),("n3","请求带上手牌","每次请求"),("n4","柜台按编号认人","凭编号")]
        e1=[tag("ti",220,160,120),A("li",'locker',1540,160,120,120)];a1=[]
        for j,(i,l,ph) in enumerate(nodes):
            x=160+j*427; e1.append(card(i,x,320,320,110,l,fontSize=32,stroke=P['accent'] if j==3 else P['secondary']))
            t=at(0,ph); a1+=[F(i,max(0,t-4)),mv(i,"scale",t,t+10,1.08,1,"spring")]
            if j<3: e1.append(E(f"ar{j}","arrow",x+320,345,107,60,P['primary'],direction="r")); a1.append(draw(f"ar{j}",t+8,8))
        e1+=[T("line",160,560,1600,60,"手牌在浏览器，东西在柜台",48,P['text'],align="center")]
        a1+=[F("ti",at(0,"发一张")),F("li",at(0,"凭编号")),F("line",at(0,"找到你"))]
        EP1=dict(id="ep1Frame",type="image",src="ep01:http-request/connect-1@220",asset=None,placeholder=True,x=1240,y=150,w=520,h=293,color=None,reuse=True,stroke=P['text2'],
            note="【待 Knoll 提供】做法同第三期 recap-2：复用第一期 http-request 的 connect-1 镜头第 220 帧（全局 1660），16:9 缩放到 520×293，2px text2 描边。")
        e2=[tag("tag",160,180,220),E("to","arrow",400,265,280,50,P['primary'],label="思路一样",direction="r",fontSize=36),
            R("token",700,200,400,160,stroke=P['accent'],radius=24,label="Token",fontSize=64),
            EP1,T("ep1Cap",1240,460,520,44,"第一期：建立连接",32,P['text2'],align="center"),
            T("carry",160,520,1600,60,"凭证带在身上，网站凭它认人",48,P['primary'],align="center"),
            T("ep1",160,600,1600,50,"接第一期：从输入 URL 到页面展示，发生了什么？",36,P['text2'],align="center"),
            T("title",160,680,1600,80,"网站怎么记住你已经登录？",56,P['accent'],align="center")]
        t=at(1,"Token"); te=AEND(5,1)
        a2=[F("tag",0),F("token",t),pop("token",t),draw("to",t,18),F("carry",at(1,"凭证")),
            F("ep1Frame",at(1,"网站凭")),F("ep1Cap",at(1,"网站凭")+6),F("ep1",at(1,"网站凭")+10),F("title",max(at(1,"网站凭")+20,te-20))]
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
EXTRA_HOLD={}  # 不用：hold 已在 map_timing.py 写进 timing.json 的 duration（条目带 extraHold 字段，不再叠加）
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
meta=dict(title="《网站怎么记住你已经登录？》",episode=4,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=False,style="深色背景+蓝青高光扁平2D（沿用前两期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880),
  notes="时长=Knoll MiMo 冰糖实测（/workspace/share/ep4-timing.json → timing.mimo.json → map_timing.py，scale 1）+ extraHold 共 180 帧（set-cookie-1 第 341 帧插 45，session-2/protect-2/recap-2 末尾各 45；纯画面停留，配音不动，后续镜头顺延）。set-cookie 合并为一个镜头 set-cookie-1（原 set-cookie-1 并入原 set-cookie-2），手牌最终飞进浏览器框内，Cookie 标在框内；同一元素有多段 opacity 动画（先淡入后淡出）按时间先后生效。recap-2 含第一期 connect-1@220 画面占位（placeholder，待 Knoll 提供）。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/cookie-session/。浏览器/服务器卡片统一样式（无窗口圆点，标签 36px）。新图标 tag/locker/thief 无文字。手牌随请求箭头移动用 x 关键帧。编号 0417 为示意。会话 ID、Set-Cookie 等英文均在白名单。")
assets=dict(reuse=[dict(id="browser",desc="浏览器卡片（标签 浏览器 36px）"),dict(id="server",desc="统一服务器卡片（无窗口圆点，标签 36px）"),dict(id="routeArrow",desc="第二期路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层")],
 new=[dict(id=f.stem,file=f"assets/{f.name}") for f in sorted((HERE/"assets").glob("*.svg"))])
sh2=[x for sc in scenes for x in sc['shots'] if x['id']=="set-cookie-1"][0]
pl=max(k['frame'] for a in sh2['animations'] for k in a['keyframes'])+6
meta['poster']=dict(shotId="set-cookie-1",localFrame=pl,frame=sh2['from']+pl,desc="服务器经 Set-Cookie 把手牌递给浏览器，手牌编号特写 + Cookie 标签",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
