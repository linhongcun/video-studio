import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,NUMS} from './data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const at=(s:Shot,i:number,p:number)=>{
 const start=Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
 const end=Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10);
 return start+(end-start)*p;
};
const phase=(s:Shot,f:number,i=0,a=.05,b=.8)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const x=(i:number)=>330+i*180;
const T=({x,y,children,size=31,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='二分查找',color=C.text}:any)=><g><T x={120} y={101} size={24} color={C.muted}>{kicker}</T><T x={120} y={184} size={52} color={color} weight={760}>{title}</T>{sub&&<T x={120} y={244} size={27} color={C.muted}>{sub}</T>}</g>;
const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={900} size={31} color={color} alpha={alpha} anchor="middle">{children}</T>;
const Target=({value=13,label='目标',alpha=1}:any)=><g opacity={alpha}><rect x={1515} y={280} width={255} height={88} rx={18} fill={C.surface} stroke={C.edge}/><T x={1544} y={334} size={27} color={C.muted}>{label}</T><T x={1728} y={339} size={45} anchor="end" color={C.gold} mono>{value}</T></g>;
const Compare=({children,alpha=1,color=C.gold}:any)=><g opacity={alpha}><T x={960} y={349} size={46} anchor="middle" color={color} weight={650} mono>{children}</T></g>;
const Result=({value,alpha=1,label='返回下标',color=C.teal,y=736}:any)=><g opacity={alpha} transform={`translate(0 ${y-736})`}><rect x={669} y={736} width={582} height={112} rx={20} fill={C.surface} stroke={color} strokeWidth={2}/><T x={924} y={807} size={35} anchor="end" color={C.muted}>{label}</T><T x={995} y={813} size={57} mono color={color}>{value}</T></g>;

type BoardProps={left?:number;right?:number;leftPos?:number;rightPos?:number;leftAlpha?:number;rightAlpha?:number;mid?:number;midAlpha?:number;alive?:number[];showIndex?:boolean;indexAlpha?:number;showPointers?:boolean;pointerAlpha?:number;showRange?:boolean;rangeAlpha?:number;mark?:number;markColor?:string;markAlpha?:number;spot?:number;spotAlpha?:number;empty?:boolean};
const Board=({left=0,right=7,leftPos=left,rightPos=right,leftAlpha=1,rightAlpha=1,mid=-1,midAlpha=1,alive=NUMS.map(()=>1),showIndex=true,indexAlpha=1,showPointers=true,pointerAlpha=1,showRange=true,rangeAlpha=1,mark=-1,markColor=C.teal,markAlpha=1,spot=-1,spotAlpha=0,empty=false}:BoardProps)=>{
 const rangeWidth=Math.max(0,(rightPos-leftPos)*180+158),isEmpty=empty||rightPos<leftPos;
 return <g data-array="ordered-unique">
  {showRange&&!isEmpty&&<rect x={x(leftPos)-79} y={425} width={rangeWidth} height={226} rx={20} fill={C.teal+'09'} stroke={C.teal} strokeOpacity={.65*rangeAlpha} fillOpacity={rangeAlpha} strokeWidth={2}/>}
  {NUMS.map((num,i)=><g key={i}>
   <g opacity={.2+.8*alive[i]} data-candidate-index={i} data-candidate-opacity={alive[i]}>
    <rect x={x(i)-65} y={462} width={130} height={117} rx={15} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <T x={x(i)} y={542} anchor="middle" size={62} mono color={i===spot?C.text:C.text}>{num}</T>
    {showIndex&&<T x={x(i)} y={622} anchor="middle" size={28} mono color={C.muted} alpha={indexAlpha}>{i}</T>}
   </g>
   {i===spot&&<rect x={x(i)-65} y={462} width={130} height={117} rx={15} fill={C.gold+'09'} stroke={C.gold} strokeWidth={3} opacity={spotAlpha}/>}
   {i===mark&&<rect x={x(i)-65} y={462} width={130} height={117} rx={15} fill={markColor+'0B'} stroke={markColor} strokeWidth={4} opacity={markAlpha}/>}
  </g>)}
  {showIndex&&<T x={180} y={622} size={23} color={C.muted} alpha={indexAlpha}>下标</T>}
  {mid>=0&&<g opacity={midAlpha} data-pointer="mid" data-index={mid}><T x={x(mid)} y={397} anchor="middle" size={27} color={C.gold}>中点 {mid}</T><path d={`M ${x(mid)} 410 V 445 m -8 -9 l 8 9 l 8 -9`} stroke={C.gold} strokeWidth={3} fill="none"/></g>}
  {showPointers&&<g opacity={pointerAlpha}>
   <g data-pointer="left" data-index={left}><path d={`M ${x(leftPos)-27} 683 V 656 m -8 9 l 8 -9 l 8 9`} stroke={C.teal} strokeWidth={3} fill="none"/><rect x={x(leftPos)-76} y={688} width={152} height={42} rx={8} fill={C.bg}/><T x={x(leftPos)} y={719} size={27} color={C.teal} anchor="middle" alpha={leftAlpha}>左边界 {left}</T></g>
   <g data-pointer="right" data-index={right}><path d={`M ${x(rightPos)+96} 774 V 665 H ${x(rightPos)+27} V 656 m -8 9 l 8 -9 l 8 9`} stroke={C.blue} strokeWidth={3} fill="none" strokeDasharray="7 5"/><rect x={x(rightPos)+20} y={779} width={152} height={42} rx={8} fill={C.bg}/><T x={x(rightPos)+96} y={810} size={27} color={C.blue} anchor="middle" alpha={rightAlpha}>右边界 {right}</T></g>
  </g>}
 </g>;
};
const alive=(l:number,r:number)=>NUMS.map((_,i)=>i>=l&&i<=r?1:0);
/** Fade the excluded cells first, move one pointer second, reveal new numeric state only at rest. */
const advance=(l:number,r:number,nextL:number,nextR:number,p:number):BoardProps=>{
 const fade=clamp(p/.4),motion=ease(clamp((p-.4)/.6));
 const cells=alive(l,r).map((a,i)=>a&&!(i>=nextL&&i<=nextR)?1-fade:a);
 const moving=motion>0&&motion<1;
 return {left:p>=1?nextL:l,right:p>=1?nextR:r,leftPos:mix(l,nextL,motion),rightPos:mix(r,nextR,motion),leftAlpha:nextL!==l&&moving?0:1,rightAlpha:nextR!==r&&moving?0:1,alive:cells,empty:p>=1&&nextL>nextR};
};
const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 if(t==='problem'){
  const spot=Math.min(7,Math.floor(phase(s,f,0,.04,.75)*8));
  return <><Head kicker="LeetCode 704 · 先看题目" title="在有序数组里，找一个数的位置" sub="输入示例 · 从小到大，所有值互不重复"/><Target/><Board showIndex={false} showRange={false} showPointers={false} spot={spot} spotAlpha={p<1?1:.3}/><T x={960} y={758} anchor="middle" size={42} color={C.gold}>目标 13 在哪里？</T><Note alpha={q}>找到它的位置，而不是重新排列数组</Note></>;
 }
 if(t==='output')return <><Head kicker="LeetCode 704 · 题目要求" title="返回位置，不是返回这个数" sub="下标从 0 开始 · 本例的值 13，对应下标 6"/><Target/><Board showPointers={false} showRange={false} mark={6} markAlpha={p}/><Result value={6} alpha={p}/><Note alpha={q} color={C.gold}>如果目标不存在，返回 −1</Note></>;
 if(t==='method'){
  const introduced=f>=Number(s.cueFrames?.labels?.['二分查找']??s.cueFrames?.sentences?.[1]??0);
  return <><Head kicker="开始解题" title="每次，只检查当前范围的中点" sub={introduced?'二分查找 · 先比较，再排除不可能的一半':'题意清楚了，再减少查找次数'}/><Target/><Board mid={introduced?3:-1} midAlpha={q}/><Note alpha={q} color={C.gold}>偶数个候选时，选中间靠左的一格</Note></>;
 }
 if(t==='first-mid')return <><Head title="7 比 13 小，能排除哪一段？" sub="中点下标：(0 + 7) ÷ 2 = 3.5 → 3"/><Target/><Compare alpha={q}>7 &lt; 13</Compare><Board mid={3} spot={3} spotAlpha={p}/><Note alpha={q} color={C.gold}>先看顺序能保证什么，再移动边界</Note></>;
 if(t==='why-safe'){
  const move=phase(s,f,1,.16,.83),state=advance(0,7,4,7,move),count=Math.min(3,Math.floor(phase(s,f,0,.1,.82)*4));
  return <><Head title="这四个数，都不可能是 13" sub="已排好序：1 ≤ 3 ≤ 5 ≤ 7 < 13"/><Target/><Compare alpha={p}>都 ≤ 7 &lt; 13</Compare><Board {...state} mid={move<.4?3:-1} spot={move===0?count:-1} spotAlpha={.8}/><Note color={move>=1?C.teal:C.gold}>{move>=1?'左边界 0 → 4 · 连同已比较的中点一起排除':'排除下标 0、1、2、3，目标不会被漏掉'}</Note></>;
 }
 if(t==='second-mid'){
  const move=phase(s,f,1,.27,.86),state=advance(4,7,6,7,move);
  return <><Head title="只在剩下的范围继续找" sub="本轮起始范围 4..7 · 中点下标 5，对应值 11"/><Target/><Compare alpha={phase(s,f,1,.01,.16)}>11 &lt; 13</Compare><Board {...state} mid={move<.4?5:-1} midAlpha={p}/><Note alpha={phase(s,f,1,.16,.26)} color={move>=1?C.teal:C.gold}>{move>=1?'左边界 4 → 6 · 只剩下标 6 和 7':'9 和 11 都不可能是 13'}</Note></>;
 }
 if(t==='found')return <><Head title="中点的值相等，返回它的下标" sub="范围 6..7 · 中点向下取整，得到下标 6"/><Target/><Compare alpha={q} color={C.teal}>13 = 13</Compare><Board left={6} right={7} mid={6} midAlpha={p} alive={alive(6,7)} mark={6} markAlpha={q} pointerAlpha={clamp(1-q/.25)}/><Result value={6} alpha={clamp((q-.3)/.7)}/><Note alpha={q}>本例检查 3 个中点：7 → 11 → 13</Note></>;
 if(t==='reset'){
  const resetting=phase(s,f,1,.04,.64),ready=resetting>=1;
  return <><Head kicker="接着看：目标不存在" title="找到以后，再把找不到的情况走完" sub={ready?'新示例 · 目标改为 8，从整个数组重新开始':'刚才：目标 13，返回下标 6'}/><Target value={ready?8:13} alpha={resetting>0&&resetting<1?.25:1}/><Board left={ready?0:6} right={7} alive={NUMS.map((_,i)=>i>=6?1:resetting)} showPointers={ready} showRange={ready} mark={ready?-1:6} markAlpha={1-resetting}/>{!ready&&<Result value={6} alpha={1-resetting}/>}<Note color={C.gold} alpha={resetting}>新一轮查找，不沿用上一轮的剩余范围</Note></>;
 }
 if(t==='missing-first'){
  const move=phase(s,f,1,.08,.83),state=advance(0,7,4,7,move);
  return <><Head title="目标是 8，同样先排除左半段" sub="中点下标 3，对应值 7"/><Target value={8}/><Compare alpha={p}>7 &lt; 8</Compare><Board {...state} mid={move<.4?3:-1} midAlpha={p}/><Note alpha={q} color={move>=1?C.teal:C.gold}>{move>=1?'范围缩到下标 4..7':'1、3、5、7 都不可能等于 8'}</Note></>;
 }
 if(t==='turn-left'){
  const move=phase(s,f,1,.18,.85),state=advance(4,7,4,4,move);
  return <><Head title="中点太大，这次排除右边" sub="下标 5 的值是 11 · 右边只会更大"/><Target value={8}/><Compare alpha={p}>8 &lt; 11 ≤ 13 ≤ 15</Compare><Board {...state} mid={move<.4?5:-1} midAlpha={p}/><Note alpha={q} color={move>=1?C.teal:C.gold}>{move>=1?'右边界 7 → 4 · 还剩一格，并没有结束':'连同中点，排除下标 5、6、7'}</Note></>;
 }
 if(t==='last-cell'){
  const move=phase(s,f,1,.27,.86),state=advance(4,4,4,3,move);
  return <><Head title="左右重合，还要检查最后一格" sub="本轮起始范围 4..4，仍然包含一个位置"/><Target value={8}/><Compare alpha={phase(s,f,1,.01,.16)}>9 &gt; 8</Compare><Board {...state} mid={move<.4?4:-1} midAlpha={p} spot={move<.4?4:-1} spotAlpha={p}/><Note alpha={phase(s,f,1,.16,.26)} color={move>=1?C.red:C.gold}>{move>=1?'左边界 4 > 右边界 3 · 候选范围为空':'右边界越过中点，退到下标 3'}</Note></>;
 }
 if(t==='absent')return <><Head title="边界交错，才说明没有候选了" sub="左边界 4 > 右边界 3 · 所有位置都已排除"/><Target value={8}/><Board left={4} right={3} alive={alive(4,3)} empty/><Result value="−1" label="没有找到，返回" color={C.gold} alpha={q} y={280}/><Note alpha={q} color={C.gold}>本例检查 3 个中点：7 → 11 → 9</Note></>;
 if(t==='rule'){
  const counts=[8,4,2,1],highlight=Math.min(3,Math.floor(q*4));
  return <><Head kicker="把过程写进程序" title="有候选就继续，更新要越过中点" sub="闭区间包含左右两端 · 重合继续，交错停止"/>
   <rect x={390} y={312} width={1140} height={102} rx={18} fill={C.surface} stroke={C.edge}/><T x={960} y={380} size={43} anchor="middle" mono color={C.gold}>while left &lt;= right:</T>
   <g opacity={q}><T x={960} y={503} size={27} anchor="middle" color={C.muted}>最多剩余候选数 · 复杂度示意，不是前例轨迹</T>{counts.map((n,i)=><g key={n}><rect x={480+i*260} y={548} width={180} height={124} rx={18} fill={C.surface} stroke={i===highlight?C.teal:C.edge} strokeWidth={i===highlight?3:1.5}/><T x={570+i*260} y={633} size={64} anchor="middle" color={i===highlight?C.teal:C.muted} mono>{n}</T>{i<3&&<T x={700+i*260} y={627} size={38} anchor="middle" color={C.muted}>→</T>}</g>)}<T x={710} y={799} size={45} anchor="middle" color={C.teal}>时间 O(log n)</T><T x={1250} y={799} size={45} anchor="middle" color={C.blue}>额外空间 O(1)</T></g><Note>每轮至少排除一半 · 只保留固定几个变量</Note></>;
 }
 return <><Head kicker="回收结论" title="排得安全，才能找得更快" sub="前提：数组已经升序排列，且值互不重复" color={C.teal}/>
  <g><rect x={230} y={350} width={680} height={380} rx={24} fill={C.surface} stroke={C.teal}/><T x={570} y={435} size={34} anchor="middle" color={C.muted}>中点的值 = 目标</T><T x={570} y={566} size={61} anchor="middle" color={C.teal}>返回下标</T><T x={570} y={653} size={30} anchor="middle" color={C.muted}>本例：13 → 下标 6</T></g>
  <g><rect x={1010} y={350} width={680} height={380} rx={24} fill={C.surface} stroke={C.gold}/><T x={1350} y={435} size={34} anchor="middle" color={C.muted}>左边界 &gt; 右边界</T><T x={1350} y={566} size={61} anchor="middle" color={C.gold}>返回 −1</T><T x={1350} y={653} size={30} anchor="middle" color={C.muted}>本例：8 → 没有候选位置</T></g>
  <T x={960} y={845} size={34} anchor="middle" color={C.muted} alpha={q}>接下来是完整代码，需要细看请暂停</T><T x={960} y={916} size={27} anchor="middle" color={C.muted}>IT小村 · 原创</T>
 </>;
};
const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null;
 const card=codeCardFrom!==null&&f>=codeCardFrom,sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  <defs><radialGradient id="lc704-bg"><stop offset="0" stopColor="#173B55" stopOpacity=".28"/><stop offset="1" stopColor={C.bg} stopOpacity="0"/></radialGradient></defs><ellipse cx="1440" cy="280" rx="950" ry="700" fill="url(#lc704-bg)"/>
  {card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}
  <T x={1790} y={91} size={25} color={C.muted} anchor="end">IT小村</T>
  <T x={120} y={1015} size={20} color={C.muted} alpha={.65}>{card?'LeetCode 704 · Python 3':'LeetCode 704 · 教学示例'}</T>
 </svg>{!hideSubtitles&&!card&&subtitle&&<div style={{position:'absolute',left:210,right:210,bottom:69,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
