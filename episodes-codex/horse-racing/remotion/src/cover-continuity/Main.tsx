import React from 'react';
import {PuzzleCanvas} from '../../../../_shared/puzzles-video/Frame';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {GROUPS,HORSES,Shot,shots} from '../data';
import {C,FONT} from './theme';
import {useLayoutAudit} from '../LayoutAudit';
import {Arrow,Board,CHAMPIONS,FINALISTS,FasterProof,Head,Node,Note,RETAINED,T,across,at,clamp,ease,mix,nodeXY,phase,steps} from './primitives';
declare const __HAS_VOICE_AUDIO__:boolean;

const alphaStage=(stage:number)=>Object.fromEntries(HORSES.map(h=>[h.id,
 (stage>=1&&h.col>=3)||(stage>=2&&h.row>=3)||(stage>=3&&h.row===2&&h.col>=1)||(stage>=4&&h.row===1&&h.col>=2)?.14:1]));
const lerpMap=(a:Record<string,number>,b:Record<string,number>,p:number)=>Object.fromEntries(HORSES.map(h=>[h.id,mix(a[h.id]??1,b[h.id]??1,p)]));
const colorMap=(ids:string[],color:string)=>Object.fromEntries(ids.map(id=>[id,color]));
const flag=(p:number,a=0,b=1)=>clamp((p-a)/Math.max(.0001,b-a));
const champPositions=Object.fromEntries(CHAMPIONS.map((id,i)=>[id,{x:1540,y:360+i*103}]));
const finalSource=Object.fromEntries(FINALISTS.map((id,i)=>[id,{x:840,y:360+i*103}]));
const finalOrder=['甲2','乙1','乙2','甲3','丙1'];
const finalResult=Object.fromEntries(finalOrder.map((id,i)=>[id,{x:1330,y:360+i*103}]));
const championSeat={x:360,y:350};
const podiumPositions:Record<string,{x:number;y:number}>={'甲1':championSeat,'甲2':{x:900,y:350},'乙1':{x:1440,y:350}};
const blendPositions=(from:Record<string,{x:number;y:number}>,to:Record<string,{x:number;y:number}>,p:number)=>Object.fromEntries(HORSES.map(h=>{
 const a=from[h.id]??nodeXY(h.id),b=to[h.id]??nodeXY(h.id);return[h.id,{x:mix(a.x,b.x,p),y:mix(a.y,b.y,p)}];
}));
const ActualFirst=({alpha=1,x=360,y=282}:any)=><g opacity={alpha}><T x={x} y={y} size={31} color={C.teal} anchor="middle" weight={750}>已确定 · 总第一</T></g>;
const Count=({value,alpha=1}:any)=><g opacity={alpha}><T x={1578} y={856} size={28} color={C.muted} anchor="middle">仍可能进入前三：<tspan fill={C.gold}>{value}</tspan> 匹</T></g>;
const CompareLabel=({x=1578,y=291,children='本场名次',alpha=1}:any)=><T x={x} y={y} size={26} color={C.muted} anchor="middle" alpha={alpha}>{children}</T>;
const ProofRelations=({names,target,reveal=3,positions={}}:any)=><g>{names.map((name:string,i:number)=>{
 const start=positions[name]??nodeXY(name),end=positions[target]??nodeXY(target),horizontal=Math.abs(start.y-end.y)<3;
 return <Arrow key={name} from={start} to={end} color={C.gold} progress={clamp(reveal-i)} curve={horizontal?-75-i*18:-(i+1)*25} alpha={clamp(reveal-i)} width={3.5}/>;
})}</g>;
const rankLabels=(ids:string[],positions:Record<string,{x:number;y:number}>,revealed:number)=>ids.map((id,i)=><T key={id} x={(positions[id]??nodeXY(id)).x+160} y={(positions[id]??nodeXY(id)).y+11} size={28} color={i<2?C.gold:C.muted} alpha={clamp(revealed-i)}>第{i+1}名</T>);

const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 if(t==='hook'){
  const take=phase(s,f,0,.13,.88),positions:Record<string,{x:number;y:number}>={};
  HORSES.forEach(h=>{positions[h.id]={x:340+h.col*170,y:355+h.row*98};});
  return <><Head title="25匹马，怎样找出总前三？" sub="每场最多5匹 · 找出全部马里的第一、第二、第三名"/>
   {[0,1,2,3,4].map(i=><g key={i}><path d={`M 1260 ${355+i*86} H 1730`} stroke={C.edge} strokeWidth={2}/><circle cx={1340} cy={355+i*86} r={14} fill={C.gold} opacity={clamp(take*5-i)}/><T x={1765} y={363+i*86} size={23} color={C.muted}>{i+1}</T></g>)}
   <T x={1490} y={298} size={27} color={C.muted} anchor="middle">一次，最多比较5匹</T>
   <Board named={false} rankHeaders={false} groupLabels={false} positions={positions} colors={colorMap(CHAMPIONS,C.text)}/>
   <g>{['总第一','总第二','总第三'].map((label,i)=><g key={label}><rect x={1235+i*185} y={803} width={160} height={64} rx={14} fill="none" stroke={C.gold+'88'} strokeDasharray="8 7"/><T x={1315+i*185} y={845} size={27} color={C.gold} anchor="middle">{label}？</T></g>)}</g>
  </>;
 }
 if(t==='rules'){
  const ids=['03','01','05','02','04'],result=['01','02','03','04','05'],progress=phase(s,f,1,.02,.86),z=steps(progress,5);
  return <><Head kicker="规则示意 · 正式赛程接下来开始" title="每场只知道先后，不能计时" sub="速度固定 · 没有并列 · 不知道跨场用时"/>
   <CompareLabel x={610} y={303}>参赛的5匹 · 示例</CompareLabel><CompareLabel x={1250} y={303}>本场名次</CompareLabel>
   {ids.map((id,i)=>{const rank=result.indexOf(id),move=rank<z.index?1:rank===z.index?z.progress:0,start={x:610,y:365+i*99},end={x:1250,y:365+rank*99};const xx=move<.25?mix(start.x,900,ease(move/.25)):move<.65?900:mix(900,end.x,ease((move-.65)/.35)),yy=move<.25?start.y:move<.65?mix(start.y,end.y,ease((move-.25)/.4)):end.y;return <Node key={id} id={'rule-'+id} label={id} x={xx} y={yy} color={move===1?C.teal:C.text}/>;})}
   {result.map((id,i)=><T key={id} x={1450} y={376+i*99} size={30} color={C.teal} alpha={clamp(progress*5-i)}>第{i+1}名</T>)}
   <Note color={C.gold}>只能比较先后，不能比较“快了多少秒”</Note>
  </>;
 }
 if(t==='groups'){
  const demo=phase(s,f,0,.05,.95),sort=phase(s,f,1,.01,.92),z=steps(sort,4),knownRows=(demo>=.5?1:0)+(sort===1?4:z.index+(z.progress>.95?1:0)),positions:Record<string,{x:number;y:number}>={},scales:Record<string,number>={};
  const order=[2,0,4,1,3],firstOut=ease(flag(demo,.1,.4)),firstBack=ease(flag(demo,.6,.9)),firstScale=demo<.1?mix(1,.7,flag(demo,0,.1)):demo>.9?mix(.7,1,flag(demo,.9,1)):.7;
  HORSES.forEach(h=>{if(h.row===0){const origin={x:420+order.indexOf(h.col)*180,y:360},away={x:1540,y:360+h.col*103},sorted=nodeXY(h.id);positions[h.id]=demo<.6?{x:mix(origin.x,away.x,firstOut),y:mix(origin.y,away.y,firstOut)}:{x:mix(away.x,sorted.x,firstBack),y:mix(away.y,sorted.y,firstBack)};scales[h.id]=firstScale;}else positions[h.id]=nodeXY(h.id);});
  const context=demo<.1?1-ease(flag(demo,0,.1)):demo>.9?ease(flag(demo,.9,1)):0,alpha=Object.fromEntries(HORSES.map(h=>[h.id,h.row===0?1:context]));
  const activeGroup=sort>0?GROUPS[z.index+1]:'甲',activeNames=Array.from({length:5},(_,i)=>activeGroup+(i+1));
  return <><Head title="先分五组，各跑一场" sub="甲、乙、丙、丁、戊 · 每行5匹，先排好组内顺序"/>
   {sort>0&&[0,1,2,3].map(i=><Arrow key={i} from={nodeXY(activeNames[i])} to={nodeXY(activeNames[i+1])} color={C.gold} progress={clamp(z.progress*4-i)} width={3}/>)}
   <Board named={true} knownRows={knownRows} positions={positions} scales={scales} alpha={alpha} colors={colorMap(activeNames,C.gold)} rankHeaders={demo>=.9}/>
   {GROUPS.map((g,i)=><T key={g} x={1285} y={372+i*103} size={23} color={i<knownRows?C.teal:C.muted} alpha={demo>=.9?1:0}>{i<knownRows?'已完成':'待比较'}</T>)}
   {demo>.4&&demo<.6&&<g><CompareLabel x={1650}>甲组本场名次</CompareLabel>{Array.from({length:5},(_,i)=><T key={i} x={1680} y={371+i*103} size={25} color={C.gold}>第{i+1}</T>)}</g>}
   <g opacity={demo>.9?1:0}><T x={1578} y={430} size={29} color={C.muted} anchor="middle">已完成</T><T x={1578} y={565} size={104} color={C.gold} anchor="middle" weight={760}>{sort===1?5:knownRows}</T><T x={1578} y={625} size={32} color={C.muted} anchor="middle">场分组赛</T></g>
   <Note>各组赛后按名次排列：左快右慢；未完成的行尚未比较</Note>
  </>;
 }
 if(t==='local-ranks'){
  const focus=phase(s,f,0,.05,.65),second=phase(s,f,1,.03,.7),alpha=Object.fromEntries(HORSES.map(h=>[h.id,lerpMap({},Object.fromEntries(HORSES.map(x=>[x.id,['甲1','甲2','甲3','乙1'].includes(x.id)?1:.2])),focus)[h.id]]));
  return <><Head title="组内第二，不等于总第二" sub="甲2 = 甲组第2名；乙1 = 乙组第1名"/>
   <Board alpha={alpha} colors={{甲2:C.gold,乙1:C.blue}}/>
   <g opacity={second}><rect x={1350} y={359} width={440} height={269} rx={20} fill={C.surface} stroke={C.edge}/><T x={1570} y={421} anchor="middle" size={31} color={C.gold}>甲2</T><T x={1570} y={497} anchor="middle" size={39}>谁更快？</T><T x={1570} y={574} anchor="middle" size={31} color={C.blue}>乙1</T></g>
   <Note color={C.gold}>跨组尚未比较，暂时不能确定</Note>
  </>;
 }
 if(t==='within-eliminate'){
  const firstReveal=phase(s,f,0,.05,.72)*3,firstFade=phase(s,f,0,.78,.98),rest=phase(s,f,1,.05,.89),z=steps(rest,4),activeGroup=rest===0?'甲':GROUPS[z.index+1],activeReveal=rest===0?firstReveal:z.progress*3,fade=rest===0?firstFade:z.progress>.92?1:0;
  const alpha=Object.fromEntries(HORSES.map(h=>[h.id,h.col<3?1:h.row===0?mix(1,.14,firstFade):h.row<z.index+1&&rest>0?.14:h.row===z.index+1&&rest>0?mix(1,.14,flag(z.progress,.92,1)):1]));
  const names=[1,2,3].map(n=>activeGroup+n),target=activeGroup+'4',colors={...colorMap(names.slice(0,Math.ceil(activeReveal)),C.gold),[target]:C.red};
  return <><Head title="有三匹确定更快，就进不了前三" sub="先看同组第4名，再将相同依据用于各组后两名"/>
   <ProofRelations names={names} target={target} reveal={activeReveal}/><Board alpha={alpha} colors={colors}/>
   <FasterProof names={names} target={target} reveal={activeReveal} conclusion={fade>.9}/>
   <Count value={rest===1?15:25-Math.round(firstFade)*2-(rest>0?z.index*2+Math.round(flag(z.progress,.92,1))*2:0)} alpha={rest===1?1:0}/>
   <Note color={C.gold}>{rest===1?'每组留下前3名，暂时还有15匹':'先显示三个更快者，再排除后面的马'}</Note>
  </>;
 }
 if(t==='champion-race'){
  const move=phase(s,f,1,.04,.86),travel=ease(flag(move,.18,.82)),positions=blendPositions({},champPositions,travel),context=move<.18?1-ease(flag(move,0,.18)):move>.82?ease(flag(move,.82,1))*.13:0,alpha=Object.fromEntries(HORSES.map(h=>[h.id,CHAMPIONS.includes(h.id)?1:move<.18?alphaStage(1)[h.id]*context:context]));
  return <><Head title="组内排好了，接着比较组冠军" sub="第六场：只请每组第1名参赛"/>
   {CHAMPIONS.map(id=>{const xy=nodeXY(id);return <rect key={id} x={xy.x-65} y={xy.y-35} width={130} height={70} rx={14} fill="none" stroke={C.edge} strokeDasharray="5 7" opacity={move}/>;})}
   <Board alpha={alpha} positions={positions} colors={colorMap(CHAMPIONS,C.gold)}/>
   <CompareLabel alpha={move}>第六场 · 5个组冠军</CompareLabel>
   <Note color={C.gold}>组内最快的马，第一次放在一起比较</Note>
  </>;
 }
 if(t==='champion-order'){
  const reveal=phase(s,f,0,.03,.9)*5,prove=phase(s,f,1,.04,.82),alpha=Object.fromEntries(HORSES.map(h=>[h.id,CHAMPIONS.includes(h.id)?1:.13]));
  return <><Head title="第六场：五个组冠军排出顺序" sub="教学示例结果 · 这不是全部马的总前三"/>
   <g opacity={prove}>{CHAMPIONS.slice(1).map(id=><Arrow key={id} from={champPositions['甲1']} to={champPositions[id]} color={C.teal} width={3} alpha={.7} curve={20}/>)}{HORSES.filter(h=>h.col>0&&h.col<3).map(h=><Arrow key={h.id} from={champPositions[h.group+'1']} to={nodeXY(h.id)} color={C.teal} progress={prove} width={2} alpha={.32}/>)}</g>
   <Board alpha={alpha} positions={champPositions} colors={{...colorMap(CHAMPIONS,C.gold),甲1:prove>.5?C.teal:C.gold}}/>
   <CompareLabel>第六场 · 本场名次</CompareLabel>{rankLabels(CHAMPIONS,champPositions,reveal)}
   <g opacity={prove}><T x={430} y={850} size={32} color={C.teal}>甲1 比其他组冠军快，也比各组其余马快</T><T x={1540} y={313} size={27} color={C.teal} anchor="middle">确定总第一</T></g>
  </>;
 }
 if(t==='not-podium'){
  const move=phase(s,f,0,.13,.45),context=1-phase(s,f,0,.0,.12),target={'甲1':{x:960,y:390},'甲2':{x:590,y:650},'乙1':{x:1330,y:650}},positions=blendPositions(champPositions,target,move),alpha=Object.fromEntries(HORSES.map(h=>[h.id,['甲1','甲2','乙1'].includes(h.id)?1:(CHAMPIONS.includes(h.id)?1:.13)*context]));
  return <><Head title="乙组冠军，还不能直接算总第二" sub="甲2和乙1都慢于甲1，但它们彼此还没有比较"/>
   <g opacity={move}><Arrow from={target['甲1']} to={target['甲2']} color={C.teal} progress={move}/><Arrow from={target['甲1']} to={target['乙1']} color={C.teal} progress={move}/><path d="M 700 650 H 1220" fill="none" stroke={C.gold} strokeWidth={3} strokeDasharray="10 12"/><rect x={850} y={616} width={220} height={65} fill={C.bg}/><T x={960} y={662} size={35} color={C.gold} anchor="middle">待比较</T><T x={960} y={315} size={30} color={C.teal} anchor="middle">已确定总第一</T></g>
   <Board positions={positions} alpha={alpha} colors={{甲1:C.teal,甲2:C.gold,乙1:C.gold}} rankHeaders={false} groupLabels={false}/>
   <g opacity={move}><T x={590} y={745} size={29} color={C.muted} anchor="middle">甲组第2名</T><T x={1330} y={745} size={29} color={C.muted} anchor="middle">乙组第1名</T></g><Note color={C.gold}>仅凭组冠军赛，不能把亚军和季军定下来</Note>
  </>;
 }
 if(t==='drop-de'){
  const reset=phase(s,f,0,.01,.18),context=phase(s,f,0,.22,.36),from={'甲1':{x:960,y:390},'甲2':{x:590,y:650},'乙1':{x:1330,y:650}},positions=blendPositions(from,{},reset),names=['甲1','乙1','丙1'];
  const reveal=phase(s,f,1,.01,.53)*3,dFade=phase(s,f,1,.54,.68),eReveal=phase(s,f,1,.69,.84)*3,eFade=phase(s,f,1,.86,.98),target=eReveal>0?'戊1':'丁1',shown=eReveal>0?eReveal:reveal;
  const alpha=Object.fromEntries(HORSES.map(h=>[h.id,(h.col>=3?.14:h.row===3?mix(1,.14,dFade):h.row===4?mix(1,.14,eFade):1)*(['甲1','甲2','乙1'].includes(h.id)?1:context)]));
  return <><Head title="回到五组：继续排除不可能的马" sub="先看丁组冠军，再将同样的依据用于戊组"/>
   <g opacity={reset}><ProofRelations names={names} target={target} reveal={shown}/></g><Board positions={positions} alpha={alpha} colors={{...colorMap(names.slice(0,Math.ceil(shown)),C.gold),[target]:C.red}} rankHeaders={reset>.5} groupLabels={reset>.5}/>
   <FasterProof names={names} target={target} reveal={shown} alpha={reset} conclusion={target==='戊1'?eFade>.5:dFade>.5}/>
   <Count value={9} alpha={eFade}/><Note color={C.gold}>连组内最快的都无缘前三，同组更慢者也可以排除</Note>
  </>;
 }
 if(t==='drop-c'){
  const names=['甲1','乙1','丙1'],target='丙2',reveal=phase(s,f,1,.01,.72)*3,fade=phase(s,f,1,.78,.96),alpha=lerpMap(alphaStage(2),alphaStage(3),fade);
  return <><Head title="丙组第二，前面也有三匹更快" sub="甲组冠军 → 乙组冠军 → 丙组冠军 → 丙组第二"/>
   <ProofRelations names={names} target={target} reveal={reveal}/><Board alpha={alpha} colors={{...colorMap(names.slice(0,Math.ceil(reveal)),C.gold),丙2:C.red}}/>
   <FasterProof names={names} target={target} reveal={reveal} conclusion={fade>.5}/><Count value={7} alpha={fade}/><Note color={C.gold}>丙组只需留下第1名</Note>
  </>;
 }
 if(t==='drop-b'){
  const names=['甲1','乙1','乙2'],target='乙3',reveal=phase(s,f,0,.02,.92)*3,fade=phase(s,f,1,.52,.92),alpha=lerpMap(alphaStage(3),alphaStage(4),fade);
  return <><Head title="乙组第三，也已经有三匹更快" sub="总冠军，加上乙组第1、第2名，刚好三匹"/>
   <ProofRelations names={names} target={target} reveal={reveal}/><Board alpha={alpha} colors={{...colorMap(names.slice(0,Math.ceil(reveal)),C.gold),乙3:C.red}}/>
   <FasterProof names={names} target={target} reveal={reveal} conclusion={fade>.5}/><Count value={6} alpha={fade}/><Note color={C.gold}>乙组保留前2名；甲组前三仍然有机会</Note>
  </>;
 }
 if(t==='six-left'){
  const reveal=phase(s,f,0,.02,.9)*3;
  return <><Head title="留下六匹，其中一匹已确定" sub="甲组前三 · 乙组前二 · 丙组第一"/>
   <Board alpha={alphaStage(4)} colors={{...colorMap(RETAINED,C.gold),甲1:q>.3?C.teal:C.gold}}/>
   {[3,2,1].map((n,i)=><g key={i} opacity={clamp(reveal-i)}><T x={1430+i*135} y={454} anchor="middle" size={62} color={C.gold} weight={750}>{n}</T>{i<2&&<T x={1495+i*135} y={451} anchor="middle" size={38} color={C.muted}>+</T>}</g>)}
   <g opacity={q}><T x={1570} y={565} size={40} color={C.gold} anchor="middle">6匹</T><T x={1570} y={668} size={29} color={C.teal} anchor="middle">甲1 已确定总第一</T><T x={1570} y={735} size={28} color={C.muted} anchor="middle">另5匹争二、三名</T></g>
   <Note color={C.teal}>总冠军已知，只缺后面两个名额</Note>
  </>;
 }
 if(t==='final-five'){
  const positions:Record<string,{x:number;y:number}>={},move=phase(s,f,1,.03,.93),travel=ease(flag(move,.15,.85)),alpha=Object.fromEntries(HORSES.map(h=>[h.id,RETAINED.includes(h.id)?1:.14*(1-flag(move,0,.15))])),scales=Object.fromEntries(FINALISTS.map(id=>[id,move<.15?mix(1,.7,flag(move,0,.15)):move>.85?mix(.7,1,flag(move,.85,1)):.7]));
  HORSES.forEach(h=>{const start=nodeXY(h.id);let end=start,amount=0;if(h.id==='甲1'){end=championSeat;amount=flag(move,0,.15);}else if(FINALISTS.includes(h.id)){end=finalSource[h.id];amount=travel;}positions[h.id]={x:mix(start.x,end.x,amount),y:mix(start.y,end.y,amount)};});
  return <><Head title="真正要比较的，只剩另外五匹" sub="第七场：甲2、甲3、乙1、乙2、丙1"/>
   <Board positions={positions} alpha={alpha} scales={scales} colors={{...colorMap(FINALISTS,C.gold),甲1:C.teal}} groupLabels={move===0} rankHeaders={move===0}/>
   <ActualFirst alpha={flag(move,.2,.5)}/><CompareLabel x={840} alpha={move}>第七场 · 5个参赛者</CompareLabel>
   <g opacity={move}><T x={360} y={461} size={28} color={C.muted} anchor="middle">不再占用跑道</T><path d="M 1120 332 V 824" stroke={C.edge} strokeWidth={2} strokeDasharray="8 10"/><T x={1450} y={560} size={38} color={C.gold} anchor="middle">争夺总第二、总第三</T></g>
   <Note color={C.gold}>总第一不必再跑，把跑道留给还未确定的候选</Note>
  </>;
 }
 if(t==='final-race'){
  const first=phase(s,f,0,.06,.94)*2,rest=phase(s,f,1,.05,.77)*3,progress=Math.min(5,first+(q>0?rest:0)),positions:Record<string,{x:number;y:number}>={'甲1':championSeat};
  finalOrder.forEach((id,i)=>{const amount=ease(clamp(progress-i)),a=finalSource[id],b=finalResult[id];positions[id]={x:mix(a.x,b.x,amount),y:mix(a.y,b.y,amount)};});
  const alpha=Object.fromEntries(HORSES.map(h=>[h.id,RETAINED.includes(h.id)?1:0]));
  return <><Head title="第七场，只取本场前两名" sub="教学示例结果 · 本场名次还不是总名次"/>
   <Board positions={positions} alpha={alpha} groupLabels={false} rankHeaders={false} colors={{...colorMap(FINALISTS,C.gold),甲1:C.teal}}/>
   <ActualFirst/><CompareLabel x={840}>参赛者</CompareLabel><CompareLabel x={1410}>第七场 · 本场名次</CompareLabel>{rankLabels(finalOrder,finalResult,progress)}
   <Note color={C.gold}>甲2先到，乙1随后；只需要本场的前两名</Note>
  </>;
 }
 if(t==='podium'){
  const moveFirst=phase(s,f,0,.05,.8),moveSecond=phase(s,f,1,.02,.73),positions:Record<string,{x:number;y:number}>={'甲1':championSeat},alpha:Record<string,number>={};
  HORSES.forEach(h=>{if(h.id==='甲2'){const a=finalResult[h.id],b=podiumPositions[h.id];positions[h.id]={x:mix(a.x,b.x,moveFirst),y:mix(a.y,b.y,moveFirst)};}else if(h.id==='乙1'){const a=finalResult[h.id],b=podiumPositions[h.id];positions[h.id]={x:mix(a.x,b.x,moveSecond),y:mix(a.y,b.y,moveSecond)};}else if(FINALISTS.includes(h.id)){positions[h.id]=finalResult[h.id];}alpha[h.id]=['甲1','甲2','乙1'].includes(h.id)?1:FINALISTS.includes(h.id)?1-moveFirst:0;});
  return <><Head title="本场前两名，补齐全部马的前三" sub="本例总名次：甲1、甲2、乙1"/>
   <Board positions={positions} alpha={alpha} groupLabels={false} rankHeaders={false} colors={{甲1:C.teal,甲2:C.gold,乙1:C.gold}} scales={{甲1:mix(1,1.4,moveSecond),甲2:mix(1,1.4,moveSecond),乙1:mix(1,1.4,moveSecond)}}/>
   <ActualFirst/><g opacity={moveFirst}><T x={900} y={282} size={34} color={C.gold} anchor="middle" weight={750}>总第二</T><T x={900} y={540} size={30} color={C.muted} anchor="middle">第七场第1名</T></g>
   <g opacity={moveSecond}><T x={1440} y={282} size={34} color={C.gold} anchor="middle" weight={750}>总第三</T><T x={1440} y={540} size={30} color={C.muted} anchor="middle">第七场第2名</T></g>
   <g opacity={moveSecond}><path d="M 360 650 H 1440" stroke={C.edge} strokeWidth={2}/><T x={900} y={754} size={46} color={C.teal} anchor="middle" weight={750}>前三名与顺序，都确定了</T></g>
   <Note>同一批候选、同一组赛果，得到完整答案</Note>
  </>;
 }
 if(t==='seven'){
  const group=phase(s,f,0,.03,.38),champ=phase(s,f,0,.45,.9),last=phase(s,f,1,.02,.42),sum=phase(s,f,1,.51,.94);
  const cards=[{x:165,title:'各组内部排顺序',count:5,alpha:group,kind:'分组赛'},{x:735,title:'比较五个组冠军',count:1,alpha:champ,kind:'冠军赛'},{x:1305,title:'确定最后两个名额',count:1,alpha:last,kind:'最后一场'}];
  return <><Head title="回看赛程：五场，加一场，再加一场" sub="每一场，都补上前面还不知道的比较"/>
   {cards.map(card=><g key={card.kind} opacity={card.alpha}><rect x={card.x} y={330} width={450} height={405} rx={24} fill={C.surface} stroke={C.edge}/><T x={card.x+225} y={403} size={33} color={C.muted} anchor="middle">{card.kind}</T><T x={card.x+225} y={551} size={112} color={C.gold} anchor="middle" weight={760}>{card.count}</T><T x={card.x+225} y={615} size={29} color={C.muted} anchor="middle">场</T><T x={card.x+225} y={686} size={28} color={C.text} anchor="middle">{card.title}</T></g>)}
   <T x={675} y={547} size={49} color={C.muted} anchor="middle" alpha={champ}>+</T><T x={1245} y={547} size={49} color={C.muted} anchor="middle" alpha={last}>+</T>
   <g opacity={sum}><T x={960} y={858} size={64} color={C.teal} anchor="middle" weight={760}>5 + 1 + 1 = 7 场</T></g>
  </>;
 }
 throw new Error('Unknown horse-racing visualType: '+t);
};

const ShotView=({s,hideSubtitles=false,auditLayout=false}:{s:Shot;hideSubtitles?:boolean;auditLayout?:boolean})=>{
 const f=useCurrentFrame(),legacyResult=s.visualType==='seven'?{...s,durationInFrames:377}:s,sceneFrame=s.visualType==='seven'?Math.min(f,376):f,shortEnd=s.visualType==='seven'&&f>=377,subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 useLayoutAudit(auditLayout,'main',s.from+f);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg data-audit-scene="true" width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  <PuzzleCanvas/>
  <Scene s={legacyResult} f={sceneFrame}/>{shortEnd&&<T x={960} y={915} size={25} color={C.muted} anchor="middle">IT小村 · 原创</T>}<T x={1790} y={92} size={25} color={C.muted} anchor="end">IT小村</T>
 </svg>{!hideSubtitles&&subtitle&&<div data-subtitle="true" style={{position:'absolute',left:200,right:200,bottom:65,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:`0 2px 5px ${C.bg}`,whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:{hideSubtitles?:boolean;auditLayout?:boolean})=><AbsoluteFill>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
