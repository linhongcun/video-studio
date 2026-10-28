import React from 'react';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../_shared/leetcode-video/Frame';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
import {Shot,shots,DEMO,GRID,LAND,Cell,TraceEvent,INITIAL,event,eventSequence,eventRange,componentCells,displayCell,scanAt} from '../data';
import {IslandMap,NeighborArrow,DiagonalGap,ISLAND_COLORS,MAP,center} from './IslandMap';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
const sentence=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
const timing=(s:Shot,i:number,p:number)=>sentence(s,i)+(Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10)-sentence(s,i))*p;
const phase=(s:Shot,f:number,i=0,a=.05,b=.84)=>clamp((f-timing(s,i,a))/Math.max(1,timing(s,i,b)-timing(s,i,a)));
const T=({x,y,children,size=30,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='LeetCode 200 · 岛屿数量'}:any)=><g><foreignObject x={0} y={0} width={1920} height={150}><LeetcodeHeader slug="number-of-islands" detail={kicker}/></foreignObject><T x={120} y={182} size={51} weight={760}>{title}</T><T x={120} y={242} size={27} color={C.muted}>{sub}</T></g>;
const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={896} size={28} anchor="middle" color={color} alpha={alpha}>{children}</T>;
const Box=({x=1050,y=507,w=730,h=342,children,color=C.edge}:any)=><g><rect x={x} y={y} width={w} height={h} rx={23} fill={C.surface} stroke={color} strokeWidth={1.8}/>{children}</g>;
const Counter=({value,label='正式岛数',hint='',color=C.teal,size=100,hintSize=25}:any)=><g data-island-counter={value}><rect x={1050} y={319} width={730} height={151} rx={24} fill={C.surface} stroke={color} strokeWidth={2}/><T x={1090} y={369} size={29} color={C.muted}>{label}</T><T x={1090} y={420} size={hintSize} color={C.muted}>{hint}</T><T x={1698} y={431} size={size} mono color={color} anchor="end">{value}</T></g>;
const Lines=({lines,x=1090,y=560,size=30,gap=56,color=C.text}:any)=><g>{lines.map((line:string,i:number)=><T key={i} x={x} y={y+i*gap} size={size} color={color}>{line}</T>)}</g>;
const Stack=({snapshot:s,title='栈 · 后放先看'}:{snapshot:TraceEvent;title?:string})=><Box w={350} h={342}>
 <T x={1083} y={552} size={28}>{title}</T><T x={1083} y={593} size={22} color={C.muted}>位置按行、列显示</T>
 {s.stack.length===0?<T x={1225} y={700} size={36} anchor="middle" color={C.muted}>空</T>:s.stack.map((cell,i)=>{const y=752-i*71,top=i===s.stack.length-1;return <g key={cell.join(',')} data-stack-cell={cell.join(',')} data-stack-top={top}><rect x={1084} y={y-44} width={230} height={57} rx={13} fill={top?C.gold+'0C':C.bg} stroke={top?C.gold:C.edge} strokeWidth={top?2.5:1.5}/><T x={1198} y={y-5} size={33} mono anchor="middle" color={top?C.gold:C.text}>{displayCell(cell)}</T>{top&&<T x={1330} y={y-5} size={22} color={C.gold}>顶</T>}</g>;})}
 <T x={1220} y={813} size={21} anchor="middle" color={C.muted}>底在下 · 顶在上</T>
</Box>;
const StatePanel=({s,lines,stackTitle='栈 · 后放先看'}:{s:TraceEvent;lines:string[];stackTitle?:string})=><><Counter value={s.count} hint="只在发现新岛起点时增加"/><Stack snapshot={s} title={stackTitle}/><Box x={1430} w={350}><Lines lines={lines} x={1460} y={556} size={25} gap={48}/><T x={1460} y={793} size={20} color={C.blue}>蓝角：外层扫描位置</T><T x={1460} y={827} size={20} color={C.muted}>归属标记 ≠ 已经展开</T></Box></>;
const GapPanel=({snapshot=INITIAL,from=[1,1],to=[2,2],preview=false}: {snapshot?:TraceEvent;from?:Cell;to?:Cell;preview?:boolean})=>{
 const a=center(from),b=center(to),x=(a.x+b.x)/2,y=(a.y+b.y)/2,extent=MAP.cell*.88;
 return <Box><T x={1090} y={553} size={28}>原图斜角处放大</T><svg x={1082} y={585} width={232} height={232} viewBox={`${x-extent/2} ${y-extent/2} ${extent} ${extent}`}><IslandMap snapshot={snapshot} showCoordinates={false} showScan={false} showState={false} showNeighbor={false} previewComponents={preview}/><DiagonalGap from={from} to={to}/></svg><Lines x={1360} y={630} size={29} gap={54} lines={['角接处仍有水隙','不是上下左右相邻','不能跨角归成一座']}/></Box>;
};
const Scene=({s,f}:{s:Shot;f:number})=>{
 const p=phase(s,f),q=phase(s,f,1),second=f>=sentence(s,1),t=s.visualType;
 if(t==='problem')return <>
  <Head title="这张地图有几座岛？" sub="4行5列的海陆地图 · 只沿上下左右相连"/><IslandMap showState={false} showNeighbor={false}/><Counter value="?" label="题目要求返回" hint="一个整数：岛屿的数量" color={C.gold}/><Box><Lines lines={['1 代表陆地，0 代表海水','上下左右连成一片，算一座岛','四周海水不是可连接的陆地']} size={30}/><g opacity={p}><rect x={1090} y={718} width={44} height={33} rx={10} fill={ISLAND_COLORS[0]} stroke="#CDB783" strokeWidth={3}/><T x={1155} y={744} size={27}>陆地</T><rect x={1390} y={718} width={44} height={33} rx={10} fill="#10394F" stroke="#69ADBD" strokeWidth={2}/><T x={1455} y={744} size={27}>海水</T></g></Box><NeighborArrow from={[0,0]} to={[0,1]} alpha={p}/><NeighborArrow from={[0,0]} to={[1,0]} alpha={p}/><Note alpha={q}>数的是整座相连陆地，不是陆地小格的数量</Note>
 </>;
 if(t==='example')return <>
  <Head title="七块陆地，连成三座岛" sub="题意答案预览 · 不是搜索过程，正式计数尚未开始"/><IslandMap showState={false} showNeighbor={false} previewComponents={second||p>.34}/><Counter value={second?3:'7块'} label={second?'本例应返回':'先看陆地小格'} hint={second?'4块 + 1块 + 2块，分别属于3座岛':'陆地块数与岛屿数量不同'} color={second?C.teal:C.gold}/><GapPanel preview/><DiagonalGap from={[1,1]} to={[2,2]} alpha={q}/><DiagonalGap from={[2,2]} to={[3,3]} alpha={q}/><Note color={C.gold}>共享边缘才相连；仅仅隔角相望，不算一座岛</Note>
 </>;
 if(t==='derive-component')return <>
  <Head kicker="思路分析 · 先想为什么不能数每一格" title="同一座岛，不能被算四遍" sub="先认出整片相连的陆地，再寻找还没归属的地方"/><IslandMap showState={false} showNeighbor={false} previewIds={second?[1]:[]} focusCells={second?[]:componentCells(1)}/><Counter value={second?'1座':'4遍'} label={second?'改成按整座归属':'逐格加一的错误尝试'} hint="这里始终是左上同一座岛" color={second?C.teal:C.red}/><Box><Lines lines={second?['先留下整座岛的归属标记','以后再遇到其中一块','就知道它已经被归在这一座']:['四块陆地共享连通的海岸','每一块各加一次，会重复','需要把它们当作同一个整体']} size={30}/></Box><Note>归属标记加在原地图上，陆地和海岸不改变</Note>
 </>;
 if(t==='derive-search'){
  const current=eventSequence(second?[15,16,17,18,22,23,27,29,35]:[3,5,6,7,8,9,10,11],second?q:p),introduced=f>=Number(s.cueFrames?.labels?.['深度优先搜索']??sentence(s,1));
  return <><Head kicker="思路分析 · 沿四邻走，记住还没看的分岔" title="沿一条分支继续，再回来接着找" sub="只在相邻陆地之间延伸，不跨海水与斜角"/><IslandMap snapshot={current} showNeighbor={true} showScan={false}/><Counter value="整座" label="这一段只在推导做法" hint="下面恢复原图，正式开始" color={C.gold}/><Box><Lines lines={['沿四个方向找相邻陆地','岔路先留下，之后再继续','同一片都归到这一座岛']} size={30}/>{introduced&&<g><rect x={1088} y={728} width={640} height={73} rx={17} fill={C.teal+'0B'} stroke={C.teal} strokeWidth={2}/><T x={1408} y={777} size={36} anchor="middle" color={C.teal}>深度优先搜索 · DFS</T></g>}</Box><Note>归整座的动作有了，再给这种搜索方法命名</Note></>;
 }
 if(t==='seed'){
  const current=second?eventSequence([1,2,3,4],q):event(1);
  return <><Head kicker="正式开始 · 清空演示标记" title="原地图不变，从第一行第一列开始" sub="岛数归零，已归属与待展开记录都清空，再逐行扫描"/><IslandMap snapshot={current} showScan={true} focusCells={!second?[[0,0]]:[]}/><StatePanel s={current} stackTitle="待展开的位置" lines={second?['发现新岛起点','岛数先加一','再标记为已归属','还没有看完四周']:['恢复原始海陆地图','正式岛数：0','归属标记：空','待展开位置：空']}/><Note>先归属，再放入待展开；同一块以后就不会重复加入</Note></>;
 }
 if(t==='stack-rule'){
  const secondFrames=s.durationInFrames-sentence(s,1),boundaryHold=Math.max(32,Math.floor(secondFrames*.20)),finishHold=Math.max(12,Math.floor(secondFrames*.08)),leadFrames=Math.max(1,secondFrames-2*boundaryHold-finishHold),local=f-sentence(s,1);
  const current=!second?eventSequence([4,5],p):local<leadFrames?eventSequence([5,6,7,8,9,10,11],local/leadFrames):local<leadFrames+boundaryHold?event(12):local<leadFrames+2*boundaryHold?event(13):event(14),introduced=f>=Number(s.cueFrames?.labels?.['栈']??sentence(s,0));
  const boundary=current.index===12||current.index===13;
  const title=current.index===12?'向左检查：越出地图边界，直接跳过':current.index===13?'向上检查：越出地图边界，直接跳过':second&&current.index===14?'四个方向都看完，再处理栈顶':'后放的先取出，先标记再放入';
  return <><Head kicker="把待展开位置记下来" title={title} sub={second?'右、下先标记入栈；左、上检查地图边界':'先放右边，再放下面；下面这一块留在顶部'}/><IslandMap snapshot={current} showScan showBoundary/><StatePanel s={current} stackTitle={introduced?'栈 · 后放先看':'待展开的位置'} lines={second?['右：陆地，标记入栈','下：陆地，标记入栈','左：越界，直接跳过','上：越界，直接跳过']:['先归属，不等于展开','右边(1,2)先放','下面(2,1)后放','下一次先取顶部']}/><Note color={boundary?C.red:C.gold}>{second?'越界→跳过，不标记、不入栈':'标记只表示已经归属，不表示四周已经看完'}</Note></>;
 }
 if(t==='take-down'){
  const current=second?eventSequence([16,17,18,22],q):eventSequence([14,15,16],p);
  return <><Head title="取出下面这一块，继续向右延伸" sub="第一行第二列仍待展开，身份和位置没有消失"/><IslandMap snapshot={current} showScan/><StatePanel s={current} lines={[current.index<22?'当前展开(2,1)':'(2,1)的四邻已看完','发现右边的(2,2)','先标记，再加入','(1,2)还留在栈底']}/><Note>岛数始终为1；在同一座岛里发现更多陆地，不再加数</Note></>;
 }
 if(t==='skip-seen'){
  const current=second?eventSequence([27,28,29,30,31,32,33,34,35],q):eventSequence([23,24,25,26,27],p);
  return <><Head title={second?(current.index<35?'回来处理留下的位置，才能找完整座':'栈空且四邻看完，第一座岛已完成'):'向上又遇见它：已有归属，不重复放入'} sub="第一行第二列早已标记；被标记与已经展开是两回事"/><IslandMap snapshot={current} showScan/><StatePanel s={current} lines={!second?['当前展开(2,2)','向上遇到(1,2)','它已归属，仍在栈中','不重复加入一次']:current.index<35?['再取出(1,2)','依四邻检查周围','归属一直保留','等四邻全部看完']:['栈已空','四块陆地都已展开','第一座岛已找完','岛数仍为1']}/><Note color={C.gold}>已有归属，就跳过加入；留下的栈项，之后照常展开</Note></>;
 }
 if(t==='resume-scan'){
  const current=second?eventSequence([58,59,60,61],q):eventSequence(eventRange(35,58),p);
  return <><Head title="找完一座，回到原来的逐行扫描" sub="已有归属的陆地和海水都跳过，直到下一个新岛起点"/><IslandMap snapshot={current} showScan/><StatePanel s={current} lines={second?['来到第3行第3列','它还没有归属','新岛起点：再加一','原首岛标记保留']:['扫描沿每一行继续','水：直接跳过','已归属：也跳过','不会重新展开首岛']}/><Note>扫描位置回到外层循环；地图与已经认出的岛屿保持原位</Note></>;
 }
 if(t==='water-boundary'){
  const current=second?eventSequence([66,67,68],q):eventSequence([61,62,63,64,65,66],p);
  return <><Head title="四周都是海水，这一座就停在这里" sub="第四行第四列只在斜角方向，不属于当前的四邻"/><IslandMap snapshot={current} showScan/><Counter value={current.count} hint="第二座只包含中央这一块"/><GapPanel snapshot={current} from={[2,2]} to={[3,3]}/><DiagonalGap from={[2,2]} to={[3,3]} alpha={q}/><Note color={C.gold}>斜角不是候选方向；不能跨过去把两座岛合并</Note></>;
 }
 if(t==='third-island'){
  const current=second?eventSequence([86,87,88,89,90,91,92,93,94,95,96,97,98,99],q):eventSequence([68,69,71,73,75,77,79,80,81,82,83,84,85,86],p);
  return <><Head title={second?(current.index<99?'把最后两块归成一座，再完成扫描':'整张地图已扫描完，返回三'):'继续扫描，右下这一座才让岛数加到三'} sub="右边相连的一块属于同一座岛，不再增加岛数"/><IslandMap snapshot={current} showScan={current.index<99}/><StatePanel s={current} lines={current.index<80?['继续逐行扫描','跳过后面的海水','寻找新的岛屿起点','此时岛数仍为2']:current.index<97?['新的起点：岛数3','向右找到相邻陆地','先归属，再加入栈','仍是同一座，不加数']:current.index<99?['第三座岛已找完','栈空，扫描仍在继续','最后一格已有归属','跳过后才返回']:['三座岛全部找完','栈空，扫描也结束','返回整数3','地形和输入都未改']}/><Note>首岛4块、中央1块、右下2块，分别只从一个新起点计数</Note></>;
 }
 if(t==='complexity')return <>
  <Head kicker="扫描结束，再看看需要多少工作" title="每块陆地最多入栈一次、取出一次" sub="m行 × n列；四邻检查是每次展开的固定工作"/><IslandMap snapshot={event(99)} showNeighbor={false}/><Counter value="O(mn)" size={62} hintSize={22} label="时间复杂度" hint="外层扫描所有格，陆地至多展开一次"/><Box><Lines lines={['本例：20个外层扫描位置','7块陆地，各入栈/出栈一次','每次展开，只检查四个方向']} size={29}/><T x={1090} y={773} size={35} color={second?C.gold:C.muted}>额外空间：O(mn)</T><T x={1090} y={820} size={23} color={C.muted}>seen和栈的最坏空间，都随地图规模增长</T></Box><Note>不把本例的最大栈长度，当作所有地图的空间上界</Note>
 </>;
 if(t==='implementation'){
  const current=second?event(8):eventSequence([5,6,7,8],p);
  return <><Head kicker="代码对应 · 明确回看第一座岛的过程" title="先标记再入栈；加数只发生在新岛起点" sub="地图仍按行列从1开始；Python下标从0开始"/><IslandMap snapshot={current} showScan/><Box y={319} h={530}><T x={1090} y={367} size={26} color={C.muted}>找到未归属的相邻陆地</T><rect x={1080} y={391} width={666} height={142} rx={16} fill={C.bg} stroke={!second?C.teal:C.edge} strokeWidth={2}/><T x={1110} y={446} size={32} mono color={current.index===7?C.gold:C.text}>seen.add((nr, nc))</T><T x={1110} y={497} size={32} mono color={current.index>=8?C.gold:C.muted}>stack.append((nr, nc))</T><g opacity={q}><T x={1090} y={590} size={26} color={C.muted}>只有外层扫描遇到新岛，才执行</T><rect x={1080} y={613} width={666} height={86} rx={15} fill={C.bg} stroke={C.gold} strokeWidth={2}/><T x={1110} y={669} size={34} mono color={C.gold}>islands += 1</T></g><T x={1090} y={759} size={23} color={C.blue}>地图(行1,列2) ↔ Python(0,1)</T><T x={1090} y={808} size={25} color={C.muted}>邻居展开里没有加一，首岛仍只数一次</T></Box><Note>完整实现使用迭代栈与seen，原始海陆地图保持不变</Note></>;
 }
 return <>
  <Head kicker="回到扫描结束的原地图" title="七块陆地，三座岛：同一座只数一次" sub="发现新岛加一 → 沿四邻扩展并标记 → 再继续扫描"/><IslandMap snapshot={event(99)} showNeighbor={false}/><Counter value={DEMO.result??3} label="最后返回" hint="原始地形与海岸一直保持"/><Box><Lines lines={['左上4块，属于第一座','中央1块，属于第二座','右下2块，属于第三座']} size={31}/><T x={1090} y={788} size={30} color={C.gold}>接下来是完整Python程序</T></Box><Note alpha={q}>完整程序可以暂停查看</Note>
 </>;
};
const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null,card=codeCardFrom!==null&&f>=codeCardFrom,sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}><defs></defs>{card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}<T x={120} y={1045} size={20} color={C.muted} alpha={.65}>{card?'LeetCode 200 · Python 3':'LeetCode 200 · 原题海陆示例'}</T>{DEMO.provisional&&<T x={960} y={1049} size={24} color={C.red} anchor="middle">布局占位 · 尚未接入实际执行轨迹</T>}</svg>{!hideSubtitles&&!card&&subtitle&&<div data-subtitle="true" style={{position:'absolute',left:210,right:210,bottom:69,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill><LeetcodeBackdrop/>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
