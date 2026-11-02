import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame,interpolate} from 'remotion';
import board from '../../storyboard.json';
import model from '../../model.json';
import timing from '../../model-timing.json';
import {RedisBackdrop,RedisHeader} from '../../../../../_shared/redis-video/Frame';
import {C,FONT,MONO} from '../../../../../_shared/redis-video/theme';

type State=typeof model.shots['01'][0]['before'];
type Stage={id:string;before:State;after:State;action:string|null;detail:string};
type Point=[number,number];
const positions:Record<string,Point>={S1:[310,440],S2:[620,440],S3:[930,440],S4:[465,700],S5:[775,700]};
const subtitles=(shot:any,f:number)=>shot.subtitles.find((s:any)=>f>=s.from&&f<=s.to)?.text||'';
const allShots=board.scenes.flatMap((s:any)=>s.shots);
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:board.meta.durationInFrames};
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const routes:Record<string,Point[]>={
 replicateR1:[[1400,515],[1300,625]],replicateR2:[[1520,515],[1630,625]],
 ping:[[370,440],[1345,440]],
 query:[[375,425],[555,425]],report:[[555,465],[375,465]],
 voteS2:[[555,470],[375,470]],voteS3:[[930,505],[930,570],[310,570],[310,505]],
 inspectR1:[[310,375],[310,325],[1150,325],[1150,620],[1300,620]],
 inspectR2:[[310,375],[310,325],[1765,325],[1765,620],[1630,620]],
 promoteCommand:[[310,375],[310,325],[1765,325],[1765,620],[1630,620]],
 roleReport:[[1630,620],[1765,620],[1765,325],[310,325],[310,375]],
 repoint:[[310,375],[310,325],[1150,325],[1150,620],[1300,620]],
 config:[[375,425],[555,425]],
 clientQuery:[[1000,640],[1070,640],[1070,320],[310,320],[310,375]],
 clientReply:[[310,375],[310,320],[1070,320],[1070,640],[1000,640]],
 clientConnect:[[1080,700],[1180,835],[1630,835],[1630,795]]
};

const Txt=({x,y,children,size=30,fill=C.text,weight=600,anchor='start',mono=false,...rest}:any)=>
 <text data-text="true" x={x} y={y} fontSize={size} fontFamily={mono?MONO:FONT} fill={fill} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const label=(x:number,y:number,text:string,size=28,fill=C.text,anchor='start')=><Txt x={x} y={y} size={size} fill={fill} anchor={anchor}>{text}</Txt>;

function pointOn(points:Point[],p:number):Point{
 const lengths=points.slice(1).map((b,i)=>Math.hypot(b[0]-points[i][0],b[1]-points[i][1]));
 let target=clamp(p)*lengths.reduce((a,b)=>a+b,0);
 for(let i=0;i<lengths.length;i++){
  if(target<=lengths[i]||i===lengths.length-1){const q=target/lengths[i];return [points[i][0]+(points[i+1][0]-points[i][0])*q,points[i][1]+(points[i+1][1]-points[i][1])*q];}
  target-=lengths[i];
 }
 return points[points.length-1];
}
const path=(points:Point[])=>points.map((p,i)=>`${i?'L':'M'}${p[0]} ${p[1]}`).join(' ');
function Connection({points,color=C.link,dashed=false,opacity=1}:{points:Point[];color?:string;dashed?:boolean;opacity?:number}){
 return <path d={path(points)} stroke={color} strokeWidth={4} strokeDasharray={dashed?'11 9':undefined} fill="none" opacity={opacity} markerEnd={`url(#${color===C.red?'arrow-red':'arrow-gray'})`}/>;
}
function Message({action,progress}:{action:string|null;progress:number}){
 if(!action)return null;
 if(action==='selfVote')return <circle data-moving-body="self-vote" cx="310" cy="440" r={70+8*Math.sin(progress*Math.PI)} fill="none" stroke={C.red} strokeWidth="6" strokeDasharray={`${progress*440} 1000`} transform="rotate(-90 310 440)"/>;
 if(action==='timeout')return <g>{label(1130,565,'等待有效回复',26,C.muted)}<path d="M1130 588H1370" stroke={C.edge} strokeWidth="9" strokeLinecap="round"/><path d={`M1130 588H${1130+240*progress}`} stroke={C.red} strokeWidth="9" strokeLinecap="round"/></g>;
 const points=routes[action];if(!points)throw Error(`Missing message route ${action}`);
 const moving=pointOn(points,progress*.94+.03);
 return <g data-message-kind={action}><Connection points={points} color={C.red} dashed/>{progress<.96&&<circle data-moving-body={action} cx={moving[0]} cy={moving[1]} r="11" fill={C.red} stroke={C.surface} strokeWidth="4"/>}</g>;
}

function Sentinel({id,state,focus}:{id:string;state:State;focus:boolean}){
 const [x,y]=positions[id],available=state.available.includes(id),voted=state.votes.includes(id);
 const active=focus||voted||state.candidate===id;
 return <g data-sentinel={id} data-available={available} opacity={available?1:.42}>
  <circle cx={x} cy={y} r="58" fill={active?C.redSoft:C.surface} stroke={active?C.red:C.edge} strokeWidth={active?5:3} strokeDasharray={available?undefined:'10 9'}/>
  <Txt x={x} y={y+12} anchor="middle" size={35} weight={800} fill={active?C.redDark:C.text}>{id}</Txt>
  <Txt x={x} y={y+96} anchor="middle" size={24} fill={C.muted}>{!available?'不可达':id==='S1'&&state.authorized?'本轮执行者':id==='S1'&&state.candidate?'执行者候选':'Sentinel 哨兵'}</Txt>
  {voted&&<g><circle cx={x+42} cy={y-43} r="18" fill={C.red}/><path d={`M${x+34} ${y-44}l6 7 11-13`} fill="none" stroke={C.surface} strokeWidth="4"/></g>}
 </g>;
}
function RedisNode({x,y,id,role,down,selected=false,rejected=false,info}:{x:number;y:number;id:string;role:string;down?:boolean;selected?:boolean;rejected?:boolean;info?:string}){
 return <g data-redis-node={id} data-role={role} data-rejected={rejected} opacity={down?.55:1}>
  <rect x={x-115} y={y-75} width="230" height="150" rx="20" fill={selected?C.redSoft:C.surface} stroke={selected||down||rejected?C.red:C.edge} strokeWidth={selected?5:3}/>
  <image href={staticFile('redis-original.svg')} x={x-96} y={y-55} width="45" height="45"/>
  <Txt x={x-36} y={y-20} size={31} weight={800}>{role} {id}</Txt>
  <Txt x={x} y={y+33} size={26} anchor="middle" fill={down?C.redDark:C.muted}>{down?'失联':info||'业务数据节点'}</Txt>
  {rejected&&<g><rect x={x-82} y={y+88} width="164" height="42" rx="10" fill={C.redSoft}/><Txt x={x} y={y+118} size={25} fill={C.redDark} anchor="middle">资格不通过</Txt></g>}
 </g>;
}
const headings:Record<string,string>={
 '01':'两份故障报告，为什么还不能换主？','02':'数据节点与哨兵，先分清两组对象','03':'一个哨兵：先形成自己的故障判断','04':'故障确认：收齐两份有效判断','05':'投票选的是执行者 S1','06':'已知五个哨兵，多数仍是三票','07':'故障确认通过，执行授权仍不足','08':'独立对照：回到投票前','09':'先检查副本资格，再考虑晋升','10':'命令已经发出，还要等角色报告','11':'重配复制关系，再恢复客户端访问','12':'多数授权，不会补齐异步复制缺口','13':'三步换主，分别解决三个问题'};
const chapterNames:Record<string,string>={failure:'故障确认',authorization:'执行授权',promotion:'副本晋升',boundary:'保证与边界'};

function Gate({x,labelText,count,total,success,visible=true}:{x:number;labelText:string;count:number;total:number;success:boolean;visible?:boolean}){
 if(!visible)return null;
 return <g data-gate={labelText}><rect x={x} y="894" width="785" height="60" rx="14" fill={success?C.redSoft:C.surface} stroke={success?C.red:C.edge} strokeWidth="2"/>
  <Txt x={x+24} y="934" size={27}>{labelText}</Txt><Txt x={x+500} y="935" size={34} anchor="middle" mono fill={success?C.redDark:C.muted}>{count}/{total}</Txt><Txt x={x+755} y="934" size={26} anchor="end" fill={success?C.redDark:C.muted}>{success?'通过':'未通过'}</Txt></g>;
}
function VoteTray({state}:{state:State}){
 return <g data-vote-tray="true"><Txt x="146" y="851" size={25} fill={C.muted}>第 {state.epoch} 轮 → S1</Txt>{state.known.map((id,i)=><g key={id}><rect x={410+i*90} y="817" width="72" height="43" rx="8" fill={state.votes.includes(id)?C.red:C.surface} stroke={state.votes.includes(id)?C.red:C.edge} strokeWidth="2"/><Txt x={446+i*90} y="847" anchor="middle" size={24} fill={state.votes.includes(id)?C.surface:C.muted}>{state.votes.includes(id)?id:'—'}</Txt></g>)}<Txt x="910" y="849" size={25} fill={C.muted}>授权票</Txt></g>;
}
function Boundary({stageIndex}:{stageIndex:number}){
 const dead=stageIndex>0;
 return <g data-boundary-example="true">
  <Txt x="960" y="294" anchor="middle" size={28} fill={C.muted}>独立边界示例 · 旧主已确认 w42，获选副本尚未收到</Txt>
  <Connection points={[[710,500],[1210,500]]} dashed opacity={.6}/><Txt x="960" y="470" anchor="middle" size={30} fill={C.redDark}>尚未复制</Txt>
  <RedisNode x={550} y={500} id="M" role="旧主" down={dead}/><RedisNode x={1370} y={500} id="R2" role={stageIndex===2?'新主':'副本'} selected={stageIndex===2}/>
  <rect x="420" y="650" width="260" height="95" rx="15" fill={C.redSoft} stroke={C.red} strokeWidth="3"/><Txt x="550" y="710" size={36} mono anchor="middle" fill={C.redDark}>w42</Txt>
  <rect x="1240" y="650" width="260" height="95" rx="15" fill={C.surface} stroke={C.edge} strokeWidth="3" strokeDasharray="10 8"/><Txt x="1370" y="709" size={30} anchor="middle" fill={C.muted}>没有 w42</Txt>
  <Txt x="550" y="807" size={27} anchor="middle" fill={C.muted}>{dead?'离线；原字节仍保留':'已经向应用确认'}</Txt><Txt x="1370" y="807" size={27} anchor="middle" fill={C.redDark}>{stageIndex===2?'晋升后仍缺这条写入':'尚未收到这条写入'}</Txt>
 </g>;
}

function Caption({text}:{text:string}){
 if(!text)return null;
 const chars=[...text],lines=[];while(chars.length)lines.push(chars.splice(0,38).join(''));
 if(lines.length>2)throw Error('COPYFIT: subtitle exceeds two lines');
 return <g data-subtitle="true"><rect x="95" y="972" width="1730" height="99" rx="12" fill={C.text} opacity=".94"/>{lines.map((line,i)=><Txt key={i} x="960" y={lines.length===1?1033:1008+i*45} size={34} fill={C.surface} anchor="middle" weight={550}>{line}</Txt>)}</g>;
}

function Canvas({shotId,stageIndex,progress=1,captions='',actualFrame=0}:{shotId:string;stageIndex:number;progress?:number;captions?:string;actualFrame?:number}){
 const stages=(model.shots as any)[shotId] as Stage[];const stage=stages[Math.min(stageIndex,stages.length-1)];
 const commit=stage.action?progress>=.94:progress>=.35;
 const state=commit?stage.after:stage.before;
 const focused=shotId==='03'&&stageIndex>0;
 const showVotes=Number(shotId)>=5&&Number(shotId)<=8;
 const showGate=shotId!=='02'&&shotId!=='12';
 const showAuth=shotId==='01'||Number(shotId)>=5;
 const showClient=shotId==='11';
 const chapter=(allShots.find(s=>s.id===shotId) as any)?.chapterId||state.chapter;
 return <svg data-canvas="redis-sentinel" data-model-state={stage.id} data-state-phase={commit?'after':'before'} data-visual-state={JSON.stringify(state)} data-action-progress={progress} data-frame={actualFrame} viewBox="0 0 1920 1080" width="1920" height="1080" style={{fontFamily:FONT,background:C.bg}}>
  <defs><marker id="arrow-gray" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5L0 9" fill={C.link}/></marker><marker id="arrow-red" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5L0 9" fill={C.red}/></marker></defs>
  <RedisBackdrop/><RedisHeader ep={50} title="Sentinel" chapter={chapterNames[chapter]}/>
  <Txt x="960" y="193" size={48} weight={850} anchor="middle">{headings[shotId]}</Txt>
  {shotId==='12'?<Boundary stageIndex={stageIndex}/>:<>
   <Txt x="145" y="268" size={25} fill={C.muted}>{shotId==='08'?'独立条件：三台可达；重新展示同轮投票':'教学示例 · 已知 5 个哨兵 / 故障确认数 2'}</Txt>
   <Txt x="145" y="315" size={30} fill={C.redDark}>监控与协调</Txt><Txt x="1280" y="315" size={30} fill={C.redDark}>保存与复制业务数据</Txt>
   {state.r1Follows==='M'?<Connection points={[[1400,515],[1300,625]]} opacity={state.mDown?.35:.8}/>:<Connection points={[[1515,720],[1415,720]]} color={C.red}/>}
   {state.r2Role==='副本'&&<Connection points={[[1520,515],[1630,625]]} opacity={state.mDown?.35:.8}/>}
   {(shotId==='03'||shotId==='04')&&<Connection points={routes.ping} dashed opacity={.35}/>}
   <Message action={stage.action} progress={progress}/>
   {state.known.map(id=><Sentinel key={id} id={id} state={state} focus={id==='S1'&&focused||id==='S1'&&state.diagnosis>0&&Number(shotId)<=4}/>)}
   <RedisNode x={1460} y={440} id="M" role={state.mDown?'旧主':'主节点'} down={state.mDown}/>
   <RedisNode x={1300} y={720} id="R1" role={state.r1Role} rejected={state.r1Rejected} info={shotId==='09'?'进度 900 / priority 0':state.r1Follows==='R2'?'跟随新主 R2':undefined}/>
   <RedisNode x={1630} y={720} id="R2" role={state.r2Role} selected={state.selected==='R2'} info={shotId==='09'?'进度 800 / priority 100':state.r2Role==='主节点'?'接管写入':undefined}/>
   {showVotes&&<VoteTray state={state}/>}
   {(shotId==='03'||shotId==='04')&&<Txt x="1040" y="857" size={27} fill={C.redDark}>{state.objective?'客观下线：故障确认通过':state.diagnosis>0?'S1：主观下线':'持续探测，等待有效回复'}</Txt>}
   {shotId==='09'&&<Txt x="1440" y="876" anchor="middle" size={27} fill={C.redDark}>{state.selected?'R2 合格，进入晋升':'先过滤资格，不先比较进度'}</Txt>}
   {shotId==='10'&&<Txt x="960" y="855" anchor="middle" size={29} fill={C.redDark}>{state.promotionObserved?'已观察到 R2 成为主节点':state.r2Role==='主节点'?'R2 已改角色；等待报告到达执行者':'发送晋升命令 → 等待角色改变'}</Txt>}
   {showClient&&<g data-client="true"><rect x="920" y="640" width="160" height="120" rx="17" fill={C.surface} stroke={C.edge} strokeWidth="3"/><Txt x="1000" y="691" anchor="middle" size={27}>客户端</Txt><Txt x="1000" y="731" anchor="middle" size={23} fill={C.muted}>{state.clientTarget==='R2'?'直连新主 R2':'查询主地址'}</Txt><Txt x="960" y="861" anchor="middle" size={27} fill={C.redDark}>{state.clientTarget==='R2'?'Sentinel 提供地址；业务请求直接连接 Redis':'重配复制关系，并传播新地址'}</Txt></g>}
   {shotId==='13'&&<g><rect x="159" y="820" width="1602" height="49" rx="12" fill={C.surface}/><Txt x="960" y="855" anchor="middle" size={30} fill={C.redDark}>{stage.detail} · 两份报告与三张授权票各司其职</Txt></g>}
   {showGate&&<><Gate x={145} labelText="故障确认" count={state.diagnosis} total={2} success={state.objective}/><Gate x={990} labelText="执行者授权" count={state.votes.length} total={3} success={state.authorized} visible={showAuth}/></>}
  </>}
  <Caption text={captions}/>
 </svg>;
}

export function Main({hideCaptions=false}:{hideCaptions?:boolean}){
 const frame=useCurrentFrame();const shot=allShots.find((s:any)=>frame>=s.from&&frame<s.from+s.durationInFrames)||allShots[allShots.length-1];const local=frame-shot.from;
 const windows=(timing.shots as any)[shot.id];const window=windows.find((w:any)=>local>=w.from&&local<w.to)||windows[windows.length-1];
 const progress=clamp((local-window.from)/Math.max(1,window.to-window.from-1));
 return <AbsoluteFill><Audio src={staticFile('audio/voice.wav')}/><Canvas shotId={shot.id} stageIndex={window.index} progress={progress} captions={hideCaptions?'':subtitles(shot,local)} actualFrame={frame}/></AbsoluteFill>;
}
export function MechanismPreview({shotId='08',stage=0,progress=1}:{shotId?:string;stage?:number;progress?:number}){
 return <AbsoluteFill><Canvas shotId={shotId} stageIndex={stage} progress={progress}/></AbsoluteFill>;
}
export function MechanismSequence({shotId='08'}:{shotId?:string}){
 const frame=useCurrentFrame(),stages=(model.shots as any)[shotId];return <AbsoluteFill><Canvas shotId={shotId} stageIndex={Math.min(stages.length-1,Math.floor(frame/60))} progress={(frame%60)/59}/></AbsoluteFill>;
}
