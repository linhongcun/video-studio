import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots} from './data';
import {C,FONT,MONO} from './theme';
import {M,COLORS,T,Head,Note,Pill,Arrow,Cache,Panel,Ring,point,arc,clamp,ease,mix,progress} from './graphics';
import {useLayoutAudit} from './LayoutAudit';
declare const __HAS_VOICE_AUDIO__:boolean;

/** All stages use shared sentence timing; no CSS or wall-clock animations. */
export const phase=(s:any,f:number)=>{
 const cues=s.cueFrames?.sentences??[20,Math.floor(s.durationInFrames*.5)];
 const a=cues[0],b=cues[1];
 return {a,b,p:progress(f,a+12,Math.min(b-15,a+110)),q:progress(f,b+10,Math.min(s.durationInFrames-30,b+125)),f};
};
const headers:Record<string,[string,string,string]>={
 expansion:['扩容为何改去向','多加一台缓存，旧键为什么改了去向？','目标：容纳更多缓存数据；先看原来的定位规则。'],
 hash:['扩容为何改去向','同一个键，先算出同一个数字','哈希值是定位用的数字，不是缓存值，也不是节点编号。'],
 modulo:['扩容为何改去向','三台缓存：用除以3的余数定位','给A、B、C编号0、1、2，按余数选择负责节点。'],
 remap:['扩容为何改去向','加上D，除数从3变成4','键没变、哈希值没变，台数一变，负责节点却可能改变。'],
 miss:['扩容为何改去向','新去向变了，旧值还在原处','56原本交给C；按新规则，却会查询A。'],
 goal:['固定位置顺时针定位','想保留旧去向，就别跟着台数重排','设计目标：新节点接走一部分，其余映射尽量不动。'],
 ring:['固定位置顺时针定位','一致性哈希：把键与节点放进同一空间','这里用0—99示意；已有节点的位置保持固定。'],
 lookup:['固定位置顺时针定位','从键的位置，顺时针找第一个节点','56是键的位置；负责它的节点，在顺时针方向确定。'],
 wrap:['固定位置顺时针定位','越过99，沿同一方向绕回0','不是选距离最近的节点，也不是每次重新编号。'],
 insert:['新节点仅接管局部','把D放到70，旧节点都不挪动','对比加入前后：哪些键会更早遇到D？'],
 local:['新节点仅接管局部','同一组十个键，只有两个改去D','比较的是负责节点；不表示缓存值已经完成搬迁。'],
 imbalance:['虚拟节点与边界','一个位置，可能分到很长或很短一段','编号空间的长度不同，不等于真实请求量或内存用量。'],
 vnodes:['虚拟节点与边界','多个虚拟位置，仍然属于同一台缓存','另一套预先配置的示例；不把重新布置当成无成本在线转换。'],
 recap:['虚拟节点与边界','扩容时少改去向，迁移与负载另行处理','固定已有位置 → 新节点接走局部 → 其余保留原去向。']
};
const KeyFlow=({y=480,p=1,q=0}:any)=><>
 <rect x={215} y={y-68} width={290} height={136} rx={20} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
 <T x={360} y={y-13} size={30} anchor="middle">商品价格的键</T><T x={360} y={y+36} size={32} anchor="middle" mono>K06</T>
 <Arrow x1={535} y1={y} x2={775} y2={y} color={C.teal}/>
 <Pill x={940} y={y} w={260} label="固定哈希算法" color={C.teal} size={31}/>
 <Arrow x1={1100} y1={y} x2={1330} y2={y} color={C.teal}/>
 <g opacity={p===1?1:0}><T x={1500} y={y+21} size={78} mono anchor="middle" color={C.gold}>56</T><T x={1500} y={y+82} size={26} anchor="middle" color={C.muted}>示例哈希输出</T></g>
 {[p,q].map((t,i)=>t>0&&t<1?<circle key={i} cx={t<.5?mix(535,775,t*2):mix(1100,1330,(t-.5)*2)} cy={y} r={9} fill={C.text}/>:null)}
 {q>0&&<T x={960} y={641} size={29} anchor="middle" color={C.muted}>同一个K06，沿同一套算法再算一次</T>}
</>;
const SampleTable=({s,f,mode='modulo'}:any)=>{
 const {a,b}=phase(s,f),base=mode==='ring'?a+15:b+10,step=mode==='ring'?10:8,duration=mode==='ring'?55:46;
 let completed=0;
 const rows=M.keys.map((k:any,i:number)=>{
  const before=mode==='ring'?k.ringBefore:k.modBefore,after=mode==='ring'?k.ringAfter:k.modAfter;
  const p=progress(f,base+i*step,base+i*step+duration),changed=before!==after;
  if(p>=1&&changed)completed++;
  return {...k,before,after,p,changed};
 });
 return <>
  <T x={120} y={346} size={29} color={C.muted}>示例哈希值</T>
  <T x={120} y={495} size={27} color={C.muted}>{mode==='ring'?'加入D前':'原规则 %3'}</T>
  <T x={120} y={676} size={27} color={C.muted}>{mode==='ring'?'加入D后':'新规则 %4'}</T>
  {rows.map((k:any,i:number)=>{const x=340+i*151;return <g key={k.id} data-sample={k.id} data-before={k.before} data-after={k.p===1?k.after:'pending'}>
   <T x={x} y={346} size={36} mono anchor="middle">{k.hash}</T>
   <Pill x={x} y={489} w={100} label={k.before} color={COLORS[k.before]} size={35}/>
   <Arrow x1={x} y1={536} x2={x} y2={610} color={k.changed?C.gold:C.edge}/>
   {k.p>0&&k.p<1&&<circle cx={x} cy={mix(540,611,k.p)} r={7} fill={C.text}/>}
   <Pill x={x} y={670} w={100} label={k.after} color={COLORS[k.after]} opacity={k.p} size={35}/>
   {k.p===1&&<T x={x} y={755} size={25} color={k.changed?C.gold:C.muted} anchor="middle">{k.changed?'改去向':'保留'}</T>}
  </g>;})}
  <T x={960} y={856} size={38} color={C.gold} anchor="middle">{completed} / 10 改去向 · 仅这组示例</T>
 </>;
};
const Expansion=({s,f}:any)=>{
 const {p,q}=phase(s,f);
 const nodeX=[430,800,1170,1540];
 return <>
  <T x={960} y={334} size={35} anchor="middle">应用：按商品键读取价格缓存</T>
  <Pill x={960} y={435} w={320} label="同一批缓存键" color={C.text} size={32}/>
  {['A','B','C','D'].map((id,i)=><g key={id} opacity={i===3?p:1}>
   <Arrow x1={960} y1={480} x2={nodeX[i]} y2={615} color={i===3?COLORS.D:C.edge} dashed={i===3}/>
   <Cache x={nodeX[i]} y={716} id={id} detail={i===3?'新增容量':i===2?'保存这个键的价格':i===0&&q===1?'未命中这个键':'已有其他缓存值'}/>
  </g>)}
  {q>0&&<g><Arrow x1={960} y1={480} x2={430} y2={615} color={C.gold} opacity={q}/><circle cx={mix(960,430,q)} cy={mix(480,615,q)} r={9} fill={C.text}/>{q===1&&<Pill x={430} y={575} w={180} label="未命中" color={C.red} size={28}/>}<T x={960} y={865} size={34} color={C.gold} anchor="middle" opacity={q}>规则一改，部分旧键被分到了别处</T></g>}
 </>;
};
const Modulo=({s,f}:any)=>{
 const {p,q}=phase(s,f);
 return <>
  <T x={960} y={399} size={64} mono anchor="middle">56 ÷ 3</T>
  <g opacity={p}><T x={960} y={511} size={55} mono anchor="middle" color={C.gold}>余 2</T></g>
  {['A','B','C'].map((id,i)=><g key={id}>
   <T x={420+i*540} y={615} size={30} mono color={COLORS[id]} anchor="middle">编号 {i}</T>
   <Cache x={420+i*540} y={736} id={id} detail={id==='C'&&q===1?'负责K06':'按余数选择'}/>
  </g>)}
  <g opacity={q}><Arrow x1={1040} y1={530} x2={1450} y2={640} color={COLORS.C}/></g>
 </>;
};
const Miss=({s,f}:any)=>{
 const {a,b,p,q}=phase(s,f),request=progress(f,a+20,a+100),returnP=progress(f,a+110,b-12);
 return <>
  <Pill x={480} y={387} w={380} label="查询K06 · 哈希56" color={C.text} size={31}/>
  <Arrow x1={480} y1={435} x2={480} y2={590} color={C.gold}/>
  <circle cx={480} cy={mix(445,586,request)} r={9} fill={C.text}/>
  <Cache x={480} y={710} id="A" detail="新去向 · 没有K06" w={370}/>
  <Cache x={1440} y={710} id="C" detail="旧值K06仍留在这里" w={410}/>
  <g opacity={returnP}><Pill x={480} y={536} w={200} label="未命中" color={C.red} size={31}/></g>
  <g opacity={q}><path d="M800 720L800 590Q800 555 835 555H1110" stroke={C.muted} strokeWidth={3} strokeDasharray="8 8" fill="none"/>
   <rect x={1130} y={435} width={480} height={133} rx={18} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
   <T x={1370} y={487} size={30} anchor="middle">数据库 · 权威数据源</T><T x={1370} y={533} size={25} anchor="middle" color={C.muted}>未命中后可回源重建缓存</T>
   <T x={960} y={861} size={31} anchor="middle" color={C.gold}>数据迁移 / 回源重建，都有额外工作</T>
  </g>
 </>;
};
const Goal=({s,f}:any)=>{
 const {p,q}=phase(s,f);
 return <>
  <T x={960} y={345} size={35} anchor="middle" color={C.gold}>设计目标 · 先明确想保留什么</T>
  {['A','B','C','D'].map((id,i)=><Cache key={id} x={390+i*380} y={558} id={id} detail={id==='D'?'只接走一部分':'尽量保留原去向'}/>)}
  <g opacity={p}><path d="M510 706Q750 838 960 731Q1200 838 1410 706" stroke={C.edge} strokeWidth={3} fill="none"/>
   <T x={960} y={819} size={35} anchor="middle">台数改变时，不重新排列已有位置</T>
  </g>
  <g opacity={q}><T x={960} y={891} size={29} color={C.teal} anchor="middle">先固定键与节点的位置，再决定谁负责哪一段</T></g>
 </>;
};
const RingSetup=({s,f}:any)=>{
 const {a,b}=phase(s,f),bend=progress(f,a+40,b-24),nodesIn=progress(f,b+12,b+72);
 return <>
  <Ring nodes={nodesIn>.05?M.nodesBefore:[]} keys={nodesIn===1?[56]:[]} focus={56} morph={bend}/>
  <Panel title={bend===1?'节点和键，共用一套位置':'先固定编号空间'}>
   <T x={1190} y={444} size={37} color={C.teal}>{bend===1?'首尾相接，按顺时针找':'0、1、2 …… 99'}</T>
   <g opacity={nodesIn}><T x={1190} y={541} size={34} color={COLORS.A}>A缓存：位置20</T><T x={1190} y={615} size={34} color={COLORS.B}>B缓存：位置50</T><T x={1190} y={689} size={34} color={COLORS.C}>C缓存：位置85</T><T x={1190} y={798} size={28} color={C.muted}>示例位置；不随台数重新编号</T></g>
  </Panel>
 </>;
};
const Lookup=({s,f,wrap=false}:any)=>{
 const {a,b}=phase(s,f),p=progress(f,a+34,b+30),value=wrap?95:56,target=wrap?120:85,done=p===1;
 return <>
  <Ring keys={[value]} focus={value} trace={{from:value,to:target,progress:p}}/>
  <Panel title={wrap?'同一规则：经过0继续找':'从键的位置出发'}>
   <T x={1190} y={447} size={42} mono color={C.text}>hash(K) = {value}</T>
   <T x={1190} y={541} size={32} color={C.gold}>{wrap?'95 → 99 → 0 → 20':'56 → 70 → 85'}</T>
   <T x={1190} y={631} size={30} color={C.muted}>{wrap?'跨过0，方向不变':'此时70没有节点，不停下'}</T>
   {done&&<><T x={1190} y={738} size={42} color={COLORS[wrap?'A':'C']}>第一个节点：{wrap?'A20':'C85'}</T><T x={1190} y={812} size={28} color={C.muted}>键的位置仍是{value}；没有移到节点上</T></>}
  </Panel>
 </>;
};
const Insert=({s,f}:any)=>{
 const {a,b,p,q}=phase(s,f),arrive=progress(f,a+14,a+95),band=progress(f,b+5,b+75);
 const segments=band>0?[{from:50,to:70,color:COLORS.D,opacity:band},{from:70,to:85,color:COLORS.C,opacity:.6}]:[{from:50,to:85,color:COLORS.C,opacity:.45}];
 return <>
  <Ring nodes={M.nodesAfter} dOpacity={arrive} keys={[56,64,78]} focus={band===1?56:undefined} segments={segments}/>
  {band>0&&<path d={arc(56,mix(85,70,band),230)} stroke={C.gold} strokeWidth={3} strokeDasharray="7 7" fill="none"/>}
  <Panel title="只插入D，旧节点位置不动">
   <T x={1190} y={445} size={38} color={COLORS.D}>新增 D · 位置70</T>
   <T x={1190} y={548} size={33} color={band===1?COLORS.D:C.muted}>{band===1?'50之后，到70为止':'原来：50之后，到85为止'}</T>
   <T x={1190} y={630} size={30} color={C.muted}>{band===1?'这一段先遇到D':'整段原本由C负责'}</T>
   {band===1&&<><T x={1190} y={738} size={38} color={COLORS.D}>56、64：C → D</T><T x={1190} y={814} size={32} color={COLORS.C}>78 仍然先遇到 C85</T></>}
  </Panel>
 </>;
};
const Imbalance=({s,f}:any)=>{
 const {a,b,p,q}=phase(s,f),counts=M.rings.after.intervalCounts;
 return <>
  <Ring nodes={M.nodesAfter} segments={[{from:85,to:120,color:COLORS.A},{from:20,to:50,color:COLORS.B},{from:50,to:70,color:COLORS.D},{from:70,to:85,color:COLORS.C}]}/>
  <Panel title={q>.6?'虚拟节点：一台机器，多个位置':'本例编号空间长度 · 共100'}>
   {['A','B','C','D'].map((id,i)=><g key={id}><T x={1190} y={437+i*83} size={31} color={COLORS[id]}>{id}</T><rect x={1250} y={410+i*83} width={counts[id]*10*p} height={34} rx={6} fill={COLORS[id]} opacity={.8}/><T x={1660} y={438+i*83} size={31} mono color={COLORS[id]}>{counts[id]}</T></g>)}
   <g opacity={q}><T x={1190} y={824} size={31} color={C.gold}>把一段，拆成分散的许多小段</T></g>
  </Panel>
 </>;
};
const VNodes=({s,f}:any)=>{
 const {a,b}=phase(s,f),join=progress(f,a+60,b-10),link=progress(f,b+10,b+100);
 const nodes=[...M.vnodesBefore,...(join>0?M.vnodesAfter.filter((n:any)=>n.physicalId==='D'):[])];
 const segments=[{from:5,to:10,color:COLORS.D,opacity:join},{from:28,to:34,color:COLORS.D,opacity:join},{from:82,to:88,color:COLORS.D,opacity:join}];
 return <>
  <Ring nodes={nodes} dOpacity={join} segments={segments} showNodeLabels={false} showZero={true} centerText="另一套示例"/>
  {M.vnodesBefore.filter((n:any)=>n.physicalId==='A').map((n:any)=>{const p=point(n.position,250);return <circle key={n.id} cx={p.x} cy={p.y} r={27} fill="none" opacity={link*.8} stroke={COLORS.A} strokeWidth={2}/>;})}
  <Panel title="颜色与字母表示同一台物理缓存">
   <T x={1190} y={437} size={33} color={COLORS.A}>A：5、38、72</T>
   <T x={1190} y={510} size={33} color={COLORS.B}>B：15、48、82</T>
   <T x={1190} y={583} size={33} color={COLORS.C}>C：28、60、94</T>
   <g opacity={join}><T x={1190} y={676} size={33} color={COLORS.D}>新增 D：10、34、88</T></g>
   <g opacity={link}><T x={1190} y={788} size={32} color={C.text}>3个A位置 → 同一A缓存</T><T x={1190} y={844} size={28} color={C.muted}>仍是4台机器，不是12台</T></g>
  </Panel>
 </>;
};
const Recap=({s,f}:any)=>{
 const {a,b,p,q}=phase(s,f),pulse=progress(f,a+10,Math.min(a+130,b-10));
 return <>
  <g opacity={1-clamp(q*2)}><Pill x={470} y={428} w={250} label="同一个热点键" color={C.gold}/><Cache x={1420} y={600} id="A" detail="单份归属" w={320}/>
   {[0,1,2,3,4].map(i=><g key={i}><Arrow x1={670} y1={408+i*49} x2={1190} y2={530+i*34} color={C.edge}/><circle cx={mix(680,1178,clamp((pulse-i*.11)/.55))} cy={mix(408+i*49,530+i*34,clamp((pulse-i*.11)/.55))} r={7} fill={C.gold}/></g>)}
   <T x={960} y={795} size={34} color={C.gold} anchor="middle">多虚拟节点，不能把一个热键拆到多台机器</T>
  </g>
  <g opacity={clamp((q-.5)*2)}>
   <Pill x={420} y={460} w={430} label="固定已有位置" color={COLORS.A} size={36}/>
   <Arrow x1={665} y1={460} x2={745} y2={460} color={C.teal}/>
   <Pill x={960} y={460} w={370} label="新节点接走局部" color={COLORS.D} size={35}/>
   <Arrow x1={1170} y1={460} x2={1255} y2={460} color={C.teal}/>
   <Pill x={1500} y={460} w={420} label="其余保留原去向" color={COLORS.B} size={35}/>
   <T x={960} y={652} size={43} anchor="middle">少改归属，减少扩容重分配</T>
   <T x={960} y={753} size={33} anchor="middle" color={C.muted}>数据迁移怎么做、请求负载怎么分，仍要单独设计</T>
   <T x={960} y={857} size={30} anchor="middle" color={C.teal}>IT小村 · 原创</T>
  </g>
 </>;
};
export const Scene=({s,f}:any)=>{
 const type=s.visualType,{a,b,p,q}=phase(s,f);let [chapter,title,sub]=headers[type]??headers.expansion;
 const labels=s.cueFrames?.labels??{};
 if(type==='ring'&&f<(labels['一致性哈希']??Math.max(1,a-2)))title='先固定位置，再建立新的定位规则';
 if(type==='imbalance'&&f<(labels['虚拟节点']??Math.max(1,b-2)))chapter='区间分配与边界';
 let content:any=null,note='教学示例 · 数字、位置与数量均为演示，不是产品性能实测';
 switch(type){
  case 'expansion':content=<Expansion s={s} f={f}/>;break;
  case 'hash':content=<><KeyFlow p={p} q={q}/><g opacity={q}><T x={960} y={741} size={39} color={C.teal} anchor="middle">同一个键 + 同一哈希算法 → 同一个结果</T></g></>;break;
  case 'modulo':content=<Modulo s={s} f={f}/>;break;
  case 'remap':content=<><g opacity={1-progress(f,b-12,b+8)}><T x={960} y={418} size={67} mono anchor="middle">56 ÷ 4，余 0</T><Cache x={620} y={671} id="C" detail="原规则：余2"/><Arrow x1={790} y1={671} x2={1130} y2={671} color={C.gold}/><Cache x={1300} y={671} id="A" detail="新规则：余0"/></g><g opacity={progress(f,b+8,b+28)}><SampleTable s={s} f={f}/></g></>;break;
  case 'miss':content=<Miss s={s} f={f}/>;break;
  case 'goal':content=<Goal s={s} f={f}/>;break;
  case 'ring':content=<RingSetup s={s} f={f}/>;break;
  case 'lookup':content=<Lookup s={s} f={f}/>;break;
  case 'wrap':content=<Lookup s={s} f={f} wrap/>;break;
  case 'insert':content=<Insert s={s} f={f}/>;note='键的哈希坐标不变；改变的是负责它的节点';break;
  case 'local':content=<SampleTable s={s} f={f} mode="ring"/>;note=f<b?'本例：取余规则8/10改去向；哈希环2/10改去向':'只有归属变化；数据迁移和切换仍需另行安排';break;
  case 'imbalance':content=<Imbalance s={s} f={f}/>;note=f<(labels['虚拟节点']??Math.max(1,b-2))?'编号空间长度不同，不代表请求量不同':'区间长度不是请求热度；虚拟节点不承诺完全平均';break;
  case 'vnodes':content=<VNodes s={s} f={f}/>;note='另一套预先配置的示例；同色位置始终属于同一物理缓存';break;
  case 'recap':content=<Recap s={s} f={f}/>;note='一致性哈希的“一致性”，不是数据强一致性或共识';break;
  default:throw Error('Unknown scene '+type);
 }
 return <><Head chapter={chapter} title={title} sub={sub}/>{content}<Note>{note}</Note><g data-visual-state={JSON.stringify({type,frame:f,phase:{a,b,p,q},nodesBefore:M.nodesBefore,nodesAfter:M.nodesAfter})}/></>;
};
const ShotView=({s,hideSubtitles=false,auditLayout=false}:any)=>{
 const f=useCurrentFrame();useLayoutAudit(auditLayout,'main',s.from+f);
 const caption=(s.subtitles??[]).find((c:any)=>f>=c.from&&f<(c.to!==undefined?c.to+1:c.from+(c.duration??0)));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <svg data-audit-scene="true" viewBox="0 0 1920 1080" width={1920} height={1080}><Scene s={s} f={f}/></svg>
  {!hideSubtitles&&caption&&<div data-subtitle="true" style={{position:'absolute',left:115,right:115,bottom:49,textAlign:'center',fontFamily:FONT,fontSize:31,lineHeight:1.45,color:C.text}}>{caption.text}</div>}
 </AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:{hideSubtitles?:boolean;auditLayout?:boolean})=><AbsoluteFill style={{background:C.bg}}>
 {__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}
</AbsoluteFill>;
