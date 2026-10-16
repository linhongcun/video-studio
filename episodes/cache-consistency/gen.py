# EP.22《后台改了价格，页面怎么还是旧的？》缓存和数据库一致性（脚本 v0.28.0：8 章 + 五张章节卡）分镜（Miyazaki）。工具链沿用 EP.21；配音未到时按字数估时长
# 比喻：后厨备菜台（延续服务端缓存那期）。仓库价目账本=数据库；备菜台+价签=缓存；改签=更新缓存；撤盘=删缓存；待撤清单+跑腿员=消息队列重试；巡视员+流水账=订阅变更日志；分仓库=从库；计时牌=TTL；全店停单=强一致；结账看账本
# 术语：缓存/一致性/更新缓存/删缓存/延迟双删/消息队列/变更日志/主从延迟/过期时间（念 TTL）/最终一致；画面无数字/英文/logo（片尾问题卡原句含「App」例外）
import json,re,math,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'_audit'));import asrcue
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext,narration,CARDS,CARD
narr=narration(); assert len(narr)==11
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

titles=["还是旧价","两份数据","读的规矩","第一层：删，而不是改","第二层：先改库，再删缓存","第三层：删失败了怎么办","第四层：主从延迟","兜底：过期时间","最终一致","四格对比","结尾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
TM=json.load(open(HERE/"timing.json"))
ASR=json.load(open(HERE/"asr_words.json")) if (HERE/"asr_words.json").exists() else {}
PARTS=[];ATLOG=[]
def AT(si,_k,phrase,words=False,nth=0):
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    p0=s.index(phrase)
    for _ in range(nth): p0=s.index(phrase,p0+1)
    off=cnt(s[:p0])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    est=round(30*(q[i]["start"]+q[i]["dur"]*off))
    ATLOG.append((KEY(si,k),phrase,est));return est
def term(i,x,y,w,label,c=None,fs=64): return R(i,x,y,w,110,stroke=c or P['primary'],radius=55,label=label,fontSize=fs)
def tag(i,x,y,text,c=None,w=None): return R(i,x,y,max(w or 0,60+44*len(text)),80,stroke=c or P['text2'],radius=40,label=text,fontSize=40)
TOUT=36;SUB0=0
# v4 分段底色（RULES / storyboard-plan：红蓝只留给红站蓝站本体）
SEG={"intro":"#0B1020"}
def seg(c): return "intro"
RED="#F87171";BLUE="#3B82F6"
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
def flash(i,t): return dict(elementId=i,property="opacity",keyframes=[dict(frame=0,value=0),dict(frame=t,value=0),dict(frame=t+6,value=0.4),dict(frame=t+18,value=0)],easing="easeInOut")
def swap(a,b,t,n=10): return [out(a,t,n),mv(b,"opacity",0,t,0,0),F(b,t,n)]
def dimto(i,pts):   # pts=[(帧,值)...]
    return dict(elementId=i,property="opacity",keyframes=[dict(frame=f,value=v) for f,v in pts],easing="easeInOut")
def SPL(): return [R("pl",100,140,800,700,"#1F2937",stroke="#475569"),R("pr",1020,140,800,700,"#1F2937",stroke="#475569")]   # 左右分屏，中间 120 px 露底色的缝
Q1='你有没有遇到过：明明改了，刷新还是旧的？';Q2='评论区说说是哪个网站或 App。';RM='点个关注不迷路，觉得有用就点赞收藏。'
def flash_el(i,t): return dict(elementId=i,property='scale',keyframes=[dict(frame=0,value=1),dict(frame=t,value=1),dict(frame=t+8,value=1.15),dict(frame=t+20,value=1)],easing='easeInOut')
exec(open(HERE/'designs.py').read())

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
    if False:   # 开场大字期间不出字幕：前置空白字幕到 SUB0-1，之后的字幕不早于 SUB0（起点相撞的往后顺延）
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
    if ids[si] in CARDS:   # v4 章节卡：独立一场，整屏换底色；无旁白，Knoll 在下一句开口前插同长静音
        cid,name,col=CARDS[ids[si]];v=TM[cid];l=v["duration"]
        ce=[R("nm",360,370,1200,170,P['panel'],stroke="#F8FAFC",radius=55,label=name,fontSize=72,chapterCard=True)]
        csh=dict(id=cid,chapterId=cid,**{"from":g},durationInFrames=l,narration="",background=col,chapterCard=dict(name=name,holdFrames=l,insertBeforeSentence=v["insertBeforeSentence"],insertBeforeText=v["insertBeforeText"]),
                 subtitles=[dict(text="",**{"from":0},to=l-1,blank=True,note="章节卡静音，不出字幕")],elements=ce+[dict(T("subtitle",160,900,1600,80,"(字幕层)",44,P['text'],align="center",role="subtitle"),reuse=True)],
                 animations=[F("nm",0,4)],transition=dict(type="crossfade",durationInFrames=4))
        scenes.append(dict(id=f"s-{cid}",chapterId=cid,title=name,**{"from":g},durationInFrames=l,background=col,chapterCard=True,narrationCharsRecount=0,shots=[csh]));g+=l;nshot+=1
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
        shots.append(dict(id=KEY(si,k),chapterId=ids[si],**{"from":f},durationInFrames=l,narration=p,subtitles=subs(p,l,si,k),elements=els,animations=an,background=SEG[seg(ids[si])],transition=dict(type="fade" if last and ids[si]!="hook" else "crossfade",durationInFrames=12 if last and ids[si]!="hook" else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],background=SEG[seg(ids[si])],segment=seg(ids[si]),**{"from":g},durationInFrames=D,narrationCharsRecount=cnt(s),shots=shots));g+=D
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
    if sh['id']=='hook-1' or sh.get('chapterCard'): continue
    la=_lastact(sh);n=sh['durationInFrames']
    if n-la>=60 or sh is allsh[-1]:
        s0=0 if sh is allsh[-1] else min(la,n-60)
        sh['camera']=dict(pushIn=dict(fromScale=1.0,toScale=1.04,startFrame=max(0,s0),endFrame=n-1,origin=[960,470],easing="easeInOut"),note="静止段轻推镜：整层（不含字幕 / 水印）缓慢放大")
PROV=any(v.get('provisional') for v in TM.values())
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《后台改了价格，页面怎么还是旧的？》",hook="老板刚在后台把价格改低，刷新页面，怎么还是旧价？顾客到底该信哪个？答案马上来。",episode=22,slug="cache-consistency",release="v0.28.0",draft=True,provisional=PROV,provisionalReason=("冰糖配音未到：按字数估时长" if PROV else None),
  pendingAudio=PROV,series="缓存",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="扁平2D（门店价签对总部价目表，本期新设；竞态 / 变更日志用泳道技术图）；正片深色底 #0B1020，章节卡 #1E293B；旧价黄价签、新价绿价签，不写数值",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames = 正片 + hold，不含片尾卡，也不再留 60 帧留白；成片总长 = durationInFrames + 60"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，4.3 字/秒估）；Knoll /workspace/share/ep22/timeline.json + words.json 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json。")+
    "术语标签念到时淡入（0..+4），完整显示 ≥69；开场第 0 帧即主体（老板改价 + 页面旧价签）；门店价签对总部价目表比喻。")
import json as _j
REUSE=("ledger","ledger-ok","todo","db","slip","timer","cashier","person-blue","retry","price-old","price-new","wrong","phone-page","hourglass","eye","ask","boss")
NEW=tuple(sorted(f[:-4] for f in os.listdir(HERE/"assets") if f.endswith('.svg') and f[:-4] not in REUSE))
assets=dict(new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png") for n in NEW],reuse=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc="EP.19–22 自绘通用图标，复用（不含后厨素材）") for n in REUSE])
import hashlib as _h
_W="/workspace/share/ep22/narration.wav"
CC=[dict(shotId=s["id"],name=s["chapterCard"]["name"],holdFrames=s["durationInFrames"],startFrame=s["from"],startSec=round(s["from"]/30,2),insertBeforeSentence=s["chapterCard"]["insertBeforeSentence"],insertBeforeText=s["chapterCard"]["insertBeforeText"]) for sc in scenes for s in sc["shots"] if s.get("chapterCard")]
meta["chapterCards"]=CC
meta["endCard"]=dict(question=Q1+Q2,reminder=RM,order="先问题后提醒，不预告下期",file="endcard.txt")
meta["finalVideoFrames"]=g+30;meta["totalsNote"]="storyboard durationInFrames = 正片 + 章节卡 hold + 术语 hold；成片 = 它 + 30 尾帧（Knoll r6 实测）（片尾问题卡与关注提醒卡在正片内，长度按旁白，可超过 60 帧）"
meta["chapterCardNote"]=f"五张章节卡各 {CARD} 帧静音 hold（名字 0→4 帧淡入，完整显示 70 帧 ≥69，转场 crossfade 4）。Knoll：在 insertBeforeSentence 那句开口前（上一章章间停顿之后）插同长静音；startSec 为成片秒，交 Tim 做 B 站分段章节"
if not PROV: meta["narration"]=dict(file=_W,sha256=_h.sha256(open(_W,"rb").read()).hexdigest(),bodyFrames=sum(v.get("origDuration",v["duration"]) for v in TM.values() if not v.get("card")))
meta["notes"]=("时长=Knoll /workspace/share/ep22/timeline.json（narration.wav 实测）。" if not PROV else "时长=暂定字数估算。")+"术语标签念到时 0..+4 淡入，完整显示 ≥69；章节卡见 chapterCards；片尾两卡为旁白原句（endcard.txt）。"
meta["timingSource"]=("/workspace/share/ep22/timeline.json（Knoll）→ map_timing.py → timing.json" if not PROV else "字数估算 4.3 字/秒（make_timing.py）；Knoll /workspace/share/ep22/ 到后 sh realign.sh 重跑")
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面另做定制 PNG，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
