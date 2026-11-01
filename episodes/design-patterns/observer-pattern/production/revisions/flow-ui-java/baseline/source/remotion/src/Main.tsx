import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import {C,FONT} from './theme';
import {at,beat} from './motion';
import {Heading,Note,Text,Frame,Path,clamp,lerp} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;
type State='待付款'|'已付款'|'已发货';
type Focus='source'|'list'|'summary'|'record'|'contract';
const SummaryPath:[number,number][]=[[1090,490],[1320,490]];
const RecordPath:[number,number][]=[[1090,700],[1320,700]];
const reverse=(a:[number,number][])=>[...a].reverse() as [number,number][];
const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??0);

const Notification:React.FC<{points:[number,number][];p:number;state?:State;text?:string;registration?:boolean}>=({points,p,state='已付款',text,registration=false})=>{
 const w=registration?140:154,direction=Math.sign(points[1][0]-points[0][0]),inset=w/2+1;
 const x=lerp(points[0][0]+direction*inset,points[1][0]-direction*inset,clamp(p)),y=lerp(points[0][1],points[1][1],clamp(p));
 const alpha=1-clamp((p-.92)/.08),color=registration?C.blue:C.gold;
 return <><Path points={points} p={p} color={color}/><div style={{position:'absolute',left:x-w/2,top:y-24,width:w,height:48,border:'2px solid '+color,borderRadius:9,background:C.bg,opacity:alpha,boxSizing:'border-box'}}><Text x={6} y={3} w={w-12} size={registration?24:23} center color={color}>{text??('17 · '+state)}</Text></div></>;
};
const Contract:React.FC<{alpha?:number;active?:boolean}>=({alpha=1,active=false})=><Text x={170} y={284} w={1590} size={28} center color={active?C.gold:C.teal} alpha={alpha}>共同通知约定：订单号 ＋ 新状态</Text>;
const Receiver:React.FC<{kind:'summary'|'record';summaryState?:State;recordStates?:State[];stopped?:boolean;active?:boolean;goal?:boolean;alpha?:number}>=({kind,summaryState='待付款',recordStates=[],stopped=false,active=false,goal=false,alpha=1})=>{
 const summary=kind==='summary',y=summary?350:610,h=summary?220:180,color=stopped?C.muted:active?C.gold:C.teal;
 return <div style={{opacity:alpha}}><Frame x={1320} y={y} w={450} h={h} label={summary?'订单摘要':'变化记录'} color={color}/>
  {summary?<>
   <Text x={1346} y={y+64} w={398} size={25} color={stopped?C.muted:C.text}>{goal?'付款后需要显示':stopped?'最后收到 · 已停止接收':summaryState==='待付款'?'初始显示':'最后收到的状态'}</Text>
   <Text x={1346} y={y+110} w={398} size={43} color={stopped?C.muted:active?C.gold:C.text} weight={700}>{goal?'17 · 已付款':('17 · '+summaryState)}</Text>
   {stopped&&<Text x={1346} y={y+174} w={398} size={22} color={C.muted}>保留旧值，不代表当前订单状态</Text>}
  </>:goal?<Text x={1346} y={y+85} w={398} size={33} color={C.muted}>付款后需要新增一条</Text>:recordStates.length===0?<Text x={1346} y={y+89} w={398} size={30} color={C.muted}>尚未收到变化</Text>:recordStates.map((state,i)=><Text key={i} x={1346} y={y+58+i*49} w={398} size={34} color={i===recordStates.length-1&&active?C.gold:C.text}>17 · {state}</Text>)}
 </div>;
};
const Source:React.FC<{state?:State;summaryMember?:boolean;recordMember?:boolean;direct?:boolean;focus?:Focus;alpha?:number;empty?:boolean;cost?:boolean}>=({state='待付款',summaryMember=true,recordMember=true,direct=false,focus,alpha=1,empty=false,cost=false})=><div style={{opacity:alpha}}>
 <Frame x={150} y={350} w={940} h={440} label={direct?'订单处理':'订单来源'} color={focus==='source'?C.gold:C.edge}/>
 <Text x={195} y={430} w={390} size={35} color={C.blue} weight={700}>订单17</Text>
 <Text x={195} y={494} w={390} size={27} color={C.muted}>当前状态</Text>
 <Text x={195} y={544} w={390} size={51} color={focus==='source'?C.gold:C.text} weight={750}>{state}</Text>
 <div style={{position:'absolute',left:625,top:407,width:2,height:331,background:focus==='list'?C.gold:C.edge}}/>
 <Text x={666} y={389} w={370} size={28} color={focus==='list'?C.gold:C.muted}>{direct?'内部点名通知安排':'当前接收者'}</Text>
 {[['summary','订单摘要',summaryMember,454],['record','变化记录',recordMember,664]].map(([key,name,member,y])=><div key={String(key)} style={{position:'absolute',left:666,top:Number(y),width:375,height:74,borderLeft:'4px solid '+(member&&!empty?(focus==='list'?C.gold:C.teal):C.edge),background:member&&!empty?C.surface:'transparent'}}>
  <Text x={20} y={12} w={335} size={33} color={member&&!empty?(focus==='list'?C.gold:C.text):C.muted}>{member&&!empty?(direct?'通知'+(key==='summary'?'摘要':'记录'):String(name)):'—'}</Text>
 </div>)}
 {cost&&<Text x={195} y={679} w={390} size={24} color={C.gold}>仍需维护接收关系</Text>}
</div>;
const Diagram:React.FC<{state?:State;summaryState?:State;recordStates?:State[];summaryMember?:boolean;recordMember?:boolean;direct?:boolean;focus?:Focus;stopped?:boolean;contract?:boolean;empty?:boolean;goal?:boolean;cost?:boolean;showPaths?:boolean}>=({state='待付款',summaryState='待付款',recordStates=[],summaryMember=true,recordMember=true,direct=false,focus,stopped=false,contract=true,empty=false,goal=false,cost=false,showPaths=true})=><>
 {showPaths&&!empty&&<>{summaryMember&&<Path points={SummaryPath} color={focus==='summary'?C.gold:C.edge}/>} {recordMember&&<Path points={RecordPath} color={focus==='record'?C.gold:C.edge}/>}</>}
 <Source state={state} summaryMember={summaryMember} recordMember={recordMember} direct={direct} focus={focus} empty={empty} cost={cost}/>
 <Receiver kind="summary" summaryState={summaryState} stopped={stopped} active={focus==='summary'} goal={goal}/>
 <Receiver kind="record" recordStates={recordStates} active={focus==='record'} goal={goal}/>
 {contract&&<Contract active={focus==='contract'}/>}
</>;
const PaidDiagram:React.FC<{focus?:Focus;stopped?:boolean;summaryMember?:boolean;state?:State;recordStates?:State[];cost?:boolean}>=({focus,stopped=false,summaryMember=true,state='已付款',recordStates=['已付款'],cost=false})=><Diagram state={state} summaryState="已付款" recordStates={recordStates} focus={focus} stopped={stopped} summaryMember={summaryMember} cost={cost}/>;

const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='order-change'){
  const p=beat(s,f,'summary'),q=beat(s,f,'record');
  return <><Heading>订单变了，谁要跟着响应？</Heading>
   <Frame x={190} y={350} w={820} h={440} label="商家处理示例订单" color={C.blue}/>
   <Text x={240} y={446} w={720} size={57} color={C.blue} weight={750}>订单17 · 待付款</Text>
   <Text x={240} y={560} w={720} size={33} color={C.muted}>接下来：订单付款</Text>
   <Text x={240} y={626} w={720} size={29} color={C.muted}>付款后，两项功能都需要响应</Text>
   <Receiver kind="summary" goal alpha={.35+.65*p}/><Receiver kind="record" goal alpha={.35+.65*q}/>
   <Note>两项是付款后的目标，本镜尚未执行状态更新</Note>
  </>;
 }
 if(kind==='direct-dependencies'){
  const p=beat(s,f,'summary'),q=beat(s,f,'record'),maintenance=beat(s,f,'maintenance');
  return <><Heading>订单处理里，点名安排每个接收方</Heading><Diagram direct contract={false} summaryMember={p>=.99} recordMember={q>=.99} focus={maintenance>.2?'source':undefined}/>
   {p>.01&&p<.99&&<Path points={SummaryPath} p={p} color={C.blue}/>}{q>.01&&q<.99&&<Path points={RecordPath} p={q} color={C.blue}/>}
   <Note color={maintenance>.2?C.gold:C.muted} alpha={maintenance}>接收方增减时，要回到订单处理内调整通知安排</Note>
  </>;
 }
 if(kind==='register-interest'){
  const p=beat(s,f,'summary'),q=beat(s,f,'record'),before=f<termAt(s,'订阅');
  return <><Heading>{before?'接下来，把接收需求与订单变化分开':f>=termAt(s,'订阅')?'订阅：接收方登记意愿，来源保留当前名单':'接收方登记意愿，来源保留当前名单'}</Heading>
   <Diagram direct={before} contract={false} summaryMember={before||p>=.99} recordMember={before||q>=.99} showPaths={before}/>
   {!before&&p>.0&&p<.99&&<Notification points={reverse(SummaryPath)} p={p} text="摘要登记" registration/>}
   {!before&&q>.0&&q<.99&&<Notification points={reverse(RecordPath)} p={q} text="记录登记" registration/>}
   <Note>{before?'先改变职责关系，订单当前仍是待付款':q>=.99?'两项都已登记；订单状态尚未变化':'接收方先登记，尚未发生订单变化通知'}</Note>
  </>;
 }
 if(kind==='common-notification'){
  const named=f>=termAt(s,'观察者模式'),p=beat(s,f,'contract'),q=beat(s,f,'responses');
  return <><Heading>{named?'观察者模式：订阅同一来源，各自响应变化':'关心同一来源变化的接收方，先建立联系'}</Heading>
   <Diagram contract={false} focus={q>.15?(q<.55?'summary':'record'):undefined}/><Contract alpha={p}/>
   <Note alpha={q}>通知交代发生了什么，显示与留痕分别由接收方负责</Note>
  </>;
 }
 if(kind==='change-before-notify'){
  const p=beat(s,f,'state'),q=beat(s,f,'notify');
  return <><Heading>{f<at(s,1,0)?'关系建立后，跟着这次付款走一遍':'订单先变为已付款，再通知当前接收者'}</Heading>
   <Diagram state={p>=.99?'已付款':'待付款'} focus={q>0?'list':p>0?'source':undefined}/>
   {q>0&&<Notification points={SummaryPath} p={q*.45}/>}
   <Note>{q>0?'消息：17 · 已付款；摘要尚未收到':p>=.99?'来源状态已更新，接收者尚未响应':'先看关系总览，再开始本次状态变化'}</Note>
  </>;
 }
 if(kind==='each-reacts'){
  const p=beat(s,f,'summary'),summary=beat(s,f,'summaryResponse'),q=beat(s,f,'record'),record=beat(s,f,'recordResponse'),sequential=beat(s,f,'sequential');
  return <><Heading>同一条变化事实，接收方分别处理</Heading>
   <Diagram state="已付款" summaryState={summary>=.99?'已付款':'待付款'} recordStates={record>=.99?['已付款']:[]} focus={q>0?(record>=.99?'record':undefined):p>=.99?'summary':undefined}/>
   {p<.99&&<Notification points={SummaryPath} p={.45+.55*p}/>}
   {q>0&&q<.99&&<Notification points={RecordPath} p={q}/>}
   <Note>{sequential>.2?'本例同步依次通知；模式本身不规定同时执行或后台执行':q>0?'摘要处理完后，再通知变化记录':summary>=.99?'摘要先收到，才显示已付款':'接着上镜，消息继续抵达摘要'}</Note>
  </>;
 }
 if(kind==='separate-responsibilities'){
  const p=beat(s,f,'summary'),q=beat(s,f,'record'),dependency=beat(s,f,'dependency'),focus:Focus=dependency>.1?(dependency<.5?'list':'contract'):q>.1?'record':'summary';
  return <><Heading>来源负责变化，接收方负责自己的响应</Heading><PaidDiagram focus={focus}/>
   <Note>{dependency>.1?'联系仍存在：来源保留接收关系，并依赖共同通知约定':q>.1?'变化记录负责新增事实，订单不掌握留痕细节':p>.1?'摘要负责显示，订单不掌握显示细节':'回看本次变化后，两项功能已各自响应'}</Note>
  </>;
 }
 if(kind==='unsubscribe-summary'){
  const p=beat(s,f,'cancel'),stopped=p>=.99,q=beat(s,f,'stopped');
  return <><Heading>{f<termAt(s,'取消订阅')?'两个模块都收到后，再看摘要怎样退出':'取消订阅：摘要退出名单，变化记录仍然保留'}</Heading>
   <PaidDiagram stopped={stopped} summaryMember={!stopped} focus={p>0&&!stopped?'list':undefined}/>
   {p>0&&!stopped&&<Notification points={reverse(SummaryPath)} p={p} text="摘要退出" registration/>}
   <Note>{stopped?'摘要保留最后收到的已付款，之后不再接收变化':p>0?'取消登记过程中，本次订单仍是已付款':'承接前次结果，本镜尚未发生下一次订单变化'}</Note>
  </>;
 }
 if(kind==='notify-remaining'){
  const p=beat(s,f,'state'),q=beat(s,f,'notify'),response=beat(s,f,'response');
  return <><Heading>同一订单变为已发货，只通知当前名单</Heading>
   <PaidDiagram state={p>=.99?'已发货':'已付款'} stopped summaryMember={false} recordStates={response>=.99?['已付款','已发货']:['已付款']} focus={response>0?'record':q>0?'list':p>0?'source':undefined}/>
   {q>0&&q<.99&&<Notification points={RecordPath} p={q} state="已发货"/>}
   <Note>{response>=.99?'记录保留两次变化；摘要没有收到已发货，旧值不再刷新':q>0?'当前名单仅有变化记录，摘要路径不发送消息':'订单先更新状态；退出的摘要保持停止接收'}</Note>
  </>;
 }
 if(kind==='change-membership'){
  const p=beat(s,f,'review'),q=beat(s,f,'scope');
  return <><Heading>{f<at(s,1,0)?'两次通知对比，再看什么可以独立变化':'共同约定不变时，接收者增减与响应各自维护'}</Heading>
   <PaidDiagram state="已发货" stopped summaryMember={false} recordStates={['已付款','已发货']} focus={q>.1?(q<.5?'list':'record'):undefined}/>
   <Note alpha={Math.max(p,q)} color={q>.1?C.teal:C.muted}>{q>.1?'来源仍保留名单和共同约定；响应细节不写入订单处理':'第一次：摘要＋变化记录；第二次：仅变化记录'}</Note>
  </>;
 }
 if(kind==='lifecycle-and-delivery'){
  const p=beat(s,f,'lifecycle'),q=beat(s,f,'boundary');
  return <><Heading>{f<at(s,1,0)?'接收关系需要维护，不用时及时退出':'同一程序内的通知，不自带崩溃补发保证'}</Heading>
   <PaidDiagram state="已发货" stopped summaryMember={false} recordStates={['已付款','已发货']} focus={p>.1&&q===0?'list':undefined} cost={q===0}/>
   <Note color={q>.1?C.gold:C.muted}>{q>.1?'崩溃后的补发和可靠投递，需要另外设计':'名单要随接收方的实际需要维护，取消后释放接收关系'}</Note>
  </>;
 }
 const direct=f<at(s,1,0),p=beat(s,f,'direct'),q=beat(s,f,'roles');
 if(direct)return <><Heading>只有一个长期固定接收方，直接通知也合理</Heading>
  <Frame x={220} y={390} w={600} h={300} label="订单处理" color={C.blue}/><Text x={265} y={485} w={510} size={47} center>状态变化后直接通知</Text>
  <Path points={[[820,540],[1190,540]]} color={C.teal} p={p}/><Frame x={1190} y={390} w={510} h={300} label="固定接收方" color={C.teal}/><Text x={1235} y={485} w={420} size={47} center>处理自己的响应</Text>
  <Note>结构服务实际需求，不必为了套用模式而增加关系</Note>
 </>;
 return <><Heading>把状态变化与响应分开，用订阅关系连接</Heading>
  <PaidDiagram state="已发货" stopped summaryMember={false} recordStates={['已付款','已发货']} focus={q<.33?'source':q<.67?'list':'record'}/>
  <Note color={C.teal}>来源变化 → 通知当前订阅者 → 接收方各自响应</Note>
  <Text x={640} y={882} w={640} size={23} center color={C.muted}>IT小村 · 原创</Text>
 </>;
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.visualType==='unsubscribe-summary'&&f<termAt(s,'取消订阅')?'摘要怎样退出':s.chapterTitle??'变化与响应'}</Text><Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>示例 · 同一程序内 · 订单17 · 待付款 → 已付款 → 已发货</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
