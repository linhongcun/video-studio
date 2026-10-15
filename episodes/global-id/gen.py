# EP.20《两个订单，怎么撞成同一个号了？》全局唯一 ID（脚本 v0.25.0 定稿）分镜（Miyazaki）。工具链沿用 EP.19；配音未到时按字数估时长
# 比喻：驿站条码打印机。色带=时间先后（色深无刻度）；徽章=站标记；流水戳（点阵疏密）=同一瞬间第几张。画面无数字/英文/logo
# 术语：自增 / 雪花算法 / 时钟回拨 / 全局唯一 ID；只有右上「IT小村」
import json,re,math,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','_audit'));import asrcue
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext,narration
narr=narration(); assert len(narr)==9
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

titles=["撞号","驿站打印机","一模一样的条码","本机自增","所有站不撞","雪花算法","停打","公共计数器","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
TM=json.load(open(HERE/"timing.json"))
ASR=json.load(open(HERE/"asr_words.json")) if (HERE/"asr_words.json").exists() else {}
PARTS=[];ATLOG=[]
def AT(si,_k,phrase,words=False):
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    est=round(30*(q[i]["start"]+q[i]["dur"]*off))
    aw=ASR.get(q[i].get("src"))
    if aw and words:
        ct=asrcue.char_times(aw,s);pos=len(asrcue.P(s[:s.index(phrase)]))
        if ct and pos<len(ct):
            g0=sum(TM[x]["duration"] for x in list(TM)[:list(TM).index(KEY(si,k))])
            est=max(0,round(30*(ct[pos]-ASR.get("_bias",0.05))-g0))
    ATLOG.append((KEY(si,k),phrase,est));return est
def term(i,x,y,w,label,c=None,fs=64): return R(i,x,y,w,110,stroke=c or P['primary'],radius=55,label=label,fontSize=fs)
def tag(i,x,y,text,c=None,w=None): return R(i,x,y,max(w or 0,60+44*len(text)),80,stroke=c or P['text2'],radius=40,label=text,fontSize=40)
def bub(i,x,y,t,c=None): return R(i,x,y,60+40*len(t),80,stroke=c or P['accent'],radius=40,label=t,fontSize=40)
TOUT=36;SUB0=45
# 术语完整显示 ≥66（terms.json）；holdOnProvisional=true
# EP.20 物件：驿站（色）= 库；条码打印机 = 发号；色带 = 时间先后（色深，无刻度）；徽章 = 站标记；流水戳（点阵疏密）= 同一瞬间第几张；小本子 = 本机自增；火花 = 撞号
def sig(i,x0,y0,x1,y1,t,dur=40,stop=None,c=None,keep=False):   # keep=True：圆点停在 stop 处不熄（镜头结束时还在半路）
    """信号线 + 移动圆点（复制）。Knoll 画线和点：节点带 knollDraw；圆点节点只作占位，动画全由 signal 参数决定。stop=圆点停在线上的比例（断电时死在半路）"""
    m=dict(knollDraw="signalLine",signal=dict(fromXY=[x0,y0],toXY=[x1,y1],dotStart=t,dotFrames=dur,dotStopAt=stop,dotKeep=keep,note="Knoll：画信号线，圆点从 from 沿线移到 to；dotStopAt≠null 时圆点停在该比例处并熄灭"))
    e=[E(i,"line",x0,y0,x1-x0,y1-y0,c or P['primary'],dashed=True,**m),R(i+"d",x0-12,y0-12,24,24,P['accent'],radius=12,knollDraw="signalDot",signalOf=i)]
    f=stop if stop is not None else 1;te=t+round(dur*f)
    a=[draw(i,0,1)]   # 圆点（signalDot）不带自己的 x/y/opacity 关键帧：只看线上 signal 参数，Knoll 画
    return e,a
def moveto(i,a,b,x0,y0,x1,y1,e="easeInOut"): return [mv(i,"x",a,b,x0,x1,e),mv(i,"y",a,b,y0,y1,e)]
def appear(i,t,n=10): return [F(i,t,n),pop(i,t)]
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # hook（v2 开场 A）：①封面大字 → 自己的订单页里混进别人的订单 ②拉远：好几个数据库各自盖条码 → 撞号火花
        tk=max(SUB0+6,at(0,"客服"));ts=max(SUB0+20,at(0,"别人的订单"))
        e=[T("t1",140,200,1000,150,"两个订单",120,P['text']),T("t2",140,370,1200,150,"怎么撞成同一个号了？",100,P['accent']),
           I("sr","barcode-same",1200,180,300),I("sb","barcode-same",1500,180,300),I("cs","spark",1400,120,200),
           I("pg","order-page",660,100,600),I("ck","clerk",1340,300,320),I("os","order-stranger",710,330,500,98),I("av","avatar-stranger",160,300,320)]
        a=[out("t1",TOUT,SUB0-TOUT),out("t2",TOUT,SUB0-TOUT),out("sr",TOUT,SUB0-TOUT),out("sb",TOUT,SUB0-TOUT),out("cs",TOUT,SUB0-TOUT),
           mv("pg","opacity",0,SUB0,0,0),F("pg",SUB0,10),mv("ck","opacity",0,tk,0,0),F("ck",tk,8),pop("ck",tk),
           mv("os","opacity",0,ts,0,0),F("os",ts,6),pop("os",ts),mv("av","opacity",0,ts+4,0,0),F("av",ts+4,8),pop("av",ts+4)]
        td=at(1,"拆成");tn=at(1,"自己编号");tc=at(1,"就撞了")
        DX=[160,620,1080,1540]
        e2=[I("pg","order-page",660,100,600)]+[I(f"d{j}","db",DX[j],180,240) for j in range(4)]+[I(f"b{j}","barcode-same",DX[j]+40,460,160) for j in range(4)]+[I("spk","spark",820,520,280)]
        a2=[mv("pg","scale",0,18,1,0.4),out("pg",10,10)]+[x for j in range(4) for x in (mv(f"d{j}","opacity",0,td+j*4,0,0),F(f"d{j}",td+j*4,8),pop(f"d{j}",td+j*4))]
        a2+=[x for j in range(4) for x in (mv(f"b{j}","opacity",0,tn+j*5,0,0),F(f"b{j}",tn+j*5,6),pop(f"b{j}",tn+j*5))]+[mv("spk","opacity",0,tc,0,0),F("spk",tc,4),pop("spk",tc)]
        return [(e,a),(e2,a2)]
    if si==1:  # signal：①怎么撞、怎么防（库在、问号气泡）②把库想成驿站 → 红蓝站 + 打印机 + 小本子（驿站只在此后出现）
        e=[I("d0","db",360,200,300),I("d1","db",1260,200,300),bub("q1",700,300,"怎么撞",P['danger']),bub("q2",760,460,"怎么防",P['success'])]
        a=[F("q1",at(0,"怎么撞"),8),pop("q1",at(0,"怎么撞")),mv("q2","opacity",0,at(0,"怎么防"),0,0),F("q2",at(0,"怎么防"),8),pop("q2",at(0,"怎么防"))]
        ty=at(1,"驿站");tp=at(1,"条码打印机");tn=at(1,"小本子")
        e2=[I("d0","db",200,200,300),I("d1","db",1420,200,300),I("sr","station-red",180,160,380),I("sb","station-blue",1360,160,380),
            I("pr","printer",640,300,240),I("pb","printer",1040,300,240),I("nr","notebook",280,540,200),I("nb","notebook",1460,540,200)]
        a2=[out("d0",ty,10),out("d1",ty,10),mv("sr","opacity",0,ty,0,0),F("sr",ty,10),pop("sr",ty),mv("sb","opacity",0,ty+6,0,0),F("sb",ty+6,10),pop("sb",ty+6),
            mv("pr","opacity",0,tp,0,0),F("pr",tp,8),pop("pr",tp),mv("pb","opacity",0,tp+4,0,0),F("pb",tp+4,8),pop("pb",tp+4),
            mv("nr","opacity",0,tn,0,0),F("nr",tn,8),pop("nr",tn),mv("nb","opacity",0,tn+4,0,0),F("nb",tn+4,8),pop("nb",tn+4)]
        return [(e,a),(e2,a2)]
    if si==2:  # clash：互不知道 → 各打出一模一样的条码 → 火花
        tp=at(0,"各打出");tc=at(0,"一模一样")
        e=[I("sr","station-red",160,140,380),I("sb","station-blue",1380,140,380),I("nr","notebook",280,500,180),I("nb","notebook",1500,500,180),
           I("br","barcode-same",520,500,260),I("bb","barcode-same",1140,500,260),I("spk","spark",820,380,280)]
        a=[mv("br","opacity",0,tp,0,0),F("br",tp,8),pop("br",tp),mv("bb","opacity",0,tp+6,0,0),F("bb",tp+6,8),pop("bb",tp+6),mv("spk","opacity",0,tc,0,0),F("spk",tc,4),pop("spk",tc)]
        return [(e,a)]
    if si==3:  # 自增：①本机只管自己这台 ②标签「自增」
        e=[I("sv","server",200,180,320),I("nb","notebook",560,280,260),I("pr","printer",1000,240,300),tag("ms",1400,300,"本机",P['primary'],200)]
        a=[F("sv",0,8),F("nb",at(0,"本机自增"),8),pop("nb",at(0,"本机自增")),F("ms",at(0,"这一台"),8)]
        e2=[I("sr","station-red",400,160,500),I("nb","notebook",1100,280,300),term("zz",760,740,300,"自增")]
        a2=[F("zz",at(1,"自增本来")),pop("zz",at(1,"自增本来"))]
        return [(e,a),(e2,a2)]
    if si==4:  # 所有站都不撞，又不能挤回一台发号机
        e=[I("sr","station-red",120,200,300),I("sb","station-blue",440,200,300),I("sg","station-green",760,200,300),
           I("hub","hub",1200,160,420),I("clk","clock",1500,520,160)]+[I(f"p{j}","person-blue",200+j*160,560,120) for j in range(4)]
        a=[mv("hub","opacity",0,at(0,"发号机"),0.35,0.35),mv("hub","opacity",at(0,"发号机"),at(0,"发号机")+10,0.35,1),
           F("clk",at(0,"挤回"),8),pop("clk",at(0,"挤回"))]+[F(f"p{j}",at(0,"挤回")+j*3,6) for j in range(4)]
        return [(e,a)]
    if si==5:  # 雪花：色带 + 徽章 + 流水戳 → 拼在一起不撞；各站自己打；标签「雪花算法」
        # shot1: 打印机盖三样
        tr=at(0,"色带");tb=at(0,"徽章");ts=at(0,"流水戳")
        e=[I("pr","printer",720,160,400),I("rb","ribbon",160,280,320),I("bd","badge-red",160,560,200),I("st","stamp-mid",1480,300,280)]
        a=[F("rb",tr,8),pop("rb",tr),F("bd",tb,8),pop("bd",tb),F("st",ts,8),pop("st",ts)]
        # shot2: 拼在一起 → 两站打出不同条码（不撞）
        e2=[I("sr","station-red",160,140,360),I("sb","station-blue",1400,140,360),
            I("br","barcode-red",240,480,280),I("bb","barcode-blue",1400,480,280),
            I("ok","ledger-ok",860,400,200)]
        a2=[F("br",0,8),F("bb",0,8),F("ok",at(0,"不会撞"),8),pop("ok",at(0,"不会撞"))]
        # shot3: 雪花算法标签
        e3=[I("rb","ribbon",200,200,280),I("bd","badge-blue",560,220,240),I("st","stamp-dense",880,200,280),
            I("bc","barcode-blue",1280,240,360),term("xh",660,740,600,"雪花算法")]
        a3=[F("xh",at(0,"雪花算法")),pop("xh",at(0,"雪花算法"))]
        return [(e,a),(e2,a2),(e3,a3)]
    if si==6:  # 钟被拨回去 → 黄灯停打，不打重复条码；标签「时钟回拨」
        e=[I("wc","wallclock",200,160,400),I("wb","wallclock-back",200,160,400),
           I("pr","printer",900,200,360),I("lp","lamp-yellow",1400,200,280),
           I("bc","barcode-red",1000,560,280),term("sb",660,740,500,"时钟回拨")]
        tb=at(0,"拨回去");ts=at(0,"停下来")
        a=[mv("wb","opacity",0,tb,0,0),F("wb",tb,8),out("wc",tb,8),
           mv("lp","opacity",0,ts,0,0),F("lp",ts,8),pop("lp",ts),
           mv("bc","opacity",0,1,0.3,0.3),F("sb",at(0,"拨回去")),pop("sb",at(0,"拨回去"))]
        return [(e,a)]
    if si==7:  # Redis 公共计数器 → 大家又都挤回一台发号机（人群向中央发号机聚拢）
        tc=at(0,"公共计数器");tj=at(0,"挤回")
        e=[I("hub","hub",760,140,400),tag("rd",1360,240,"公共计数器",P['accent'],320)]+[I(f"p{j}","person-red" if j%2 else "person-blue",160+j*340,600,140) for j in range(5)]
        a=[F("hub",tc,8),pop("hub",tc),F("rd",tc,8)]+[x for j in range(5) for x in moveto(f"p{j}",tj+j*2,tj+j*2+24,160+j*340,600,700+j*90,560)]
        return [(e,a)]
    if si==8:  # 回顾：数据库拆开之后，订单号按全局不撞 → 全局唯一 ID
        e=[I("d0","db",120,160,200),I("d1","db",360,160,200),I("d2","db",600,160,200),
           I("br","barcode-red",160,440,220),I("bb","barcode-blue",480,440,220),
           I("ok","ledger-ok",900,280,260),term("qy",1180,700,560,"全局唯一 ID",fs=56)]
        a=[F("qy",at(0,"全局唯一 ID")),pop("qy",at(0,"全局唯一 ID")),F("ok",at(0,"全局不撞"),8),pop("ok",at(0,"全局不撞"))]
        return [(e,a)]

def subs(t,L,si,k):
    S=sentences(t);q=TM[KEY(si,k)]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？" and len(m[-1]+c)<=24: m[-1]+=c   # EP.18：合并后不超过 24 字
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
        _ids={x['id'] for x in els};an=[x for x in an if x['elementId'] in _ids]   # 去掉指向已删节点的动画
        els=[dict(e) for e in els]+[dict(T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],align="center",role="subtitle"),reuse=True)]
        for a in an:
            for kf in a['keyframes']:
                if not 0<=kf['frame']<=l-1: CLAMP.append((KEY(si,k),a['elementId'],a['property'],kf['frame'],l))
                kf['frame']=max(0,min(l-1,kf['frame']))
        last=k==len(parts)-1
        shots.append(dict(id=KEY(si,k),chapterId=ids[si],**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationCharsRecount=cnt(s),shots=shots));g+=D
# 图片节点（Knoll 2026-10-15：渲染器照图片节点加图片元素）：每个 image 元素补 appearFrame / disappearFrame（镜头内帧，按 opacity 关键帧算；null=到镜头末尾）、z（叠放顺序，越大越上）、tagText（贴在该物件上的小标签文字）
TAGS={}   # 本期不贴任何小标签文字
def _op(sh,eid,f):
    v=1.0;K=[k for a in sh['animations'] if a['elementId']==eid and a['property']=='opacity' for k in a['keyframes']]
    if not K: return 1.0
    K=sorted(K,key=lambda k:k['frame'])
    if f<=K[0]['frame']: return K[0]['value']
    for a_,b_ in zip(K,K[1:]):
        if a_['frame']<=f<=b_['frame']: return a_['value']+(b_['value']-a_['value'])*(f-a_['frame'])/max(1,b_['frame']-a_['frame'])
    return K[-1]['value']
for sc in scenes:
    for sh in sc['shots']:
        for z,e in enumerate(sh['elements']):
            if e['type']!='image': continue
            vis=[f for f in range(sh['durationInFrames']) if _op(sh,e['id'],f)>0.01]
            e['appearFrame']=vis[0] if vis else None
            e['disappearFrame']=(vis[-1]+1) if vis and vis[-1]<sh['durationInFrames']-1 else None
            e['z']=z
            if e['id'] in TAGS: e['tagText']=TAGS[e['id']]

def _lastact(sh):
    K=[k['frame'] for a in sh['animations'] if a['property']!='drawProgress' for k in a['keyframes']]
    return max(K) if K else 0
allsh=[x for sc in scenes for x in sc['shots']]
for sh in allsh:
    if sh['id']=='hook-1': continue
    la=_lastact(sh);n=sh['durationInFrames']
    if n-la>=60 or sh is allsh[-1]:
        s0=0 if sh is allsh[-1] else min(la,n-60)
        sh['camera']=dict(pushIn=dict(fromScale=1.0,toScale=1.04,startFrame=max(0,s0),endFrame=n-1,origin=[960,470],easing="easeInOut"),note="静止段轻推镜：整层（不含字幕 / 水印）缓慢放大")
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《两个订单，怎么撞成同一个号了？》",hook="两个订单怎么撞成同一个号了",episode=20,slug="global-id",release="v0.25.0-A",draft=True,provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  pendingAudio=PROV,series=None,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.15–19）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾卡（只含全片结尾 60 帧留白）"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，4.3 字/秒估）；Knoll /workspace/share/ep20/timeline.json + words.json 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json。")+
    "术语标签（自增 / 雪花算法 / 时钟回拨 / 全局唯一 ID）念到时淡入（0..+4），完整显示 ≥66；开场第 0 帧即封面；驿站条码打印机比喻（色带 / 徽章 / 流水戳，画面无数字刻度）；素材自绘 + 复用 EP.19。")
NEW=("order-page","order-stranger","avatar-stranger","db","badge-blue","badge-green","badge-red","badge-yellow","barcode-blue","barcode-green","barcode-red","barcode-same","hub","lamp-green","lamp-red","lamp-yellow","notebook","notebook-torn","printer","ribbon","ribbon-early","ribbon-late","stamp-dense","stamp-mid","stamp-sparse","wallclock","wallclock-back","window")
REUSE=("clerk","clerk-busy","clock","crash","idtag","ledger","ledger-bad","ledger-ok","order","parcel-blue","parcel-red","person-blue","person-red","server","spark","station","station-blue","station-green","station-red","station-yellow")
assets=dict(new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png") for n in NEW],
  reuse=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc="EP.19 自绘，复用") for n in REUSE])
meta["timingSource"]=("/workspace/share/ep20/timeline.json（Knoll）→ map_timing.py → timing.json" if not PROV else "字数估算 4.3 字/秒（make_timing.py）；Knoll /workspace/share/ep20/ 到后 sh realign.sh 重跑")
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面用 cover/ep20-*.png 定制设计，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
