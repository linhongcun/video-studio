import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,Event as TraceEvent,TraceCase,MAIN,EXTRA,STORYBOARD,shots,LABELS,CITY_POS,PARENT_POS} from '../data';
import {C,FONT,MONO,GROUP_COLORS} from './theme';
import {CodeCard} from './CodeCard';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../../../../_shared/leetcode-video/Frame';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>{x=clamp(x);return x*x*(3-2*x);};
const end=(s:Shot)=>s.codeCardFrom??s.durationInFrames-10;
const at=(s:Shot,i:number,p:number)=>{const a=s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0),b=s.cueFrames?.sentences?.[i+1]??end(s);return a+(b-a)*p;};
const progress=(s:Shot,f:number,i=0,a=.05,b=.85)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const Text=({x,y,size=28,color=C.text,children,anchor='start',weight=500,opacity=1,mono=false,...rest}:any)=><text x={x} y={y} fontSize={size} fill={color} textAnchor={anchor} fontWeight={weight} opacity={opacity} fontFamily={mono?MONO:FONT} {...rest}>{children}</text>;
const Panel=({x=1160,y=253,w=660,h=635,children}:any)=><g><rect x={x} y={y} width={w} height={h} rx={28} fill={C.surface} stroke={C.edge} strokeWidth={1.8}/>{children}</g>;
const Note=({children,color=C.gold}:any)=><Text x={960} y={937} size={29} color={color} anchor="middle">{children}</Text>;
const city=(i?:number)=>i===null||i===undefined?'—':LABELS[i];
// Only choose already-recorded snapshots. No union/find runs in the renderer.
const stable=(c:TraceCase,e:TraceEvent)=>c.events.filter(q=>q.id<=e.id&&['init','decrement','finish'].includes(q.type)).slice(-1)[0]??c.events[0];
type Beat=[number,number,number];
type Playback={event:TraceEvent;previous:TraceEvent;committed:TraceEvent;p:number};
function play(s:Shot,f:number,c:TraceCase,initial:number,beats:Beat[]):Playback{
 let id=initial,previous=initial,start=0,next=end(s);
 for(let i=0;i<beats.length;i++){const t=at(s,beats[i][0],beats[i][1]);if(f<t){next=t;break;}previous=id;id=beats[i][2];start=t;next=i+1<beats.length?at(s,beats[i+1][0],beats[i+1][1]):end(s);}
 const e=c.events[id];return {event:e,previous:c.events[previous],committed:stable(c,e),p:ease((f-start)/Math.max(1,Math.min(18,(next-start)*.65)))};
}
const fixed=(c:TraceCase,id:number):Playback=>({event:c.events[id],previous:c.events[id],committed:stable(c,c.events[id]),p:1});
const colors=(e:TraceEvent,i:number)=>GROUP_COLORS[e.groupRoots[i]];
const Building=({x,y,color=C.blue,active=false}:any)=><g transform={`translate(${x} ${y})`}>
 <circle r={52} cy={-6} fill={C.bg} stroke={color} strokeWidth={active?4:2} strokeOpacity={active?1:.58}/>
 <path d="M -36 26 V -12 H -15 V 26 M -8 26 V -41 H 17 V 26 M 25 26 V -22 H 39 V 26" fill={C.surface} stroke={color} strokeWidth={2.4}/>
 {[-30,-22,0,9,30].map((xx,i)=><g key={i}>{[0,1].map(j=><rect key={j} x={xx} y={i===2||i===3?-30+j*17:-4+j*13} width={4} height={6} rx={1} fill={color} opacity={.8}/>)}</g>)}
 <line x1={-43} x2={44} y1={29} y2={29} stroke={color} strokeWidth={2.5}/>
 </g>;
function CityGraph({c=MAIN,e=MAIN.events[0],highlight=[],grouped=true,focus=[],travel=1,caseLabel='主例 · 6座城市',showMapping=true,representatives=false}:any){
 const highlighted=(a:number,b:number)=>highlight.some((pair:number[])=>pair[0]===a&&pair[1]===b||pair[0]===b&&pair[1]===a);
 return <Panel x={100} w={1020}>
  <Text x={135} y={298} size={28} weight={650}>城市之间的相连关系</Text><Text x={1085} y={298} size={22} color={C.muted} anchor="end">{caseLabel}</Text>
  {grouped&&e.groups.map((g:number[])=>{const xs=g.map(i=>CITY_POS[i][0]),ys=g.map(i=>CITY_POS[i][1]),x=Math.min(...xs)-78,y=Math.min(...ys)-82,w=Math.max(...xs)-x+78,h=Math.max(...ys)-y+95,color=colors(e,g[0]);return <rect key={g.join(',')} x={x} y={y} width={w} height={h} rx={g.length===1?65:60} fill={color+'08'} stroke={color} strokeWidth={2} strokeOpacity={.3} data-connected-group={g.map(i=>city(i)).join('')}/>;})}
  {c.edges.map((pair:number[])=>{const[a,b]=pair,[x1,y1]=CITY_POS[a],[x2,y2]=CITY_POS[b],active=highlighted(a,b),length=Math.hypot(x2-x1,y2-y1);return <g key={pair.join('-')} data-input-edge={pair.join('-')}><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.muted} strokeWidth={4} opacity={.42}/>{active&&<line x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.gold} strokeWidth={7} strokeDasharray={length} strokeDashoffset={length*(1-travel)}/>}</g>;})}
  {CITY_POS.map(([x,y],i)=><g key={i} data-city={city(i)}><Building x={x} y={y} color={grouped?colors(e,i):C.blue} active={focus.includes(i)}/><Text x={x} y={y+76} anchor="middle" size={31} color={focus.includes(i)?C.gold:C.text} weight={700}>{city(i)}</Text>{representatives&&e.parent[i]===i&&<g><path d={`M ${x-13} ${y-73} L ${x-7} ${y-84} L ${x} ${y-75} L ${x+7} ${y-84} L ${x+13} ${y-73} Z`} fill={colors(e,i)}/><Text x={x} y={y-94} anchor="middle" size={21} color={colors(e,i)}>代表</Text></g>}</g>)}
  <Text x={135} y={852} size={21} color={C.muted}>{showMapping?'A–F 对应下标 0–5 · 位置不代表真实地理':'教学关系示意 · 不是实际地图'}</Text>
 </Panel>;
}
function Count({pb,label='当前已记组数'}:{pb:Playback;label?:string}){const pending=['link','resize'].includes(pb.event.type);return <g data-count={pb.event.count} data-count-pending={pending}><Text x={1195} y={300} size={27} color={C.muted}>{label}</Text><Text x={1775} y={315} size={66} anchor="end" color={pending?C.gold:C.teal} mono weight={650}>{pb.event.count}</Text>{pending&&<Text x={1505} y={300} size={22} color={C.gold}>合并中 · 待更新</Text>}</g>;}
function ParentRecords({pb,named=true}:any){
 const e:TraceEvent=pb.event,route=e.path??[],activeCities=new Set<number>(route.length?route:(e.roots??[]));
 return <Panel><Count pb={pb}/><Text x={1195} y={354} size={23} color={C.muted}>归属记录 · 虚线不是城市相连关系</Text>
  {e.parent.map((parent:number,i:number)=>{const[x,y]=PARENT_POS[i],[tx,ty]=PARENT_POS[parent],active=route.includes(i)||e.type==='link'&&e.parentBefore?.[i]!==parent;if(parent===i)return <path key={'a'+i} d={`M ${x+30} ${y-30} C ${x+68} ${y-83},${x-67} ${y-83},${x-30} ${y-30}`} fill="none" stroke={active?C.gold:C.muted} strokeWidth={active?4:2} strokeDasharray="7 6" markerEnd="url(#arrow-parent)"/>;const pathD=i===4?`M ${x-40} ${y} H ${tx+60} V ${ty} H ${tx+45}`:`M ${x} ${y-40} V ${ty} H ${tx+(x<tx?-45:45)}`;return <path key={'a'+i} d={pathD} fill="none" stroke={active?C.gold:colors(e,i)} strokeWidth={active?4:2.7} strokeDasharray="8 6" markerEnd="url(#arrow-parent)" data-parent-arrow={`${city(i)}-${city(parent)}`}/>;})}
  {PARENT_POS.map(([x,y],i)=><g key={i} data-parent-node={city(i)}><circle cx={x} cy={y} r={38} fill={C.bg} stroke={activeCities.has(i)?C.gold:colors(e,i)} strokeWidth={activeCities.has(i)?4:2.5}/><Text x={x} y={y+11} size={31} color={activeCities.has(i)?C.gold:C.text} weight={650} anchor="middle">{city(i)}</Text><Text x={x} y={y+70} size={21} anchor="middle" color={e.parent[i]===i?colors(e,i):C.muted}>{e.parent[i]===i?(named?'根 · 代表':'指向自己'):'记录 '+city(e.parent[i])}</Text></g>)}
  <Text x={1195} y={767} size={23} color={C.muted}>parent · 记录上一级</Text>
  {e.parent.map((parent:number,i:number)=><g key={i}><Text x={1242+i*95} y={805} anchor="middle" size={21} color={C.muted}>{city(i)}</Text><rect x={1206+i*95} y={818} width={72} height={43} rx={9} fill={C.bg} stroke={C.edge}/><Text x={1242+i*95} y={850} anchor="middle" size={27} color={colors(e,i)} mono>{city(parent)}</Text></g>)}
 </Panel>;
}
function Matrix({s,f,c=MAIN}:any){
 const second=f>=at(s,1,0),pair=f<at(s,0,.42)?[0,1]:f<at(s,1,.42)?[1,2]:[3,4],gx=1250,gy=410,step=79;
 return <Panel><Text x={1195} y={302} size={29} weight={650}>主例：城市相连表</Text><Text x={1195} y={346} size={23} color={C.muted}>行与列都按 A–F 排列</Text>
  {LABELS.map((l,i)=><g key={i}><Text x={gx+i*step} y={gy-28} anchor="middle" color={C.muted} size={23}>{l}</Text><Text x={gx-49} y={gy+i*step+12} anchor="middle" color={C.muted} size={23}>{l}</Text></g>)}
  {c.inputMatrix.map((row:number[],a:number)=>row.map((value,b)=>{const chosen=a===pair[0]&&b===pair[1],sym=a===pair[1]&&b===pair[0],dim=second&&b<=a;return <g key={a+'-'+b} opacity={dim?.20:1} data-matrix-cell={`${a}-${b}`}><rect x={gx+b*step-30} y={gy+a*step-24} width={60} height={58} rx={10} fill={chosen||sym&&!second?C.gold+'20':value?C.blue+'10':C.bg} stroke={chosen||sym&&!second?C.gold:C.edge} strokeWidth={chosen?3:1}/><Text x={gx+b*step} y={gy+a*step+17} anchor="middle" size={31} color={chosen||sym&&!second?C.gold:value?C.text:C.muted} mono>{value}</Text></g>;}))}
  <Text x={1490} y={882} anchor="middle" size={23} color={C.gold}>{second?'a < b：只看严格上三角':`${city(pair[0])}–${city(pair[1])} 与 ${city(pair[1])}–${city(pair[0])} 是同一对关系`}</Text>
 </Panel>;
}
// The input table and this graph are two views of MAIN.inputMatrix.  A cell
// chooses an existing input pair; the renderer never invents a connection.
const INTRO_POS=[[1115,500],[1370,485],[1635,500],[1150,715],[1400,715],[1690,715]];
function InputTable({pair=null,showMapping=true}:any){
 const gx=310,gy=427,step=82,rowStep=75;
 return <Panel x={100} y={282} w={820} h={607}>
  <Text x={140} y={328} size={31} weight={700}>输入：isConnected</Text>
  <Text x={880} y={328} size={22} color={C.muted} anchor="end">6 × 6 教学示例</Text>
  <Text x={186} y={381} size={21} color={C.muted}>行 i</Text>
  <Text x={790} y={381} size={21} color={C.muted}>列 j</Text>
  {LABELS.map((l,i)=><g key={'label'+i}>
   <Text x={gx+i*step} y={383} size={25} color={pair?.[1]===i?C.gold:C.muted} anchor="middle" mono>{i}</Text>
   <Text x={215} y={gy+i*rowStep+11} size={25} color={pair?.[0]===i?C.gold:C.muted} anchor="middle" mono>{i}</Text>
  </g>)}
  {MAIN.inputMatrix.map((row:number[],i:number)=>row.map((value,j)=>{const active=pair?.[0]===i&&pair?.[1]===j;return <g key={i+'-'+j} data-input-cell={`${i}-${j}`} data-input-value={value} data-input-active={active}>
   <rect x={gx+j*step-31} y={gy+i*rowStep-29} width={62} height={60} rx={11} fill={active?C.gold+'25':value?C.blue+'12':C.bg} stroke={active?C.gold:C.edge} strokeWidth={active?3:1.3}/>
   <Text x={gx+j*step} y={gy+i*rowStep+13} size={33} color={active?C.gold:value?C.text:C.muted} anchor="middle" mono>{value}</Text>
  </g>;}))}
  <Text x={510} y={872} size={21} color={C.muted} anchor="middle">{showMapping?'行、列都对应同一批城市 · 下标从0开始':'0只表示没有直接相连，不排除间接连通'}</Text>
 </Panel>;
}
function InputGraph({edges=MAIN.edges,active=null,travel=1,groups=false,abcOnly=false,indirect=false,focus=[]}:any){
 const final=MAIN.events[51],visibleGroups=groups?final.groups:abcOnly?[[0,1,2]]:[];
 const activePair=(pair:number[])=>active&&pair[0]===active[0]&&pair[1]===active[1];
 return <Panel x={960} y={282} w={860} h={607}>
  <Text x={1000} y={328} size={29} weight={700}>同一份输入，画成城市关系</Text>
  <Text x={1000} y={367} size={22} color={C.muted}>A–F 依次对应下标 0–5 · 不是实际地图</Text>
  {visibleGroups.map((g:number[])=>{const xs=g.map(i=>INTRO_POS[i][0]),ys=g.map(i=>INTRO_POS[i][1]),x=Math.min(...xs)-76,y=Math.min(...ys)-79,w=Math.max(...xs)-x+76,h=Math.max(...ys)-y+106,color=GROUP_COLORS[g[0]];return <rect key={'group'+g.join()} x={x} y={y} width={w} height={h} rx={52} fill={color+'0B'} stroke={color} strokeWidth={2} strokeOpacity={.6} data-province-group={g.map(i=>city(i)).join('')}/>;})}
  {edges.map((pair:number[])=>{const[a,b]=pair,[x1,y1]=INTRO_POS[a],[x2,y2]=INTRO_POS[b],on=activePair(pair)||(indirect&&(a===0&&b===1||a===1&&b===2)),length=Math.hypot(x2-x1,y2-y1),segmentTravel=indirect?clamp(travel*2-(a===1?1:0)):travel;return <g key={pair.join('-')} data-intro-edge={pair.join('-')}>
   {indirect&&on&&<line x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.blue} strokeWidth={4} opacity={.6} data-fixed-input-edge={pair.join('-')}/>}
   <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={on?C.gold:C.blue} strokeWidth={on?7:4} opacity={on?1:.6} strokeDasharray={on?length:undefined} strokeDashoffset={on?length*(1-segmentTravel):undefined}/>
  </g>;})}
  {INTRO_POS.map(([x,y],i)=><g key={i} data-input-city={i}><Building x={x} y={y} active={focus.includes(i)} color={groups||abcOnly&&i<3?colors(final,i):C.blue}/><Text x={x} y={y+77} size={30} color={focus.includes(i)?C.gold:C.text} weight={700} anchor="middle">{city(i)} <tspan fill={C.muted} fontSize={24}>({i})</tspan></Text></g>)}
 </Panel>;
}
function MatrixFirst({s,f}:{s:Shot;f:number}){
 const t=s.visualType,second=f>=at(s,1,0);
 if(t==='input-matrix')return <><InputTable/><Panel x={960} y={282} w={860} h={607}>
  <Text x={1000} y={337} size={32} weight={700}>先读懂这一格</Text>
  <Text x={1010} y={420} size={35} color={C.gold} mono>isConnected[i][j]</Text>
  <Text x={1010} y={487} size={31}>1：城市 i 与 j 直接相连</Text>
  <Text x={1010} y={545} size={31}>0：城市 i 与 j 没有直连</Text>
  <Text x={1000} y={649} size={33} color={C.teal} weight={700}>返回：省份总数</Text>
  <Text x={1000} y={704} size={26} color={C.muted}>直接或间接连通的一组城市＝一省</Text>
  <g opacity={second?1:0}><Text x={1000} y={784} size={29}>0 ↔ A　1 ↔ B　2 ↔ C</Text><Text x={1000} y={837} size={29}>3 ↔ D　4 ↔ E　5 ↔ F</Text></g>
 </Panel></>;
 if(t==='matrix-to-graph'){
  const turn=at(s,0,.50),bc=at(s,1,.11),de=at(s,1,.35),self=at(s,1,.65);
  const pair=f<turn?[0,1]:f<bc?[0,2]:f<de?[1,2]:f<self?[3,4]:[5,5];
  const edges:number[][]=[];
  if(f>=at(s,0,.12))edges.push([0,1]);
  if(f>=bc)edges.push([1,2]);
  if(f>=de)edges.push([3,4]);
  const p=f<turn?progress(s,f,0,.12,.37):pair[0]===1?progress(s,f,1,.11,.30):pair[0]===3?progress(s,f,1,.35,.57):1;
  return <><InputTable pair={pair}/><InputGraph edges={edges} active={pair} travel={p} focus={pair[0]===5?[5]:pair}/>
   <Text x={1390} y={865} anchor="middle" size={25} color={C.gold}>{pair[0]===5?'[5][5] = 1：自己；F没有其他连线':`[${pair[0]}][${pair[1]}] = ${MAIN.inputMatrix[pair[0]][pair[1]]}：${MAIN.inputMatrix[pair[0]][pair[1]]?'画出 '+city(pair[0])+'—'+city(pair[1]):'不画 A—C 直线'}`}</Text>
  </>;
 }
 const groups=second&&f>=at(s,1,.12),abc=f>=at(s,0,.48);
 return <><InputTable pair={[0,2]} showMapping={false}/><InputGraph edges={MAIN.edges} indirect={!groups} travel={progress(s,f,0,.1,.43)} abcOnly={abc&&!groups} groups={groups} focus={[0,2]}/>
  <Text x={1390} y={865} anchor="middle" size={groups?30:25} color={groups?C.teal:C.gold} weight={groups?700:500}>{groups?'ABC ／ DE ／ F → 返回 3':'[0][2] = 0，但 A → B → C 仍能连通'}</Text>
 </>;
}
const HEADER:Record<string,[string,string]>={problem:['没有直接相连，为什么仍是一组？','题目给出城市相连关系，求省份总数'],indirect:['A和C，能经过B连通','ABC、DE、F各是一组；孤城也计入'],'derive-groups':['不必保留每条中间路线','只需要判断同组，并把不同的组合在一起'],representative:['怎样记住哪些城市已经同组？','每组选择一个代表；同组城市找到同一代表'],parent:['沿归属记录，找到组代表','指向自己的位置就是根；归属箭头不是相连关系'],name:['先找两边的根，再合并不同组','已经理解查询与合并，再给这套做法命名'],'merge-ab':['从头处理主例：先看A和B','明确重置为6组；只在真正合并后减少组数'],'merge-bc':['B连接C，为什么要连接两个根？','先查B得到A，再查C得到C'],finish:['D与E合并，F保持独立','ABC、DE、F：完整主例最终是3省'],'already-connected':['补例：另加A和C的直接连接','新输入重新扫描，先处理AB、AC，再检查BC'],matrix:['回到主例：相连表怎样读？','主例没有AC直连；对称格描述同一对关系'],closing:['跨组才合并，每次少一省','完整程序使用按大小合并与路径减半']};
function Scene({shot:s}:{shot:Shot}){
 const f=useCurrentFrame(),t=s.visualType,p=progress(s,f),q=progress(s,f,1);if(s.codeCardFrom!==undefined&&f>=s.codeCardFrom)return <><CodeCard/><LeetcodeHeader slug="number-of-provinces" compact/></>;
 let c=MAIN,pb=fixed(MAIN,0),body:React.ReactNode=null,note:React.ReactNode=null;
 const chapter=({problem:'先看题目要什么',derive:'从分组需要推导做法',walk:'沿主例处理相连关系',code:'写成完整程序'} as any)[s.chapterId]??'省份数量';const named=t==='name'&&f>=(s.cueFrames?.labels?.['并查集']??at(s,1,0));let h=HEADER[t]??['省份数量',''];if(named)h=['并查集：查询同组，合并两组','根不同才合并，合并一次才少一省'];
 if(['input-matrix','matrix-to-graph','province'].includes(t)){
  h=({ 'input-matrix':['省份数量：先读二维数组','这一格表示什么？题目又要求返回什么？'], 'matrix-to-graph':['一格数字，对应哪一对城市？','把数组里的直接相连关系，逐条画出来'],province:['没有直连，也可能属于同一个省','直接或间接连通算一省；独立城市也算一省']} as Record<string,[string,string]>)[t];
  body=<MatrixFirst s={s} f={f}/>;
  note=t==='input-matrix'?'输入是二维数组；城市图只是同一份数据的另一种画法':t==='matrix-to-graph'?'只按题目里的1画线；0表示没有直接相连':'返回省份数量，而不是直接连接的条数';
 }else if(t==='problem'){
  body=<><CityGraph grouped={false} highlight={f>=at(s,0,.2)?[[0,1]]:[]} travel={p}/><Panel><Text x={1210} y={335} size={32} weight={650}>输入：哪些城市相连</Text><Text x={1210} y={405} size={29} color={C.muted}>直接相连，或能间接连通</Text><Text x={1210} y={458} size={29} color={C.muted}>都属于同一个省份</Text><Text x={1210} y={580} size={32} color={C.gold} opacity={q}>返回：省份总数</Text><g opacity={q}><Text x={1210} y={655} size={29}>孤城自己也算1省</Text><Building x={1510} y={760} color={C.gold}/><Text x={1580} y={770} size={28} color={C.gold}>F</Text></g></Panel></>;note='先看题目要数什么：省份，不是连接条数';
 }else if(t==='indirect'){
  const done=q>.15,e=done?MAIN.events[51]:MAIN.events[0];body=<><CityGraph e={e} grouped={done} highlight={p<.5?[[0,1]]:[[0,1],[1,2]]} travel={p<.5?p*2:1} focus={[0,2]}/><Panel><Text x={1210} y={335} size={32} weight={650}>A和C之间没有直连</Text><Text x={1510} y={445} size={45} color={C.gold} anchor="middle">A — B — C</Text><Text x={1510} y={505} size={29} color={C.muted} anchor="middle">经过B，仍然连通</Text><g opacity={clamp(q*3)}><Text x={1210} y={630} size={30}>ABC　／　DE　／　F</Text><Text x={1210} y={739} size={29} color={C.muted}>返回</Text><Text x={1740} y={765} size={112} color={C.teal} anchor="end" mono>3</Text></g></Panel></>;note='A–C没有直接线；它们通过B属于同一组';
 }else if(t==='derive-groups'){
  pb=play(s,f,MAIN,0,[[0,.55,12],[1,.18,30]]);body=<><CityGraph e={pb.committed} highlight={f<at(s,1,0)?[[0,1]]:[[1,2]]}/><Panel><Count pb={pb} label="分组操作示意"/><Text x={1210} y={425} size={34} color={C.gold}>先问：是不是同一组？</Text><Text x={1210} y={495} size={28} color={C.muted}>已经同组 → 保持不变</Text><g opacity={q}><Text x={1210} y={635} size={34} color={C.teal}>跨组 → 合成一组</Text><Text x={1210} y={705} size={28} color={C.muted}>每合并一次，只少一组</Text></g></Panel></>;note=f<at(s,0,.55)?'开始想算法：回到尚未处理的6个独立组':'分组需要：查询是否同组 ＋ 合并不同组';
 }else if(t==='representative'){
  const reset=f>=at(s,1,0);pb=fixed(MAIN,reset?0:51);body=<><CityGraph e={pb.committed} representatives/><Panel><Text x={1210} y={325} size={30} color={C.gold}>{reset?'初始：每城代表自己':'每组只需一个共同代表'}</Text><g opacity={reset?1:p}>{pb.event.groups.map((g,i)=><g key={g.join()}><Text x={1230} y={410+i*(reset?70:135)} size={32} color={colors(pb.event,g[0])}>{g.map(i=>city(i)).join('、')}</Text><Text x={1660} y={410+i*(reset?70:135)} size={32} color={colors(pb.event,g[0])} anchor="middle">→ {city(pb.event.groupRoots[g[0]])}</Text></g>)}</g><Text x={1210} y={850} size={25} color={C.muted}>{reset?'还没处理任何相连关系：6个代表':'代表是一种归属记录，不是新连接'}</Text></Panel></>;note=reset?'明确回到初始状态：六座城市，六个独立组':'同组城市，找到的是同一个代表';
 }else if(t==='parent'){
  pb=play(s,f,MAIN,12,[[0,.30,18],[0,.50,19],[0,.74,21],[1,.10,22]]);body=<><CityGraph e={pb.committed} highlight={[[0,1]]} focus={[0,1]}/><ParentRecords pb={pb}/></>;note='表示法示意 · 只改归属记录，原来的相连实线不变';
 }else if(t==='name'){
  pb=play(s,f,MAIN,12,[[0,.08,18],[0,.25,22],[0,.42,25],[0,.59,26],[0,.77,28],[1,.18,30]]);body=<><CityGraph e={pb.committed} highlight={[[1,2]]} focus={pb.event.roots??[1,2]}/><ParentRecords pb={pb}/></>;note=named?'并查集：查到同根就不变，跨组才合并':'把C的根接到A的根；原城市之间不新增相连线';
 }else if(t==='merge-ab'){
  pb=play(s,f,MAIN,0,[[0,.09,1],[0,.24,4],[0,.40,7],[0,.58,8],[0,.78,10],[1,.10,12],[1,.45,19],[1,.73,22]]);body=<><CityGraph e={pb.committed} highlight={[[0,1]]} focus={pb.event.path??[0,1]}/><ParentRecords pb={pb}/></>;note=pb.event.id<12?'主例从6组重走：先找A和B的根，再接根':'B记录A；查B沿归属记录找到代表A';
 }else if(t==='merge-bc'){
  pb=play(s,f,MAIN,12,[[0,.04,17],[0,.17,18],[0,.35,21],[0,.52,22],[0,.69,25],[0,.86,26],[1,.18,28],[1,.55,30]]);body=<><CityGraph e={pb.committed} highlight={[[1,2]]} focus={pb.event.path??pb.event.roots??[1,2]}/><ParentRecords pb={pb}/></>;note=pb.event.id<28?'B找到A，C找到C；两边的根不同':pb.event.id<30?'归属记录C → A · 合并中，待计数更新':'ABC同组，5组变4组；A–C仍然没有直接连接';
 }else if(t==='finish'){
  pb=play(s,f,MAIN,30,[[0,.05,37],[0,.20,40],[0,.34,43],[0,.46,44],[0,.58,46],[0,.77,48],[1,.12,49],[1,.26,50],[1,.44,51]]);body=<><CityGraph e={pb.committed} highlight={[[3,4]]} representatives={q>.25} focus={q>.2?[5]:[3,4]}/><ParentRecords pb={pb}/></>;note=pb.event.count===3?'最后3省：ABC、DE、F；孤城F不可漏掉':'D与E跨组，只有真正合并后才从4减到3';
 }else if(t==='already-connected'){
  c=EXTRA;pb=play(s,f,c,0,[[0,.12,0],[0,.40,12],[0,.76,24],[1,.12,39],[1,.40,40]]);body=<><CityGraph c={c} e={pb.committed} highlight={f<at(s,0,.36)?[[0,2]]:f<at(s,0,.68)?[[0,1]]:f<at(s,1,0)?[[0,2]]:[[1,2]]} caseLabel="补例局部 · 新增AC" focus={f>=at(s,1,0)?[1,2]:[]}/><ParentRecords pb={pb}/></>;note=f<at(s,1,0)?'不同输入，重新从6组开始：AB → AC → BC':'补例局部：BC已经同组，保持4；DE尚未处理';
 }else if(t==='matrix'){
  body=<><CityGraph e={MAIN.events[51]} highlight={f<at(s,0,.42)?[[0,1]]:f<at(s,1,.42)?[[1,2]]:[[3,4]]}/><Matrix s={s} f={f}/></>;note='回到原主例：自己不合并，同一对只看一次，0不触发合并';
 }else if(t==='closing'){
  body=<><CityGraph e={MAIN.events[51]} representatives/><Panel><Text x={1210} y={330} size={29} color={C.muted}>主例最终结果</Text><Text x={1735} y={445} size={112} color={C.teal} anchor="end" mono>3</Text><Text x={1210} y={535} size={31} color={C.gold}>读表：n(n − 1) / 2 对</Text><Text x={1210} y={610} size={31}>时间 O(n² α(n))</Text><Text x={1210} y={675} size={31}>额外空间 O(n)</Text><Text x={1210} y={755} size={23} color={C.muted}>α增长极慢；代码按大小合并</Text><Text x={1210} y={795} size={23} color={C.muted}>并用路径减半缩短查找</Text></Panel></>;note='根不同才合并；每真正合并一次，就少一省';
 }
 return <><svg width={1920} height={1080} viewBox="0 0 1920 1080" data-trace-event={pb.event.id} data-trace-case={c===EXTRA?'extraCycle':'main'}><defs><marker id="arrow-parent" markerWidth={8} markerHeight={8} refX={7} refY={4} orient="auto"><path d="M 0 0 L 8 4 L 0 8" fill={C.muted}/></marker></defs><rect width={1920} height={1080} fill={C.bg}/><Text x={120} y={193} size={49} weight={750}>{h[0]}</Text><Text x={120} y={245} size={28} color={C.muted}>{h[1]}</Text>{body}<Note>{note}</Note></svg><LeetcodeHeader slug="number-of-provinces" detail={chapter}/></>;
}
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),s=shots.find(s=>f>=s.from&&f<s.from+s.durationInFrames)??shots[shots.length-1],local=f-s.from,card=s.codeCardFrom!==undefined&&local>=s.codeCardFrom,caption=(s.subtitles??[]).find(v=>local>=v.from&&local<(v.to!==undefined?v.to+1:v.from+(v.duration??0))),pending=Boolean((STORYBOARD.meta as any).pendingAudio);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><LeetcodeBackdrop/>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&!pending&&<Audio src={staticFile('audio/voice.wav')}/ >}{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><Scene shot={s}/></Sequence>)}{!hideSubtitles&&!card&&caption&&<div data-subtitle="true" style={{position:'absolute',left:110,right:110,bottom:33,minHeight:67,display:'flex',alignItems:'center',justifyContent:'center',padding:'9px 22px',borderRadius:14,background:C.bg+'EB',color:C.text,fontSize:32,lineHeight:1.5,textAlign:'center'}}>{caption.text}</div>}</AbsoluteFill>;
};
