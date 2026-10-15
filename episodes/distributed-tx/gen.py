# EP.21《两个库，怎么一起成功或一起失败？》分布式事务（脚本 v0.26.0）分镜（Miyazaki）。工具链沿用 EP.20；配音未到时按字数估时长
# 比喻：驿站 + 拿对讲机的调度员。红站=订单账本，蓝站=货架；铅笔单/待出库格子=准备；绿红牌=能否提交；盖章/擦掉=统一生效/撤回；对讲机没声=干等；条子+跑腿员+签收=可靠消息
# 术语：两阶段提交 / 可靠消息 / 最终一致 / 分布式事务；只有右上「IT小村」；画面无数字/英文/logo
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

titles=["下单没扣","驿站","各管各的","先问准备好","两阶段提交","对讲机断了","可靠消息","最终一致","回顾"]
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
def show(i,t,n=8): return [mv(i,"opacity",0,t,0,0),F(i,t,n),pop(i,t)]
def TERM(i,t): return [F(i,t),pop(i,t)]
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # hook：①封面大字 → 手机成功页 + 付钱 → 货架满着、红叉 ②两个数据库各记各的：一个绿勾一个红叉
        e=[T("t1",140,200,1000,150,"两个库",120,P['text']),T("t2",140,370,1500,150,"怎么一起成功或一起失败？",96,P['accent']),
           I("ph","phone-ok",300,140,420),I("cn","coin",120,520,200),I("sh","shelf",1100,160,460),I("xx","ledger-bad",1400,520,240)]
        a=[out("t1",TOUT,SUB0-TOUT),out("t2",TOUT,SUB0-TOUT),mv("ph","opacity",0,SUB0,0,0),F("ph",SUB0,10)]
        a+=show("cn",max(SUB0+4,at(0,"付了钱")))+show("sh",max(SUB0+10,at(0,"仓库")))+show("xx",max(SUB0+16,at(0,"没扣库存")),6)
        e2=[I("d0","db",300,160,320),I("d1","db",1300,160,320),I("ok","ledger-ok",320,520,280),I("bad","ledger-bad",1320,520,280),I("sp","spark",820,300,280)]
        a2=[F("d0",0,8),F("d1",0,8)]+show("ok",at(1,"一个成了"))+show("bad",at(1,"另一个没成"),6)+show("sp",at(1,"另一个没成")+6,4)
        return [(e,a),(e2,a2)]
    if si==1:  # signal：①两个库 + 问号 → 一起成功（绿牌×2）②库变驿站：红站+账本，蓝站+货架
        e=[I("d0","db",260,200,320),I("d1","db",1340,200,320),I("q","ask",780,160,360),I("g0","sign-green",300,540,200),I("g1","sign-green",1400,540,200)]
        a=show("q",at(0,"怎么做到"))+show("g0",at(0,"一起成功"))+show("g1",at(0,"一起成功")+4)
        ty=at(0,"驿站");e2=[I("d0","db",200,200,300),I("d1","db",1420,200,300),I("sr","station-red",160,140,400),I("sb","station-blue",1360,140,400),I("lg","ledger",620,420,300),I("sh","shelf",1000,380,340)]
        a2=[out("d0",ty,10),out("d1",ty,10)]+show("sr",ty,10)+show("sb",ty+6,10)+show("lg",at(0,"记订单"))+show("sh",at(0,"管货架"))
        return [(e,a),(e2,a2)]
    if si==2:  # local：①单库能整笔擦掉 → 分成红站蓝站，红站擦自己的，管不到蓝站货架 ②中间空位 + 问号：得有人统一指挥
        td=at(0,"分到不同的库")
        e=[I("db","db",760,160,400),I("er","note-erased",820,560,200),I("sr","station-red",160,140,380),I("sb","station-blue",1380,140,380),
           I("e2","note-erased",260,520,220),I("sh","shelf",1420,500,300),I("xx","ledger-bad",1180,560,200)]
        a=show("er",at(0,"全部撤回"))+[out("db",td,10),out("er",td,10)]+show("sr",td,10)+show("sb",td+6,10)+show("e2",at(0,"撤回自己"))+show("sh",at(0,"对方的货架"))+show("xx",at(0,"管不到"),6)
        e2=[I("sr","station-red",160,140,380),I("sb","station-blue",1380,140,380),I("q","ask",760,220,400)]
        a2=show("q",at(1,"统一指挥"))
        return [(e,a),(e2,a2)]
    if si==3:  # prepare：①调度员拿对讲机出场 ②问号气泡 → 红站铅笔单（不盖章）→ 蓝站货进待出库格子锁住
        e=[I("sr","station-red",160,140,360),I("sb","station-blue",1400,140,360),I("dp","dispatcher",760,200,400)]
        a=show("dp",at(0,"调度员"),10)
        e2=[I("sr","station-red",120,120,340),I("sb","station-blue",1460,140,340),I("dp","dispatcher",780,100,360),I("q","ask",820,480,240),
            I("np","note-pencil",220,480,300),I("sl","slot-locked",1400,480,340)]
        a2=[F("dp",0,6)]+show("q",at(0,"准备好了吗"))+show("np",at(1,"铅笔"))+show("sl",at(1,"待出库"))+[out("q",at(1,"铅笔"),8)]
        return [(e,a),(e2,a2)]
    if si==4:  # commit：①绿牌×2 → 盖章；红牌 → 全部擦掉 ②术语「两阶段提交」：铅笔单 → 盖章单
        tg=at(0,"绿牌");ts=at(0,"一起盖章");tr=at(0,"红牌");te=at(0,"全部擦掉")
        e=[I("sr","station-red",120,120,320),I("sb","station-blue",1480,140,320),I("dp","dispatcher",800,100,320),
           I("g0","sign-green",200,460,200),I("g1","sign-green",1520,460,200),I("st","stamp",820,460,220),I("ns","note-stamped",480,460,260),
           I("r1","sign-red",1520,460,200),I("ne","note-erased",1160,460,260)]
        a=show("g0",tg)+show("g1",tg+4)+show("st",ts)+show("ns",ts+6)+[out("st",tr,8),out("ns",tr,8),out("g1",tr,6)]+show("r1",tr,6)+show("ne",te)
        e2=[I("np","note-pencil",360,200,320),I("ns","note-stamped",1240,200,320),I("st","stamp",860,240,200),term("lj",660,740,600,"两阶段提交")]
        a2=[F("np",0,8)]+show("st",at(1,"再统一生效"))+show("ns",at(1,"再统一生效")+6)+TERM("lj",at(1,"两阶段提交"))
        return [(e,a),(e2,a2)]
    if si==5:  # stuck：对讲机没声（红叉）→ 铅笔单、锁着的货原地不动 → 沙漏干等
        tn=at(0,"没声")
        e=[I("dp","dispatcher",780,100,360),I("df","dispatcher-off",780,100,360),I("np","note-pencil",200,420,300),I("sl","slot-locked",1380,420,340),I("hg","hourglass",820,500,280)]
        a=[F("dp",0,6),mv("df","opacity",0,tn,0,0),F("df",tn,6),out("dp",tn,6)]+show("hg",at(0,"干等"))
        return [(e,a)]
    if si==6:  # message：①调度员淡去 ②红站同一页账写订单+条子 → 跑腿员拿条子跑到蓝站 → 签收 ③重复条子打叉；术语「可靠消息」
        e=[I("sr","station-red",160,140,360),I("sb","station-blue",1400,140,360),I("dp","dispatcher",780,200,360)]
        a=[mv("dp","opacity",0,at(0,"不找"),1,1),mv("dp","opacity",at(0,"不找"),at(0,"不找")+12,1,0.15)]
        tr=at(0,"跑腿员")
        e2=[I("sr","station-red",120,120,360),I("sb","station-blue",1440,140,360),I("lg","ledger",160,500,280),I("sp","slip",460,520,220),
            I("rn","runner",500,300,260),I("sg","signed",1460,520,260)]
        a2=show("lg",at(0,"同一页账"))+show("sp",at(0,"条子"))+show("rn",tr)+moveto("rn",tr+10,at(0,"签收"),500,300,1160,300)+show("sg",at(0,"签收"))+[out("sp",tr+10,8)]
        e3=[I("sb","station-blue",200,140,380),I("bc","barcode-red",660,200,300),I("sg","signed",660,500,280),I("dup","slip-dup",1120,360,320),term("kk",660,740,600,"可靠消息")]
        a3=show("bc",at(0,"认单号"))+[F("sg",0,8)]+show("dup",at(0,"重复送来"))+TERM("kk",at(1,"可靠消息"))
        return [(e,a),(e2,a2),(e3,a3)]
    if si==7:  # eventual：订单记上（绿勾账本）+ 货架还满（黄灯）→ 「最后一定对上」时中间那箱货被搬走（滑出 + 淡出，留下空格）→ 绿勾；术语「最终一致」
        tf=at(0,"最后一定对上")
        e=[I("lg","ledger-ok",200,200,340),I("sh","shelf-gap",1300,160,400),I("bx","box",1460,326,80),I("lp","lamp-yellow",820,180,240),I("ok","ledger-ok",820,440,240),term("zz",660,740,600,"最终一致")]
        a=[F("lg",0,8),F("sh",0,8),F("bx",0,8)]+show("lp",at(0,"对不上"))+[out("lp",tf,8)]+moveto("bx",tf,tf+20,1460,326,1560,560)+[mv("bx","opacity",tf+8,tf+22,1,0)]+show("ok",tf+14)+TERM("zz",at(0,"最终一致"))
        return [(e,a)]
    if si==8:  # recap：天平：左 调度员+沙漏（稳但慢），右 跑腿员（快）+ 黄灯（短暂对不上）；术语「分布式事务」
        e=[I("bl","balance",760,120,400),I("dp","dispatcher",160,160,320),I("hg","hourglass",460,300,200),I("rn","runner",1420,160,320),I("lp","lamp-yellow",1260,320,160),term("fb",660,740,600,"分布式事务")]
        a=[F("bl",0,10)]+show("dp",at(0,"都说好"))+show("hg",at(0,"稳但慢"))+show("rn",at(0,"先记下来"))+show("lp",at(0,"短暂对不上"))+TERM("fb",at(1,"分布式事务"))
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
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《两个库，怎么一起成功或一起失败？》",hook="你下单付了钱，页面显示成功，仓库却根本没扣库存",episode=21,slug="distributed-tx",release="v0.26.0",draft=True,provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  pendingAudio=PROV,series="数据库入门",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.15–20）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾卡（只含全片结尾 60 帧留白）"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，4.3 字/秒估）；Knoll /workspace/share/ep21/timeline.json + words.json 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json。")+
    "术语标签（两阶段提交 / 可靠消息 / 最终一致 / 分布式事务）念到时淡入（0..+4），完整显示 ≥66；开场第 0 帧即封面；驿站 + 对讲机调度员比喻；素材自绘 + 复用 EP.19/20。")
import json as _j
REUSE=("station-red","station-blue","ledger","ledger-ok","ledger-bad","spark","parcel-red","person-blue","db","barcode-red","barcode-blue","badge-red","lamp-yellow")
NEW=tuple(sorted(f[:-4] for f in os.listdir(HERE/"assets") if f.endswith('.svg') and f[:-4] not in REUSE))
assets=dict(new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png") for n in NEW],reuse=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc="EP.19/20 自绘，复用") for n in REUSE])
meta["timingSource"]=("/workspace/share/ep21/timeline.json（Knoll）→ map_timing.py → timing.json" if not PROV else "字数估算 4.3 字/秒（make_timing.py）；Knoll /workspace/share/ep21/ 到后 sh realign.sh 重跑")
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面另做定制 PNG，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
