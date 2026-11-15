import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
import {C,FONT,MONO} from '../../../../../_shared/leetcode-video/theme';
import {TRACE,STORYBOARD,shots,Shot,Run,TraceEvent} from './data';
import {actionProgress,clamp,ease} from './timeline';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const RIGHT='#A5B4FC',BAD='#FB8C92',X=220,DX=250,W=160,Y=395;
const T=({x,y,children,size=30,color=C.text,anchor='start',mono=false,weight=500,...rest}:any)=><text x={x} y={y} fill={color} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const pill=(x:number,y:number,label:string,color:string)=><g><rect x={x-35} y={y-34} width={70} height={44} rx={10} fill={color}/><T x={x} y={y-2} anchor="middle" color={C.bg} mono size={27} weight={700}>{label}</T></g>;
function ArrayRow({values,i=-1,l=-1,r=-1,fromL=l,fromR=r,p=1,sorted=true,dim=false}:any){
 return <g opacity={dim?0.4:1}>
 {values.map((v:number,j:number)=>{
 const active=j===i||j===Math.round(l)||j===Math.round(r);
 const color=j===i?C.gold:j===l?C.teal:j===r?RIGHT:C.edge;
 const excluded=sorted&&i>=0&&(j<i||(j>i&&(j<Math.min(l,r)||j>Math.max(l,r))));
 return <g key={j} opacity={excluded?0.3:1}>
 <rect x={X+j*DX} y={Y} width={W} height={110} rx={18} fill={active?'#1D314C':C.surface} stroke={color} strokeWidth={active?5:2}/>
 <T x={X+j*DX+W/2} y={Y+75} size={54} color={color===C.edge?C.text:color} anchor="middle" mono weight={700}>{v}</T>
 <T x={X+j*DX+W/2} y={Y+150} size={22} color={C.muted} anchor="middle">下标 {j}</T>
 {excluded&&<path d={`M${X+j*DX+20} ${Y+90}l120 -70`} stroke={C.muted} strokeWidth={3}/>}
 </g>})}
 {i>=0&&pill(X+i*DX+W/2,Y-70,'i',C.gold)}
 {l>=0&&pill(X+(fromL+(l-fromL)*p)*DX+W/2,Y-10,'L',C.teal)}
 {r>=0&&pill(X+(fromR+(r-fromR)*p)*DX+W/2,Y-65,'R',RIGHT)}
 </g>;
}
function Result({rows,x=220,y=805}:{rows:number[][];x?:number;y?:number}){
 return <g><T x={x} y={y-45} color={C.muted} size={24}>已找到的不同组合</T>
 {rows.length?rows.map((v,k)=><g key={k}><rect x={x+k*560} y={y-10} width={510} height={75} rx={15} fill="#153A3A" stroke={C.teal}/><T x={x+k*560+255} y={y+40} mono anchor="middle" color={C.teal} size={38}>{'['+v.join(', ')+']'}</T></g>):<T x={x} y={y+35} mono color={C.muted}>[ ]</T>}</g>;
}
function current(shot:Shot,frame:number,run:Run){
 const acts=(shot.actionCues??[]).filter(a=>a.events?.length);
 let last=acts.length?run.events[acts[0].events![0]]:run.events[run.events.length-1];
 let frac=0;
 for(const a of acts){
  const p=actionProgress(shot,frame,a.id,0,0.88);
  if(p<=0)break;
  const list=a.events!;
  const index=Math.min(list.length-1,Math.floor(p*list.length));
  last=run.events[list[index]];
  frac=p>=0.999?1:(p*list.length-index);
  if(p<0.999)break;
 }
 return {event:last,frac};
}
function TraceBoard({run,event:e,frac}: {run:Run;event:TraceEvent;frac:number}){
 const move=ease((frac-0.18)/0.68);
 const l=e.nextL??e.l,r=e.nextR??e.r;
 const rows=e.kind==='hit'&&frac<0.28?e.result.slice(0,-1):e.result;
 const moved=move>0.85;
 const el=moved?l:e.l,er=moved?r:e.r;
 const sum=e.i<el&&el<er?run.sorted[e.i]+run.sorted[el]+run.sorted[er]:null;
 const val=(v:number)=>v<0?'('+v+')':v;
 const notes:Record<string,[string,string]>={
 'fix':['固定一个数，检查它右侧的候选',C.gold],
 'low':['和偏小：当前右端已经最大 → 排除当前 L',C.teal],
 'high':['和偏大：当前左端已经最小 → 排除当前 R',RIGHT],
 'hit':['和等于零 → 记录这个数值组合',C.teal],
 'skip-left':['命中后跳过左端的当前值',C.teal],
 'skip-right':['命中后跳过右端的当前值',RIGHT],
 'cross':['L 与 R 相遇 → 结束本轮',C.muted],
 'skip-fixed':['固定值与上一轮相同 → 跳过这一轮',C.gold],
 'stop':['固定值已大于零 → 停止',C.gold]};
 const [note,nc]=notes[e.kind]??['',C.text];
 const equation=sum!==null&&e.kind!=='skip-fixed'&&e.kind!=='cross';
 return <>
 <T x={220} y={290} size={25} color={C.gold}>固定值 i</T><T x={500} y={290} size={25} color={C.teal}>左指针 L</T><T x={820} y={290} size={25} color={RIGHT}>右指针 R</T>
 <ArrayRow values={run.sorted} i={e.i} l={l} r={r} fromL={e.l} fromR={e.r} p={move}/>
 {equation?<T x={960} y={655} size={48} color={sum===0?C.teal:sum!<0?C.gold:RIGHT} anchor="middle" mono>{`${val(run.sorted[e.i])} + ${val(run.sorted[el])} + ${val(run.sorted[er])} = ${sum}`}</T>:<T x={960} y={655} anchor="middle" size={36} color={C.muted}>{e.kind==='skip-fixed'?'这个固定数值已经完整查找过':'本轮候选已检查完'}</T>}
 <T x={960} y={720} anchor="middle" size={29} color={nc}>{note}</T>
 <Result rows={rows}/>
 </>;
}
function Input({shot,frame}:{shot:Shot;frame:number}){
 const p=actionProgress(shot,frame,'second');
 return <>
 <T x={220} y={300} color={C.muted} size={26}>官方示例 1 · 输入</T><ArrayRow values={TRACE.main.input} sorted={false}/>
 <T x={960} y={660} size={42} color={C.gold} anchor="middle">三个不同位置 · 总和为 0 · 数值组合不重复</T>
 <g opacity={p}><Result rows={[[-1,-1,2],[-1,0,1]]}/></g>
 </>;
}
function Sort({shot,frame}:{shot:Shot;frame:number}){
 const p=actionProgress(shot,frame,'first',0,0.55),q=actionProgress(shot,frame,'second',0,0.55);
 const ranked=TRACE.main.input.map((v,j)=>({v,j})).sort((a,b)=>a.v-b.v||a.j-b.j);
 return <>
 <T x={220} y={300} color={C.muted} size={26}>从小到大排序；重复次数保留</T>
 {TRACE.main.input.map((v,j)=>{const dest=ranked.findIndex(z=>z.j===j);const x=X+(j+(dest-j)*p)*DX;return <g key={j}><rect x={x} y={Y} width={W} height={110} rx={18} fill={C.surface} stroke={C.edge} strokeWidth={3}/><T x={x+W/2} y={Y+75} mono size={54} anchor="middle">{v}</T></g>})}
 <g opacity={q}>{pill(X+W/2,330,'i',C.gold)}{pill(X+DX+W/2,385,'L',C.teal)}{pill(X+5*DX+W/2,330,'R',RIGHT)}
 <T x={960} y={640} mono size={46} color={C.gold} anchor="middle">i &lt; L &lt; R</T><T x={960} y={715} size={32} anchor="middle">固定一个位置，另两个指针只在右侧查找</T></g>
 </>;
}
function Edge({shot,frame}:{shot:Shot;frame:number}){
 const p=actionProgress(shot,frame,'second',0,0.4);
 return <>
 <T x={220} y={300} size={28} color={C.muted}>官方示例 3 · 相同数值，三个不同位置</T>
 <g transform="translate(0,-25)"><ArrayRow values={[0,0,0]} i={0} l={1} r={2}/></g>
 <T x={1250} y={445} mono size={40} color={C.teal}>→ [[0, 0, 0]]</T>
 <g opacity={p}><T x={220} y={670} size={28} color={C.muted}>官方示例 2 · 没有和为零的组合</T>
 <T x={220} y={750} size={45} mono>[0, 1, 1]</T><T x={1250} y={750} size={40} mono color={BAD}>→ [ ]</T></g>
 <T x={220} y={850} size={31} color={C.gold}>位置不能复用，数值可以重复，结果组合只输出一次</T>
 </>;
}
function Close({shot,frame}:{shot:Shot;frame:number}){
 const p=actionProgress(shot,frame,'second',0,0.35);
 return <>
 <Result rows={TRACE.main.result} y={380}/>
 {['和 < 0：L 右移，排除当前左端','和 > 0：R 左移，排除当前右端','和 = 0：记录，跳过两端当前值','固定值与上一轮相同：跳过'].map((line,j)=><T key={line} x={220} y={560+j*78} size={36} color={j===2?C.teal:C.text}>{line}</T>)}
 <g opacity={p}><T x={1280} y={560} size={42} color={C.gold} mono>O(n²)</T><T x={1280} y={615} size={27} color={C.muted}>每轮 O(n) × 最多 n 轮</T>
 <T x={1280} y={735} size={42} color={C.gold} mono>O(n)</T><T x={1280} y={790} size={27} color={C.muted}>除输出外的额外空间</T><T x={1280} y={835} size={25} color={C.muted}>有序副本与排序工作空间</T></g>
 </>;
}
const titles:Record<string,string>={input:'三数之和：找全组合，怎样不重复？',sort:'排序后，用大小关系排除候选',low:'和偏小，为什么可以移动左指针？',hit:'固定第一个 -1，找到第一组',next:'继续向内，找到第二组',finish:'跳过重复固定值，再检查 0',duplicate:'去重补例：跳过两端等值段',edge:'数值可以相同，位置必须不同',close:'每次移动都有排除依据'};
function splitSubtitle(text:string){
 const chunks=text.match(/[^，；：。！？]+[，；：。！？]?/g)??[text];const lines:string[]=[];let line='';
 for(const c of chunks){if(line.length+c.length>44&&line){lines.push(line);line='';}line+=c;}
 if(line)lines.push(line);return lines.flatMap(l=>l.match(/.{1,44}/g)??[]);
}
function Scene({shot,hideSubtitles}:{shot:Shot;hideSubtitles:boolean}){
 const frame=useCurrentFrame(),n=Number(shot.id);
 if(shot.codeCardFrom!==undefined&&frame>=shot.codeCardFrom)return <CodeCard/>;
 const run=n===7?TRACE.duplicates:TRACE.main,state=current(shot,frame,run);
 return <AbsoluteFill style={{background:C.bg}}><LeetcodeBackdrop/><LeetcodeHeader slug="three-sum" identity={{number:15,method:'双指针'}} detail={shot.chapterTitle}/>
 <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
 <T x={130} y={215} size={42} weight={600}>{titles[['','','sort','low','hit','next','finish','duplicate','edge','close'][n]]??(n===1?titles.input:titles.sort)}</T>
 <T x={1785} y={215} size={22} color={C.gold} anchor="end">{n===7?'去重补例':n===8?'官方边界示例':'官方示例 1'}</T>
 {n===1?<Input shot={shot} frame={frame}/>:n===2?<Sort shot={shot} frame={frame}/>:n<=7?<TraceBoard run={run} {...state}/>:n===8?<Edge shot={shot} frame={frame}/>:<Close shot={shot} frame={frame}/>}
 {!hideSubtitles&&(shot.subtitles??[]).map((s,i)=>{
 if(frame<s.from||frame>(s.to??s.from+(s.duration??90)))return null;
 const lines=splitSubtitle(s.text),top=1020-lines.length*39;
 return <g data-subtitle={true} key={i}><rect x={150} y={top-32} width={1620} height={lines.length*39+25} rx={12} fill="#0B1220"/>
 {lines.map((l,j)=><T key={j} x={960} y={top+j*39} size={27} anchor="middle">{l}</T>)}</g>;
 })}
 </svg></AbsoluteFill>;
}
export function Main({hideSubtitles=false}:{hideSubtitles?:boolean}){
 return <AbsoluteFill>{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><Scene shot={s} hideSubtitles={hideSubtitles}/></Sequence>)}
 {__HAS_VOICE_AUDIO__&&!STORYBOARD.meta.pendingAudio&&<Audio src={staticFile('audio/voice.wav')}/>}</AbsoluteFill>;
}
