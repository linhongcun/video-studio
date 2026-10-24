import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots} from './data';
import {C,FONT} from './theme';
import {at} from './motion';
import {Text,Title,Note,Node,Packet,Transit,Arrow,Tick,Fact,StateBoard,ease,lerp,clamp} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;
const phase=(s:Shot,f:number,i:number,a=.05,b=.7)=>ease(f,at(s,i,a),at(s,i,b)-at(s,i,a));
const cue=(s:Shot,t:string)=>Number(s.cueFrames?.labels?.[t]??Math.max(1,Number(s.cueFrames?.sentences?.[0]??9)-2));
const subgoal=<Text x={130} y={270} w={1650} size={27} color={C.muted}>同一目标：判断订单 8124 能否申请退款</Text>;
const known=['签收：3 天（订单查询）','使用情况：未知'];
const complete=['签收：3 天（订单查询）','规则：7 天内，且未使用','用户补充：未使用'];
const ChangeAction=({p,from,to,color=C.gold}:{p:number;from:string;to:string;color?:string})=><div style={{position:'absolute',left:1320,top:468,width:440,height:90,overflow:'hidden'}}><Text x={0} y={lerp(0,-105,p)} w={440} size={51} color={C.muted} alpha={1-p} center weight={700}>{from}</Text><Text x={0} y={lerp(105,0,p)} w={440} size={51} color={color} alpha={p} center weight={700}>{to}</Text></div>;
const QueryNodes=({model,program,source,sourceName='查询来源',focus='',modelVisible=true}:{model:string[];program:string[];source:string[];sourceName?:string;focus?:string;modelVisible?:boolean})=><><Node x={420} name={modelVisible?'模型':'选择位置'} lines={model} active={focus==='model'} color={C.blue}/><Node x={980} name="执行程序" lines={program} active={focus==='program'} color={C.gold}/><Node x={1540} name={sourceName} lines={source} active={focus==='source'} color={C.teal}/></>;
const outPath=(p:number,text:string)=>p<.5?<Transit text={text+'请求'} x1={420} x2={980} p={p*2} color={C.gold}/>:<Transit text={'程序执行'+text} x1={980} x2={1540} p={(p-.5)*2} color={C.teal} w={470}/>;
const backPath=(p:number,text:string)=>p<.5?<Transit text={text} x1={1540} x2={980} p={p*2} color={C.blue}/>:<Transit text={text} x1={980} x2={420} p={(p-.5)*2} color={C.blue}/>;
const questionPath=(p:number)=>p<.5?<Transit text="询问请求" x1={420} x2={980} p={p*2} color={C.gold}/>:<Transit text="商品有没有使用过？" x1={980} x2={1540} p={(p-.5)*2} color={C.gold} w={470}/>;

const Scene=({s,f}:{s:Shot;f:number})=>{
 const id=Number(s.id);
 if(id===1){
  const sec=f/30,stage=sec<1.9?0:sec<4?1:2;
  let transit:React.ReactNode=null;
  if(sec>=.3&&sec<1.3)transit=outPath(clamp((sec-.3)/1),'查订单');
  else if(sec>=1.3&&sec<1.9)transit=backPath(clamp((sec-1.3)/.6),'订单结果 · 已收起');
  else if(sec>=1.9&&sec<3)transit=outPath(clamp((sec-1.9)/1.1),'查规则');
  else if(sec>=3&&sec<3.9)transit=backPath(clamp((sec-3)/.9),'规则结果 · 已收起');
  else if(sec>=4&&sec<5)transit=questionPath(clamp(sec-4));
  return <><Title><span style={{opacity:f>=cue(s,'智能体')?1:0}}>AI 智能体，</span>下一步怎么选？</Title><Text x={130} y={270} w={1650} size={27} color={C.muted}>先看这次变化 · 订单 8124 能否申请退款？</Text>
   <Node x={420} name="下一步" lines={[stage===0?'查询订单':stage===1?'查询规则':'询问用户？']} active color={stage===2?C.gold:C.blue}/>
   <Node x={980} name="执行程序" lines={[stage===2?'传递问题':'执行查询']} active={stage<2} color={C.teal}/>
   <Node x={1540} name={stage===2?'用户':'查询来源'} lines={[stage===2?'商品用过吗？':stage===0?'订单记录':'退款规则']} active={stage===2} color={C.gold}/>
   {transit}<Note color={C.gold}>{sec>=4?'查着订单，怎么突然回来问你？':'同一笔咨询：查订单、查规则，然后呢？'}</Note></>;
 }
 if(id===2){
  const request=phase(s,f,0,.05,.3),query=phase(s,f,0,.4,.7),returned=phase(s,f,1,.04,.85),checked=f>=at(s,0,.38),visible=f>=cue(s,'模型');
  return <><Title>回到第一次查询：先拿本单资料</Title>{subgoal}
   <QueryNodes modelVisible={visible} model={returned>.99?['订单结果已返回']:['选择：查订单 8124']} program={checked?[returned>0?'回传本单结果':'读取权限：通过']:[request>.99?'核对读取权限':'等待调用请求']} source={query>.99?['本单记录已取回']:['等待读取本单']} sourceName="订单查询" focus={returned>.99?'model':query>0?'source':'program'}/>
   {returned>0?backPath(returned,'订单查询结果'):f<at(s,0,.4)?<Transit text="查订单 8124 请求" x1={420} x2={980} p={request} color={C.gold} w={460}/>:<Transit text="程序执行订单查询" x1={980} x2={1540} p={query} color={C.teal} w={460}/>}
   <Note alpha={visible?1:0}>模型提出请求，程序核对权限后真正执行</Note></>;
 }
 if(id===3){
  const p=phase(s,f,0,.05,.4),u=phase(s,f,0,.45,.8),q=phase(s,f,1,.05,.65);
  return <><Title>查到签收时间，还需要对照规则</Title>{subgoal}
   <StateBoard known={[]} missing={q>.2?'适用的\n退款规则':''} next={q>.8?'查规则':'待选择'} active={q>.8} color={C.blue}/>
   <div style={{transform:`translateY(${lerp(55,0,p)}px)`,opacity:p}}><Fact y={395} fresh color={C.blue}>{known[0]}</Fact></div>
   <div style={{transform:`translateY(${lerp(55,0,u)}px)`,opacity:u}}><Fact y={490} color={C.gold}>{known[1]}</Fact></div>
   <Arrow x1={1180} x2={1280} y={525} p={q} color={C.blue} alpha={q}/>
   <Note alpha={q}>签收时间拿到了，申请条件还要从规则里查</Note></>;
 }
 if(id===4){
  const outward=phase(s,f,0,.08,.8),returned=phase(s,f,1,.05,.85);
  return <><Title>缺规则，就发出查规则的请求</Title><Text x={130} y={270} w={1660} size={27} color={C.muted}>已知签收 3 天、使用未知 → 还缺适用规则</Text>
   <QueryNodes model={returned>.99?['规则原文已返回']:['选择：查退款规则']} program={[returned>0?'把原文结果交回模型':'执行只读查询']} source={outward>.99?['返回对应规则原文']:['读取本单适用政策']} sourceName="规则查询" focus={returned>.99?'model':outward>.5?'source':'program'}/>
   {returned>0?backPath(returned,'对应规则原文'):outPath(outward,'查规则')}
   <Note>这次查询，是由“还缺规则”这个缺口推动的</Note></>;
 }
 if(id===5){
  const p=phase(s,f,0,.05,.42),u=phase(s,f,0,.48,.85),q=phase(s,f,1,.05,.65);
  return <><Title>返回的规则，提出两个条件</Title><Text x={130} y={270} w={1660} size={27} color={C.muted}>教学示例政策 · 两项需要同时满足</Text>
   <Text x={130} y={330} w={600} size={27} color={C.muted}>已经拿到：本单查询结果</Text>
   <Fact y={414} color={C.blue}>签收：3 天</Fact><Fact y={527} color={C.gold}>使用情况：未知</Fact>
   <Text x={1010} y={330} w={760} size={27} color={C.muted}>新拿到：本单适用的示例规则</Text>
   <Node x={1390} y={405} w={760} h={290} name="可以申请，需要同时满足" lines={[]} active color={C.blue}/>
   <Text x={1050} y={503} w={680} size={40} color={C.blue} alpha={p}>签收 7 天内</Text>
   <Text x={1050} y={585} w={680} size={40} color={C.gold} alpha={u}>并且，未使用</Text>
   <Note alpha={q}>拿到了规则，不代表拿到了“是否使用”的事实</Note></>;
 }
 if(id===6){
  const p=phase(s,f,0,.05,.7),q=phase(s,f,1,.05,.7);
  return <><Title>使用情况未知，下一步就改成询问</Title>{subgoal}
   <StateBoard known={['签收 3 天，符合 7 天内','规则还要求：未使用','使用情况：未知']} missing={q>.2?'是否\n使用过？':'对照两项\n申请条件'} next="" active={q>.75} highlight={q>.2?2:0} color={q>.2?C.gold:C.teal}/>
   <Tick x={705} y={432} alpha={p}/><ChangeAction p={q} from="查询规则" to="询问用户"/>
   <Arrow x1={1180} x2={1280} y={525} p={q} color={C.gold} alpha={q}/>
   <Note alpha={q} color={C.gold}>规则给了条件，却没有填上“使用情况”这个缺口</Note></>;
 }
 if(id===7){
  const p=phase(s,f,0,.05,.8),wait=f>=at(s,1,.05);
  return <><Title>把缺少的信息，问给用户</Title><Text x={130} y={270} w={1660} size={27} color={C.gold}>还缺：这件商品是否使用过？</Text>
   <QueryNodes model={['选择：询问使用情况']} program={[wait?'本轮暂停':'把问题送给用户']} source={[wait?'等待用户补充':'商品有没有使用过？']} sourceName="用户" focus={wait?'source':'model'}/>
   {questionPath(p)}
   <Note color={C.gold}>{wait?'问题送到了，这一轮停下来等补充':'这次选择了询问，而不是再做一次查询'}</Note></>;
 }
 if(id===8){
  const p=phase(s,f,0,.05,.8),q=phase(s,f,1,.05,.8);
  return <><Title>用户补充，也要带着来源交回模型</Title>{subgoal}
   <QueryNodes model={q>.99?['订单 + 规则','用户补充：未使用']:['等待补充信息']} program={p>.99?['保留已查到的资料','加入用户回答']:['接收用户回答']} source={['没有使用过','来源：用户补充']} sourceName="用户回答" focus={q>.99?'model':'program'}/>
   {q>0?<Transit text="订单 + 规则 + 用户补充" x1={980} x2={420} p={q} color={C.blue} w={500}/>:<Transit text="用户补充：未使用" x1={1540} x2={980} p={p} color={C.blue} w={450}/>}
   <Note>回答和先前的查询资料，成为本次判断的共同输入</Note></>;
 }
 if(id===9){
  const p=phase(s,f,0,.08,.7),q=phase(s,f,1,.05,.65);
  return <><Title>按当前资料，给出有依据的建议</Title>{subgoal}
   <StateBoard known={complete} missing={'当前资料\n已经补齐'} next={p>.7?'给出建议':'核对资料'} active={p>.7} highlight={2} color={C.teal} missingColor={C.teal}/>
   <Packet x={960} y={705} w={1150} color={C.teal} alpha={p}>按目前查询与用户陈述：可以申请</Packet>
   <Text x={1410} y={785} w={360} size={22} color={C.muted} alpha={q} center>本片未执行退款</Text>
   <Note alpha={q}>这一轮完成的是有依据的申请建议</Note></>;
 }
 if(id===10){
  const p=phase(s,f,0,.05,.8),q=phase(s,f,1,.05,.8);
  return <><Title>模型选动作，程序真正执行</Title><Text x={130} y={270} w={1660} size={27} color={C.muted}>回看这次查询的分工 · 不重做一遍咨询</Text>
   <svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><rect x={170} y={350} width={1050} height={300} rx={18} stroke={C.blue} strokeWidth={2} fill="none"/></svg>
   <Text x={225} y={315} w={940} size={25} color={C.blue} center>智能体中的模型与执行控制</Text>
   <QueryNodes model={q>.99?['收到结果后','下一步：询问用户']:['选择：查规则']} program={[q>0?'把结果反馈给模型':'实际执行查询']} source={['提供规则结果']} sourceName="查询来源" focus={q>.99?'model':p>.5?'source':'program'}/>
   {q>0?backPath(q,'查询结果'):outPath(p,'查规则')}
   <Note>执行结果回到模型，下一次选择才有了新的依据</Note></>;
 }
 const p=phase(s,f,0,.05,.7),q=phase(s,f,1,.05,.7);
 return <><Title>原来，那次反问是这样选出来的</Title><Text x={130} y={270} w={1660} size={27} color={C.muted}>回到查完规则时 · 兑现开头的悬念</Text>
  <StateBoard known={['签收：3 天','规则：7 天内，且未使用','使用情况：未知']} missing={'是否\n使用过？'} next="" highlight={p>.5?2:-1} active={q>.75} color={C.gold}/>
  <ChangeAction p={q} from="继续查资料？" to="询问用户"/>
  <Arrow x1={1180} x2={1280} y={525} p={q} color={C.gold} alpha={q}/>
  <Note color={C.teal} alpha={q}>返回的信息改变缺口，缺口改变下一步选择</Note>
  <Text x={650} y={884} w={620} size={23} color={C.muted} alpha={q} center>IT小村 · 原创</Text>
 </>;
};

const ShotView=({s,captions}:{s:Shot;captions:boolean})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(x=>f>=x.from&&f<=(x.to??x.from+(x.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 82% 4%,#173B5544,transparent 62%)'}}/>
  <Text x={130} y={63} w={1320} size={25} color={C.muted}>同一示例订单 8124 · 只看下一步怎样选</Text>
  <Text x={1700} y={62} w={150} size={25}>IT小村</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:930,minHeight:100,padding:'8px 12px',boxSizing:'border-box',background:`${C.bg}F8`,fontSize:39,lineHeight:1.4,fontWeight:500,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
