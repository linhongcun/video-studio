import React from 'react';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../_shared/leetcode-video/Frame';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,COUNTS} from '../data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
import {Staircase,Walker,Hop,Route,StairGeometry,MAIN_STAIRS,foot,clamp,smooth,hopCurve} from './Staircase';
declare const __HAS_VOICE_AUDIO__:boolean;
const sentence=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
const at=(s:Shot,i:number,p:number)=>sentence(s,i)+(Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10)-sentence(s,i))*p;
const phase=(s:Shot,f:number,i=0,a=.06,b=.8)=>smooth((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const T=({x,y,children,size=31,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='爬楼梯',color=C.text}:any)=><g><foreignObject x={0} y={0} width={1920} height={150}><LeetcodeHeader slug="climbing-stairs" detail={kicker}/></foreignObject><T x={120} y={184} size={52} color={color} weight={760}>{title}</T>{sub&&<T x={120} y={245} size={28} color={C.muted}>{sub}</T>}</g>;
const Note=({children,color=C.muted,alpha=1,y=884}:any)=><T x={960} y={y} size={29} color={color} alpha={alpha} anchor="middle">{children}</T>;
const Result=({children,alpha=1,color=C.teal,y=842}:any)=><T x={960} y={y} size={42} anchor="middle" color={color} alpha={alpha} weight={650}>{children}</T>;
const MAIN=MAIN_STAIRS;
const BIG:StairGeometry={x:500,baseY:780,width:250,rise:100,steps:3};
const PATHS=[[1,1,1],[1,2],[2,1]];
const mini=(i:number):StairGeometry=>({x:205+i*563,baseY:708,width:100,rise:75,steps:3});
const groupColor=(path:number[])=>path[path.length-1]===1?C.teal:C.gold;
const pathWords=(path:number[])=>path.map(v=>v===1?'一阶':'两阶').join(' → ');
/** Route identities and positions stay fixed across shots 02–04. */
const ThreeWalks=({progress=1,mode='paths',lastProgress=1,groupAlpha=1}:any)=><g data-three-stair-walks="111/12/21">{PATHS.map((path,i)=>{
 const g=mini(i),color=groupColor(path),prefixLength=path.length-1,walked=mode==='prefix'?(prefixLength*progress+lastProgress)/path.length:mode==='last'?(prefixLength+lastProgress)/path.length:progress;
 return <g key={i} data-route-identity={i+1}>
  <T x={g.x+g.width} y={310} size={30} anchor="middle">走法{i+1}</T>
  {mode!=='paths'&&<g opacity={groupAlpha}><rect x={g.x-31} y={330} width={264} height={49} rx={13} fill={color+'0B'} stroke={color} strokeWidth={1.5}/><T x={g.x+101} y={364} size={23} anchor="middle" color={color}>最后上{path[path.length-1]===1?'一':'两'}阶这一组</T></g>}
  <Staircase geometry={g} showOrigin terminalLabel="终点" numberSize={21}/><Route geometry={g} path={path} progress={walked} highlightLast={mode!=='paths'} lastColor={color} walkerScale={.81}/>
  <T x={g.x+102} y={800} size={26} anchor="middle" color={mode==='paths'?C.blue:color}>{mode==='prefix'&&lastProgress===0?`前面到第${3-path[path.length-1]}阶`:pathWords(path)}</T>
 </g>;
})}</g>;
const CountScene=({step,progress}:any)=>{
 const values:(number|null)[]=COUNTS.map((n,i)=>i<step-1?n:i===step-1&&progress>=.90?n:null),one=clamp(progress*2),two=clamp(progress*2-1),done=progress>=.90,p=foot(MAIN,step);
 return <g data-last-step-counting={step}>
  <Staircase geometry={MAIN} counts={values} focus={{[step-1]:C.teal,[step-2]:C.gold}} target={step}/>
  <Hop geometry={MAIN} from={step-1} to={step} progress={one} color={C.teal} showWalker={!done&&progress<.5}/><Hop geometry={MAIN} from={step-2} to={step} progress={two} color={C.gold} showWalker={!done&&progress>=.5} alpha={two>0?1:0}/>{done&&<Walker x={p.x} y={p.y} color={C.teal}/>}
  <T x={628} y={335} size={25} color={C.teal}>到第{step-1}阶的{COUNTS[step-2]}种，各接上最后一阶</T><T x={628} y={375} size={25} color={C.gold} alpha={two>0?1:0}>到第{step-2}阶的{COUNTS[step-3]}种，各接上最后两阶</T>
  <Result><tspan fill={C.teal}>{COUNTS[step-2]}种</tspan> + <tspan fill={C.gold}>{COUNTS[step-3]}种</tspan> = {done?`${COUNTS[step-1]}种`:'待算'}</Result><Note>弧线表示最后一步上几阶；台阶侧面的数字表示有几种走法</Note>
 </g>;
};
const Variable=({x,name,value,step,color,alpha=1}:any)=>{
 const p=foot(MAIN,step);
 return <g opacity={alpha} data-variable={name} data-step={step} data-value={value}><path d={`M ${x} 792 C ${x} 704, ${p.x+23} 685, ${p.x+23} ${p.y+59}`} stroke={color} strokeWidth={2} strokeDasharray="7 7" fill="none"/><rect x={x-225} y={792} width={450} height={107} rx={19} fill={C.surface} stroke={color} strokeWidth={2}/><T x={x-190} y={831} size={27} mono color={color}>{name}</T><T x={x+190} y={831} size={23} anchor="end" color={C.muted}>第{step}阶的方法数</T><T x={x} y={882} size={40} anchor="middle" color={color}><tspan fontFamily={MONO}>{value}</tspan>种</T></g>;
};
const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1),second=f>=sentence(s,1);
 if(t==='problem')return <>
  <Head kicker="LeetCode 70 · 先看题目" title="爬楼梯：一共有多少种走法？" sub="输入示例 n = 3 · 从地面出发，每次上一阶或两阶"/><Staircase geometry={BIG} terminalLabel="第3阶 · 终点" numberSize={25}/><Route geometry={BIG} path={[1,2]} progress={phase(s,f,0,.08,.91)} walkerScale={1.15}/><g opacity={p}><T x={397} y={516} size={33} color={C.blue}>先上一阶</T><T x={975} y={320} size={33} color={C.blue}>再上两阶</T></g><g opacity={q}><rect x={1430} y={505} width={330} height={198} rx={23} fill={C.surface} stroke={C.gold} strokeWidth={2}/><T x={1595} y={559} size={26} anchor="middle" color={C.muted}>要求返回</T><T x={1595} y={628} size={37} anchor="middle" color={C.gold}>不同走法的数量</T></g><Note color={C.gold}>只能上1或2阶 · 必须恰好到终点</Note>
 </>;
 if(t==='order')return <><Head kicker="LeetCode 70 · 看清不同走法" title="同一段楼梯，可以这样走三次" sub="从各自的地面重新出发 · 每条轨迹都恰好到第3阶"/><ThreeWalks progress={phase(s,f,0,.02,.91)}/><Result alpha={q}>返回：3种不同走法</Result><Note alpha={q} color={C.gold}>先上一阶再上两阶，与先上两阶再上一阶，顺序不同</Note></>;
 if(t==='last-step')return <>
  <Head kicker="从走法里找规律" title="先看：到终点的最后一步" sub={second?'回看末步：上一阶从第2阶来，上两阶从第1阶来':'仍是刚才三条走法，位置与身份保持不变'}/><ThreeWalks mode={second?'last':'paths'} progress={1} lastProgress={q} groupAlpha={q}/>{!second&&<g opacity={p}>{PATHS.map((path,i)=><path key={i} d={hopCurve(mini(i),3-path[path.length-1],3).d} fill="none" stroke={groupColor(path)} strokeWidth={6}/>)}</g>}<Result alpha={q}>最后一步只有：上一阶，或上两阶</Result><Note alpha={q}>最后一步的起点，就在终点前一阶或前两阶</Note>
 </>;
 if(t==='no-overlap')return <><Head kicker="为什么能把两组相加" title="前面的每条走法，接上对应的最后一步" sub={second?'保持三条走法的身份，分别接回同一个终点':'先看前缀：走法1和3到第2阶；走法2到第1阶'}/><ThreeWalks mode="prefix" progress={p} lastProgress={second?q:0}/><Result alpha={q}><tspan fill={C.teal}>2种</tspan> + <tspan fill={C.gold}>1种</tspan> = 3种</Result><Note alpha={q}>末步不同，不会重复；末步只有1或2，不会遗漏</Note></>;
 if(t==='bases'){
  const r=clamp((f-sentence(s,1))/Math.max(1,s.durationInFrames-12-sentence(s,1))),which=r<.24?0:r<.64?1:2,route=[[1],[1,1],[2]][which],walk=which===0?r/.24:which===1?(r-.24)/.4:(r-.64)/.36;
  return <>
  <Head kicker="换成六阶，同一规则" title="先从能直接数清的两阶开始" sub="楼梯往上延伸到六阶 · 先数清一阶、两阶怎么走"/><Staircase geometry={MAIN} counts={[r>.20?1:null,r>.94?2:null,null,null,null,null]} focus={{1:C.teal,2:C.gold}}/><Route geometry={MAIN} path={route} progress={walk} highlightLast lastColor={C.gold}/><g opacity={q}><T x={750} y={345} size={28} color={C.teal}>到第1阶：只有上一阶，1种</T><T x={750} y={389} size={28} color={C.gold}>到第2阶：一阶再一阶，或直接上两阶，2种</T></g><Note>{which===0?'从地面上一阶，到第1阶只有这一种走法':which===1?'从地面重新出发：一阶，再上一阶':'从地面重新出发：直接上两阶'}</Note>
 </>;
 }
 if(t==='grow')return <><Head kicker="沿着同一段楼梯往上算" title={second?'接着到第四阶：前面有3种和2种':'先到第三阶：前面有2种和1种'} sub="固定最后一步，前面的每种走法都能接到当前这一阶"/><CountScene step={second?4:3} progress={second?q:p}/></>;
 if(t==='thirteen'){
  const stageSix=f>=at(s,0,.54),progress=stageSix?smooth((f-at(s,0,.6))/Math.max(1,at(s,1,.87)-at(s,0,.6))):smooth((f-at(s,0,.03))/Math.max(1,at(s,0,.45)-at(s,0,.03)));
  return <><Head kicker="继续往上，来到终点" title={stageSix?'第六阶的最后一步：从第5阶或第4阶来':'先算第五阶：5种加3种，得到8种'} sub={stageSix?'第5阶的8种各上一阶；第4阶的5种各上两阶':'楼梯与已有计数的位置保持不变'}/><CountScene step={stageSix?6:5} progress={progress}/></>;
 }
 if(t==='dynamic-programming'){
  const introduced=f>=Number(s.cueFrames?.labels?.['动态规划']??sentence(s,1)),pos=foot(MAIN,introduced?5:6);
  return <><Head kicker={introduced?'动态规划 · 回看计算过程':'答案已经得到，再看需要保存什么'} title="沿途的结果可以复用，下一步只看前两阶" sub={introduced?'回看：准备计算第6阶，先把终点计数恢复为待算':'台阶一直存在，侧面的计数帮助我们看清整个过程'}/><Staircase geometry={MAIN} counts={introduced?[1,2,3,5,8,null]:COUNTS} focus={introduced?{4:C.gold,5:C.teal}:{6:C.teal}} dimCountsBefore={introduced?4:0}/><Walker x={pos.x} y={pos.y} color={C.teal}/>{introduced&&<g opacity={q}><T x={665} y={340} size={29} color={C.gold}>保留第4阶的5种</T><T x={665} y={382} size={29} color={C.teal}>保留第5阶的8种</T></g>}<Result alpha={q}>计算下一阶，只需要前两阶的方法数</Result><Note alpha={q}>淡化的是早期计数；真实的台阶和原有走法没有消失</Note></>;
 }
 if(t==='rolling'){
  const sum=phase(s,f,1,.03,.34),change=phase(s,f,1,.57,.87),swapped=change>=.5,oldAlpha=clamp(1-2*change),newAlpha=clamp(2*change-1),pos=foot(MAIN,swapped?6:5);
  return <><Head kicker="把楼梯上的计数映射到变量" title="先用旧值求和，再把两项一起前移" sub={swapped?'更新后：prev对应第5阶，curr对应第6阶':'更新前：prev对应第4阶，curr对应第5阶'}/><Staircase geometry={MAIN} counts={[1,2,3,5,8,swapped?13:null]} focus={swapped?{5:C.gold,6:C.teal}:{4:C.gold,5:C.teal}} dimCountsBefore={swapped?5:4}/><Walker x={pos.x} y={pos.y} color={C.teal}/><g opacity={sum}><rect x={1510} y={520} width={295} height={144} rx={20} fill={C.surface} stroke={C.gold}/><T x={1657} y={563} size={25} anchor="middle" color={C.muted}>先算出新值</T><T x={1657} y={628} size={39} anchor="middle" mono color={C.gold}>5 + 8 = 13</T></g><Variable x={648} name="prev" value={5} step={4} alpha={oldAlpha} color={C.gold}/><Variable x={1240} name="curr" value={8} step={5} alpha={oldAlpha} color={C.teal}/><Variable x={648} name="prev" value={8} step={5} alpha={newAlpha} color={C.gold}/><Variable x={1240} name="curr" value={13} step={6} alpha={newAlpha} color={C.teal}/></>;
 }
 if(t==='implementation'){
  const ready=q>=.52,crop:StairGeometry={x:1380,baseY:754,width:137,rise:103,steps:3};
  return <><Head kicker="把刚才的过程写进程序" title="先算右边的旧值，再一起更新左边" sub="循环从第三阶开始，直到输入要求的终点"/><rect x={120} y={319} width={1130} height={442} rx={24} fill={C.surface} stroke={C.edge}/>{['if n <= 2: return n','prev, curr = 1, 2','for step in range(3, n + 1):'].map((line,i)=><T key={line} x={171} y={389+i*67} mono size={33} color={i===2?C.text:C.muted}>{line}</T>)}<g opacity={q}><rect x={150} y={583} width={1070} height={119} rx={14} stroke={C.gold} strokeWidth={2} fill={C.gold+'06'}/><T x={175} y={632} mono size={32} color={C.gold}>prev, curr = curr, prev + curr</T><T x={175} y={676} mono size={27} color={ready?C.teal:C.muted}>{ready?'右侧得到(8, 13)，再整体赋值':'先读旧值：curr=8，prev+curr=5+8'}</T></g><T x={1560} y={345} size={25} anchor="middle" color={C.muted}>放大：第4–6阶</T><Staircase geometry={crop} counts={[5,8,13]} focus={ready?{2:C.gold,3:C.teal}:{1:C.gold,2:C.teal}} labelOffset={3} showOrigin={false} terminalLabel="第6阶" countSize={30} numberSize={21}/><T x={1327} y={750} size={45} color={C.muted}>…</T><Walker x={foot(crop,ready?3:2).x} y={foot(crop,ready?3:2).y} color={C.teal} scale={.9}/><Result alpha={q} y={840}>{ready?'两个变量一起对应第5阶、第6阶':'旧的5种和8种，都要参与这一轮计算'}</Result><Note>只有一阶或两阶时直接返回；其他情况再进入循环</Note></>;
 }
 if(t==='boundary')return <><Head kicker="回到完整的六阶楼梯" title="每阶只计算一次，只留两个计数" sub="真实走法仍在楼梯上；程序只保存计算下一阶需要的信息"/><Staircase geometry={MAIN} counts={COUNTS} focus={{5:C.gold,6:C.teal}} dimCountsBefore={5}/><Walker x={foot(MAIN,6).x} y={foot(MAIN,6).y} color={C.teal}/><g opacity={p}><T x={700} y={345} size={36} color={C.teal}>时间 O(n)</T><T x={1120} y={345} size={36} color={C.gold}>额外空间 O(1)</T></g><Result alpha={q}>只记两项，来自本题的前两阶依赖</Result><Note alpha={q}>其他动态规划问题，未必也能只保存两个数</Note></>;
 return <><Head kicker="回应最初的楼梯问题" title="恰好走到第六阶，共有十三种走法" sub="最后一步分两类，逐阶得到答案，再滚动保留两个计数" color={C.teal}/><Staircase geometry={MAIN} counts={COUNTS} focus={{5:C.gold,6:C.teal}} dimCountsBefore={5}/><Walker x={foot(MAIN,6).x} y={foot(MAIN,6).y} color={C.teal}/><Result>同一段楼梯 · 同一终点 · 13种走法</Result><Note alpha={q}>接下来是完整程序，需要细看请暂停</Note></>;
};
const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null,card=codeCardFrom!==null&&f>=codeCardFrom,sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}><defs></defs>{card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}<T x={120} y={1045} size={20} color={C.muted} alpha={.65}>{card?'LeetCode 70 · Python 3':'LeetCode 70 · 教学示例'}</T></svg>{!hideSubtitles&&!card&&subtitle&&<div data-subtitle="true" style={{position:'absolute',left:210,right:210,bottom:69,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill><LeetcodeBackdrop/>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
