# EP.06《为什么一家店忙不过来，还要开好几家一起干？》分镜生成（Miyazaki）。工具链沿用 EP.04 cookie-session/gen.py
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
from common_split import ids,SPLIT as _SP,SCRIPT
src=open(SCRIPT).read()
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
def F(i,a,n=12): return fade(i,a,a+n)
def pop(i,a): return mv(i,"scale",a,a+12,0,1,"spring")
titles=["一家柜台排长队","单点忙不过来","多开柜台加导购","怎么分人","健康检查","回顾"]
SPLIT={i:_SP[c] for i,c in enumerate(ids)}
def KEY(si,k): return f"{ids[si]}-{k+1}"
def sentences(s): return re.findall(r'[^。？]+[。？]',s)
CARD=dict(stroke=P['secondary'],radius=16,fontSize=36)
def card(i,x,y,w,h,label,**k): return R(i,x,y,w,h,**{**CARD,"label":label,**k})
def browser(x,y,w=360,h=220): return card("browser",x,y,w,h,"浏览器",reuse=True)
def server(i,x,y,w,h,label): return card(i,x,y,w,h,label,reuse=True,note="统一服务器卡片（同浏览器样式，无窗口圆点，标签 36px）")
TM=json.load(open(HERE/"timing.json"))
PARTS=[]
def AT(si,_k,phrase):
    # 自动定位短语所在的镜头（本章内唯一），返回该镜头内的相对帧
    hits=[(k,j) for k,pt in enumerate(PARTS) for j,x in enumerate(sentences(pt)) if phrase in x]; assert hits,(si,phrase)
    k,i=hits[0]; S=sentences(PARTS[k]); s=S[i]
    off=cnt(s[:s.index(phrase)])/max(1,cnt(s)); q=TM[KEY(si,k)]["sentences"]; assert len(q)==len(S)
    return round(30*(q[i]["start"]+q[i]["dur"]*off))
def AEND(si,k): return TM[KEY(si,k)]["audioFrames"]
def store(i,x,y,s=200,**k): return A(i,"store",x,y,s,s,**k)
def ctr(i,x,y,s=200,kind="idle",**k): return A(i,f"counter-{kind}",x,y,s,s,**k)
def gre(i,x,y,s=240,**k): return A(i,"greeter",x,y,s,s,**k)
REV=None  # 第四章：v1（三种分法）或修订版（两种 + 过渡句），由脚本内容自动判断
def shots_for(si,L):
    at=lambda k,p:AT(si,k,p)
    VC=[200,420,640]  # 竖排三家柜台的 y
    def stack(kinds,x=1300,s=200,pre="c"): return [ctr(f"{pre}{j}",x,y,s,kd) for j,(y,kd) in enumerate(zip(VC,kinds))]
    if si==0:  # 一家柜台排长队
        e1=[T("prev",160,140,800,50,"上一期：CDN 带你到最近的门店",36,P['text2'],align="center"),
            store("store",160,220,340),T("storeT",160,580,340,50,"家门口的门店",40,P['primary'],align="center"),
            A("queue","queue",560,380,760,198),ctr("counter",1380,260,380,"busy"),T("counterT",1380,660,380,50,"只有一个柜台",40,P['accent'],align="center"),
            T("slow",160,760,1600,60,"人一多，排长队，点单越来越慢",48,P['danger'],align="center")]
        a1=[F("prev",0),F("store",0),F("storeT",0),F("counter",at(0,"只有一个柜台")),F("counterT",at(0,"只有一个柜台")),
            F("queue",at(0,"人一多")),mv("queue","x",at(0,"人一多"),at(0,"排长队"),300,560),F("slow",at(0,"点单越来越慢"))]
        e2=[R("spin",160,600,400,80,stroke=P['text2'],radius=16,label="页面转圈",fontSize=40),server("srv",1160,240,440,300,"服务器"),
            R("timeout",1160,600,440,80,stroke=P['danger'],radius=16,label="超时",fontSize=40),T("q",600,620,480,110,"？",96,P['accent'],align="center")]
        a2=[F("srv",0)]
        t=at(0,"所有请求")
        for j in range(5):
            e2.append(E(f"r{j}","arrow",160,220+j*70,980,40,P['danger'] if j==4 else P['primary'],direction="r")); a2.append(draw(f"r{j}",t+j*5,14))
        a2+=[F("spin",at(0,"转圈")),F("timeout",at(0,"超时")),pop("timeout",at(0,"超时")),F("q",at(1,"怎么解决")),pop("q",at(1,"怎么解决"))]
        return [(e1,a1),(e2,a2)]
    if si==1:  # 单点故障
        e1=[store("store",160,220,300),R("shut",160,560,300,80,stroke=P['danger'],radius=16,label="整家店关门",fontSize=36),
            ctr("open",760,180,400,"busy"),ctr("closed",760,180,400,"closed"),
            R("spof",660,640,600,100,stroke=P['danger'],radius=50,label="单点故障",fontSize=56),
            T("only",1220,320,540,50,"只靠一个柜台",40,P['text'],align="center")]
        t=at(0,"它一休息")
        a1=[F("store",0),F("open",0),F("only",at(0,"只靠")),F("spof",0),pop("spof",0),out("open",t,t+12),F("closed",t),F("shut",at(0,"关门"))]
        e2=[R("far",160,160,760,90,stroke=P['secondary'],radius=16,label="远 → CDN 管",fontSize=40),
            R("many",1000,160,760,90,stroke=P['danger'],radius=16,label="人多挤垮 → 另一件事",fontSize=40),
            server("srv",160,320,520,420,""),ctr("one",260,330,320,"busy"),T("oneT",160,670,520,50,"一台机器",40,P['text'],align="center")]
        a2=[F("far",at(0,"远的人慢")),F("many",at(0,"人一多挤垮")),F("srv",at(1,"一台机器")),F("one",at(1,"一台机器")),F("oneT",at(1,"一台机器"))]
        for j,(lab,ph) in enumerate([("中央处理器","中央处理器"),("内存","内存"),("网口","网口")]):
            y=340+j*130
            e2+=[T(f"g{j}",740,y,300,50,lab,40,P['text'],align="right"),R(f"tr{j}",1080,y,680,56,P['panel'],stroke=P['text2'],radius=28),R(f"fill{j}",1080,y,680,56,P['danger'],radius=28,note="仪表顶红：opacity 渐显（整条满格）")]
            a2+=[F(f"g{j}",at(1,ph)),F(f"tr{j}",at(1,ph)),mv(f"fill{j}","opacity",at(1,"高峰")+j*6,at(1,"高峰")+j*6+12,0,0.9)]
        e2.append(T("peak",740,760,1020,56,"高峰一到就扛不住",44,P['danger'],align="center")); a2.append(F("peak",at(1,"扛不住")))
        return [(e1,a1),(e2,a2)]
    if si==2:  # 多开柜台 + 导购
        e1=[T("multi",160,140,1600,56,"多开几家柜台 + 门口站个导购",44,P['text'],align="center"),
            gre("greeter",400,260,300),T("lbT",340,580,420,50,"导购 = 负载均衡器",40,P['accent'],align="center")]
        a1=[F("multi",0)]
        for j in range(3):
            e1.append(ctr(f"c{j}",1000+j*260,260,240)); a1+=[F(f"c{j}",at(0,"多开几家")+j*8),pop(f"c{j}",at(0,"多开几家")+j*8)]
        e1.append(T("backT",1000,520,760,50,"后端服务器：多台一起干活",36,P['primary'],align="center"))
        a1+=[F("backT",at(0,"后端服务器")),F("greeter",at(0,"门口再站")),F("lbT",at(0,"负载均衡器"))]
        e2=[R("sign",160,140,1600,80,stroke=P['secondary'],radius=16,label="还是同一家店，地址没变",fontSize=40),gre("greeter",600,330,240)]+stack(["idle","idle","idle"],x=1400,s=180)
        for c in e2[-3:]: c['y']+=50
        CY=[c['y'] for c in e2[-3:]]
        a2=[F("greeter",0)]+[F(f"c{j}",0) for j in range(3)]
        t=at(0,"分到空闲")
        for j in range(3):
            y=CY[j]+65; e2.append(E(f"to{j}","arrow",860,y,520,50,P['success'],direction="r")); a2.append(draw(f"to{j}",t+j*8,15))
        # 排队的客人：从导购左边依次走到三家柜台（x/y 关键帧），最后一位往前补位
        for j in range(4):
            x0=440-j*95; e2.append(A(f"p{j}","person",x0,400,130,130)); a2.append(F(f"p{j}",0))
            if j<3:
                s0=t+j*14; a2+=[mv(f"p{j}","x",s0,s0+30,x0,1260),mv(f"p{j}","y",s0,s0+30,400,CY[j]+25)]
        s3=t+3*14+10; a2.append(mv("p3","x",s3,s3+20,155,440))
        a2+=[F("sign",at(1,"同一家店"))]
        return [(e1,a1),(e2,a2)]
    if si==3:  # 怎么分人
        S=narr[3]; three="第三种" in S
        base=lambda:[gre("greeter",160,330,240)]
        e1=base()+[T("how",160,140,1000,64,"导购怎么分人？",52,P['text'],align="center"),
            R("rr",160,620,860,90,stroke=P['primary'],radius=16,label="① 轮询：一人一家，轮着来",fontSize=40)]+stack(["idle","idle","idle"])
        a1=[F("greeter",0),F("how",0)]+[F(f"c{j}",0) for j in range(3)]+[F("rr",at(0,"轮询")),pop("rr",at(0,"轮询"))]
        t=at(0,"一人一家")
        for j in range(3):
            y=VC[j]+75; e1+=[E(f"to{j}","arrow",420,y,860,50,P['primary'],direction="r"),R(f"n{j}",1540,VC[j]+60,120,80,stroke=P['accent'],radius=40,label=str(j+1),fontSize=48)]
            a1+=[draw(f"to{j}",t+j*14,12),F(f"n{j}",t+j*14+6)]
        loads=[("3 单",3),("1 单",1),("5 单",5)]
        e2=base()+[R("lc",160,140,1000,90,stroke=P['success'],radius=16,label="② 最少连接：谁手里单子少，就指向谁",fontSize=36)]+stack(["busy","idle","busy"])
        a2=[F("greeter",0)]+[F(f"c{j}",0) for j in range(3)]+[F("lc",at(0,"最少连接")),pop("lc",at(0,"最少连接"))]
        for j,(lab,_) in enumerate(loads):
            e2.append(R(f"load{j}",1540,VC[j]+60,200,80,stroke=P['success'] if j==1 else P['danger'],radius=40,label=lab,fontSize=40)); a2.append(F(f"load{j}",at(0,"单子少")))
        e2.append(E("pick","arrow",420,VC[1]+75,860,50,P['success'],direction="r")); a2.append(draw("pick",at(0,"就往哪指"),15))
        e2.append(T("fair",160,620,860,50,"忙的时候更公平",40,P['text2'],align="center")); a2.append(F("fair",at(0,"更公平")))
        if three:  # v1：第三种「看健康」——第三家柜台打叉跳过
            e2+=[ctr("bad",1300,VC[2],200,"closed"),T("x",1300,VC[2]+40,200,120,"✕",96,P['danger'],align="center"),R("hc",160,720,860,90,stroke=P['danger'],radius=16,label="③ 看健康：坏掉的柜台跳过",fontSize=40)]
            a2+=[F("bad",at(1,"第三种")),out("c2",at(1,"第三种"),at(1,"第三种")+12),out("load2",at(1,"第三种"),at(1,"第三种")+12),F("x",at(1,"跳过")),F("hc",at(1,"第三种"))]
        else:      # 修订版：两种 + 过渡句（字幕已有，画面不写字）；末尾最后一家柜台灯闪 → 引出第五章健康检查
            lx,ly=1300+round(120*200/512)-17,VC[2]+round(190*200/512)-17
            e2.append(R("lamp",lx,ly,34,34,P['muted'],radius=17,note="灯闪：灰圆盖住状态灯（灭）→ 亮 → 灭，最后保持熄灭"))
            L1=L[1]; tf=max(at(1,"前提"),min(at(1,"前提")+20,L1-22))
            a2+=[mv("lamp","opacity",0,tf,0,0,"linear"),mv("lamp","opacity",tf,tf+3,0,1,"linear"),mv("lamp","opacity",tf+6,tf+9,1,0,"linear"),mv("lamp","opacity",tf+12,tf+15,0,1,"linear")]
        return [(e1,a1),(e2,a2)]
    if si==4:  # 健康检查
        e1=[gre("greeter",160,330,240),R("hcT",160,140,860,90,stroke=P['success'],radius=16,label="健康检查：定时问一声",fontSize=40),A("heart","health",200,620,160,160)]+stack(["idle","closed","idle"])
        a1=[F("greeter",0)]+[F(f"c{j}",0) for j in range(3)]
        t=at(0,"定时问问")
        for j in range(3):
            y=VC[j]+75; e1.append(E(f"ask{j}","arrow",420,y,860,50,P['text2'],label="还开着吗？" if j==0 else "",direction="r",fontSize=32,dash=True)); a1.append(draw(f"ask{j}",t+j*8,15))
        e1+=[R("no",1540,VC[1]+60,200,80,stroke=P['danger'],radius=40,label="不回",fontSize=40)]
        a1+=[F("no",at(0,"还开着吗")+20),F("hcT",at(0,"健康检查")),F("heart",at(0,"健康检查")),pop("heart",at(0,"健康检查"))]
        HX=[700,940,1180]
        e2=[gre("greeter",160,300,240)]+[ctr(f"c{j}",x,300,200,"idle") for j,x in enumerate(HX)]+[ctr("cX",HX[1],300,200,"closed"),ctr("cNew",1420,300,200,"idle"),
            R("pause",700,560,440,80,stroke=P['danger'],radius=16,label="不回：先不派单",fontSize=36),R("back",700,670,440,80,stroke=P['success'],radius=16,label="恢复：再排回来",fontSize=36),
            R("elastic",1180,600,560,110,stroke=P['accent'],radius=55,label="弹性扩展",fontSize=56)]
        o={e['id']:e for e in e2}; e2=[o[k] for k in ("greeter","c0","cX","c1","c2","cNew","pause","back","elastic")]  # cX（休息）在 c1（恢复）下层
        r=at(0,"等它恢复")
        a2=[F("greeter",0),F("c0",0),F("c2",0),F("cX",0),F("pause",at(0,"先不派单")),mv("c1","opacity",0,r,0,0,"linear"),F("c1",r),out("cX",r,r+12),F("back",r),
            F("cNew",at(1,"新开的柜台")),mv("cNew","x",at(1,"新开的柜台"),at(1,"新开的柜台")+15,1560,1420),F("elastic",at(1,"弹性扩展")),pop("elastic",at(1,"弹性扩展"))]
        return [(e1,a1),(e2,a2)]
    if si==5:  # 回顾
        e1=[T("cdnH",160,160,760,56,"CDN：去哪座城的店",44,P['primary'],align="center"),A("map","map",160,250,760,266),T("cdnS",160,560,760,50,"解决：路太远",40,P['text'],align="center"),
            T("lbH",1000,160,760,56,"负载均衡：进店后去哪个柜台",40,P['accent'],align="center"),gre("greeter",1000,280,200)]+[ctr(f"c{j}",1240+j*170,300,150) for j in range(3)]+[
            T("lbS",1000,560,760,50,"解决：人太多",40,P['text'],align="center")]
        a1=[F("cdnH",0),F("map",0),F("cdnS",at(0,"路太远")),F("lbH",at(0,"负载均衡")),F("greeter",at(0,"负载均衡"))]+[F(f"c{j}",at(0,"负载均衡")+4*j) for j in range(3)]+[F("lbS",at(0,"人太多"))]
        e2=[T("both",160,160,1600,60,"两套一起用：路近更快，多柜台更扛得住",44,P['text'],align="center"),
            A("queue","queue",160,330,560,146),gre("greeter",780,300,220)]+[ctr(f"c{j}",1100+j*220,300,200) for j in range(3)]+[
            T("final",160,620,1600,70,"人再多，高峰也能稳住",56,P['primary'],align="center")]
        a2=[F("both",0),F("queue",0),mv("queue","x",0,40,120,160),F("greeter",0)]+[F(f"c{j}",0) for j in range(3)]+[F("final",at(1,"所以"))]
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
scenes=[];g=0;nshot=0;CLAMP=[]
for si,s in enumerate(narr):
    S=sentences(s);parts=[];i=0
    for n in SPLIT[si]: parts.append("".join(S[i:i+n]).strip());i+=n
    assert i==len(S) and "".join(parts).replace(' ','')==s.replace(' ','')
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
    D=sum(L);scenes.append(dict(id=f"s{si}",chapterId=ids[si],title=titles[si],**{"from":g},durationInFrames=D,narrationChars=CNT[si],narrationCharsRecount=cnt(s),shots=shots));g+=D
PROV=any(v.get('provisional') for v in TM.values())
meta=dict(title="《为什么一家店忙不过来，还要开好几家一起干？》",episode=6,slug="load-balancing",release="v0.10.0",width=1920,height=1080,fps=30,durationInFrames=g,provisionalTiming=PROV,style="深色背景+蓝青高光扁平2D（沿用前几期）",palette=P,font="Noto Sans SC",
  safeArea=dict(margin=80,subtitleBand=[900,980],contentMaxY=880,watermarkClearZone=[1700,80,1840,130]),
  branding=dict(spec="episodes/_shared/branding/spec.json v1.3.0",cornerWatermark="右上「IT小村」40%，留空区 x1700–1840 y80–130",centerWatermark=None,endCard="由 <ChannelBranding> 自动追加 60 帧，本分镜不画；durationInFrames 不含片尾"),
  notes=("时长=暂定（make_timing.py：第三期 MiMo 冰糖实测校准，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）。配音到后：Knoll 的 ep6 timing 存为 timing.mimo.json → map_timing.py（scale 1）→ gen.py → validate.py。" if PROV else "时长=Knoll MiMo 实测，map_timing.py scale 1。")+"extraHold：spof-1 末尾 +30 帧纯画面停留（common_split.HOLDS；Knoll timing 已含则不重复加）。"+
   f"脚本：{'v1（第四章三种分法）' if '第三种' in narr[3] else '修订版（第四章两种分法 + 过渡「前提是柜台得开着」）'}，script.md mtime {int(Path(SCRIPT).stat().st_mtime)}。贯穿比喻接第五期连锁店：导购 = 负载均衡器，柜台 = 后端服务器。from 为全局帧，subtitles 与 keyframes 帧相对镜头。image 的 asset 路径相对 episodes/load-balancing/。新图标 greeter/counter-idle/counter-busy/counter-closed/person/queue/health 自绘无文字；复用第五期 store/map。英文白名单：CDN。branding v1.3.0：只有右上水印（留空区 x1700–1840 y80–130）+ 60 帧片尾卡（全局组件），无中央水印，全片无「我是 IT小村」。")
assets=dict(reuse=[dict(id="server",desc="统一服务器卡片"),dict(id="routeArrow",desc="路线箭头 drawProgress"),dict(id="subtitle",desc="字幕层"),
  dict(id="store",file="assets/store.svg",from_="cdn/assets/store.svg"),dict(id="map",file="assets/map.svg",from_="cdn/assets/map.svg")],
 new=[dict(id=n,file=f"assets/{n}.svg") for n in ("greeter","counter-idle","counter-busy","counter-closed","person","queue","health")])
PS="solution-2"; sh=[x for sc in scenes for x in sc['shots'] if x['id']==PS][0]
pl=299  # Nolan 定：solution-2 局部 299
meta['poster']=dict(shotId=PS,localFrame=pl,frame=sh['from']+pl,desc="排队的客人经导购走到三家空闲柜台 + 「还是同一家店，地址没变」",file="poster.jpg")
json.dump(dict(meta=meta,assets=assets,scenes=scenes),open(HERE/"storyboard.json","w"),ensure_ascii=False,indent=1)
print('clamped keyframes:',CLAMP or 'none');print(g,nshot,[(s['chapterId'],s['from'],s['durationInFrames']) for s in scenes])
