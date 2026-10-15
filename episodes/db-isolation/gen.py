# EP.16《没封箱的包裹，别人看得见吗？》（脚本 v0.21.0 定稿）分镜生成（Miyazaki）。工具链沿用 EP.15 db-transaction/gen.py
# 比喻：第 3 章前的大纸箱 = 一笔事务（沿用 EP.15 box-open / box-sealed）；第 4、5 章的青色小包裹（parcel-row，贴行号）= 一行数据。
# 画面不出现任何隔离级别名、任何英文；术语标签只用中文（隔离级别 / 脏读 / 不可重复读 / 幻读）；示例数字标「示例」
import json,re,math,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','_audit'));import asrcue
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext,narration
narr=narration(); assert len(narr)==7
def cnt(s): return len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",success="#22C55E",accent="#F59E0B",danger="#F87171")
def R(i,x,y,w,h,c=P['panel'],**k): return dict(id=i,type="rect",x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def T(i,x,y,w,h,t,fs=40,c=P['text'],**k): return dict(id=i,type="text",x=x,y=y,w=w,h=h,text=t,fontSize=fs,**{"color":c,"reuse":False,**k})
def E(i,ty,x,y,w,h,c,**k): return dict(id=i,type=ty,x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def I(i,name,x,y,w,h=None,**k): return dict(id=i,type="image",asset=f"assets/{name}.svg",x=x,y=y,w=w,h=w if h is None else h,**{"color":None,"reuse":False,**k})
def fade(i,a=0,b=12): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=0),dict(frame=b,value=1)],easing="easeOut")
def mv(i,p,a,b,va,vb,e="easeInOut"): return dict(elementId=i,property=p,keyframes=[dict(frame=a,value=va),dict(frame=b,value=vb)],easing=e)
def draw(i,a,n=15): return mv(i,"drawProgress",a,a+n,0,1,"easeOut")
def F(i,a,n=12): return fade(i,a,a+n)
def out(i,a,n=10): return mv(i,"opacity",a,a+n,1,0)
def pop(i,a): return mv(i,"scale",a,a+12,0,1,"spring")
def hl(i,a,c=P['success'],c0=P['secondary']): return mv(i,"strokeColor",a,a+10,c0,c)
titles=["看见了又没了","同一个仓库","偷看没封箱的","看两眼不一样","数两遍多一个","代价","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
TM=json.load(open(HERE/"timing.json"))
ASR=json.load(open(HERE/"asr_words.json")) if (HERE/"asr_words.json").exists() else {}
PARTS=[]
def AT(si,_k,phrase):   # 非术语画面动作的时刻：按字数插值（术语标签另由 labelfix 按词级 ASR 对齐）
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def term(i,x,y,w,label,c=None,fs=64): return R(i,x,y,w,110,stroke=c or P['primary'],radius=55,label=label,fontSize=fs)
def ex(i,x,y,w=300): return T(i,x,y,w,40,"（示例）",28,P['text2'],align="center")
def parcel(i,x,y,w,num,op=None):   # 一行数据 = 青色小包裹，白色标签上写行号
    e=[I(i,"parcel-row",x,y,w),T(i+"n",x+round(w*0.40),y+round(w*0.52),round(w*0.30),round(w*0.22),num,max(28,round(w*0.13)),"#0E7490",align="center")]
    return e
def stairs(p,x,y0,w,gap,hs,hi=None):   # 几档规矩：不写级别名，只画由低到高的台阶
    return [R(f"{p}{j}",x+j*(w+gap),y0-h,w,h,stroke=(P['accent'] if j==hi else P['primary']),radius=12) for j,h in enumerate(hs)]
TOUT=36;SUB0=45   # hook-1（Nolan 2026-10-14）：封面大字完整显示 0–36 帧，36–45 淡出；第一条字幕从 45 帧进（0–44 空白字幕）
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 开场即封面：第 0 帧满屏，不淡入（参照 cover/ep16-16x9.png）；Nolan：大字 60 帧后退场（TOUT），字幕等大字退场后（SUB0）才进
        tg=at(0,"又没了");tb=at(0,"还没封箱的包裹")
        e=[T("t1",280,80,1100,150,"没封箱的包裹",128,P['text']),T("t2",280,236,1200,150,"别人看得见吗？",128,P['accent']),
           I("you","person",300,450,280),I("eye","eye",600,470,150),E("sight","line",770,545,190,0,P['primary'],dashed=True),
           I("box","box-open",980,400,400),R("plus",1440,450,260,110,stroke=P['accent'],radius=20,label="+100",fontSize=64),ex("ex",1420,580)]
        a=[out("t1",TOUT,SUB0-TOUT),out("t2",TOUT,SUB0-TOUT),mv("plus","opacity",tg,tg+10,1,0.25),mv("box","scale",tb,tb+8,1,1.08),mv("box","scale",tb+8,tb+16,1.08,1)]
        return [(e,a)]
    if si==1:  # 同一个仓库：上期的封箱 → 很多人同时在打包 → 你能看到吗
        tw=at(0,"可仓库里");tm=at(0,"很多人在打包");ty=at(0,"你能不能看到")
        X=[240,760,1280]
        e1=[I("sealed","box-sealed",760,200,400)]+[I(f"w{j}","person",x,300,180) for j,x in enumerate(X)]+[I(f"b{j}","box-open",x+180,380,160) for j,x in enumerate(X)]+[
            I("eye","eye",860,660,180)]
        a1=[F("sealed",0,8),out("sealed",tw)]+[F(f"w{j}",tm+j*6,8) for j in range(3)]+[F(f"b{j}",tm+j*6+4,8) for j in range(3)]+[F("eye",ty),pop("eye",ty)]
        e2=stairs("st",460,720,220,40,[120,200,280,360])+[T("lo",460,736,220,56,"松",40,P['text2'],align="center"),T("hi",1240,736,220,56,"严",40,P['text2'],align="center"),
            term("gl",760,170,400,"隔离级别")]
        a2=[F(f"st{j}",j*5,8) for j in range(4)]+[F("lo",0),F("hi",0),F("gl",at(0,"隔离级别")),pop("gl",at(0,"隔离级别"))]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 脏读：偷看别人没封箱的事务，他倒着撤回
        tp=at(0,"偷看");tr=at(0,"倒着撤回")
        base=[I("you","person",200,400,240),I("eye","eye",440,420,120),I("box","box-open",860,320,400),I("own","person",1340,380,220)]
        e1=base+[R("plus",950,230,220,90,stroke=P['accent'],radius=18,label="+100",fontSize=52),R("seen",160,230,420,100,stroke=P['text2'],radius=18,label="看到 +100",fontSize=44),
            ex("ex",160,340,420),I("rw","rewind",1360,200,140)]
        a1=[F("seen",tp),F("ex",tp),draw("sight",tp) if False else F("eye",tp-6,6),F("rw",tr),pop("rw",tr),mv("plus","y",tr+8,tr+30,230,380,"easeIn"),out("plus",tr+24,8)]
        e2=base+[R("seen",160,230,420,100,stroke=P['text2'],radius=18,label="看到 +100",fontSize=44),ex("ex",160,340,420),E("strike","line",180,280,380,0,P['danger']),
            T("x",590,220,120,120,"×",96,P['danger'],align="center"),term("dr",860,740,400,"脏读")]
        tv=at(0,"已经被撤回")
        a2=[draw("strike",tv,10),F("x",tv+6),pop("x",tv+6),F("dr",at(1,"脏读")),pop("dr",at(1,"脏读"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 不可重复读：同一行看两眼，中间别人提交了新版本
        t1=at(0,"看了两眼");tn=at(0,"封箱寄出了新版本");t2=at(0,"两眼内容不一样")
        base=parcel("row",820,240,280,"3 号")+[T("h1",160,260,400,56,"第 1 眼",40,P['text2'],align="center"),R("v1",160,330,400,180,stroke=P['secondary'],radius=20,label="100",fontSize=80),
              T("h2",1360,260,400,56,"第 2 眼",40,P['text2'],align="center"),R("v2",1360,330,400,180,stroke=P['accent'],radius=20,label="200",fontSize=80),ex("ex",160,530,400)]
        e1=base+[I("new","box-sealed",880,600,160)]
        a1=[F("row",0,8),F("rown",0,8),F("h1",t1),F("v1",t1),F("ex",t1),F("new",tn),mv("new","y",tn+12,tn+36,600,520),out("new",tn+36,8),mv("row","scale",tn+40,tn+48,1,1.08),mv("row","scale",tn+48,tn+56,1.08,1),
            F("h2",t2),F("v2",t2)]
        e2=base+[T("ne",860,560,200,140,"≠",120,P['danger'],align="center"),term("nr",660,740,600,"不可重复读")]
        a2=[F("ne",0,8),F("nr",at(0,"不可重复读")),pop("nr",at(0,"不可重复读"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 幻读：数两遍，多出一个
        t1=at(0,"你数一遍");t2=at(0,"再数一遍");tg=at(0,"凭空冒出来")
        r1=[T("p1",160,220,240,60,"第 1 遍",40,P['text2'])]+sum([parcel(f"a{j}",440+j*260,160,200,str(j+1)) for j in range(3)],[])+[T("c1",1500,220,260,70,"3 个",52,P['text'])]
        r2=[T("p2",160,520,240,60,"第 2 遍",40,P['text2'])]+sum([parcel(f"b{j}",440+j*260,460,200,str(j+1)) for j in range(4)],[])+[T("c2",1500,520,260,70,"4 个",52,P['accent'])]
        ring=[R("ring",1200,450,240,220,radius=30,stroke=P['accent'],color="#00000000",dashed=True)]
        e1=r1+r2+ring+[ex("ex",1480,300,300)]
        A1=[F(x,t1) for x in ["p1","c1","ex"]]+[F(f"a{j}",t1+j*5,6) for j in range(3)]+[F(f"a{j}n",t1+j*5,6) for j in range(3)]
        A2=[F(x,t2) for x in ["p2"]]+[F(f"b{j}",t2+j*5,6) for j in range(3)]+[F(f"b{j}n",t2+j*5,6) for j in range(3)]+[
            mv("b3","opacity",tg-10,tg+10,0,0.6),F("b3n",tg),F("ring",tg),F("c2",tg)]
        e2=r1+r2+ring+[ex("ex",1480,300,300),term("pr",760,740,400,"幻读")]
        a2=[mv("b3","opacity",0,1,0.6,0.6),F("pr",at(0,"幻读")),pop("pr",at(0,"幻读"))]
        return [(e1,A1+A2),(e2,a2)]
    if si==5:  # 代价：规矩严能挡更多；但要排队、撞车整单重来
        ts=at(0,"能挡住");tq=at(0,"排队等");tc=at(0,"撞车了");tr=at(0,"整单重来")
        e=[I("shield","shield",200,240,320)]+[I(f"q{j}","person",760+j*140,330,130) for j in range(3)]+[I("clk","clock",860,560,140),T("qT",760,720,400,56,"排队",40,P['text2'],align="center"),
           I("crash","crash",1360,260,260),I("rw","rewind",1420,540,140),T("rT",1340,720,300,56,"重来",40,P['text2'],align="center")]
        a=[F("shield",0,8),pop("shield",ts)]+[F(f"q{j}",tq+j*5,8) for j in range(3)]+[F("clk",tq+10),F("qT",tq),F("crash",tc),pop("crash",tc),F("rw",tr),F("rT",tr)]
        return [(e,a)]
    if si==6:  # 回顾
        e1=stairs("st",200,740,140,30,[100,180,260,340])+[term("gl",180,170,520,"隔离级别"),I("eye","eye",1180,200,180),I("bo","box-open",980,430,280),I("bs","box-sealed",1360,430,280)]
        a1=[F(f"st{j}",0,6) for j in range(4)]+[F("eye",0,6),F("bo",0,6),F("bs",at(0,"刚封好")),F("gl",at(0,"隔离级别"))]
        e2=[term("d0",160,170,480,"脏读",P['danger'],56),term("d1",700,170,520,"不可重复读",P['accent'],56),term("d2",1280,170,480,"幻读",P['secondary'],56)]+stairs("st",600,760,140,30,[100,180,260,340],hi=2)+[
            T("pick",940,800-340-120,200,56,"你选的",40,P['accent'],align="center")]
        tp=at(1,"你选的那一档")
        a2=[F(f"st{j}",0,6) for j in range(4)]+[F("d0",at(0,"脏读")),F("d1",at(0,"不可重复读")),F("d2",at(0,"幻读")),hl("st2",tp,P['accent'],P['primary']),F("pick",tp)]
        return [(e1,a1),(e2,a2)]
def subs(t,L,si,k):
    S=sentences(t);q=TM[KEY(si,k)]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
            else: m.append(c)
        tot=sum(cnt(x) for x in m);acc=0;ct=None;pos=0
        aw=ASR.get(qq.get("src"))
        if aw: ct=asrcue.char_times(aw,s)   # 词级：按位置对齐到脚本字序（同音错字不影响）
        g0=sum(TM[x]["duration"] for x in list(TM)[:list(TM).index(KEY(si,k))])
        for c in m:
            if ct: f_=math.floor(30*(ct[pos]-ASR.get("_bias",0.1))-g0)   # 字幕不晚于配音：去掉宁晚偏置，向下取整
            else: f_=round(30*(qq["start"]+qq["dur"]*acc/tot))
            res.append({"text":subtext(c.strip().rstrip('，；：。？')),"from":max(0,f_),"src":qq.get("src"),"voiceFrom":max(0,f_)});acc+=cnt(c);pos+=len(asrcue.P(c))
    for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    res[0]["from"]=0
    if (si,k)==(0,0):   # 开场大字期间不出字幕：前置空白字幕到 SUB0-1，之后的字幕不早于 SUB0（起点相撞的往后顺延）
        for r in res: r["from"]=max(r["from"],SUB0)
        for a_,b_ in zip(res,res[1:]):
            if b_["from"]<a_["from"]+30: b_["from"]=a_["from"]+30   # 被大字推后的字幕至少留 30 帧可读；其余按配音起点不动
        res.insert(0,{"text":"","from":0,"blank":True,"note":"开场封面大字期间不出字幕"})
        for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    return res
scenes=[];g=0;nshot=0;CLAMP=[]
for si,s in enumerate(narr):
    S=sentences(s);parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S)
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
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationCharsRecount=cnt(s),shots=shots));g+=D
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《没封箱的包裹，别人看得见吗？》",hook="没封箱的包裹别人看得见吗",episode=16,slug="db-isolation",release="v0.21.0",provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  series=None,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.15）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，按 EP.15 实测语速估，章尾 60 帧）；Knoll timeline 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll 实测（map_timing.py，章 = 首句起 → 末句止 + 60 帧）。")+"术语标签（隔离级别 / 脏读 / 不可重复读 / 幻读，只用中文）念到时淡入（words.json 词级，句首不早于句子起点再 +0.1 s）；开场第 0 帧即封面画面；第 3 章大纸箱 = 事务，第 4、5 章青色小包裹 = 一行数据；画面无英文、无级别名；示例数字标「示例」。素材全部自绘。")
assets=dict(reuse=[dict(id="subtitle",desc="字幕层"),dict(id="person",file="assets/person.svg",desc="小人（EP.14 自绘）")],
  new=[dict(id=n,file=f"assets/{n}.svg",desc=d) for n,d in (("coin","硬币 ¥"),("fault","故障闪电"),("box-open","打开的包裹=事务"),("box-sealed","封箱（青胶带+✓）=提交"),("rewind","倒放=回滚"),("box-half","拆成两半+✗=不能寄一半"),("account","账户卡（备用，未上画面）"))])
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面用 cover/ep16-*.png 定制设计，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
