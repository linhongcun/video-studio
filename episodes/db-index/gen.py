# EP.14《加个索引，为啥就快了？》（脚本 v0.19.0）分镜生成（Miyazaki）。工具链沿用 EP.12 degradation/gen.py
# 贯穿比喻：一本厚书。翻书 = 全表扫描，目录 = 索引，多层目录 = B+ 树，目录太多 = 维护成本。不出现具体倍数 / 层数 / MySQL / InnoDB；示例数字标「示例」
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext
src=open(SCRIPT).read()
narr=re.findall(r'- 旁白：(.+)',src); assert len(narr)==6
CNT=[int(x) for x in re.findall(r'- 字数：(\d+)',src)]
def cnt(s): return len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
P=dict(bg="#0B1020",panel="#111827",primary="#22D3EE",secondary="#3B82F6",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",success="#22C55E",accent="#F59E0B",danger="#F87171")
def R(i,x,y,w,h,c=P['panel'],**k): return dict(id=i,type="rect",x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def T(i,x,y,w,h,t,fs=40,c=P['text'],**k): return dict(id=i,type="text",x=x,y=y,w=w,h=h,text=t,fontSize=fs,**{"color":c,"reuse":False,**k})
def A(i,name,x,y,w,h,**k): return dict(id=i,type="image",asset=f"assets/{name}.svg",x=x,y=y,w=w,h=h,**{"color":None,"reuse":False,**k})
def E(i,ty,x,y,w,h,c,**k): return dict(id=i,type=ty,x=x,y=y,w=w,h=h,**{"color":c,"reuse":False,**k})
def I(i,name,x,y,w,h=None,**k): return A(i,name,x,y,w,w if h is None else h,**k)
def fade(i,a=0,b=12): return dict(elementId=i,property="opacity",keyframes=[dict(frame=a,value=0),dict(frame=b,value=1)],easing="easeOut")
def mv(i,p,a,b,va,vb,e="easeInOut"): return dict(elementId=i,property=p,keyframes=[dict(frame=a,value=va),dict(frame=b,value=vb)],easing=e)
def draw(i,a,n=15): return mv(i,"drawProgress",a,a+n,0,1,"easeOut")
def F(i,a,n=12): return fade(i,a,a+n)
def pop(i,a): return mv(i,"scale",a,a+12,0,1,"spring")
def dim(i,a,v=0.3): return mv(i,"opacity",a,a+12,1,v)
def hl(i,a,c=P['accent'],c0=P['secondary']): return mv(i,"strokeColor",a,a+10,c0,c)
titles=["一下子就搜到","一页一页翻","先查目录","多层目录","目录不是越多越好","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
TM=json.load(open(HERE/"timing.json"))
PARTS=[]
def AT(si,_k,phrase):
    # 短语在本章哪个镜头（本章内第一次出现），返回该镜头内相对帧（按送 TTS 文字的字数比例插值）
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=tts(S[i]); ph=tts(phrase)
    off=cnt(s[:s.index(ph)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def term(i,x,y,w,label,c=None,fs=64): return R(i,x,y,w,110,stroke=c or P['primary'],radius=55,label=label,fontSize=fs)
def tag(i,x,y,w,label,c=None,fs=40,h=84): return R(i,x,y,w,h,stroke=c or P['text2'],radius=16,label=label,fontSize=fs)
def tick(i,x,y,c=P['success'],fs=96): return T(i,x,y,120,120,"✓",fs,c,align="center")
def pages(p,x,y,n,a,step,w=150,h=210):   # 一页页翻：书页从右往左滑走（opacity 归零），错开 step 帧
    els=[R(f"{p}{j}",x,y,w,h,"#F3F4F6",radius=6) for j in range(n)];an=[]
    for j in range(n):
        t=a+j*step; an+=[dict(elementId=f"{p}{j}",property="opacity",keyframes=[dict(frame=0,value=0),dict(frame=max(1,t),value=0),dict(frame=t+2,value=1),dict(frame=t+step,value=1),dict(frame=t+step+6,value=0)],easing="linear"),
                         mv(f"{p}{j}","x",t+2,t+step+6,x,x-w,"easeIn")]
    return els,an
def tree(on=0,lv=(0,0,0)):   # 多层目录：大目录 → 小目录 ×3 → 具体位置 ×9（不画节点细节、不标层数）
    C=[460,960,1460];els=[R("L1",760,130,400,100,stroke=P['secondary'],radius=20,label="大目录",fontSize=44),
        E("v1","line",960,230,0,70,P['text2']),E("h1","line",460,300,1000,0,P['text2'])]
    els+=[E(f"v2{j}","line",c,300,0,70,P['text2']) for j,c in enumerate(C)]+[R(f"L2{j}",c-170,370,340,96,stroke=P['secondary'],radius=18,label="小目录",fontSize=40) for j,c in enumerate(C)]
    for j,c in enumerate(C):
        els+=[E(f"v3{j}","line",c,466,0,54,P['text2']),E(f"h3{j}","line",c-160,520,320,0,P['text2'])]+[E(f"v4{j}{m}","line",c+d,520,0,60,P['text2']) for m,d in enumerate((-160,0,160))]
        els+=[R(f"L3{j}{m}",c+d-65,580,130,70,"#1F2937",stroke=P['muted'],radius=12) for m,d in enumerate((-160,0,160))]
    return els
TREE_L1=["L1","v1","h1"];TREE_L2=[f"v2{j}" for j in range(3)]+[f"L2{j}" for j in range(3)]
TREE_L3=[f"v3{j}" for j in range(3)]+[f"h3{j}" for j in range(3)]+[f"v4{j}{m}" for j in range(3) for m in range(3)]+[f"L3{j}{m}" for j in range(3) for m in range(3)]
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    if si==0:  # 一下子就搜到
        rows=[R(f"rw{j}",1040,470+j*34,700,24,"#1F2937",radius=6) for j in range(11)]
        e1=[I("phone","phone",120,170,600),R("search",820,200,920,100,stroke=P['primary'],radius=50,label="订单号 A20261014",fontSize=40),T("ex1",820,310,300,40,"（示例）",28,P['text2'])]+rows+[
            R("hit",1040,470+5*34-14,700,52,"#14532D",stroke=P['success'],radius=10,label="找到了",fontSize=36),T("q",790,560,220,200,"？",160,P['accent'],align="center")]
        ts=at(0,"搜一个订单号");tr=at(0,"成千上万");th=at(0,"一下子就出来");tq=at(0,"数据库是怎么")
        a1=[F("phone",0),F("search",ts),F("ex1",ts)]+[F(f"rw{j}",tr+j*3,8) for j in range(11)]+[F("hit",th),pop("hit",th),F("q",tq),pop("q",tq)]
        e2=[I("shelf","shelf",160,140,960,480),tag("dbT",160,650,280,"数据库",P['primary'],44),I("book","book",1260,200,420,420),term("idx",1270,660,400,"索引")]
        tb=at(1,"厚书");ti=at(1,"数据库的索引")+cnt("数据库的")*0
        a2=[F("shelf",0),F("dbT",0),F("book",tb),pop("book",tb),F("idx",at(1,"索引")),pop("idx",at(1,"索引"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 一页一页翻（全表扫描）
        tp=at(0,"一页一页往后翻");tf=at(0,"从第一页")
        pe,pa=pages("pg",560,300,6,tp-6,max(8,(L[0]-tp-20)//6))
        e1=[I("book","book",200,200,480,480),tag("noToc",230,700,420,"没有目录",P['danger'],40)]+pe+[I("man","person",900,420,280),
            T("cnt",1220,300,560,80,"第 1、2、3、4、5……页",48,P['accent']),T("cntT",1220,220,560,56,"已翻到",36,P['text2'])]
        a1=[F("book",0),F("noToc",at(0,"没有目录")),F("man",tf),mv("man","y",tp,tp+20,420,400)]+pa+[F("cntT",tf),F("cnt",tf),mv("cnt","charsVisible",tf,L[0]-40,2,len("第 1、2、3、4、5……页"))]
        rows=[R(f"r{j}",240,180+j*58,640,44,"#1F2937",radius=8) for j in range(11)]
        tr=at(1,"一行一行");te=at(1,"读一遍");tt=at(1,"全表扫描");ts=at(1,"表小");tb=at(1,"表一大")
        e2=[R("tbl",220,160,680,660,stroke=P['secondary'],radius=16)]+rows+[R("bar",232,174,656,56,"#22D3EE33",stroke=P['primary'],radius=10),
            term("fts",1080,170,520,"全表扫描",P['accent']),
            R("sm",1080,430,220,150,stroke=P['success'],radius=14),tag("smT",1080,600,220,"小表",P['success'],40)]+[R(f"s{j}",1100,450+j*40,180,28,"#1F2937",radius=6) for j in range(3)]+[
            R("bg",1380,380,300,400,stroke=P['danger'],radius=14),tag("bgT",1380,800-6,300,"大表",P['danger'],40,h=76)]+[R(f"b{j}",1400,396+j*30,260,20,"#1F2937",radius=4) for j in range(12)]
        a2=[F("tbl",0)]+[F(f"r{j}",0) for j in range(11)]+[F("bar",tr),mv("bar","y",tr+6,max(tr+30,te),174,174+10*58,"linear"),F("fts",tt),pop("fts",tt),
            F("sm",ts)]+[F(f"s{j}",ts) for j in range(3)]+[F("smT",ts),F("bg",tb)]+[F(f"b{j}",tb+j*2,6) for j in range(12)]+[F("bgT",tb)]
        return [(e1,a1),(e2,a2)]
    if si==2:  # 先查目录（索引）——第 2 镜左右对比 = 封面帧
        E3=[("用户","第 12 页"),("订单","第 128 页"),("商品","第 305 页")]
        e1=[I("toc","toc",160,200,420,420)]+[R(f"en{j}",640,200+j*120,600,96,stroke=P['secondary'],radius=14,label=f"{a} …… {b}",fontSize=40) for j,(a,b) in enumerate(E3)]+[
            T("ex2",640,560,300,40,"（示例）",28,P['text2']),E("go","arrow",1250,343,170,50,P['accent'],direction="r"),I("book","book",1420,200,380,380),tick("ok",1550,580)]
        tc=at(0,"先查目录");te=at(0,"第几页");tpg=at(0,"查到页码");tj=at(0,"直接翻过去")
        a1=[F("toc",tc)]+[F(f"en{j}",te+j*6) for j in range(3)]+[F("ex2",te),hl("en1",tpg),draw("go",tj,15),F("book",0),F("ok",tj+15),pop("ok",tj+15)]
        e2=[E("div","line",960,120,0,740,P['muted']),tag("lT",160,130,240,"翻书",P['text2'],40),tag("rT",1040,130,280,"查目录",P['primary'],40),
            I("bookL","book",170,260,380,380),I("manL","person",560,440,240),T("cntL",160,690,720,70,"第 1、2、3、4、5、6……页",44,P['accent']),
            I("tocR","toc",1040,260,300,300),E("goR","arrow",1350,385,150,50,P['accent'],direction="r"),I("bookR","book",1510,260,300,300),tick("okR",1600,560),term("idx",1180,700,400,"索引")]
        ti=at(1,"就叫索引")+round(30*0);tk=at(1,"直接跳到")
        a2=[F(x,0) for x in ("div","lT","rT","bookL","manL","tocR","bookR")]+[F("cntL",0),mv("cntL","charsVisible",0,L[1]-30,2,len("第 1、2、3、4、5、6……页")),
            draw("goR",tk-10,15),F("okR",tk+6),pop("okR",tk+6),F("idx",at(1,"索引")),pop("idx",at(1,"索引"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 多层目录（B+ 树）
        tt=at(0,"很厚");tl=at(0,"做成好几层");t1=at(0,"大目录指到");t2=at(0,"小目录，");t3=at(0,"具体的位置")
        e1=[I("thick","toc",660,200,600,600)]+tree()
        a1=[F("thick",0),mv("thick","scale",tt,tt+20,1,1.25),dim("thick",tl,0)]+[F(x,t1) for x in TREE_L1]+[F(x,t2) for x in TREE_L2]+[F(x,t3) for x in TREE_L3]
        e2=tree()+[E("p1","line",960,230,0,70,P['accent']),E("p2","line",960,300,0,70,P['accent']),E("p3","line",960,466,0,54,P['accent']),E("p4","line",1120,520,0,60,P['accent']),
            tick("ok",1060,660,P['success'],80),term("bt",1360,150,400,"B+ 树")]
        t0=at(1,"最上面");tf=at(1,"翻几层");td=at(1,"就找到了");tb=at(1,"B+树")
        a2=[hl("L1",t0),F("p1",t0+8),F("p2",t0+14),hl("L21",tf),F("p3",tf+8),F("p4",tf+14),hl("L312",td,P['accent'],P['muted']),F("ok",td+6),pop("ok",td+6),F("bt",tb),pop("bt",tb)]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 目录不是越多越好
        TC=[(220,130),(220,520),(1500,130),(1500,520)]
        tq=at(0,"是不是越多越好");tg=at(0,"书每改一页");tm=at(0,"都得跟着改");tz=at(0,"占纸");tx=at(0,"光挑用哪一本")
        e1=[I("book","book",760,160,400,400),T("q",860,560,200,160,"？",120,P['accent'],align="center"),R("edit",1000,260,90,90,"#7F1D1D",stroke=P['danger'],radius=45,label="改",fontSize=44)]+[
            I(f"t{j}","toc",x,y,200,200) for j,(x,y) in enumerate(TC)]+[
            E("aL0","arrow",440,205,320,50,P['danger'],direction="l"),E("aL1","arrow",440,595,320,50,P['danger'],direction="l"),
            E("aR0","arrow",1160,205,330,50,P['danger'],direction="r"),E("aR1","arrow",1160,595,330,50,P['danger'],direction="r"),I("run","person",900,620,200)]+[
            I(f"pile{j}","toc",760+j*14,140+j*40,260,260) for j in range(5)]+[I("pick","person",1180,560,220),T("q2",1400,560,200,160,"？",120,P['accent'],align="center")]
        BK=["book","edit","run"]+[f"t{j}" for j in range(4)]+["aL0","aL1","aR0","aR1"]
        a1=[F("book",0)]+[F(f"t{j}",0) for j in range(4)]+[F("q",tq),pop("q",tq),dim("q",tg,0),F("edit",tg),pop("edit",tg)]+[draw(x,tm+j*5,15) for j,x in enumerate(("aL0","aR0","aL1","aR1"))]+[
            F("run",tm),mv("run","x",tm,tm+40,900,560),mv("run","x",tm+40,max(tm+41,tz-12),560,1240)]+[dim(x,tz-6,0) for x in BK]+[F(f"pile{j}",tz+j*5,8) for j in range(5)]+[
            dim(f"pile{j}",tx-2,0.6) for j in range(5)]+[F("pick",tx),F("q2",tx+6),pop("q2",tx+6)]
        e2=[tag("w",160,200,480,"写入变慢",P['danger'],48,h=110),tag("s",720,200,480,"占空间",P['accent'],48,h=110),tag("c",1280,200,480,"要挑选",P['secondary'],48,h=110),
            I("i0","book",300,350,200),I("i1","toc",860,350,200),I("i2","person",1420,350,200),term("nm",560,650,800,"索引不是越多越好",P['danger'],56)]
        tw=at(1,"拖慢写入");ts=at(1,"占用空间");tc=at(1,"挑用哪一个");tn=at(1,"索引不是越多越好")
        e2[3]["asset"]="assets/book.svg";e2[4]["asset"]="assets/toc.svg";e2[5]["asset"]="assets/person.svg"
        a2=[F("w",tw),F("i0",tw),F("s",ts),F("i1",ts),F("c",tc),F("i2",tc),F("nm",tn),pop("nm",tn)]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        X=[150,570,990,1410];W=360
        e1=[I("c0","book",X[0]+80,170,200),I("c1","toc",X[1]+80,170,200),I("c3","toc",X[3]+40,170,160),I("c3b","toc",X[3]+120,200,160),
            R("m1",X[2]+120,170,120,60,stroke=P['secondary'],radius=10),R("m2",X[2]+30,290,120,60,stroke=P['secondary'],radius=10),R("m3",X[2]+210,290,120,60,stroke=P['secondary'],radius=10),
            E("mv","line",X[2]+180,230,0,30,P['text2']),E("mh","line",X[2]+90,260,180,0,P['text2']),
            term("r0",X[0],440,W,"全表扫描",P['accent'],48),term("r1",X[1],440,W,"索引",P['primary'],48),term("r2",X[2],440,W,"B+ 树",P['primary'],48),term("r3",X[3],440,W,"适量",P['success'],48)]
        for e in e1:
            if e["id"] in("c0","c1","c3","c3b"): e["asset"]=f"assets/{ {'c0':'book','c1':'toc','c3':'toc','c3b':'toc'}[e['id']] }.svg"
        T0=at(0,"只能全表扫描");T1=at(0,"建了索引");T2=at(0,"多层目录");T3=at(0,"够用就好")
        a1=[F("c0",T0),F("r0",at(0,"全表扫描")),F("c1",T1),F("r1",at(0,"索引")),F("m1",T2),F("m2",T2+4),F("m3",T2+4),F("mv",T2),F("mh",T2),F("r2",T2),F("c3",T3-10),F("c3b",T3-10),F("r3",T3)]
        e2=[I("phone","phone",200,170,600),R("hit",900,300,700,110,"#14532D",stroke=P['success'],radius=16,label="找到了",fontSize=44),I("toc","toc",1100,470,320)]
        a2=[F("phone",0),F("hit",at(1,"搜到了订单")),pop("hit",at(1,"搜到了订单")),F("toc",at(1,"背后")),pop("toc",at(1,"背后"))]
        return [(e1,a1),(e2,a2)]
# I(i,name,...) 的 name 参数在回顾里被 id 占位，修正 asset
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
        shots.append(dict(id=KEY(si,k),chapterId=ids[si],**{"from":f},durationInFrames=l,narration=p,**({"ttsText":tts(p)} if tts(p)!=p else {}),subtitles=subs(p,l,si,k),elements=els,animations=an,transition=dict(type="fade" if last else "crossfade",durationInFrames=12 if last else 8)))
        f+=l;nshot+=1
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),shots=shots));g+=D
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《加个索引，为啥就快了？》",hook="加个索引为啥就快了",episode=14,slug="db-index",release="v0.19.0",series="技术基础（暂定，合集上线前再定）",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  tts=dict(note="pronunciation.md：送 TTS 的旁白把「B+树」写成「B 加树」；字幕 / 标签写「B+ 树」。镜头 ttsText = 送 TTS 文字",replace={"B+树":"B 加树"}),
  notes=("时长=暂定（make_timing.py：EP.03 MiMo 冰糖语速，英文词≈1.5 汉字，句间 0.28 秒，每章尾 60 帧）。Knoll 逐句 timing 到后：sh realign.sh（默认 /workspace/share/ep14/*timing*.json）。" if PROV else "时长=Knoll 实测（map_timing.py，scale 1）。")+
   "术语标签（全表扫描 / 索引 / B+ 树 / 索引不是越多越好）在念到该词时淡入（_audit/labelfix.py 对齐，容差 0..+5 帧）；画面不重复字幕句子（术语除外）；示例数字标「示例」；不出现倍数、层数、MySQL / InnoDB。素材全部自绘（assets/*.svg，无文字）。")
assets=dict(reuse=[dict(id="subtitle",desc="字幕层")],new=[dict(id=n,file=f"assets/{n}.svg",desc=d) for n,d in (("book","厚书（自绘）"),("toc","目录小册（自绘）"),("person","小人（自绘，同第九期 guest 风格）"),("phone","手机（自绘）"),("shelf","书架=数据库（自绘）"))])
PS="index-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
PARTS[:]=[x['narration'] for x in scenes[2]['shots']]
def _full_at(eid):   # 某元素淡入 / 弹出全部完成的帧
    return max(k['frame'] for a in sh['animations'] if a['elementId']==eid for k in a['keyframes'])
pl=min(sh['durationInFrames']-1,max(_full_at("idx"),_full_at("okR"),_full_at("goR"))+6)
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="左右对比：左「翻书」小人一页页翻、页码计数往上跳；右「查目录」目录→箭头→书，✓ 直达；术语标签「索引」",file="poster.jpg")
_CS=HERE/"cover-spec.json";_cov=json.load(open(_CS)) if _CS.exists() else None
json.dump(dict(meta=meta,assets=assets,scenes=scenes,**({"cover":_cov} if _cov else {})),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
