import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {TRACE,EVENTS,Shot,Item,STORYBOARD,shots} from './data';
import {at,clamp,ease,play as playEvents,fixed as fixedEvent,Playback} from './timeline';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
declare const __HAS_VOICE_AUDIO__:boolean;
const Text=({x,y,size=29,color=C.text,children,anchor='start',weight=500,opacity=1,mono=false,...rest}:any)=><text data-qa-text="true" x={x} y={y} fontSize={size} fill={color} textAnchor={anchor} fontWeight={weight} opacity={opacity} fontFamily={mono?MONO:FONT} {...rest}>{children}</text>;
const Panel=({x=100,y=285,w=1720,h=600,children}:any)=><g><rect x={x} y={y} width={w} height={h} rx={26} fill={C.surface} stroke={C.edge} strokeWidth={1.5}/>{children}</g>;
const Note=({children,color=C.gold}:any)=><Text x={960} y={935} size={28} color={color} anchor="middle">{children}</Text>;
const POS=[[1270,425],[1050,625],[1490,625],[920,810]];
const fixed=(id:number)=>fixedEvent(id,EVENTS);
const play=(s:Shot,f:number)=>playEvents(s,f,EVENTS);
const itemLabel=(item:Item)=>`${item[1]} × ${item[0]}`;
function ArrayInput({highlight=-1,y=370}:any){return <g>{TRACE.sample.map((n,i)=><g key={i}><rect x={154+i*101} y={y} width={88} height={76} rx={12} fill={highlight===i?C.gold+'22':C.bg} stroke={highlight===i?C.gold:C.edge} strokeWidth={highlight===i?3:1.5}/><Text x={198+i*101} y={y+51} size={36} mono anchor="middle" color={highlight===i?C.gold:C.text}>{n}</Text><Text x={198+i*101} y={y+105} size={20} mono anchor="middle" color={C.muted}>{i}</Text></g>)}</g>;}
function CountTable({pb,showState=true,processed=6}:any){const e=pb?.event,retained=new Set((e?.heap??[]).map((v:Item)=>v[1]));if(e?.kind==='remove-root')retained.delete(e.removed[1]);return <Panel x={100} w={590}><Text x={140} y={334} size={28} weight={650}>示例计数表</Text><Text x={275} y={384} size={24} color={C.muted}>数字</Text><Text x={468} y={384} size={24} color={C.muted}>出现次数</Text>{TRACE.counts.map((v,i)=>{const active=e?.candidate===v.num||e?.removed?.[1]===v.num,color=active?C.gold:retained.has(v.num)?C.teal:C.text;return <g key={v.num} opacity={i<processed?1:.24}><rect x={137} y={407+i*69} width={516} height={58} rx={12} fill={active?C.gold+'12':C.bg} stroke={active?C.gold:C.edge} strokeWidth={active?2:1}/><Text x={305} y={448+i*69} anchor="middle" size={30} mono color={color}>{v.num}</Text><Text x={508} y={448+i*69} anchor="middle" size={30} mono color={color}>{v.cnt}</Text>{showState&&retained.has(v.num)&&<Text x={163} y={445+i*69} size={22} color={C.teal}>留</Text>}</g>;})}<Text x={142} y={860} size={23} color={C.muted}>节点中：数字 × 出现次数</Text></Panel>;}
function Tree({pb,title='候选的小顶堆',showRule=false,named=true,showFill=false,schematic=false}: {pb:Playback;title?:string;showRule?:boolean;named?:boolean;showFill?:boolean;schematic?:boolean}){
 const {event:e,p}=pb;let current=e.heap,previous=e.before;
 // Deletion has a visible empty root; the last node stays put until replacement.
 if(e.kind==='remove-root')current=e.before;
 if(e.kind==='replace-root'){const prev=TRACE.events[e.id-1];previous=prev.before;}
 const highlighted=new Set(e.indices??[]),removed=e.removed?.[1];
 const moves=['swap-up','swap-down','replace-root'].includes(e.kind),append=e.kind==='append';
 const n=e.kind==='remove-root'?e.before.length-1:e.heap.length;
 const desc:Record<string,string>={init:'初始为空',append:'先放在最后一个位置','compare-up':'只与它的父节点比较','swap-up':'次数更少，向上交换','push-done':'插入结束：父次数 ≤ 孩子次数','remove-root':`删除堆顶：${removed??''}（${e.removed?.[0]??''}次）`,'replace-root':'最后一个节点补到堆顶','compare-children':'先找两个孩子中次数更少的','compare-down':'再比较父节点与这个孩子','swap-down':'父次数更大，向下交换','pop-done':'删除结束：恢复父 ≤ 孩子'};
 const displayNum=e.kind==='remove-root'?e.before.length:n;
 const invariant=e.heap.every((item,i)=>i===0||e.heap[Math.floor((i-1)/2)][0]<=item[0]);
 const settled=invariant&&p>.99&&['push-done','pop-done'].includes(e.kind);
 const rootText=!named?'顶端 · 次数最少':!e.heap.length?'堆顶位置':e.kind==='remove-root'?'堆顶 · 删除中':settled?'堆顶 · 次数最少':'堆顶 · 待调整';
 return <Panel x={725} w={1095}><Text x={770} y={334} size={29} weight={650}>{title}</Text><Text x={1770} y={334} size={25} anchor="end" color={n>3?C.gold:C.teal}>{n} 个节点{n>3?' · 暂时超过 k':''}</Text>
  {Array.from({length:Math.max(0,displayNum-1)},(_,i)=>i+1).map(i=>{const [x,y]=POS[i],[px,py]=POS[Math.floor((i-1)/2)];return <line key={i} x1={px} y1={py+40} x2={x} y2={y-41} stroke={showRule?C.teal:C.edge} strokeWidth={showRule?4:3}/>;})}
  <Text x={1270} y={363} size={23} anchor="middle" color={C.gold}>{rootText}</Text>
  {current.map((item,i)=>{const old=previous.findIndex(v=>v[1]===item[1]),start=old<0?[1700,800]:POS[old],target=POS[i],t=moves?p:1,dx=target[0]-start[0],dy=target[1]-start[1],distance=Math.hypot(dx,dy),arc=moves&&distance>0?Math.sin(Math.PI*t)*(e.kind==='replace-root'?150:100):0,x=start[0]+dx*t+(distance?-dy/distance*arc:0),y=start[1]+dy*t+(distance?dx/distance*arc:0),hidden=e.kind==='remove-root'&&i===0,opacity=hidden?1-p:append&&i===current.length-1?p:1,active=highlighted.has(i),color=active?C.gold:C.teal;return <g key={item[1]} transform={`translate(${x} ${y})`} opacity={opacity} data-node-num={item[1]} data-node-frequency={item[0]} data-node-slot={i}><rect x={-87} y={-42} width={174} height={84} rx={19} fill={C.bg} stroke={color} strokeWidth={active?3.5:2}/><Text x={0} y={13} size={34} mono anchor="middle" color={color} weight={650}>{itemLabel(item)}</Text>{e.kind==='compare-children'&&i===e.chosen&&<Text x={0} y={78} size={23} anchor="middle" color={C.gold}>选次数更少的</Text>}</g>;})}
  {showFill&&<Text x={770} y={797} size={25} color={C.muted}>填位：顶端 → 下一层左 → 下一层右 → 再下一层</Text>}
  <Text x={1770} y={856} size={25} anchor="end" color={C.gold}>{schematic?'结构示意：父的次数 ≤ 孩子的次数':desc[e.kind]}</Text>
 </Panel>;
}
const HEADERS:Record<string,[string,string]>={
 problem:['只找最高频的 3 个数字，需要排完所有数字吗？','输入数组 nums 与 k；按出现次数比较，返回 k 个不同数字'],
 count:['先数清楚，每个数字出现几次','输入有 16 个位置；相同数字的次数累加到一行'],
 'keep-k':['只要 3 个结果，为什么一直保留全部候选？','处理一个新数字时，先加入候选，再从 4 个里留下 3 个'],
 'discard-min':['该删谁？当前次数最少的那个','已有 3 个次数不低于它的候选；以后不会再需要它'],
 'parent-rule':['怎样快速找到次数最少的候选？','把候选排成树：每个父节点的次数，不大于自己的孩子'],
 name:['小顶堆：让次数最少的候选留在顶端','下面从空堆开始，按计数表逐行加入数字'],
 'push-two':['加入数字 2：先放末尾，再比较父节点','2 出现 2 次；父节点 1 出现 3 次'],
 'push-three':['加入数字 3：次数更少，继续向上','比较的是出现次数，节点里的数字用于区分对象'],
 'push-four':['加入数字 4：先暂时保留 4 个节点','4 次不小于父节点的 3 次，因此留在末尾'],
 'pop-three':['超过 k=3：删除次数最少的堆顶','先删根，再用最后一个节点补上空位'],
 'push-five':['加入数字 5：先放到末尾','5 次不小于父节点的 3 次，不用向上交换'],
 'pop-two':['再次超过 k：删除数字 2','末位补根后，与次数更少的孩子比较'],
 'push-six':['加入数字 6：只有 1 次，逐层上浮','先与 5 的 5 次比较，再与 1 的 3 次比较'],
 'pop-six':['新来的数字 6，自己被淘汰','低频候选进来，也会成为最先删除的堆顶'],
 code:['把刚才的动作，写成两步代码','堆里保存（出现次数，数字）；先按次数比较'],
 closing:['最终留下 1、4、5，返回顺序不限','先统计，再维护 k 个候选；不需要把全部数字排完序'],
};
function Scene({shot:s}:{shot:Shot}){
 const f=useCurrentFrame(),t=s.visualType,second=f>=at(s,1,0),p=ease((f-at(s,0,.08))/Math.max(1,at(s,0,.84)-at(s,0,.08))),q=ease((f-at(s,1,.08))/Math.max(1,at(s,1,.8)-at(s,1,.08)));
 if(s.codeCardFrom!==undefined&&f>=s.codeCardFrom)return <><CodeCard/><LeetcodeHeader slug="top-k-frequent-elements" identity={{number:347,method:'小顶堆'}} compact/></>;
 let pb=play(s,f),body:React.ReactNode=null,note:React.ReactNode='每个节点显示“数字 × 次数”；只按出现次数决定高低';
 if(t==='problem'){
  body=<Panel><Text x={150} y={335} size={29} color={C.muted}>示例 nums =</Text><ArrayInput/><Text x={180} y={605} size={42} color={C.gold}>k = 3</Text><Text x={180} y={690} size={32}>找出现次数最高的 3 个不同数字</Text><g opacity={q}><Text x={1050} y={615} size={28} color={C.muted}>本例可以返回</Text><Text x={1050} y={700} size={57} mono color={C.teal}>[1, 4, 5]</Text><Text x={1050} y={763} size={27} color={C.muted}>返回数字本身 · 顺序不限</Text></g></Panel>;note='按频次选数字；不是按数字大小，也不是返回出现次数';
 }else if(t==='count'){
  const index=second?Math.min(15,6+Math.floor(q*10)):Math.min(5,Math.floor(p*6)),partial=TRACE.counts.map(v=>TRACE.sample.slice(0,index+1).filter(n=>n===v.num).length);body=<Panel><Text x={150} y={335} size={28} color={C.muted}>示例数组：从左向右数</Text><ArrayInput highlight={index} y={365}/>{TRACE.counts.map((v,i)=><g key={v.num}><rect x={185+i*264} y={590} width={230} height={210} rx={20} fill={C.bg} stroke={C.edge}/><Text x={300+i*264} y={645} size={30} anchor="middle" color={C.muted}>数字 {v.num}</Text><Text x={300+i*264} y={727} size={56} mono anchor="middle" color={C.teal}>{partial[i]}</Text><Text x={300+i*264} y={776} size={25} anchor="middle" color={C.muted}>次</Text></g>)}</Panel>;note='计数完成后，每个不同数字只处理一次';
 }else if(t==='keep-k'||t==='discard-min'){
  const showFour=second||t==='discard-min',arr=t==='keep-k'?[[3,1],[2,2],[1,3],[4,4]]:[[3,1],[2,2],[1,3],[4,4]];
  body=<><CountTable showState={false}/><Panel x={725} w={1095}><Text x={775} y={345} size={30} color={C.muted}>只比较当前候选 · 不做完整排序</Text>{arr.map((v,i)=><g key={v[1]} opacity={i===3&&!showFour?0:t==='discard-min'&&i===2&&second?1-q:1}><rect x={800+(i%2)*480} y={415+Math.floor(i/2)*170} width={400} height={125} rx={22} fill={C.bg} stroke={t==='discard-min'&&i===2?C.gold:C.edge} strokeWidth={t==='discard-min'&&i===2?3:2}/><Text x={1000+(i%2)*480} y={493+Math.floor(i/2)*170} size={43} mono anchor="middle" color={t==='discard-min'&&i===2?C.gold:C.teal}>{itemLabel(v)}</Text></g>)}<Text x={1270} y={835} size={31} color={C.gold} anchor="middle">{t==='keep-k'?'先加入 4 × 4，再从 4 个里留 3 个':'删 3 × 1：其他 3 个的次数都更高'}</Text></Panel></>;note=t==='keep-k'?'这里只推导需要哪些操作；还没有开始正式建堆':'保留“已处理数字中”的前三名；继续加入新的候选';
 }else if(t==='parent-rule'){
  pb=fixed(10);body=<><CountTable pb={pb} showState={false}/><Tree pb={pb} title="结构示意：用父子关系找最少次数" showRule={second} named={false} schematic/><g opacity={q}><Text x={1270} y={520} size={26} anchor="middle" color={C.gold}>1 ≤ 3　且　1 ≤ 2</Text><Text x={1270} y={775} size={26} anchor="middle" color={C.muted}>沿父子关系往下，次数不会变小</Text></g></>;note='结构示意：父的次数 ≤ 孩子次数，所以根的次数最少';
 }else if(t==='code'){
  body=<Panel><Text x={150} y={350} size={30} color={C.muted}>heap 中每项：(cnt, num) = (出现次数, 数字)</Text><rect x={145} y={400} width={1630} height={165} rx={20} fill={C.bg} stroke={!second?C.gold:C.edge} strokeWidth={2}/><Text x={185} y={463} size={36} mono color={!second?C.gold:C.muted}>heapq.heappush(heap, (cnt, num))</Text><Text x={185} y={528} size={29} color={C.muted}>放到末尾，按父子关系向上调整</Text><g opacity={q}><rect x={145} y={610} width={1630} height={165} rx={20} fill={C.bg} stroke={C.teal} strokeWidth={2}/><Text x={185} y={675} size={36} mono color={C.teal}>if len(heap) &gt; k: heapq.heappop(heap)</Text><Text x={185} y={739} size={29} color={C.muted}>只有超过 k，才删除当前次数最少的堆顶</Text></g></Panel>;note='两段代码，对应刚才的“加入”与“超出后删除”';
 }else if(t==='closing'){
  pb=fixed(40);body=<><CountTable pb={pb}/><Tree pb={pb} title="最终候选：数字 1、5、4"/><g opacity={q}><rect x={745} y={736} width={1055} height={133} rx={18} fill={C.surface} stroke={C.edge}/><Text x={780} y={782} size={29}>时间 O(n + u log(k + 1))</Text><Text x={780} y={827} size={25} color={C.muted}>额外空间 O(u + k) · u 为不同数字的数量</Text></g></>;note='堆数组是 [1, 5, 4]；答案顺序不限，不需要额外排序';
 }else{
  if(t==='name'&&!second)pb=fixed(10);
  if(t==='push-five'&&second)pb={...pb,event:{...pb.event,candidate:2,indices:[0]}};
  body=<><CountTable pb={pb} showState={t!=='name'||second}/><Tree pb={pb} title={t==='name'?(second?'从空堆开始：先加入 1 × 3':f>=(s.cueFrames?.labels?.['小顶堆']??1)?'结构示意 · 小顶堆':'结构示意 · 给父子关系命名'):undefined} named={t!=='name'||second||f>=(s.cueFrames?.labels?.['小顶堆']??1)} schematic={t==='name'&&!second} showFill={t==='name'&&!second}/></>;
  if(t==='name')note='重新从空堆开始；按计数表的 1、2、3、4、5、6 依次处理';
  if(t==='push-four'||t==='push-five')note='插入后的临时状态可有 k+1 个节点；随后才删除堆顶';
  if(t==='pop-three'||t==='pop-two'||t==='pop-six')note='补根之后，选择次数更少的孩子，才能同时保持两边的父子规则';
  if(t==='push-six')note='6 的次数最少，经过两次比较和交换，来到堆顶';
 }
 const h=HEADERS[t]??['前 K 个高频元素',''],chapter=({problem:'题目与计数',derive:'推导需要的操作',heap:'建立父子规则',walk:'按同一组数字逐步执行',code:'程序与结果'} as Record<string,string>)[s.chapterId]??'前 K 个高频元素';
 const hideName=t==='name'&&f<(s.cueFrames?.labels?.['小顶堆']??at(s,0,.03));
 return <><svg width={1920} height={1080} viewBox="0 0 1920 1080" data-trace-event={pb.event.id} data-trace-kind={pb.event.kind} data-shot={s.id}><rect width={1920} height={1080} fill={C.bg}/><Text x={120} y={195} size={46} weight={750}>{hideName?'让次数最少的候选留在顶端':h[0]}</Text><Text x={120} y={246} size={27} color={C.muted}>{h[1]}</Text>{body}<Note>{note}</Note></svg><LeetcodeHeader slug="top-k-frequent-elements" identity={{number:347,method:'小顶堆'}} detail={chapter}/></>;
}
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),s=shots.find(s=>f>=s.from&&f<s.from+s.durationInFrames)??shots[shots.length-1],local=f-s.from,card=s.codeCardFrom!==undefined&&local>=s.codeCardFrom,caption=(s.subtitles??[]).find(v=>local>=v.from&&local<(v.to!==undefined?v.to+1:v.from+(v.duration??0))),pending=Boolean((STORYBOARD.meta as any).pendingAudio);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><LeetcodeBackdrop/>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&!pending&&<Audio src={staticFile('audio/voice.wav')}/ >}{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><Scene shot={s}/></Sequence>)}{!hideSubtitles&&!card&&caption&&<div data-subtitle="true" style={{position:'absolute',left:110,right:110,bottom:29,minHeight:67,display:'flex',alignItems:'center',justifyContent:'center',padding:'9px 22px',borderRadius:14,background:C.bg+'EB',color:C.text,fontSize:31,lineHeight:1.5,textAlign:'center'}}>{caption.text}</div>}</AbsoluteFill>;
};
