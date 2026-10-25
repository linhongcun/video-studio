import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import {C,FONT} from './theme';
import {Heading,Note,Reset,Text,Frame,Path} from './objects';
import {at,beat} from './motion';
import {ProductPanel,BusinessBenefits,UpgradeBoundary,RoleStructure,RuntimeNodes,MessageCard,ReceiptCard,Passing,JavaCodeCard} from './components';
import javaCard from './java-card.json';
declare const __HAS_VOICE_AUDIO__:boolean;
const cue=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??at(s,0,0));
const Waiting:React.FC<{x:number;title:string;body:string}>=({x,title,body})=><>
 <Frame x={x} y={565} w={660} h={220} label={title}/><Text x={x+26} y={659} w={608} size={31} color={C.muted}>{body}</Text>
</>;
const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='product-reminder'){
  const click=beat(s,f,'click'),accepted=beat(s,f,'accepted')>=.99;
  return <><Heading>接入通知服务，为什么值得主动包一层？</Heading><ProductPanel state={accepted?'accepted':click>=.99?'submitting':'ready'} click={click}/><Note>从同一个发货提醒功能，看业务怎样使用外部服务</Note></>;
 }
 if(kind==='business-first')return <><Heading>先定自己的业务用法，把外部细节留在接入处</Heading><BusinessBenefits second={f>=at(s,1,0)}/><Note>业务按自己的需要使用，减少外部升级对业务的牵动</Note></>;
 if(kind==='adapter-structure'){
  const p=beat(s,f,'relations'),shown=f>=cue(s,'适配器模式');
  return <><Heading>{shown?'适配器模式：让外部服务按业务约定接入':'先按业务需要组织这层接入关系'}</Heading><RoleStructure adapter focus={p<.3?'target':p<.67?'adapter':'sdk'}/><Note>{p<.3?'发货提醒依赖自己的通知约定':p<.67?'适配器履行这个约定，集中转换请求和结果':'适配器持有并调用外部服务，由服务实际提交'}</Note></>;
 }
 if(kind==='submit-through-target'){
  const active=f>=at(s,1,0),p=beat(s,f,'request');
  if(!active)return <><Heading>设计定好后，回看刚才那一次提交</Heading><RoleStructure adapter/><Note>同一次订单17发货提醒，现在展开它的内部协作</Note></>;
  return <><Heading>发货提醒只按自己的约定提交</Heading><Reset>同一次提交回看</Reset><RuntimeNodes focus={p>=.99?'adapter':'client'}/><Passing from={[570,430]} to={[750,430]} p={p} label="按约定提交"/><MessageCard x={180} kind="business" active={p<.99}/>{p>=.99?<MessageCard x={1080} kind="business" active/>:<Waiting x={1080} title="适配器接收业务请求" body="买家地址 + 提醒正文"/>}<Note>发货提醒不需要处理服务自己的字段组织方式</Note></>;
 }
 if(kind==='convert-and-delegate'){
  const p=beat(s,f,'convert'),q=beat(s,f,'delegate');
  return <><Heading>{q>0?'转换完成，委托外部服务提交':'先把业务请求转换成服务接受的格式'}</Heading><Reset>同一次提交回看</Reset><RuntimeNodes focus={q>=.99?'sdk':'adapter'}/><Passing from={[1170,430]} to={[1350,430]} p={q} label="委托调用"/><MessageCard x={180} kind="business" active={p<.99}/>{p>=.99?<MessageCard x={1080} kind="service" active={q<.99}/>:<Waiting x={1080} title="适配器准备服务请求" body="对应接收目标与消息内容"/>}<Passing from={[840,677]} to={[1080,677]} p={p} label="转换请求"/><Note>{q>=.99?'收件人和正文保持不变；真正提交由服务执行':'适配器负责格式转换，并调用自己持有的服务'}</Note></>;
 }
 if(kind==='return-and-feedback'){
  if(f>=at(s,1,0)){
   const displayed=beat(s,f,'display')>=.99;
   return <><Heading>同一编号回到页面，业务取得受理结果</Heading><Reset>同一次提交 · Q17</Reset><ProductPanel state={displayed?'accepted':'submitting'} replay/><Note>已受理 · 等待回执；受理不等于送达</Note></>;
  }
  const produced=beat(s,f,'produced')>=.99,received=beat(s,f,'received'),mapped=beat(s,f,'mapped'),returned=beat(s,f,'returned');
  return <><Heading>把服务的排队结果，转换成业务的已受理</Heading><RuntimeNodes returned focus={returned>=.99?'client':received>=.99?'adapter':'sdk'}/><Passing from={[1350,430]} to={[1170,430]} p={received} label="服务回执"/><Passing from={[750,430]} to={[570,430]} p={returned} label="业务结果"/>{mapped>=.99?<ReceiptCard x={180} kind="business" active/>:<Waiting x={180} title="转换为业务受理结果" body={received>=.99?'适配器转换服务返回的含义':'等待服务返回结果'}/>}{produced?<ReceiptCard x={1080} kind="service" active={received<.99}/>:<Waiting x={1080} title="外部通知服务" body="本次提交的返回结果"/>}<Passing from={[1080,677]} to={[840,677]} p={mapped} label="转换结果"/><Note>服务返回已排队和Q17，适配器统一为已受理和同一编号</Note></>;
 }
 if(kind==='external-upgrade'){
  if(f<at(s,1,0))return <><Heading>这次提交结束后，后来服务升级会影响哪里？</Heading><ProductPanel state="accepted" replay/><Note>先结束这次提交，再看后来的开发变更</Note></>;
  const request=beat(s,f,'requestChange'),receipt=beat(s,f,'receiptChange');
  return <><Heading>{receipt>0?'服务的返回格式，也多了一层包装':'服务升级了，请求格式发生变化'}</Heading><Reset>后来升级 · 开发对照</Reset><UpgradeBoundary requestV2={request>=.99} requestChanging={request>0&&request<.99} receiptV2={receipt>=.99} receiptProgress={receipt}/><Note>外部使用方式变了，发货提醒需要的通知约定仍然一样</Note></>;
 }
 if(kind==='boundary-change'){
  const request=beat(s,f,'requestUpdate'),receipt=beat(s,f,'receiptUpdate'),assembly=beat(s,f,'assemblyUpdate');
  const stable=f>=at(s,1,0);
  return <><Heading>{stable?'通知约定和发货流程保留，外部格式留在接入处':assembly>0?'更新创建与接线，把V2服务接入':receipt>0?'在适配器里更新返回转换':'在适配器里更新请求转换'}</Heading><Reset>后来升级 · 开发对照</Reset><UpgradeBoundary requestV2 receiptV2 requestUpdated={request>=.99} receiptUpdated={receipt>=.99} assemblyUpdated={assembly>=.99}/><Note color={stable?C.teal:C.muted}>{stable?'同样的业务需要，仍用自己的通知约定和发货流程':'调整适配映射和装配；业务不跟着记住外部字段与包装'}</Note></>;
 }
 if(kind==='cost-and-corruption'){
  const second=f>=at(s,1,0);
  return <><Heading>{second?'接入层仍要维护，也要看服务能力是否满足业务':'让业务保持自己的规则，外部变化留在接入处'}</Heading><RoleStructure adapter scope focus="adapter"/><Note>{second?'这层要维护和测试；新服务满足不了业务时，上层也可能要改':'适配器可以承担这样的防腐作用，转换外部接口细节'}</Note></>;
 }
 if(f<at(s,1,0))return <><Heading>先定业务自己的约定，再转换并委托已有服务</Heading><RoleStructure adapter focus="adapter"/><Note>主动按业务需要接入，让服务差异集中在边界</Note></>;
 return <><Heading>主动包一层：业务按自己的方式用，升级少牵动</Heading><BusinessBenefits second/><Note color={C.teal}>本例业务需要不变，外部格式的升级影响留在接入边界</Note><Text x={640} y={884} w={640} size={23} color={C.muted} center>IT小村 · 原创</Text></>;
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 if(Number.isInteger(s.javaCardFrom)&&f>=s.javaCardFrom)return <JavaCodeCard card={javaCard}/>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.chapterTitle??'接口对不上，怎样接入新服务？'}</Text><Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>教学示例 · 订单17 · 模拟通知服务</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
