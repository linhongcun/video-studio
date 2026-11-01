import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,MAIN_NUMS,DUPLICATE_NUMS} from './data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
const at=(s:Shot,i:number,p:number)=>{
 const start=Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
 const end=Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10);
 return start+(end-start)*p;
};
const phase=(s:Shot,f:number,i=0,a=.05,b=.8)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const T=({x,y,children,size=31,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='两数之和',color=C.text}:any)=><g><T x={120} y={101} size={24} color={C.muted}>{kicker}</T><T x={120} y={184} size={51} color={color} weight={760}>{title}</T>{sub&&<T x={120} y={244} size={27} color={C.muted}>{sub}</T>}</g>;
const Note=({children,color=C.muted,alpha=1,y=895}:any)=><T x={960} y={y} size={30} color={color} alpha={alpha} anchor="middle">{children}</T>;
const num=(n:number)=>String(n).replace('-', '−');
const ax=(i:number,count:number,wide=false)=>wide?420+i*270:count===3?350+i*260:230+i*195;
const ArrayView=({nums=MAIN_NUMS,current=-1,visited=-1,pair=[],pairAlpha=1,wide=false,showIndex=true,indexAlpha=1,unvisitedLabel=false}:any)=><g data-array={nums.join(',')}>
 {nums.map((n:number,i:number)=>{
  const active=i===current,chosen=pair.includes(i),xx=ax(i,nums.length,wide),yy=wide?435:380,ww=wide?172:146;
  return <g key={i} data-array-index={i} data-array-value={n} data-visited={i<=visited}>
   <rect x={xx-ww/2} y={yy} width={ww} height={132} rx={17} fill={C.surface} stroke={active?C.gold:i<=visited?C.teal:C.edge} strokeWidth={active?4:2}/>
   <T x={xx} y={yy+91} anchor="middle" size={68} color={active?C.gold:C.text} mono>{n}</T>
   {chosen&&<rect x={xx-ww/2-5} y={yy-5} width={ww+10} height={142} rx={20} fill={C.teal+'0B'} stroke={C.teal} strokeWidth={4} opacity={pairAlpha}/>}
   {showIndex&&<T x={xx} y={yy+181} anchor="middle" size={29} color={chosen?C.teal:C.muted} alpha={indexAlpha} mono>{i}</T>}
   {active&&<g><T x={xx} y={yy-48} anchor="middle" size={28} color={C.gold}>当前下标 {i}</T><path d={`M ${xx} ${yy-32} V ${yy-12} m -8 -9 l 8 9 l 8 -9`} fill="none" stroke={C.gold} strokeWidth={3}/></g>}
   {unvisitedLabel&&i>current&&<T x={xx} y={yy+232} anchor="middle" size={23} color={C.muted}>未访问</T>}
  </g>;
 })}
 {showIndex&&<T x={wide?218:118} y={(wide?435:380)+181} size={24} color={C.muted} alpha={indexAlpha}>下标</T>}
</g>;
type Entry={value:number;index:number;alpha?:number};
const HashTable=({entries=[],highlight=null,hitAlpha=0,introduced=true}: {entries?:Entry[];highlight?:number|null;hitAlpha?:number;introduced?:boolean})=><g data-hash-table="value-to-prior-index">
 <rect x={1275} y={302} width={510} height={462} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
 <T x={1310} y={351} size={29} color={C.teal}>{introduced?'哈希表':'先前记录'}</T>
 <T x={1745} y={351} anchor="end" size={22} color={C.muted}>按值直接查询</T>
 <T x={1410} y={400} anchor="middle" size={24} color={C.muted}>数值</T><T x={1645} y={400} anchor="middle" size={24} color={C.muted}>先前下标</T>
 {entries.length===0&&<g><T x={1530} y={518} size={34} anchor="middle" color={C.muted}>暂无记录</T><T x={1530} y={575} size={25} anchor="middle" color={C.muted}>查询会得到“未记录”</T></g>}
 {entries.map((entry,i)=><g key={entry.value} opacity={entry.alpha??1} data-map-key={entry.value} data-map-index={entry.index}>
  <rect x={1307} y={427+i*91} width={446} height={73} rx={12} fill={C.bg} stroke={highlight===entry.value?C.teal:C.edge} strokeOpacity={highlight===entry.value?.4+.6*hitAlpha:1} strokeWidth={highlight===entry.value?3:1}/>
  <T x={1410} y={479+i*91} size={42} anchor="middle" color={highlight===entry.value?C.teal:C.text} mono>{entry.value}</T>
  <T x={1524} y={476+i*91} size={31} anchor="middle" color={C.muted}>→</T>
  <T x={1645} y={479+i*91} size={42} anchor="middle" color={highlight===entry.value?C.teal:C.text} mono>{entry.index}</T>
 </g>)}
 <T x={1530} y={730} size={23} anchor="middle" color={C.muted}>这里只保存先前位置</T>
</g>;
const Result=({pair=[0,3],alpha=1,y=790}:any)=><g opacity={alpha} data-return-pair={pair.join(',')}>
 <rect x={360} y={y-67} width={600} height={106} rx={20} fill={C.surface} stroke={C.teal} strokeWidth={2}/>
 <T x={550} y={y} size={32} anchor="middle" color={C.muted}>返回下标</T><T x={780} y={y+4} size={55} anchor="middle" color={C.teal} mono>{`[${pair.join(', ')}]`}</T>
</g>;
type ProcessProps={nums?:number[];target?:number;current:number;entries:Entry[];need:number;calc?:number;query?:number;feedback?:number;insert?:Entry|null;insertP?:number;hit?:number|null;found?:number;result?:number[];note?:string};
const Process=({nums=MAIN_NUMS,target=9,current,entries,need,calc=1,query=0,feedback=0,insert=null,insertP=0,hit=null,found=0,result=[0,current],note}:ProcessProps)=>{
 const shown=[...entries,...(insert&&insertP>0?[{...insert,alpha:insertP}]:[])];
 return <>
  <ArrayView nums={nums} current={current} visited={current-1} pair={found>0?result:[]} pairAlpha={found} unvisitedLabel={found>0}/>
  <HashTable entries={shown} highlight={feedback>0&&hit!==null?need:null} hitAlpha={feedback}/>
  <g opacity={calc}><T x={230} y={639} size={26} color={C.muted}>目标 {target} · 需要的另一个数值</T><T x={560} y={720} size={58} anchor="middle" color={C.gold} mono>{`${target} − ${nums[current]} = ${num(need)}`}</T></g>
  <g opacity={query} data-query-key={need}><rect x={890} y={657} width={245} height={83} rx={15} fill={C.gold+'0B'} stroke={C.gold} strokeWidth={2}/><T x={1012} y={710} size={30} anchor="middle" color={C.gold}>查询 {num(need)}</T><path d="M 1148 699 H 1245 m -11 -8 l 11 8 l -11 8" fill="none" stroke={C.gold} strokeWidth={3}/></g>
  {feedback>0&&<g opacity={feedback} data-query-result={hit===null?'missing':'found'}><T x={1518} y={829} size={34} anchor="middle" color={hit===null?C.gold:C.teal}>{hit===null?`${num(need)} 未记录`:`查到 ${need} → 下标 ${hit}`}</T></g>}
  {insert&&<T x={1518} y={884} size={27} anchor="middle" color={C.teal} alpha={insertP}>{`再记录 ${insert.value} → ${insert.index}`}</T>}
  {found>0&&<Result pair={result} alpha={found} y={840}/>}
  {note&&<T x={660} y={found>0?914:862} size={28} anchor="middle" color={C.muted}>{note}</T>}
 </>;
};
const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 if(t==='approach-pairs'){
  const second=f>=Number(s.cueFrames?.sentences?.[1]??s.durationInFrames*.5);
  const current=second?2:1,candidate=second&&q>=.52?1:0;
  const trialProgress=second?(candidate===0?clamp(q/.42):clamp((q-.52)/.42)):p;
  const tests=second?[['3 + 8 = 11',true],['3 + 11 = 14',candidate===1||trialProgress>.7],['8 + 11 = 19',candidate===1&&trialProgress>.7]]:[['3 + 8 = 11',trialProgress>.7]];
  const start=ax(current,MAIN_NUMS.length),end=ax(candidate,MAIN_NUMS.length);
  return <><Head kicker="先从题目条件入手" title="最直接：拿两个位置，逐个相加试试" sub="方法推导 · 每来一个新数，看看哪些先前位置能与它配对"/>
   <ArrayView current={current} visited={current-1}/>
   <rect x={end-78} y={375} width={156} height={142} rx={20} fill="none" stroke={C.blue} strokeWidth={4}/>
   <path d={`M ${start} 585 C ${start} 647, ${end} 647, ${end} 585`} pathLength={1} strokeDasharray="1" strokeDashoffset={1-trialProgress} fill="none" stroke={C.blue} strokeWidth={3}/>
   <g opacity={clamp((trialProgress-.4)/.3)}><T x={660} y={724} size={53} anchor="middle" color={C.gold} mono>{`${MAIN_NUMS[candidate]} + ${MAIN_NUMS[current]} = ${MAIN_NUMS[candidate]+MAIN_NUMS[current]}`}</T>
    <T x={660} y={795} size={33} anchor="middle" color={C.muted}>和不等于目标 9，还得继续找</T></g>
   <g data-approach="candidate-pair-trials"><rect x={1275} y={302} width={510} height={462} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <T x={1310} y={352} size={29} color={C.blue}>这里尝试过的数对</T>
    {tests.map(([label,shown],i)=><g key={String(label)} opacity={shown?1:0}><T x={1530} y={444+i*86} anchor="middle" size={36} mono>{String(label)}</T><T x={1530} y={481+i*86} anchor="middle" size={24} color={C.muted}>不等于目标 9</T></g>)}
    <T x={1530} y={729} size={25} anchor="middle" color={C.muted}>前面有几格，就可能尝试几对</T>
   </g>
   <Note>换到下一个数，又可能扫描许多先前位置</Note>
  </>;
 }
 if(t==='approach-complement')return <><Head kicker="把要找的东西先确定下来" title="当前值固定，另一个值已经确定" sub="方法推导 · 假设走到下标 3 的 6；此时先前有 3、8、11"/>
  <ArrayView current={3} visited={2} pair={q>=.7?[0]:[]} unvisitedLabel/>
  <path d="M 157 345 V 318 H 693 V 345" fill="none" stroke={C.teal} strokeWidth={2}/><T x={425} y={301} anchor="middle" size={26} color={C.teal}>先前位置 0、1、2</T>
  <g opacity={p}><T x={660} y={673} size={29} anchor="middle" color={C.muted}>目标减去当前值，就是需要的另一个值</T><T x={660} y={759} size={62} anchor="middle" color={C.gold} mono>9 − 6 = 3</T></g>
  <g opacity={q} data-approach="complement-query"><rect x={1275} y={302} width={510} height={462} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
   <T x={1530} y={361} anchor="middle" size={28} color={C.muted}>新的问题只有一个</T><T x={1530} y={470} anchor="middle" size={43} color={C.gold}>先前出现过 3 吗？</T><T x={1530} y={545} anchor="middle" size={31} color={C.muted}>若出现过，它在哪个下标？</T><T x={1530} y={658} anchor="middle" size={44} color={C.teal} alpha={q>=.7?1:0}>这里是下标 0</T>
  </g>
  <Note>不用再猜另一个数，只需查询已确定的需要值</Note>
 </>;
 if(t==='approach-choice'){
  const introduced=f>=Number(s.cueFrames?.labels?.['哈希表']??s.cueFrames?.sentences?.[1]??0);
  const reset=phase(s,f,1,.3,.74),official=reset>=1;
  const entries=official?[]:[{value:3,index:0,alpha:p*(1-reset)},{value:8,index:1,alpha:p*(1-reset)},{value:11,index:2,alpha:p*(1-reset)}];
  return <><Head kicker={official?'正式执行 · 从头开始':'让记录回答刚才的问题'} title={official?'方法选定，清空记录从头执行':'按值留下位置，下一次就能查询'} sub={introduced?'哈希表 · 按数值查询先前下标':'方法推导 · 需要的记录是“数值 → 先前下标”'}/>
   <ArrayView current={official?0:3} visited={official?-1:2}/>
   <HashTable entries={entries} introduced={introduced} highlight={introduced&&!official?3:null} hitAlpha={1-reset}/>
   {!official?<g opacity={1-reset}><T x={660} y={702} size={41} anchor="middle" color={C.gold}>需要数值 3，就查询它的先前下标</T><T x={660} y={778} size={32} anchor="middle" color={C.teal}>记住数值和位置，供后面的数使用</T></g>:<g><T x={660} y={701} size={42} anchor="middle" color={C.gold}>空表 · 当前下标 0，数值 3</T><T x={660} y={779} size={32} anchor="middle" color={C.teal}>先查需要的值，没查到才记录当前值</T></g>}
   <Note color={official?C.teal:C.muted}>{official?'下面从第一个数开始，完整执行一遍':'这里在推导记录方式，下一步清空后正式执行'}</Note>
  </>;
 }
 if(t==='problem')return <><Head kicker="LeetCode 1 · 先看题目" title="两数相加等于 9，选哪两格？" sub="输入示例 · 整数数组 [3,8,11,6,15] · 目标 9"/><ArrayView wide showIndex={q>0} indexAlpha={q}/><T x={960} y={768} size={42} anchor="middle" color={C.gold}>选两个数，让它们相加等于目标</T><Note color={C.gold} alpha={q}>必须选两个不同下标 · 同一格不能用两次</Note></>;
 if(t==='output')return <><Head kicker="LeetCode 1 · 题目要求" title="返回这两格的下标，不是数值" sub="下标从 0 开始 · 数值 3 + 6 = 9"/><ArrayView wide pair={[0,3]} pairAlpha={p}/><T x={960} y={754} size={56} anchor="middle" color={C.teal} mono alpha={p}>返回 [0, 3]</T><T x={960} y={832} size={29} anchor="middle" color={C.muted} alpha={q}>恰好一组答案 · 返回 [3, 0] 也可以</T><Note>两个不同位置可以存放相同的值</Note></>;
 if(t==='lookup'){
  const intro=f>=Number(s.cueFrames?.labels?.['哈希表']??s.cueFrames?.sentences?.[1]??0);
  return <><Head kicker="题意清楚了，再看方法" title="当前的数，需要和谁配对？" sub={intro?'哈希表 · 数值 → 先前下标':'目标减去当前值，就是需要的另一个数值'}/>
   <ArrayView current={0}/><g opacity={p}><T x={660} y={701} size={58} anchor="middle" color={C.gold} mono>9 − 3 = 6</T><T x={660} y={770} size={30} anchor="middle" color={C.muted}>需要的数值：6</T></g>
   {intro&&<g opacity={q}><HashTable/><T x={660} y={856} size={29} anchor="middle" color={C.teal}>先查需要的值 → 没查到，再记录当前值</T></g>}
  </>;
 }
 if(['first','second','negative'].includes(t)){
  const current=t==='first'?0:t==='second'?1:2,need=9-MAIN_NUMS[current],prior=[{value:3,index:0},{value:8,index:1}].slice(0,current),insert={value:MAIN_NUMS[current],index:current};
  return <><Head title={t==='first'?'先查 6：空表里没有记录':t==='second'?'先查 1，再记录当前的 8':'需要负二，也能正常查询'} sub={`教学示例 · 目标 9 · 当前下标 ${current}，数值 ${MAIN_NUMS[current]}`}/>
   <Process current={current} entries={prior} need={need} calc={phase(s,f,0,.02,.25)} query={phase(s,f,0,.26,.48)} feedback={phase(s,f,0,.53,.78)} insert={insert} insertP={phase(s,f,1,.18,.72)} note={t==='negative'?'−2 是需要的数值，不是数组下标':'先得到“未记录”，才能写入当前值'}/>
  </>;
 }
 if(t==='found')return <><Head title="需要 3，这次查到了先前下标 0" sub="教学示例 · 当前下标 3，数值 6 · 后面的 15 不用访问"/><Process current={3} entries={[{value:3,index:0},{value:8,index:1},{value:11,index:2}]} need={3} calc={phase(s,f,0,.02,.22)} query={phase(s,f,0,.24,.42)} feedback={phase(s,f,0,.48,.78)} hit={0} found={phase(s,f,1,.1,.62)} result={[0,3]}/></>;
 if(t==='reset'){
  const reset=phase(s,f,1,.04,.65),ready=reset>=1;
  return <><Head kicker="接着看：重复值与不同下标" title={ready?'新输入：两个 3 来自不同位置':'刚才找到答案，再换一个输入'} sub={ready?'新输入 · [3,8,3] · 目标 6 · 表重新清空':'刚才：[3,8,11,6,15]，目标 9，返回 [0,3]'}/>
   {!ready?<g opacity={1-reset}><ArrayView nums={MAIN_NUMS} current={3} visited={2} pair={[0,3]}/><HashTable entries={[{value:3,index:0},{value:8,index:1},{value:11,index:2}]}/><Result pair={[0,3]} y={800}/></g>:<><ArrayView nums={DUPLICATE_NUMS}/><HashTable/><T x={660} y={724} size={54} anchor="middle" color={C.gold}>目标改成 6</T><T x={660} y={810} size={31} anchor="middle" color={C.muted}>清空记录，从下标 0 重新开始</T></>}
   <Note alpha={reset} color={C.gold}>这是一个独立的新示例</Note>
  </>;
 }
 if(t==='duplicate-first')return <><Head title="第一个 3，需要另一个 3" sub="新输入 · [3,8,3] · 目标 6 · 查询时表仍为空"/><Process nums={DUPLICATE_NUMS} target={6} current={0} entries={[]} need={3} calc={phase(s,f,0,.02,.22)} query={phase(s,f,0,.24,.42)} feedback={phase(s,f,0,.48,.78)} insert={{value:3,index:0}} insertP={phase(s,f,1,.18,.72)} note="不能用下标 0 和它自己配对"/></>;
 if(t==='duplicate-found'){
  const second=f>=Number(s.cueFrames?.sentences?.[1]??s.durationInFrames*.5);
  if(!second)return <><Head title="先处理 8：需要 −2，没有记录" sub="新输入 · 目标 6 · 表中已经保存 3 → 0"/><Process nums={DUPLICATE_NUMS} target={6} current={1} entries={[{value:3,index:0}]} need={-2} calc={phase(s,f,0,.01,.12)} query={phase(s,f,0,.14,.27)} feedback={phase(s,f,0,.32,.45)} insert={{value:8,index:1}} insertP={phase(s,f,0,.52,.8)} note="查询结果先出现，再记录 8 → 1"/></>;
  return <><Head title="最后的 3，查到先前的 3" sub="同值，来自不同位置 · 命中后直接返回，不覆盖旧下标"/><Process nums={DUPLICATE_NUMS} target={6} current={2} entries={[{value:3,index:0},{value:8,index:1}]} need={3} calc={phase(s,f,1,.01,.12)} query={phase(s,f,1,.14,.27)} feedback={phase(s,f,1,.32,.48)} hit={0} found={phase(s,f,1,.55,.8)} result={[0,2]}/></>;
 }
 if(t==='order'){
  const wrong=f>=Number(s.cueFrames?.sentences?.[1]??s.durationInFrames*.5),write=phase(s,f,1,.04,.25),query=phase(s,f,1,.31,.5),bad=phase(s,f,1,.56,.83);
  return <><Head kicker="把规则写进程序" title="先查再记，配对下标一定不同" sub="查询命中：直接返回 · 未命中：才记录当前位置"/>
   <rect x={160} y={324} width={730} height={420} rx={22} fill={C.surface} stroke={C.edge}/><T x={205} y={387} size={28} color={C.muted}>正确顺序</T>
   <T x={225} y={486} size={39} color={C.gold} mono>if need in seen:</T><T x={225} y={547} size={29} color={C.muted}>先查询 · 命中就返回</T><path d="M 240 580 V 610 m -8 -9 l 8 9 l 8 -9" fill="none" stroke={C.teal} strokeWidth={3}/><T x={225} y={669} size={39} color={C.teal} mono>seen[x] = i</T>
   {!wrong?<g opacity={p}><T x={1360} y={418} size={35} anchor="middle" color={C.teal}>表里只保存先前下标</T><T x={1360} y={535} size={63} anchor="middle" color={C.teal} mono>先前下标 &lt; i</T><T x={1360} y={638} size={31} anchor="middle" color={C.muted}>命中位置必定不同于当前格</T></g>:<g><rect x={995} y={324} width={760} height={420} rx={22} fill={C.red+'07'} stroke={C.red}/><T x={1035} y={383} size={27} color={C.red}>错误顺序假设 · 回看新例下标 0</T><T x={1375} y={456} size={30} anchor="middle" color={C.muted}>当前 3，需要 3 · 假设表从空开始</T><T x={1375} y={531} size={39} anchor="middle" color={C.gold} alpha={write}>先记录 3 → 0</T><T x={1375} y={592} size={31} anchor="middle" color={C.gold} alpha={query}>再查 3：查到了自己</T><g opacity={bad}><T x={1375} y={680} size={47} anchor="middle" color={C.red} mono>错误 [0, 0]</T><path d="M 1240 657 L 1510 688" stroke={C.red} strokeWidth={5}/></g></g>}
   <Note color={wrong?C.red:C.teal}>{wrong?'两次使用同一格，违反题目要求':'先查 → 只与先前位置配对；未命中 → 再记录'}</Note>
  </>;
 }
 return <><Head kicker="回收结论" title="先查，再记录：让下标天然不同" sub="哈希表按值查询 · 每个数组元素最多访问一次" color={C.teal}/>
  <g><rect x={180} y={330} width={480} height={240} rx={22} fill={C.surface} stroke={C.gold}/><T x={420} y={400} anchor="middle" size={31} color={C.muted}>先查询需要的数值</T><T x={420} y={492} anchor="middle" size={44} color={C.gold}>只配对先前下标</T></g>
  <g><rect x={720} y={330} width={480} height={240} rx={22} fill={C.surface} stroke={C.teal}/><T x={960} y={400} anchor="middle" size={31} color={C.muted}>没有找到</T><T x={960} y={492} anchor="middle" size={44} color={C.teal}>再记录当前下标</T></g>
  <g><rect x={1260} y={330} width={480} height={240} rx={22} fill={C.surface} stroke={C.teal}/><T x={1500} y={400} anchor="middle" size={31} color={C.muted}>查询命中</T><T x={1500} y={492} anchor="middle" size={44} color={C.teal}>直接返回下标对</T></g>
  <g opacity={p}><T x={610} y={704} size={46} anchor="middle" color={C.teal}>平均时间 O(n)</T><T x={1320} y={704} size={46} anchor="middle" color={C.blue}>额外空间 O(n)</T><T x={960} y={774} size={27} anchor="middle" color={C.muted}>表中最多保存随输入长度增长的记录</T></g>
  <Note alpha={q}>接下来是完整 Python 解法，需要细看请暂停</Note>
 </>;
};
const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null;
 const card=codeCardFrom!==null&&f>=codeCardFrom,sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  <defs><radialGradient id="lc1-bg"><stop offset="0" stopColor="#173B55" stopOpacity=".25"/><stop offset="1" stopColor={C.bg} stopOpacity="0"/></radialGradient></defs><ellipse cx="1420" cy="280" rx="950" ry="700" fill="url(#lc1-bg)"/>
  {card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}
  <T x={1790} y={91} size={25} color={C.muted} anchor="end">IT小村</T><T x={120} y={1015} size={20} color={C.muted} alpha={.65}>{card?'LeetCode 1 · Python 3':'LeetCode 1 · 教学示例'}</T>
 </svg>{!hideSubtitles&&!card&&subtitle&&<div style={{position:'absolute',left:210,right:210,bottom:69,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
