import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,COUNTS} from './data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const sentence=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
const at=(s:Shot,i:number,p:number)=>mix(sentence(s,i),Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10),p);
const phase=(s:Shot,f:number,i=0,a=.06,b=.8)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const T=({x,y,children,size=31,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='爬楼梯',color=C.text}:any)=><g><T x={120} y={101} size={24} color={C.muted}>{kicker}</T><T x={120} y={184} size={52} color={color} weight={760}>{title}</T>{sub&&<T x={120} y={245} size={28} color={C.muted}>{sub}</T>}</g>;
const Note=({children,color=C.muted,alpha=1,y=874}:any)=><T x={960} y={y} size={30} color={color} alpha={alpha} anchor="middle">{children}</T>;
const nodeX=(i:number)=>335+i*250;
type BoardProps={values?:(number|null)[];active?:number[];target?:number;progress?:number;y?:number;history?:boolean;dim?:number;completed?:number;showTitle?:boolean};
const Board=({values=COUNTS,active=[],target=-1,progress=0,y=500,history=false,dim=1,completed=-1,showTitle=true}:BoardProps)=> <g data-count-board="six-steps">
 {showTitle&&<><T x={177} y={y-72} size={23} color={C.muted}>到达</T><T x={177} y={y+25} size={23} color={C.muted}>方法数</T></>}
 {COUNTS.map((_,i)=>{
  const isActive=active.includes(i),isTarget=i===target,isEarlier=history&&i<Math.min(...active),alpha=isEarlier?dim:1;
  return <g key={i} opacity={alpha} data-step={i+1} data-count={values[i]??'pending'} data-active={isActive}>
   {i<5&&<path d={`M ${nodeX(i)+81} ${y} H ${nodeX(i+1)-81}`} stroke={C.edge} strokeWidth={2}/>}
   <T x={nodeX(i)} y={y-72} anchor="middle" size={29} color={isActive?C.teal:C.muted}>第{i+1}阶</T>
   <rect x={nodeX(i)-81} y={y-53} width={162} height={106} rx={20} fill={C.surface} stroke={isTarget?C.gold:isActive||i===completed?C.teal:C.edge} strokeWidth={isTarget||isActive||i===completed?3:2}/>
   <T x={nodeX(i)} y={y+24} anchor="middle" size={64} color={isTarget&&values[i]!==null?C.gold:isActive||i===completed?C.teal:values[i]===null?C.muted:C.text} mono>{values[i]??'?'}</T>
   {isActive&&<T x={nodeX(i)} y={y+101} anchor="middle" size={24} color={C.teal}>本轮旧计数</T>}
  </g>;
 })}
 {target>=2&&<g data-count-dependencies={target+1}>
  {[target-2,target-1].map((i,j)=>{
   const start=nodeX(i)+64,end=nodeX(target)-64,top=y-165-j*42;
   return <g key={i} opacity={progress>0?1:0}>
    <path d={`M ${start} ${y-54} C ${start} ${top}, ${end} ${top}, ${end} ${y-54}`} pathLength={1} stroke={j?C.gold:C.teal} strokeWidth={4} strokeDasharray="1" strokeDashoffset={1-clamp(progress/.72)} fill="none"/>
    <path d={`M ${end-8} ${y-66} l 8 12 l 8 -12`} fill="none" stroke={j?C.gold:C.teal} strokeWidth={3} opacity={clamp((progress-.6)/.15)}/>
   </g>;
  })}
 </g>}
</g>;
const Formula=({a,b,value,step,alpha=1,settled=false,y=750}:any)=><g opacity={alpha} data-formula-step={step}>
 <T x={960} y={y-58} size={25} color={C.muted} anchor="middle">计算第{step}阶的方法数</T>
 <T x={960} y={y+15} size={55} anchor="middle" mono color={settled?C.teal:C.gold}>{a} + {b} = {value}</T>
</g>;
const Paths=({reveal=3,group=false,highlight=false,complete=true}:any)=>{
 const paths=[[1,1,1],[1,2],[2,1]],rowY=[365,510,695];
 return <g data-path-examples="n3">
  {group&&paths.map((path,i)=><rect key={i} x={365} y={rowY[i]-68} width={1195} height={126} rx={20} stroke={path[path.length-1]===1?C.teal:C.gold} fill={(path[path.length-1]===1?C.teal:C.gold)+'06'} strokeWidth={2}/>) }
  {paths.map((path,i)=>{
   let running=0;const alpha=clamp(reveal-i);
   return <g key={i} opacity={alpha} data-path={path.join(',')}>
    <T x={285} y={rowY[i]+25} size={28} anchor="end" color={C.muted}>走法 {i+1}</T>
    {path.map((v,j)=>{const start=running;running+=v;const last=j===path.length-1;return <g key={j}>
     <rect x={415+start*245} y={rowY[i]-33} width={v*245-16} height={83} rx={14} fill={C.surface} stroke={highlight&&last?C.gold:C.edge} strokeWidth={highlight&&last?4:2}/>
     <T x={415+(start+v/2)*245-8} y={rowY[i]+23} anchor="middle" size={44} color={highlight&&last?C.gold:C.text} mono>+{v}</T>
     {highlight&&last&&<T x={415+(start+v/2)*245-8} y={rowY[i]-51} anchor="middle" size={23} color={C.gold}>最后一步</T>}
    </g>})}
    {complete&&<T x={1195} y={rowY[i]+24} size={31} color={C.teal}>到第3阶</T>}
    {group&&<T x={1455} y={rowY[i]+23} anchor="middle" size={27} color={path[path.length-1]===1?C.teal:C.gold}>{path[path.length-1]===1?'末步 +1':'末步 +2'}</T>}
   </g>;
  })}
 </g>;
};
const Role=({x,value,step,name,alpha=1,color=C.teal}:any)=><g opacity={alpha} data-variable={name} data-step={step} data-value={value}>
 <rect x={x-185} y={645} width={370} height={146} rx={22} stroke={color} fill={C.surface} strokeWidth={2}/>
 <T x={x-145} y={689} size={27} mono color={color}>{name}</T><T x={x+137} y={694} size={25} anchor="end" color={C.muted}>第{step}阶方法数</T>
 <T x={x} y={764} size={58} anchor="middle" mono color={color}>{value}</T>
</g>;
const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1),second=f>=sentence(s,1);
 if(t==='problem')return <>
  <Head kicker="LeetCode 70 · 先看题目" title="爬楼梯：一共有多少种走法？" sub="输入示例 · n = 3，共三阶"/>
  <g data-input="n=3">
   {[1,2,3].map((v,i)=><g key={v}><rect x={550+i*285} y={428} width={202} height={145} rx={20} fill={C.surface} stroke={i===2?C.teal:C.edge} strokeWidth={i===2?3:2}/><T x={651+i*285} y={518} anchor="middle" size={44}>第{v}阶</T>{i<2&&<path d={`M ${760+i*285} 500 h 64 m -10 -8 l 10 8 l -10 8`} stroke={C.edge} strokeWidth={3} fill="none"/>}</g>)}
   <T x={651} y={361} size={34} anchor="middle" color={C.gold}>每步 +1</T><T x={936} y={361} size={34} anchor="middle" color={C.gold}>或 +2</T><T x={1221} y={641} size={30} anchor="middle" color={C.teal}>终点：恰好到第3阶</T>
  </g>
  <g opacity={q}><T x={960} y={763} size={44} anchor="middle" color={C.gold}>返回不同走法的数量</T><Note>每步只能上1或2阶 · 不能越过终点</Note></g>
 </>;
 if(t==='order')return <>
  <Head kicker="LeetCode 70 · 题目要求" title="顺序不同，也算不同走法" sub="每个数字表示这一步上几阶 · 三条走法都恰好到第3阶"/>
  <Paths reveal={1+2*phase(s,f,0,.02,.84)}/>
  <g opacity={q}><rect x={1420} y={390} width={295} height={250} rx={25} fill={C.surface} stroke={C.teal} strokeWidth={2}/><T x={1567} y={452} size={29} color={C.muted} anchor="middle">返回方法数</T><T x={1567} y={570} size={104} color={C.teal} anchor="middle" mono>3</T></g>
  <Note color={C.gold} alpha={q}>先1后2，与先2后1，是两种顺序</Note>
 </>;
 if(t==='last-step')return <>
  <Head kicker="按最后一步分组" title="到第三阶，最后一步只有两类" sub={second?'末步 +1：前面到第2阶；末步 +2：前面到第1阶':'继续看刚才三条走法，先标出它们的最后一步'}/>
  <Paths group={second} highlight={p>.2}/>
  <Note alpha={q}>看最后一步，才能确定前面应该到哪一阶</Note>
 </>;
 if(t==='no-overlap')return <>
  <Head kicker="相加为什么正确" title="两类走法：不重复，也不遗漏" sub="固定最后一步，前面的每种走法都恰好对应一种完整走法"/>
  <g><rect x={295} y={325} width={1330} height={203} rx={24} fill={C.surface} stroke={C.teal} strokeWidth={2}/><T x={350} y={380} size={29} color={C.teal}>到第2阶 · 2种</T><T x={350} y={454} size={42} mono>[1,1]   [2]</T><T x={920} y={424} anchor="middle" size={38} color={C.gold}>接上 +1 →</T><T x={1115} y={452} size={39} mono>[1,1,1]  [2,1]</T></g>
  <g opacity={p}><rect x={295} y={565} width={1330} height={167} rx={24} fill={C.surface} stroke={C.gold} strokeWidth={2}/><T x={350} y={620} size={29} color={C.gold}>到第1阶 · 1种</T><T x={350} y={692} size={42} mono>[1]</T><T x={920} y={665} anchor="middle" size={38} color={C.gold}>接上 +2 →</T><T x={1115} y={691} size={42} mono>[1,2]</T></g>
  <g opacity={q}><T x={960} y={810} size={48} color={C.teal} anchor="middle" mono>2 + 1 = 3</T><Note>末步不同，不会重复；末步只有1或2，不会遗漏</Note></g>
 </>;
 if(t==='bases')return <>
  <Head kicker="现在求六阶" title="先从能直接数清的两个起点开始" sub="同一规则逐阶计算 · 问号表示尚未计算"/>
  <Board values={[1,2,null,null,null,null]} active={p>.85?[0,1]:[]}/>
  <g opacity={q}><T x={600} y={741} anchor="middle" size={33} color={C.teal}>第1阶：[1] → 1种</T><T x={1250} y={741} anchor="middle" size={33} color={C.teal}>第2阶：[1,1]、[2] → 2种</T></g>
  <Note>起点来自合法走法，不是先假设后面的计数</Note>
 </>;
 if(t==='grow'){
  const target=second?3:2,progress=second?q:p,values:(number|null)[]=[1,2,second||p>=.86?3:null,second&&q>=.86?5:null,null,null];
  return <><Head kicker="逐阶计算" title={second?'接着算第四阶：把3和2相加':'先算第三阶：把2和1相加'} sub="每次只看前两阶已经得到的方法数"/><Board values={values} active={[target-2,target-1]} target={target} progress={progress}/><Formula step={target+1} a={COUNTS[target-2]} b={COUNTS[target-1]} value={progress>=.72?COUNTS[target]:'?'} alpha={progress} settled={progress>=.86}/><Note>旧计数先合流，新结果再落到对应的阶</Note></>;
 }
 if(t==='thirteen'){
  const target=second?5:4,progress=second?q:p,values:(number|null)[]=[1,2,3,5,second||p>=.86?8:null,second&&q>=.86?13:null];
  return <><Head kicker="同一条六阶计数" title={second?'最后一步不同，两组相加得到十三':'先把第五阶的方法数算出来'} sub={second?'第5阶8种接上1阶；第4阶5种接上2阶':'第3阶3种 + 第4阶5种 = 第5阶8种'}/><Board values={values} active={[target-2,target-1]} target={target} progress={progress}/>{second&&<g opacity={q}><T x={nodeX(3)} y={655} size={28} anchor="middle" color={C.teal}>最后 +2</T><T x={nodeX(4)} y={655} size={28} anchor="middle" color={C.gold}>最后 +1</T></g>}<Formula step={target+1} a={COUNTS[target-2]} b={COUNTS[target-1]} value={progress>=.72?COUNTS[target]:'?'} alpha={progress} settled={progress>=.86}/><Note color={second&&q>=.86?C.teal:C.muted}>先算清8和5，再得到第6阶的13种走法</Note></>;
 }
 if(t==='dynamic-programming'){
  const introduced=f>=Number(s.cueFrames?.labels?.['动态规划']??sentence(s,1));
  return <><Head kicker="接着看：究竟要保存什么" title="算下一项，只需要前两项" sub={introduced?'动态规划 · 回到准备计算第6阶：复用前两项':'六阶答案已经得到，再回看每轮计算需要的信息'}/><Board values={introduced?[1,2,3,5,8,null]:COUNTS} active={introduced?[3,4]:[]} history={introduced} dim={mix(1,.24,q)}/>{introduced?<><T x={585} y={710} anchor="middle" size={30} alpha={q} color={C.muted}>第1–3阶：解释留痕，不必保存</T><T x={1340} y={710} anchor="middle" size={31} alpha={q} color={C.teal}>准备计算第6阶</T><Note alpha={q} color={C.gold}>本题的下一项，只依赖前两阶的方法数</Note></>:<Note>完整计数表方便看过程，但不是必需的内存</Note>}</>;
 }
 if(t==='rolling'){
  const sum=phase(s,f,1,.05,.33),change=phase(s,f,1,.57,.87),swapped=change>=.5,oldAlpha=clamp(1-2*change),newAlpha=clamp(2*change-1);
  return <><Head kicker="两个滚动变量" title="先用旧值求和，再整体换角色" sub={swapped?'更新后：两个变量分别对应第5阶与第6阶':'更新前：两个变量分别对应第4阶与第5阶'}/><Board y={420} values={[1,2,3,5,8,swapped?13:null]} active={swapped?[4,5]:[3,4]} history dim={.22}/><g opacity={sum}><T x={960} y={580} size={43} mono anchor="middle" color={C.gold}>旧值 5 + 8 = 13</T></g><Role x={620} name="prev" value={5} step={4} alpha={oldAlpha}/><Role x={1300} name="curr" value={8} step={5} alpha={oldAlpha} color={C.gold}/><Role x={620} name="prev" value={8} step={5} alpha={newAlpha}/><Role x={1300} name="curr" value={13} step={6} alpha={newAlpha} color={C.gold}/><Note color={swapped?C.teal:C.muted}>{swapped?'两项身份一起前移，下一轮仍只保留前两项':'求出13之前，旧的5和8都保持不变'}</Note></>;
 }
 if(t==='implementation'){
  const rightReady=q>=.52;
  return <><Head kicker="把过程写进程序" title="从第三阶循环到终点，右侧先求值" sub="n为1或2时直接返回；其余情况从已知的1和2开始"/>
   <rect x={175} y={315} width={1570} height={421} rx={24} fill={C.surface} stroke={C.edge}/>
   {['if n <= 2: return n','prev, curr = 1, 2','for step in range(3, n + 1):'].map((line,i)=><T key={line} x={235} y={385+i*64} mono size={36} color={i===2?C.text:C.muted}>{line}</T>)}
   <g opacity={q}><rect x={215} y={574} width={1485} height={102} rx={13} stroke={C.gold} strokeWidth={2} fill={C.gold+'06'}/><T x={255} y={640} mono size={38} color={C.gold}>prev, curr = curr, prev + curr</T></g>
   <g opacity={q}><T x={960} y={805} size={37} mono anchor="middle" color={rightReady?C.teal:C.gold}>{rightReady?'(8, 13) → prev, curr':'旧值 prev=5，curr=8 → (8, 5+8)'}</T><Note>右侧先用全部旧值算完，再赋给左侧两个变量</Note></g>
  </>;
 }
 if(t==='boundary')return <>
  <Head kicker="回收依赖与成本" title="两数够用，因为本题只依赖前两项" sub="每一级只计算一次 · 保存固定数量的变量"/>
  <Board values={COUNTS} active={[4,5]} history dim={.24}/>
  <g opacity={p}><T x={640} y={748} size={45} anchor="middle" color={C.teal}>时间 O(n)</T><T x={1290} y={748} size={45} anchor="middle" color={C.gold}>额外空间 O(1)</T></g><Note alpha={q} color={C.gold}>其他动态规划问题，未必也能只保存两个数</Note>
 </>;
 return <>
  <Head kicker="回应开头的问题" title="到第六阶，共有十三种走法" sub="不枚举全部路径，也不必保存整张计数表" color={C.teal}/>
  <Board active={[4,5]} history dim={.24}/>
  <T x={960} y={740} size={35} anchor="middle" color={C.text}>按最后一步分组 → 前两项相加 → 滚动保留两数</T><Note alpha={q}>接下来是完整程序，需要细看请暂停</Note>
 </>;
};
const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null;
 const card=codeCardFrom!==null&&f>=codeCardFrom,sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  <defs><radialGradient id="lc70-bg"><stop offset="0" stopColor="#173B55" stopOpacity=".28"/><stop offset="1" stopColor={C.bg} stopOpacity="0"/></radialGradient></defs><ellipse cx="1440" cy="280" rx="950" ry="700" fill="url(#lc70-bg)"/>
  {card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}
  <T x={1790} y={91} size={25} color={C.muted} anchor="end">IT小村</T>
  <T x={120} y={1015} size={20} color={C.muted} alpha={.65}>{card?'LeetCode 70 · Python 3':'LeetCode 70 · 教学示例'}</T>
 </svg>{!hideSubtitles&&!card&&subtitle&&<div style={{position:'absolute',left:210,right:210,bottom:69,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
