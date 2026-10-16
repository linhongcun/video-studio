# EP.21《两个库，怎么一起成功或一起失败？》分布式事务（脚本 v0.26.0 v4 分界返工：26 章 + 四张章节卡）分镜（Miyazaki）。工具链沿用 EP.20；配音未到时按字数估时长
# 比喻：驿站 + 拿对讲机的调度员。红站=订单账本，蓝站=货架；铅笔单/待出库格子=准备；绿红牌=能否提交；盖章/擦掉=统一生效/撤回；对讲机没声=干等；条子+跑腿员+签收=可靠消息
# 术语：两阶段提交 / 预留确认取消（TCC）/ 补偿事务（Saga）/ 可靠消息 / 最终一致 / 分布式事务；只有右上「IT小村」；画面无数字/英文/logo
import json,re,math,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','_audit'));import asrcue
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT,tts,subtext,narration,CARDS,CARD
narr=narration(); assert len(narr)==26
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

titles=["下单没扣","驿站","各管各的","第一种：两阶段提交","先问准备好","一起盖章或一起擦掉","对讲机断了","两阶段提交收尾","第二种：TCC","预留","确认或取消","三套动作","TCC 收尾","第三种：Saga","先做","再补偿","补偿的代价","Saga 收尾","第四种：可靠消息","条子先暂存","邮局回头问","送到为止","可靠消息的代价","可靠消息收尾","最终一致","四格对比"]
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
SEG={"intro":"#0B1020","pc":"#E8B53A","tcc":"#2FA38A","saga":"#8E6BBF","msg":"#C9733A","end":"#D9D6CF"}
def seg(c): return "intro" if c in("hook","signal","local") else ("end" if c in("eventual","recap") else c.split('-')[0])
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
def shots_for(si,L):
    at=lambda k,p,n=0:AT(si,k,p,nth=n);c=ids[si]
    if c=="hook":   # 第 0 帧即主体：左「订单」账本 + 绿勾 +「成功」，右「库存」货架货没少；念「怎么一起成败」两边各亮一下
        e=SPL()+[R("fl",100,140,800,700,"#FDE68A"),R("fr",1020,140,800,700,"#FDE68A"),tag("tl",420,180,"订单"),tag("tr",1346,180,"库存"),
           I("lg","ledger-ok",300,300,400),tag("ok",430,720,"成功",P['success']),I("sh","shelf",1220,300,400)]
        t=at(0,"怎么一起成败");return [(e,[flash("fl",t),flash("fr",t+4)])]
    if c=="signal":   # ①分屏延续：两边各有一个库，一个成了 / 另一个没成 ②驿站比喻：订单→红站，库存→蓝站
        e=SPL()+[tag("tl",420,180,"订单"),tag("tr",1346,180,"库存"),I("lg","ledger-ok",300,300,400),I("sh","shelf",1220,300,400),
           I("d0","db",140,170,140),I("d1","db",1060,170,140),I("no","nope",1320,400,220)]
        a=show("d0",at(0,"数据库"))+show("d1",at(0,"数据库")+4)+[F("lg",0,1)]+show("no",at(0,"另一个没成"),6)
        ty=at(0,"驿站")
        e2=SPL()+[tag("tl",420,180,"订单"),tag("tr",1346,180,"库存"),tag("tR",420,180,"红站",RED),tag("tB",1346,180,"蓝站",BLUE),
            I("lg","ledger-ok",300,300,400),I("sh","shelf",1220,300,400),I("sr","station-red",300,280,400),I("sb","station-blue",1220,280,400),
            I("l2","ledger",160,620,200),I("s2","shelf",1580,620,200)]
        a2=swap("tl","tR",ty)+swap("tr","tB",ty+4)+swap("lg","sr",ty,14)+swap("sh","sb",ty+4,14)+show("l2",at(0,"记订单"))+show("s2",at(0,"管货架"))
        return [(e,a),(e2,a2)]
    if c=="local":   # ①一个库能整笔撤回 → 分成红站蓝站，各撤各的，管不到对方 ②四块色板依次亮：四种办法
        td=at(0,"分到不同的库")
        e=[I("db","db",760,160,400),I("er","note-erased",820,560,200),I("sr","station-red",160,140,380),I("sb","station-blue",1380,140,380),
           I("e2","note-erased",260,520,220),I("sh","shelf",1420,500,300),I("xx","nope",1440,520,260)]
        a=show("er",at(0,"全部撤回"))+[out("db",td,10),out("er",td,10)]+show("sr",td,10)+show("sb",td+6,10)+show("e2",at(0,"撤回自己"))+show("sh",at(0,"对方的货架"))+show("xx",at(0,"管不到"),6)
        t4=at(0,"四种")
        e2=[I("sr","station-red",160,140,300),I("sb","station-blue",1460,140,300)]+[R(f"c{j}",280+j*360,520,280,180,col,radius=28) for j,col in enumerate((SEG['pc'],SEG['tcc'],SEG['saga'],SEG['msg']))]
        a2=[x for j in range(4) for x in show(f"c{j}",t4+j*6,8)]
        return [(e,a),(e2,a2)]
    # —— 第一种：两阶段提交（琥珀黄；调度员 + 对讲机、铅笔单、待出库格子、绿红牌、盖章 / 擦掉） ——
    if c=="pc-open":
        e=[I("sr","station-red",160,160,380),I("sb","station-blue",1380,160,380),I("dp","dispatcher",760,200,400)]
        return [(e,show("dp",at(0,"调度员"),10))]
    if c=="pc-prepare":
        e=[I("sr","station-red",160,160,360),I("sb","station-blue",1400,160,360),I("dp","dispatcher",760,200,400),I("q0","ask",500,160,220),I("q1","ask",1180,160,220)]
        a=[F("dp",0,6)]+show("q0",at(0,"准备好了吗"))+show("q1",at(0,"准备好了吗")+6)
        e2=[I("sr","station-red",120,140,340),I("sb","station-blue",1460,160,300),I("dp","dispatcher",780,140,360),I("np","note-pencil",220,500,300),I("sl","slot-locked",1380,480,360)]
        return [(e,a),(e2,[F("dp",0,6)]+show("np",at(0,"铅笔"))+show("sl",at(0,"待出库")))]
    if c=="pc-commit":
        tg=at(0,"绿牌");ts=at(0,"一起盖章");tr=at(0,"红牌");te=at(0,"全部擦掉")
        e=[I("sr","station-red",120,140,320),I("sb","station-blue",1480,160,280),I("dp","dispatcher",800,140,320),
           I("g0","sign-green",200,480,200),I("g1","sign-green",1520,480,200),I("st","stamp",820,480,220),I("ns","note-stamped",480,480,260),
           I("r1","sign-red",1520,480,200),I("ne","note-erased",1160,480,260)]
        a=show("g0",tg)+show("g1",tg+4)+show("st",ts)+show("ns",ts+6)+[out("st",tr,8),out("ns",tr,8),out("g1",tr,6)]+show("r1",tr,6)+show("ne",te)
        return [(e,a)]
    if c=="pc-cost":
        tn=at(0,"没声")
        e=[I("dp","dispatcher",780,140,340),I("df","dispatcher-off",780,140,340),I("np","note-pencil",180,440,300),I("sl","slot-locked",1380,440,360),I("hg","hourglass",820,500,260),
           I("pb","person-blue",1560,160,220),I("no","nope",1560,160,220)]
        a=[F("dp",0,6)]+swap("dp","df",tn,6)+show("np",at(0,"铅笔单"))+show("sl",at(0,"锁着货"))+show("hg",at(0,"干等"))+show("pb",at(1,"别人"))+show("no",at(1,"买不走"),6)
        return [(e,a)]
    if c=="pc-wrap":
        t=at(0,"再统一生效")
        e=[I("np","note-pencil",360,200,320),I("st","stamp",860,240,200),I("ns","note-stamped",1240,200,320),term("lj",660,740,600,"两阶段提交")]
        return [(e,show("np",at(0,"先准备"))+show("st",t)+show("ns",t+6)+TERM("lj",at(0,"两阶段提交")))]
    # —— 第二种：预留确认取消（青绿；已预留封条、青绿制服调度员，不带对讲机） ——
    if c=="tcc-open":
        e=[I("sb","station-blue",160,180,360),I("db","db",720,200,320),I("no","nope",720,200,320),I("bs","box-sealed",1260,220,380)]
        return [(e,show("db",at(1,"数据库"))+show("no",at(1,"锁货"),6)+show("bs",at(1,"贴封条")))]
    if c=="tcc-try":
        e=[I("sb","station-blue",120,160,340),I("sh","shelf",560,160,420),I("bs","box-sealed",680,300,160),tag("yl",560,620,"已预留",P['accent']),
           I("pb","person-blue",1280,240,280),I("no","nope",1300,240,240)]
        return [(e,[F("sh",0,6)]+show("bs",at(0,"封条"))+show("yl",at(0,"已预留"))+show("pb",at(0,"别人买不走"))+show("no",at(0,"别人买不走")+6,6))]
    if c=="tcc-confirm":
        e=[I("dp","dispatcher-teal",1440,180,300),I("ok","ledger-ok",120,140,240),I("t1","seal-torn",480,160,220),I("pr","parcel-red",800,160,220),
           I("bad","ledger-bad",120,500,240),I("t2","seal-torn",480,520,220),I("sh","shelf",820,460,320),tag("ws",1200,580,"照常卖",P['success'])]
        a=show("dp",at(0,"调度员"),10)+show("ok",at(0,"订单成了"))+show("t1",at(0,"撕掉封条"))+show("pr",at(0,"真正出库"))+moveto("pr",at(0,"真正出库")+8,at(0,"真正出库")+40,800,160,1120,160)
        a+=show("bad",at(0,"订单没成"))+show("t2",at(0,"撕掉封条",1))+show("sh",at(0,"货留在架上"))+show("ws",at(0,"照常卖"))
        e2=[I("p0","parcel-red",260,200,240),I("p1","parcel-red",560,200,240),tag("s2",320,520,"都确认",P['success']),I("h0","shelf",1060,200,240),I("h1","shelf",1360,200,240),tag("s3",1160,520,"都取消",RED)]
        a2=show("p0",at(0,"都确认"))+show("p1",at(0,"都确认")+4)+show("s2",at(0,"都确认"))+show("h0",at(0,"都取消"))+show("h1",at(0,"都取消")+4)+show("s3",at(0,"都取消"))
        return [(e,a),(e2,a2)]
    if c=="tcc-cost":
        ts=at(0,"锁货的时间短")
        e=[I("bs","box-sealed",160,220,300),I("st","seal-torn",160,220,300),I("ts","three-sheets",720,180,420),I("dup","cmd-dup",1340,240,320)]
        return [(e,show("bs",ts)+swap("bs","st",ts+24,8)+show("ts",at(0,"三套动作"))+show("dup",at(0,"重复送来")))]
    if c=="tcc-wrap":
        e=[I("bs","box-sealed",240,180,280),I("pr","parcel-red",820,180,280),I("sh","shelf",1360,180,300),term("tc",600,740,720,"预留确认取消")]
        return [(e,show("bs",at(0,"先预留"))+show("pr",at(0,"再确认"))+show("sh",at(0,"取消"))+TERM("tc",at(0,"TCC")))]
    # —— 第三种：补偿事务（紫；空货架、重新上架的反向箭头；无调度员、无封条） ——
    if c=="saga-open":
        e=[I("sr","station-red",160,160,360),I("sb","station-blue",1400,160,360),I("sh","shelf",760,300,400)]
        return [(e,show("sh",at(1,"不先锁货")))]
    if c=="saga-do":
        to=at(1,"出了库")
        e=[I("sr","station-red",160,140,340),I("sb","station-blue",1420,140,340),I("m1","done-mark",1460,500,180),I("m2","done-mark",200,500,180),
           I("sh","shelf",1000,420,300),I("sg","shelf-gap",1000,420,300),I("bx","box",1110,520,90),I("lg","ledger",440,460,240)]
        a=show("m1",at(0,"直接盖章"))+show("m2",at(0,"通知下一个站"))+[F("sh",0,6)]+swap("sh","sg",to,4)+[mv("bx","opacity",0,to,0,0),F("bx",to,4)]+moveto("bx",to,to+30,1110,520,760,640)+[out("bx",to+24,8)]+show("lg",at(1,"记订单"))
        return [(e,a)]
    if c=="saga-compensate":
        tf=at(0,"失败了");tr=at(0,"重新上架")
        e=[I("sr","station-red",160,140,340),I("bad","ledger-bad",200,500,260),I("sb","station-blue",1420,140,340),I("sg","shelf-gap",900,300,420),I("rs","restock",560,260,260),I("bx","box",820,660,110)]
        a=[F("sg",0,6)]+show("bad",tf)+show("rs",at(0,"反向的动作"))+show("bx",at(0,"反向的动作")+6)+moveto("bx",tr,tr+30,820,660,1062,436)
        e2=[I("rw","rewind-no",240,200,360),I("bx","box",860,280,200),I("sh","shelf",1300,180,360)]
        return [(e,a),(e2,show("rw",at(0,"时光倒流"))+show("bx",at(0,"出过库"))+show("sh",at(0,"补了回来")))]
    if c=="saga-cost":
        e=[I("ey","eye",240,220,320),I("sg","shelf-gap",760,160,400),I("pb","person-blue",1360,200,300)]
        a=show("pb",at(0,"别人"))+show("ey",at(0,"看见"))+show("sg",at(0,"货架空了"))
        e2=[I("rs","restock",240,200,340),I("bad","ledger-bad",760,220,300),I("ey","eye",1260,140,240),I("rt","retry",1300,420,260)]
        a2=show("rs",at(0,"补回来"))+show("bad",at(0,"也可能失败"))+show("ey",at(0,"盯着"))+show("rt",at(0,"能重试"))
        return [(e,a),(e2,a2)]
    if c=="saga-wrap":
        t=at(0,"失败了")
        e=[I("bx","box",300,280,240),I("rs","restock",820,220,300),I("sh","shelf",1340,200,320),term("bc",660,740,600,"补偿事务")]
        return [(e,show("bx",at(0,"先做"))+show("rs",t)+show("sh",at(0,"再补偿"))+TERM("bc",at(0,"Saga")))]
    # —— 第四种：可靠消息（橙棕；邮局、条子、作废戳、问号气泡、单号徽章） ——
    if c=="msg-open":
        e=[I("sr","station-red",160,160,380),I("lg","ledger",620,420,260),I("sp","slip",1000,300,260),I("sb","station-blue",1400,160,340)]
        return [(e,show("lg",at(1,"自己记账"))+show("sp",at(1,"条子")))]
    if c=="msg-half":
        tj=at(0,"交给邮局")
        e=[I("sr","station-red",120,160,340),I("sp","slip",500,300,220),I("po","post-office",1200,160,440),I("no","nope",1640,600,160)]
        a=show("sp",at(0,"条子"))+show("po",at(0,"邮局"))+moveto("sp",tj,tj+30,500,300,1300,560)+show("no",at(0,"不送"),6)
        e2=[I("sr","station-red",120,140,300),I("ok","ledger-ok",160,480,260),I("po","post-office",760,160,400),I("rn","runner",1360,160,320),
            I("bad","ledger-bad",500,520,240),I("sv","slip-void",1260,540,300)]
        a2=[F("po",0,6)]+show("ok",at(0,"订单记好了"))+show("rn",at(0,"可以送了"))+[out("rn",at(0,"订单没记成")-6,8),out("ok",at(0,"订单没记成")-6,8)]+show("bad",at(0,"订单没记成"))+show("sv",at(0,"作废"))
        return [(e,a),(e2,a2)]
    if c=="msg-check":
        e=[I("po","post-office",1240,160,420),I("q","ask",760,160,300),I("sr","station-red",160,160,380),I("ok","ledger-ok",220,560,240),I("rn","runner",1260,580,260)]
        return [(e,[F("po",0,6)]+show("q",at(0,"回头问"))+show("ok",at(1,"记上了"))+show("rn",at(1,"才送")))]
    if c=="msg-deliver":
        t1=at(0,"再送一次")
        e=[I("sb","station-blue",1420,160,340),I("rn","runner",200,200,300),I("no","nope",1460,560,200),I("bd","badge-red",760,520,240),I("dup","slip-dup",1120,540,280)]
        a=show("rn",at(0,"送到蓝站"))+moveto("rn",at(0,"送到蓝站"),at(0,"没处理好"),200,200,1000,200)+show("no",at(0,"没处理好"),6)+[out("no",t1,8)]+moveto("rn",t1,t1+20,1000,200,1060,200)
        a+=show("bd",at(0,"认单号"))+show("dup",at(0,"重复送来"))
        e2=[I("ok","ledger-ok",260,240,320),I("sg","signed",1220,240,360)]
        return [(e,a),(e2,[F("ok",0,6)]+show("sg",at(0,"送到为止")))]
    if c=="msg-cost":
        e=[I("sb","station-blue",1420,160,340),I("rn","runner",900,200,320),I("ok","ledger-ok",240,240,320),I("no","nope",280,280,240)]
        return [(e,show("rn",at(0,"重送"))+[F("ok",0,6)]+show("no",at(0,"不能撤回"),6))]
    if c=="msg-wrap":
        e=[I("ok","ledger-ok",300,220,320),I("rn","runner",820,220,300),I("sg","signed",1300,220,340),term("kk",660,740,600,"可靠消息")]
        return [(e,show("ok",at(0,"先记下来"))+show("rn",at(0,"再保证送到"))+show("sg",at(0,"送到")+12)+TERM("kk",at(0,"可靠消息")))]
    # —— 结尾（中性浅灰）——
    if c=="eventual":   # 紫段、橙棕段各取一格缩略画面并排：这两种都是最终一致
        e=[R("tp",160,160,600,460,P['panel'],stroke=SEG['saga']),I("p1","shelf-gap",220,220,320),I("p2","restock",500,320,240),
           R("tb",1160,160,600,460,P['panel'],stroke=SEG['msg']),I("b1","post-office",1200,220,300),I("b2","slip",1480,360,240),
           I("lp","lamp-yellow",860,180,200),I("ok","ledger-ok",860,420,200),term("zz",660,740,600,"最终一致")]
        ts=at(0,"Saga");tm_=at(0,"可靠消息")
        a=[x for i in("tp","p1","p2") for x in show(i,ts)]+[x for i in("tb","b1","b2") for x in show(i,tm_)]+TERM("zz",at(0,"最终一致"))+show("lp",at(0,"对不上"))+[out("lp",at(0,"最后再对上"),8)]+show("ok",at(0,"最后再对上"))
        return [(e,a)]
    if c=="recap":   # 四格对比：每格 标题 + 怎么做 + 代价（旁白原句）；念到哪格哪格亮
        Q=[("两阶段提交","先准备、再统一生效","货一直锁着，别人也买不走",SEG['pc']),("预留确认取消","先预留，再确认或取消","每个业务都得自己写预留、确认、取消这三套动作",SEG['tcc']),
           ("补偿事务","先做，失败了再补偿","中间那段时间，别人能看见货架空了",SEG['saga']),("可靠消息","先记下来，再保证送到","蓝站没处理好，只能重送，不能撤回订单",SEG['msg'])]
        XY=[(100,140),(980,140),(100,510),(980,510)]
        mk=lambda: [R(f"q{j}",x,y,840,350,P['panel'],stroke=col,radius=24,label=f"{t}\n{h}\n{k}",fontSize=40,quote=True,quoteNote="旁白原句（Nolan 定：四格每格一句怎么做 + 一句代价）") for j,((t,h,k,col),(x,y)) in enumerate(zip(Q,XY))]
        T_=[at(0,"两阶段提交"),at(0,"TCC"),at(0,"Saga"),at(0,"可靠消息")]+[L[0]]
        a=[]
        for j in range(4):
            p=[(0,0.35),(T_[j],0.35),(T_[j]+8,1)]
            if j<3: p+=[(T_[j+1],1),(T_[j+1]+8,0.45)]
            a.append(dimto(f"q{j}",p))
        e2=[dict(x,dimmed=True) for x in mk()]+[term("fb",660,435,600,"分布式事务")]
        a2=[dimto(f"q{j}",[(0,1 if j==3 else 0.45),(8,0.3)]) for j in range(4)]+TERM("fb",at(0,"分布式事务"))
        return [(mk(),a),(e2,a2)]
    raise SystemExit(("no design",c))

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
meta=dict(title="《两个库，怎么一起成功或一起失败？》",hook="下单成功，库存没扣？怎么一起成败？答案马上来。",episode=21,slug="distributed-tx",release="v0.26.0-v4",draft=True,provisional=PROV,provisionalReason=("Knoll 配音未到：按字数估时长" if PROV else None),
  pendingAudio=PROV,series="数据库入门",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="扁平2D（沿用 EP.15–20 素材风格）；v4 每段一种底色：开场深色 / 第一种琥珀黄 / 第二种青绿 / 第三种紫 / 第四种橙棕 / 结尾中性浅灰（scene.background、shot.background，Knoll 整屏铺底色；红蓝只给红站蓝站）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，从第 0 帧起常显（开场即封面），留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames = 正片 + hold，不含片尾卡，也不再留 60 帧留白；成片总长 = durationInFrames + 60"),
  shotSentences={k:n for c in ids for k,n in zip([f"{c}-{j+1}" for j in range(len(_SP[c]))],_SP[c])},
  notes=("时长=暂定（make_timing.py，4.3 字/秒估）；Knoll /workspace/share/ep21/timeline.json + words.json 到后 sh realign.sh 直接重跑。" if PROV else "时长=Knoll timeline.json。")+
    "术语标签（两阶段提交 / 预留确认取消〔念 TCC〕/ 补偿事务〔念 Saga〕/ 可靠消息 / 最终一致 / 分布式事务；画面无英文）念到时淡入（0..+4），完整显示 ≥66；开场第 0 帧即封面；驿站 + 对讲机调度员比喻；素材自绘 + 复用 EP.19/20。")
import json as _j
REUSE=("station-red","station-blue","ledger","ledger-ok","ledger-bad","spark","parcel-red","person-blue","db","barcode-red","barcode-blue","badge-red","lamp-yellow")
NEW=tuple(sorted(f[:-4] for f in os.listdir(HERE/"assets") if f.endswith('.svg') and f[:-4] not in REUSE))
assets=dict(new=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png") for n in NEW],reuse=[dict(id=n,file=f"assets/{n}.svg",png=f"assets/{n}.png",desc="EP.19/20 自绘，复用") for n in REUSE])
import hashlib as _h
_W="/workspace/share/ep21/narration.wav"
CC=[dict(shotId=s["id"],name=s["chapterCard"]["name"],holdFrames=s["durationInFrames"],startFrame=s["from"],startSec=round(s["from"]/30,2),insertBeforeSentence=s["chapterCard"]["insertBeforeSentence"],insertBeforeText=s["chapterCard"]["insertBeforeText"]) for sc in scenes for s in sc["shots"] if s.get("chapterCard")]
meta["chapterCards"]=CC
meta["finalVideoFrames"]=g+60;meta["totalsNote"]="storyboard durationInFrames = 正片（配音 7326 帧）+ 章节卡 hold + 术语 hold；成片 = 它 + 品牌片尾 60 帧"
meta["chapterCardNote"]=f"四张章节卡各 {CARD} 帧静音 hold（名字 0→4 帧淡入，完整显示 70 帧 ≥69，转场 crossfade 4）。Knoll：在 insertBeforeSentence 那句开口前（上一章章间停顿之后）插同长静音；startSec 为成片秒，交 Tim 做 B 站分段章节"
if not PROV: meta["narration"]=dict(file=_W,sha256=_h.sha256(open(_W,"rb").read()).hexdigest(),bodyFrames=sum(v.get("origDuration",v["duration"]) for v in TM.values() if not v.get("card")))
meta["notes"]=("时长=Knoll /workspace/share/ep21/timeline.json（narration.wav 实测）。" if not PROV else "时长=暂定字数估算。")+"开场 ch1-1 一条 take（4.94 s）按 Knoll 小句实测比例拆三段对位。术语标签念到时 0..+4 淡入，完整显示 ≥69；章节卡见 chapterCards；四格对比每格为旁白原句。"
meta["timingSource"]=("/workspace/share/ep21/timeline.json（Knoll）→ map_timing.py → timing.json" if not PROV else "字数估算 4.3 字/秒（make_timing.py）；Knoll /workspace/share/ep21/ 到后 sh realign.sh 重跑")
PS="hook-1";sh=[x for sc in scenes for x in sc["shots"] if x["id"]==PS][0];pl=0
meta["poster"]=dict(shotId=PS,localFrame=pl,frame=sh["from"]+pl,desc="开场即封面画面（正式封面另做定制 PNG，不取视频帧）",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes]);print('poster',PS,pl,meta['poster']['frame'])
