# EP.15《扣了钱，对方没到账？》（脚本 v0.20.0，**待村长定稿：临时版 provisional**）分镜生成（Miyazaki）。工具链沿用 EP.14 db-index/gen.py
# 贯穿比喻：转账 = 两步（左账户 −100、右账户 +100）；包裹 = 事务；封箱寄出 = 提交；钱沿原路倒放回来 = 回滚；包裹不能拆开寄一半 = 原子性。
# 画面不放 COMMIT/ROLLBACK/ACID（术语标签只用中文）；余额 500/200 是示例，每个出现余额的镜头都标「（示例）」
import json,re
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
titles=["扣了没到","拆成两步","同一个包裹","封箱","倒着撤回","不能拆一半","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
TM=json.load(open(HERE/"timing.json"))
PARTS=[]
def AT(si,_k,phrase):   # 非术语画面动作的时刻：按字数插值（术语标签另由 labelfix 按词级 ASR 对齐）
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def term(i,x,y,w,label,c=None,fs=64): return R(i,x,y,w,110,stroke=c or P['primary'],radius=55,label=label,fontSize=fs)
def tick(i,x,y,c=P['success'],fs=96,t="✓"): return T(i,x,y,120,120,t,fs,c,align="center")
# ── 固定布局：左「你」账户、右「朋友」账户（全片同一位置）。余额用叠放的两张卡互换（旧卡淡出、新卡淡入）
AL,AR,AY,AW,AH=160,1320,380,440,200
def accounts(l="500",r="200",l2=None,r2=None):
    e=[I("pL","person",AL+150,170,150),I("pR","person",AR+150,170,150),
       R("bL",AL,AY,AW,AH,stroke=P['secondary'],radius=24,label=l,fontSize=88),R("bR",AR,AY,AW,AH,stroke=P['secondary'],radius=24,label=r,fontSize=88),
       T("nL",AL,AY+AH+16,AW,50,"你",40,P['text2'],align="center"),T("nR",AR,AY+AH+16,AW,50,"朋友",40,P['text2'],align="center"),
       T("ex",AL,AY+AH+76,AW,40,"（示例）",28,P['text2'],align="center")]
    if l2: e.append(R("bL2",AL,AY,AW,AH,stroke=P['secondary'],radius=24,label=l2,fontSize=88))
    if r2: e.append(R("bR2",AR,AY,AW,AH,stroke=P['secondary'],radius=24,label=r2,fontSize=88))
    return e
def swap(a,b,t): return [out(a,t),F(b,t)]
CX=760;CW=400   # 中间区域 x 640–1280
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 开场即封面（Nolan：抖音前 5 秒）：第 0 帧满屏出齐——标题大字 + 你 400（500 划掉）+ 硬币被闪电截断 +「？」+ 朋友 200 红框；布局参照 cover/ep15-16x9.png
        tm=at(0,"没收到");tq=at(0,"钱去哪儿了")
        BX,BY,BW,BH=270,420,400,320;RX=1650-BW;py=BY+BH*0.58
        e=[T("t1",280,80,900,150,"扣了钱，",128,P['text']),T("t2",280,236,1100,150,"对方没到账？",128,P['accent']),
           R("bL",BX,BY,BW,BH,stroke=P['secondary'],radius=36,label="400",fontSize=150),
           T("old",BX,BY+20,BW,70,"500",56,P['muted'],align="center"),E("strike","line",BX+140,BY+58,120,0,P['danger']),
           R("bR",RX,BY,BW,BH,stroke=P['danger'],radius=36,label="200",fontSize=150),
           T("nL",BX,BY+BH+14,BW,60,"你",48,P['text2'],align="center"),T("nR",RX,BY+BH+14,BW,60,"朋友",48,P['text2'],align="center"),
           T("ex",BX+BW,BY+BH+20,RX-BX-BW,50,"（余额为示例）",36,P['text2'],align="center"),
           E("path","line",BX+BW+30,round(py),280,0,P['accent'],dashed=True),I("coin","coin",BX+BW+90,round(py-60),120),
           I("bolt","fault",1010,round(py-130),170,240),T("q",1100,300,140,160,"？",128,P['accent'],align="center")]
        a=[mv("bolt","scale",tm,tm+6,1,1.15),mv("bolt","scale",tm+6,tm+14,1.15,1),mv("q","scale",tq,tq+6,1,1.2),mv("q","scale",tq+6,tq+14,1.2,1)]
        return [(e,a)]
    if si==1:  # 拆成两步
        t1=at(0,"先从你账上减");t2=at(0,"再往他账上加")
        e1=accounts()+[R("s1",680,200,560,110,stroke=P['secondary'],radius=18,label="第 1 步  −100",fontSize=44),R("s2",680,560,560,110,stroke=P['secondary'],radius=18,label="第 2 步  +100",fontSize=44)]
        a1=[F("s1",t1),pop("s1",t1),F("s2",t2),pop("s2",t2)]
        td=at(1,"第一步做完");tf=at(1,"第二步出了故障");tx=at(1,"扣了钱")
        e2=accounts(l2="400")+[R("s1",680,200,560,110,stroke=P['secondary'],radius=18,label="第 1 步  −100",fontSize=44),R("s2",680,560,560,110,stroke=P['secondary'],radius=18,label="第 2 步  +100",fontSize=44),
            tick("k1",1110,195,P['success'],80),I("bolt","fault",890,360,160),tick("x2",1110,555,P['danger'],96,"×")]
        a2=[hl("s1",td)]+swap("bL","bL2",td)+[F("k1",td),pop("k1",td),F("bolt",tf),pop("bolt",tf),hl("s2",tf+6,P['danger']),F("x2",tf+8),pop("x2",tf+8),
            mv("bR","strokeColor",tx,tx+10,P['secondary'],P['danger'])]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 同一个包裹 = 事务
        tb=at(0,"装进同一个包裹");ty=at(0,"一起做完");tn=at(0,"都不做")
        e1=accounts()+[I("box","box-open",CX,300,CW),R("s1",680,140,270,90,stroke=P['secondary'],radius=16,label="第 1 步",fontSize=40),R("s2",970,140,270,90,stroke=P['secondary'],radius=16,label="第 2 步",fontSize=40),
            T("yy",700,720,240,100,"✓ ✓",72,P['success'],align="center"),T("nn",980,720,240,100,"× ×",72,P['danger'],align="center")]
        a1=[F("s1",0),F("s2",0),F("box",tb-12),pop("box",tb-12),mv("s1","y",tb+4,tb+28,140,380,"easeIn"),mv("s2","y",tb+10,tb+34,140,380,"easeIn"),out("s1",tb+28,8),out("s2",tb+34,8),
            F("yy",ty),F("nn",tn)]
        e2=accounts()+[I("box","box-open",CX,250,CW),term("tx",CX,720,CW,"事务")]
        a2=[mv("box","y",0,16,300,250),F("tx",at(1,"事务")),pop("tx",at(1,"事务"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 封箱寄出 = 提交
        ts=at(0,"封箱寄出");tj=at(0,"寄出");tg=at(0,"真正生效")
        e1=accounts(l2="400",r2="300")+[I("box","box-open",CX,300,CW),I("sealed","box-sealed",CX,300,CW)]
        a1=[out("box",ts,8),F("sealed",ts,8),pop("sealed",ts),mv("sealed","x",tj+12,tj+40,CX,CX+120),mv("sealed","x",tj+40,tj+56,CX+120,CX)]+swap("bL","bL2",tg)+swap("bR","bR2",tg)+[
            hl("bL2",tg+8),hl("bR2",tg+8)]
        e2=accounts("400","300")+[I("sealed","box-sealed",CX,250,CW),term("cm",CX,720,CW,"提交")]
        a2=[F("cm",at(0,"提交")),pop("cm",at(0,"提交"))]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 半路出问题 → 倒放：钱沿原路一步步回来 = 回滚
        tp=at(0,"出了问题");tr=at(0,"倒着撤回");tm=at(0,"钱原路回到");td=at(0,"就像倒放")
        e1=accounts("400","200",l2="500")+[I("box","box-open",CX,300,CW),I("bolt","fault",CX+CW-80,260,140),I("rw","rewind",890,150,140),
            E("path","line",AL+AW+20,AY+100,CX-AL-AW-40,0,P['primary'],dashed=True),I("coin","coin",CX+150,AY+40,100)]
        st=max(tm,tr+20);n=4;seg=(CX+150-(AL+AW-60))/n;stp=max(8,(td-st)//n)
        a1=[F("box",0),F("bolt",tp),pop("bolt",tp),F("rw",tr),pop("rw",tr),draw("path",tr+6,20),F("coin",tr+10,8)]+[
            mv("coin","x",st+j*stp,st+j*stp+stp-2,round(CX+150-j*seg),round(CX+150-(j+1)*seg),"easeOut") for j in range(n)]+swap("bL","bL2",st+n*stp)+[
            out("coin",st+n*stp,6),pop("rw",td)]
        e2=accounts("500","200")+[I("rw","rewind",CX+80,250,240),term("rb",CX,720,CW,"回滚")]
        a2=[F("rb",at(0,"回滚")),pop("rb",at(0,"回滚"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 不能拆开寄一半 = 原子性（不放账户卡）
        tw=at(0,"整个寄到");tb=at(0,"原样退回")
        e1=[I("half","box-half",200,260,420),I("bs","box-sealed",820,180,200),E("ar1","arrow",1050,255,220,50,P['success'],direction="r"),I("pr","person",1300,170,200),tick("k1",1520,200),
            I("bo","box-open",820,500,200),I("rw","rewind",1080,520,160),I("pl","person",1300,490,200),tick("k2",1520,520)]
        a1=[F("half",0),pop("half",0)]+[F(x,tw) for x in ("bs","pr","k1")]+[draw("ar1",tw+4)]+[F(x,tb) for x in ("bo","rw","pl","k2")]+[pop("k1",tw+10),pop("k2",tb+10)]
        e2=[I("whole","box-sealed",200,240,420),I("bs","box-sealed",820,180,200),E("ar1","arrow",1050,255,220,50,P['success'],direction="r"),I("pr","person",1300,170,200),tick("k1",1520,200),
            I("bo","box-open",820,500,200),I("rw","rewind",1080,520,160),I("pl","person",1300,490,200),tick("k2",1520,520),term("at",190,720,440,"原子性")]
        a2=[F("whole",0,8),F("at",at(0,"原子性")),pop("at",at(0,"原子性"))]
        return [(e1,a1),(e2,a2)]
    if si==6:  # 回顾：四格（开头就出图，术语卡按念到点亮）
        X=[150,570,990,1410];W=360
        e=[R("frame",120,200,1680,560,stroke=P['primary'],radius=28),I("c0","box-open",X[0]+80,260,200),I("c1","box-sealed",X[1]+80,260,200),I("c2","rewind",X[2]+90,270,180),I("c3","box-half",X[3]+80,260,200),
           term("r0",X[0],580,W,"事务",P['primary'],48),term("r1",X[1],580,W,"提交",P['success'],48),term("r2",X[2],580,W,"回滚",P['accent'],48),term("r3",X[3],580,W,"原子性",P['primary'],48)]
        a=[F("frame",0,8),F("c0",0,8),F("c1",at(0,"做完就提交")-6),F("c2",at(0,"出错就回滚")-6),F("c3",at(0,"全程保证")-6)]+[F(f"r{j}",at(0,w)) for j,w in enumerate(("事务","提交","回滚","原子性"))]
        return [(e,a)]
def subs(t,L,si,k):
    S=sentences(t);q=TM[KEY(si,k)]["sentences"];res=[]
    for s,qq in zip(S,q):
        cl=[x for x in re.findall(r'[^，；：。？]+[，；：。？]?',s) if x.strip()];m=[]
        for c in cl:
            if m and cnt(m[-1])<8 and m[-1][-1] not in "。？": m[-1]+=c
            else: m.append(c)
        tot=sum(cnt(x) for x in m);acc=0
        for c in m: res.append({"text":subtext(c.strip().rstrip('，；：。？')),"from":round(30*(qq["start"]+qq["dur"]*acc/tot))});acc+=cnt(c)
    for i,r in enumerate(res): r["to"]=(res[i+1]["from"]-1) if i+1<len(res) else L-1
    res[0]["from"]=0
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
meta=dict(title="《扣了钱，对方没到账？》",hook="扣了钱对方没到账",episode=15,slug="db-transaction",release="v0.20.0",provisional=True,provisionalReason="脚本待村长定稿；配音为 Knoll 第 1 轮",
  series=None,width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用 EP.14）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes="时长=Knoll 实测（map_timing.py，章 = 首句起 → 末句止 + 60 帧）。术语标签（事务 / 提交 / 回滚 / 原子性，只用中文）按 words.json 词级时间（asr_words.json，句首不早于句子起点，再 +0.1 s，宁晚勿早）由 _audit/labelfix.py 对齐；画面不复述字幕；余额为示例；不出现 COMMIT/ROLLBACK/ACID。素材全部自绘（assets/*.svg）。")
assets=dict(reuse=[dict(id="subtitle",desc="字幕层"),dict(id="person",file="assets/person.svg",desc="小人（EP.14 自绘）")],
  new=[dict(id=n,file=f"assets/{n}.svg",desc=d) for n,d in (("coin","硬币 ¥"),("fault","故障闪电"),("box-open","打开的包裹=事务"),("box-sealed","封箱（青胶带+✓）=提交"),("rewind","倒放=回滚"),("box-half","拆成两半+✗=不能寄一半"),("account","账户卡（备用，未上画面）"))])
PS="split-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
def _full_at(eid): return max(k['frame'] for a in sh['animations'] if a['elementId']==eid for k in a['keyframes'])
pl=min(sh['durationInFrames']-1,max(_full_at("x2"),_full_at("bR"))+10)
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="封面候选：两步卡片——第 1 步 ✓（你 500→400），第 2 步被闪电劈中 ✗，朋友 200 未到账（红框）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
