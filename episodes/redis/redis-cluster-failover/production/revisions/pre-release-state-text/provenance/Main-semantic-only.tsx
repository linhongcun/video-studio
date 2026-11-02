import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {RedisHeader,RedisBackdrop} from '../../../../../_shared/redis-video/Frame';
import {C,FONT,MONO} from '../../../../../_shared/redis-video/theme';
import {createMiddlewareIdentity} from '../../../../../_shared/middleware-identity';
import {shots,Shot,PREVOICE} from './data';
import source from '../../model.json';
declare const __HAS_VOICE_AUDIO__:boolean;
const Mark=createMiddlewareIdentity(React),M=source as any;
const clip=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(f:number,a:number,b:number)=>{const v=clip((f-a)/Math.max(1,b-a));return v*v*(3-2*v);};
const state=(id:string)=>{const s=M.timeline.find((q:any)=>q.id===id);if(!s)throw Error('Missing model '+id);return s;};
type Step={at:number;id:string};type Flight={kind:string;from:string;to:string;start:number;end:number;label:string};
export function sceneTiming(s:Shot){
 const d=s.durationInFrames,a=s.voice?.[0]?.localStart??10,b=s.voice?.[0]?.localEnd??d*.44,c=s.voice?.[1]?.localStart??d*.51,e=s.voice?.[1]?.localEnd??d-30;
 const early=(p:number)=>a+(b-a)*p,late=(p:number)=>c+(e-c)*p,n=Number(s.id),steps:Step[]=[],flights:Flight[]=[];
 const put=(at:number,id:string)=>steps.push({at,id}),fly=(kind:string,from:string,to:string,start:number,end:number,label:string)=>flights.push({kind,from,to,start,end,label});
 if(n===1)put(0,'offline');
 if(n===2)put(0,'normal');
 if(n===3){put(0,'offline');fly('probe','B','A',early(.10),early(.62),'乙发出探测，甲未回复');put(late(.18),'pfail');}
 if(n===4){put(0,'pfail');fly('report','C','B',early(.20),early(.80),'丙 → 乙：有效期内的故障报告');put(late(.40),'fail');fly('failure','B','A1',late(.49),late(.88),'传播确认故障 FAIL');}
 if(n===5)put(0,'eligible');
 if(n===6){put(0,'eligible');put(early(.27),'request');fly('request','A1','B',early(.36),early(.77),'甲副本请求授权 · 轮次6');fly('request','A1','C',early(.50),late(.12),'甲副本请求授权 · 轮次6');}
 if(n===7){put(0,'request');fly('vote','B','A1',late(.12),late(.61),'乙 → 甲副本：本轮授权');put(late(.61),'vote-b');}
 if(n===8){put(0,'vote-b');fly('vote','C','A1',early(.08),early(.66),'丙 → 甲副本：本轮授权');put(early(.66),'vote-bc');}
 if(n===9){put(0,'vote-bc');put(early(.18),'promoted');fly('announce','A1','B',late(.10),late(.42),'新主公布槽归属 · 配置轮次6');put(late(.42),'announced-b');fly('announce','A1','C',late(.19),late(.68),'新主公布槽归属 · 配置轮次6');put(late(.68),'announced-bc');}
 if(n===10){put(0,'minority-reset');put(early(.45),'minority-request');fly('vote','B','A1',late(.09),late(.47),'乙 → 甲副本：本轮授权');put(late(.47),'minority-one');}
 if(n===11)put(0,'success-return');
 if(n===12)put(0,'summary');
 return {a,b,c,e,steps,flights,early,late};
}
export function stateAt(s:Shot,f:number){return [...sceneTiming(s).steps].reverse().find(q=>f>=q.at)?.id??'normal';}
type Txt={x:number;y:number;w:number;size?:number;color?:string;align?:'start'|'middle'|'end';alpha?:number;mono?:boolean;children:React.ReactNode};
const T:React.FC<Txt>=({x,y,w,size=28,color=C.text,align='start',alpha=1,mono=false,children})=>{
 const ref=useRef<SVGTextElement>(null);useLayoutEffect(()=>{const el=ref.current;if(el&&alpha>.1&&el.getComputedTextLength()>w+2)console.error('COPYFIT',el.textContent,el.getComputedTextLength(),w);});
 return <text ref={ref}data-text data-copyfit data-width={w}x={x}y={y}fontSize={size}fontFamily={mono?MONO:FONT}fontWeight={600}textAnchor={align}fill={color}opacity={alpha}>{children}</text>;
};
const line=(points:number[][])=>points.map((p,i)=>(i?'L':'M')+p.join(' ')).join(' ');
const position=(points:number[][],p:number)=>{const ds=points.slice(1).map((q,i)=>Math.hypot(q[0]-points[i][0],q[1]-points[i][1]));let dist=clip(p)*ds.reduce((a,b)=>a+b,0);for(let i=0;i<ds.length;i++){if(dist<=ds[i]||i===ds.length-1){const q=dist/Math.max(ds[i],1);return [points[i][0]+(points[i+1][0]-points[i][0])*q,points[i][1]+(points[i+1][1]-points[i][1])*q];}dist-=ds[i];}return points[0];};
const NAMES:Record<string,string>={A:'主节点甲',B:'主节点乙',C:'主节点丙',A1:'甲的副本',B1:'乙的副本',C1:'丙的副本'};
const XY:Record<string,number[]>={A:[360,415],B:[960,415],C:[1560,415],A1:[360,720],B1:[960,720],C1:[1560,720]};
function route(from:string,to:string){
 if(from==='B'&&to==='A')return [[895,415],[720,415],[720,365],[620,365],[620,415],[425,415]];
 if(from==='C'&&to==='B')return [[1495,415],[1320,415],[1320,365],[1200,365],[1200,415],[1025,415]];
 const master=from==='A1'?to:from,offset=master==='C'?1320:1200,x=XY[master][0],masterEdge=master==='C'?x-65:x+65;
 const path=[[masterEdge,415],[offset,415],[offset,595],[620,595],[620,720],[425,720]];
 return from==='A1'?[...path].reverse():path;
}
const Motion:React.FC<{q:Flight;f:number}>=({q,f})=>{
 if(f<q.start||f>=q.end)return null;const pts=route(q.from,q.to),p=position(pts,ease(f,q.start,q.end)),dash=q.kind==='report'||q.kind==='failure';
 return <g data-flight={q.kind}data-from={q.from}data-to={q.to}><path d={line(pts)}fill="none"stroke={q.kind==='probe'?C.muted:C.red}strokeWidth={dash?2:4}strokeDasharray={dash?'9 8':undefined}opacity={.9}/><circle data-moving-body={q.kind}cx={p[0]}cy={p[1]}r={q.kind==='vote'?13:9}fill={q.kind==='vote'?C.red:C.surface}stroke={C.red}strokeWidth={3}/></g>;
};
const Node:React.FC<{id:string;v:any;alpha?:number;focus?:boolean;status?:string}>=({id,v,alpha=1,focus=false,status})=>{
 const [x,y]=XY[id],available=v.reachable.includes(id),promoted=id==='A1'&&v.candidateRole==='master',name=promoted?'甲的副本 → 新主':NAMES[id],color=available?focus?C.red:C.text:C.muted;
 return <g data-node={id}data-role={promoted?'master':id.length===1?'master':'replica'}data-reachable={String(available)}opacity={alpha}>
 <circle cx={x}cy={y}r={63}fill={available?C.surface:C.edge}stroke={color}strokeWidth={focus?5:2}/>
 <foreignObject x={x-29}y={y-29}width={58}height={58}><div style={{opacity:available?1:.3}}><Mark kind="redis"size={58}/></div></foreignObject>
 {!available&&<path d={`M${x-46} ${y-46}L${x+46} ${y+46}M${x+46} ${y-46}L${x-46} ${y+46}`}fill="none"stroke={C.muted}strokeWidth={5}/>}
 <T x={x}y={y+101}w={460}size={30}align="middle"color={color}>{name}</T>
 {status&&<T x={x}y={y+140}w={460}size={23}align="middle"color={color}>{status}</T>}
 </g>;
};
const Panel:React.FC<{x:number;y:number;w:number;h:number;children:React.ReactNode;red?:boolean}>=({x,y,w,h,children,red=false})=><g><rect x={x}y={y}width={w}height={h}rx={18}fill={C.surface}stroke={red?C.red:C.edge}strokeWidth={red?3:2}/>{children}</g>;
const Scene:React.FC<{s:Shot}>=({s})=>{
 const f=useCurrentFrame(),n=Number(s.id),tm=sceneTiming(s),v=state(stateAt(s,f)),focus=n>=5?'A1':n===3?'B':n===4?'B':'A',late=ease(f,tm.c,tm.c+25),minority=n===10,boundary=n===11,recap=n===12;
 const titles:Record<number,string>={1:'旧主失联，副本为什么还不能直接接管？',2:'先认清：三个持槽主节点，各有自己的副本',3:'一次超时，只能先形成自己的怀疑',4:v.failure==='FAIL'?'多数近期故障判断已汇合，再传播确认结果':'还要收集其他主节点的近期故障报告',5:'确认旧主故障后，副本先检查参选条件',6:'副本提高选举轮次，再请求主节点授权',7:v.votes.length?'乙的一票已抵达，副本仍不能晋升':'谁能投票，要先看主节点资格',8:v.authorized?'第二票抵达，才获得接管授权':'还在等丙的本轮授权回复',9:v.views.C==='A1'?'新槽归属已经传播到其他节点':'获得授权后，提升并公布新的槽归属',10:'独立对照：本次只有一位主节点能回复',11:'授权接管，不能补出尚未复制的写入',12:'把故障判断、授权和槽归属连起来'};
 const chapter=n<=4?'确认故障':n<=8?'请求授权':n<=10?'接管槽':'授权边界';
 const tag=n===2?'故障前拓扑 · 示例槽范围；不是一致性哈希环':minority?'重新从参选前开始 · 旧主FAIL已知；这次丙在投票时不可达':boundary?'回到前面成功分支 · 复制数据与接管资格分别解释':'正常自动故障转移 · 三主三副本教学示例 · 非实测轮次与时延';
 const slotProgress=n<9?0:n===9?ease(f,tm.early(.23),tm.early(.78)):minority?0:1;
 const badgeY=slotProgress<.5?285:590,badgeAlpha=slotProgress===0||slotProgress===1?1:slotProgress<.2?1-slotProgress/.2:slotProgress>.8?(slotProgress-.8)/.2:0;
 const marker=position([[130,316],[85,316],[85,621],[130,621]],slotProgress);
 return <g data-model-state={v.id}data-election-epoch={v.electionEpoch}data-config-epoch={v.configEpoch}data-votes={JSON.stringify(v.votes)}data-slot-owner={v.slotOwner}data-candidate-role={v.candidateRole}>
 <RedisHeader ep={51}title="Cluster"chapter={chapter}/><T x={115}y={185}w={1690}size={43}>{titles[n]}</T><T x={115}y={237}w={1690}size={25}color={C.muted}>{tag}</T>
 <g opacity={boundary?0:1}>
 {['B','C'].map((id,i)=><g key={id}><rect x={730+i*600}y={285}width={460}height={63}rx={12}fill={C.surface}stroke={C.edge}strokeWidth={2}/><T x={960+i*600}y={326}w={430}size={26}align="middle"mono>槽 {i===0?'5461–10922':'10923–16383'}</T></g>)}
 </g>
 <g data-slot-badge="A"data-slot-owner-visual={slotProgress===1?'A1':slotProgress===0?'A':'moving'}transform={`translate(0 ${badgeY-285})`}opacity={badgeAlpha}>
 <rect x={130}y={285}width={460}height={63}rx={12}fill={C.redSoft}stroke={C.red}strokeWidth={2}/><T x={360}y={326}w={430}size={26}align="middle"mono>槽 0–5460</T></g>
 {(slotProgress>0&&slotProgress<1)&&<g><path d="M130 316H85V621H130"fill="none"stroke={C.red}strokeWidth={2}strokeDasharray="8 6"/><circle data-moving-body="slot-owner-change"cx={marker[0]}cy={marker[1]}r={11}fill={C.red}/></g>}
 {(n<=2)&&(n===1?['A']:['A','B','C']).map(id=>{const[x]=XY[id];return <path key={id}d={`M${x-64} 415H${x-100}V720H${x-64}`}fill="none"stroke={C.link}strokeWidth={2}/>;})}
 <Node id="A"v={v}focus={focus==='A'}status={n===2?'原来持有槽0–5460':v.failure==='PFAIL'?'旧主失联 · 还只是本地怀疑':'旧主失联'}/>
 <Node id="B"v={v}focus={focus==='B'}alpha={boundary?0:1}status={n>=7&&!minority&&v.votes.includes('B')?'本轮已授权':'持槽主节点 · 有投票资格'}/>
 <Node id="C"v={v}alpha={boundary?0:1}status={minority?'本次不可达':n>=8&&v.votes.includes('C')?'本轮已授权':'持槽主节点 · 有投票资格'}/>
 <Node id="A1"v={v}focus={focus==='A1'}status={v.candidateRole==='master'?'接管甲原来的槽':n>=6?'候选副本 · 没有自票':'复制甲的数据'}/>
 {n===2&&<><Node id="B1"v={v}status="只复制乙的数据"/><Node id="C1"v={v}status="只复制丙的数据"/></>}
 {(n===3||n===4)&&<Panel x={730}y={655}w={1060}h={206}red={v.failure==='FAIL'}><T x={765}y={704}w={990}size={30}color={C.red}>{n===3?'乙的本地视图':'故障报告阶段 · 不是授权选票'}</T><T x={765}y={763}w={990}size={36}>{v.failure==='FAIL'?'乙判断 + 丙近期报告 = 多数确认':n===3&&v.failure!=='PFAIL'?'等待甲的有效回复':'甲：疑似故障 PFAIL'}</T><T x={765}y={818}w={990}size={25}color={C.muted}>{v.failure==='FAIL'?'确认故障 FAIL 已形成，向可达节点传播':n===3&&v.failure!=='PFAIL'?'尚未形成疑似故障':'本地疑似状态不能直接触发晋升'}</T></Panel>}
 {n===5&&<Panel x={730}y={655}w={1060}h={206}><T x={765}y={701}w={990}size={30}color={C.red}>合格副本，再安排尝试时间</T>{['旧主已FAIL且原来持有槽','复制断连时间在允许范围内','短暂等待；多个副本时，进度影响先后'].map((t,i)=><T key={t}x={765}y={748+i*40}w={990}size={26}alpha={i===0?1:i===1?ease(f,tm.early(.30),tm.early(.40)):late}>{'✓ '+t}</T>)}</Panel>}
 {(n>=6&&n<=10)&&<Panel x={730}y={655}w={1060}h={206}red={v.authorized}>
 <T x={765}y={703}w={990}size={29}color={C.red}>{n===9?(v.candidateRole==='master'?'新主公布配置轮次6的槽归属':'多数授权已满足，准备提升并公布槽归属'):`选举轮次 ${v.electionEpoch} · 三个持槽主节点，需要2票`}</T>
 <T x={765}y={770}w={990}size={45}color={C.text}>{n===9?`乙的槽表：${v.views.B==='A1'?'新主':'旧主'}　丙的槽表：${v.views.C==='A1'?'新主':'旧主'}`:`已抵达的本轮授权：${v.votes.length} / 2`}</T>
 <T x={765}y={824}w={990}size={26}color={C.muted}>{n===9?(v.candidateRole==='master'?'本地已接管；公告抵达后，对方才更新槽表':'随后提升、接管，再发布新槽归属'):v.authorized?'多数授权已满足，随后才能提升与接管':minority?'一位主节点 + 一个副本，仍只有一张主节点选票':'甲离线不改变原分母；旧轮次回复不混入本轮'}</T>
 </Panel>}
 {n===11&&<>
 <Panel x={730}y={340}w={1060}h={214}><T x={765}y={389}w={990}size={30}color={C.muted}>离线旧主的数据</T><T x={765}y={446}w={990}size={31}>已复制记录1　│　末条写入2已确认</T><T x={765}y={507}w={990}size={27}color={C.red}>写入2尚未到达副本，旧主字节仍保留</T></Panel>
 <Panel x={730}y={655}w={1060}h={206}red><T x={765}y={704}w={990}size={30}color={C.red}>新主实际拥有的数据</T><T x={765}y={763}w={990}size={34}>已复制记录1　│　写入2缺失</T><T x={765}y={820}w={990}size={27}color={C.muted}>多数授权不能凭空补齐尚未复制的数据</T></Panel></>}
 {recap&&<Panel x={730}y={655}w={1060}h={206}><T x={765}y={705}w={990}size={33}color={C.red}>故障报告 → 主节点授权 → 新槽归属</T><T x={765}y={768}w={990}size={31}>先确认旧主故障，再给副本接管资格</T><T x={765}y={824}w={990}size={26}color={C.muted}>选票够了才晋升；异步复制仍有数据丢失边界</T></Panel>}
 {tm.flights.map((q,i)=><Motion key={i}q={q}f={f}/>)}
 {tm.flights.some(q=>f>=q.start&&f<q.end)&&<T x={730}y={642}w={1060}size={25}color={C.red}>{tm.flights.find(q=>f>=q.start&&f<q.end)?.label}</T>}
 {n===1&&<T x={730}y={751}w={1050}size={44}color={C.red}alpha={late}>还没有接管资格：为什么？</T>}
 {recap&&<T x={1805}y={898}w={400}size={27}align="end"color={C.muted}>IT小村 · 原创</T>}
 </g>;
};
const ShotView:React.FC<{s:Shot;captions:boolean}>=({s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));
 return <AbsoluteFill data-shot={s.id}data-prevoice={String(PREVOICE)}style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><svg width={1920}height={1080}><RedisBackdrop/><Scene s={s}/></svg>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:110,right:110,top:929,height:108,padding:'0 20px',boxSizing:'border-box',display:'flex',alignItems:'center',justifyContent:'center',fontSize:37,lineHeight:1.4,textAlign:'center',background:C.bg+'F5',borderRadius:14}}>{sub.text}</div>}</AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id}from={s.from}durationInFrames={s.durationInFrames}><ShotView s={s}captions={showSubtitles&&!hideSubtitles}/></Sequence>)}</AbsoluteFill>;
