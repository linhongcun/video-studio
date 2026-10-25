import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import {C,FONT} from './theme';
import {Heading,Note,Reset,Text,Frame,Path} from './objects';
import {at,beat} from './motion';
import {ProductPanel,ContractComparison,RoleStructure,RuntimeNodes,MessageCard,ReceiptCard,Passing,JavaCodeCard} from './components';
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
  return <><Heading>换了通知服务，发货提醒怎样继续用？</Heading><ProductPanel state={accepted?'accepted':click>=.99?'submitting':'ready'} click={click}/><Note>{accepted?'这次提交已受理，还要等待送达回执':'先看商家在订单页做什么，再展开背后的接入问题'}</Note></>;
 }
 if(kind==='incompatible-contracts')return <><Heading>接入前：同一个提醒任务，两套使用约定</Heading><Reset>接入前 · 开发视角 · 此处没有正在执行的请求</Reset><ContractComparison/><Note>业务要的是提交提醒并取得受理结果；服务却有自己的入参与结果表达</Note></>;
 if(kind==='roles-and-target'){
  const p=beat(s,f,'roles'),active=f>=at(s,1,0),focus=!active?'none':p<.35?'client':p<.66?'target':'sdk';
  return <><Heading>先摆清职责，再看怎样让双方配合</Heading><Reset>接入前 · 结构分析 · 契约关系不是执行路径</Reset><RoleStructure focus={focus}/><Note>{!active?'同一订单功能：谁使用，按什么约定，谁实际处理？':focus==='client'?'业务方发起订单17提醒，不处理服务自己的格式细节':focus==='target'?'目标通知约定说明业务需要什么，不是转发消息的对象':'已有外部服务负责实际处理；两套约定之间还缺一个转换者'}</Note></>;
 }
 if(kind==='introduce-adapter'){
  const shown=f>=cue(s,'适配器模式'),p=beat(s,f,'relations');
  return <><Heading>{shown?'适配器模式：转换成业务需要的使用约定':'怎样填上两套约定之间的缺口？'}</Heading><Reset>接入前 · 结构接线 · 不在一次请求运行中临时添加适配器</Reset><RoleStructure adapter={shown} focus={p<.5?'adapter':'sdk'}/><Note>{p<.5?'适配器履行目标约定，让业务按原方式使用':'适配器持有已有服务；转换后还要真正委托它执行'}</Note></>;
 }
 if(kind==='submit-through-target'){
  const active=f>=at(s,1,0),p=beat(s,f,'request');
  if(!active)return <><Heading>结构接好了，回看刚才那一次提交</Heading><Reset>机制回看 · 同一次订单17提醒 · 不再点击发送</Reset><RoleStructure adapter/><Note>先说明回看，再沿同一请求观察实际执行；不把开发接线当作现场运行</Note></>;
  return <><Heading>业务按通知约定，把同一请求交给适配器</Heading><Reset>机制回看 · 同一次提交 · 目标约定只约束调用，不转发请求</Reset><RuntimeNodes focus={p>=.99?'adapter':'client'}/><Passing from={[570,430]} to={[750,430]} p={p} label="按约定提交"/><MessageCard x={180} kind="business" active={p<.99}/>{p>=.99?<MessageCard x={1080} kind="business" active/>:<Waiting x={1080} title="适配器等待业务请求" body="收到之后，再准备服务接受的格式"/>}<Note>{p>=.99?'适配器已接到同一买家地址和同一条提醒正文':'运行请求直接从业务方到适配器，不经过目标契约节点'}</Note></>;
 }
 if(kind==='convert-and-delegate'){
  const p=beat(s,f,'convert'),q=beat(s,f,'delegate');
  return <><Heading>{q>0?'格式准备好，再调用持有的外部服务':'适配器先转换格式，保留原来的值与含义'}</Heading><Reset>机制回看 · 同一次提交 · 此时尚未取得受理结果</Reset><RuntimeNodes focus={q>=.99?'sdk':'adapter'}/><Passing from={[1170,430]} to={[1350,430]} p={q} label="委托调用"/><MessageCard x={180} kind="business" active={p<.99}/>{p>=.99?<MessageCard x={1080} kind="service" active={q<.99}/>:<Waiting x={1080} title="适配器准备服务请求" body="对应接收目标与消息内容"/>}<Passing from={[840,677]} to={[1080,677]} p={p} label="转换入参"/><Note>{q>=.99?'请求已经交给教学模拟服务；提交执行与返回受理结果是两步':q>0?'适配器真正委托所持有的服务，不只把标签换个名字':'只改变使用格式：买家地址和“订单17已发货”保持不变'}</Note></>;
 }
 if(kind==='map-acceptance'){
  const produced=beat(s,f,'produced')>=.99,received=beat(s,f,'received'),mapped=beat(s,f,'mapped'),returned=beat(s,f,'returned');
  return <><Heading>{mapped>=.99?'把已排队转换为已受理，原编号一起带回':'服务交回已排队和编号，尚未完成送达'}</Heading><Reset>机制回看 · 同一次提交 · Q17始终是同一受理编号</Reset><RuntimeNodes returned focus={returned>=.99?'client':received>=.99?'adapter':'sdk'}/><Passing from={[1350,430]} to={[1170,430]} p={received} label="服务回执"/><Passing from={[750,430]} to={[570,430]} p={returned} label="业务结果"/>{mapped>=.99?<ReceiptCard x={180} kind="business" active/>:<Waiting x={180} title="适配器准备业务结果" body={received>=.99?'已收到服务结果，按业务含义转换':'尚未取得服务返回结果'}/>}{produced?<ReceiptCard x={1080} kind="service" active={received<.99}/>:<Waiting x={1080} title="教学模拟服务" body="处理本次提交，准备返回结果"/>}<Passing from={[1080,677]} to={[840,677]} p={mapped} label="转换受理含义"/><Note>{returned>=.99?'同一编号Q17已回到业务方，接着回到刚才的订单页面':mapped>=.99?'已受理表示提交被接下，不能读成消息已经送达':produced?'“已排队”来自本例模拟服务回执，不代表买家已经收到消息':'服务尚未交回结果时，不提前显示已受理'}</Note></>;
 }
 if(kind==='accepted-ui'){
  const done=beat(s,f,'display')>=.99;
  return <><Heading>同一结果回到页面：已受理，等待送达回执</Heading><Reset>机制回看结束 · 同一次提交 · Q17</Reset><ProductPanel state={done?'accepted':'submitting'} replay/><Note>适配器能转换使用约定，不能把排队受理变成已经送达</Note></>;
 }
 if(kind==='rejection-and-unknown'){
  const active=f>=at(s,1,0),p=beat(s,f,'unknown');
  if(!active)return <><Heading>受理过程走完，再看转换不能越过的边界</Heading><Reset>主线Q17仍为已受理 · 接下来仅说明规则，不另发请求</Reset><ProductPanel state="accepted" replay/><Note>下面的拒绝与未知，是转换规则说明，不改写刚才那一次结果</Note></>;
  return <><Heading>确定拒绝与结果未知，不能当成同一种结果</Heading><Reset>规则说明 · 不另发请求 · 主线Q17保持已受理</Reset>
   <Frame x={200} y={355} w={1520} h={175} label="服务明确拒绝" color={C.red}/><Text x={250} y={426} w={650} size={36}>服务明确说不接受</Text><Path points={[[920,453],[1100,453]]} color={C.red}/><Text x={1150} y={426} w={510} size={36} color={C.red}>业务返回拒绝</Text>
   <Frame x={200} y={590} w={1520} h={195} label="技术异常、超时或未知回执" color={p>0?C.gold:C.edge}/><Text x={250} y={660} w={650} size={36}>没有确认受理结果</Text><Path points={[[920,687],[1100,687]]} color={C.gold}/><Text x={1150} y={653} w={510} size={32} color={C.gold}>不能假报已受理
也不能当作确定拒绝</Text><Note>适配器要守住结果的业务含义；本例不自动重试</Note></>;
 }
 if(kind==='maintenance-scope'){
  const p=beat(s,f,'scope');
  return <><Heading>目标约定不变时，把服务格式细节集中起来</Heading><Reset>能力能对应、目标约定不变时 · 创建、接线和配置仍需调整</Reset><RoleStructure adapter scope={p>0} focus={p>0?'adapter':'target'}/><Note>{p>0?'服务的格式和状态转换集中在适配器；并不等于全系统零改动':'看清稳定边界，再判断哪些改动能够被隔离'}</Note></>;
 }
 if(kind==='cost-and-simple-option'){
  if(f<at(s,1,0))return <><Heading>两套约定本来一致时，直接使用也合理</Heading><Reset>比较选型前提 · 不另发提醒，不切换第二家服务</Reset><Frame x={180} y={410} w={600} h={265} label="业务方" color={C.teal}/><Text x={220} y={505} w={520} size={36}>需要的约定</Text><Text x={220} y={579} w={520} size={30} color={C.muted}>与服务的使用约定一致</Text><Frame x={1140} y={410} w={600} h={265} label="已有服务" color={C.blue}/><Text x={1180} y={505} w={520} size={36}>可直接使用</Text><Text x={1180} y={579} w={520} size={30} color={C.muted}>不必为了模式增加转换层</Text><Path points={[[780,545],[1140,545]]}/><Note>前提不同，结构选择也可以不同</Note></>;
  return <><Heading>新增转换层，也增加了维护和测试成本</Heading><Reset>需要检查：入参转换、返回结果、错误边界</Reset><RoleStructure adapter focus="adapter" scope/><Note>结构接线、转换规则和错误含义，都需要有人维护</Note></>;
 }
 const p=beat(s,f,'roles');
 if(f>=at(s,1,0))return <><Heading>以业务需要的方式接入，守住结果含义</Heading><Reset>同一次订单17提醒 · Q17 · 已受理不等于已送达</Reset><ProductPanel state="accepted" replay/><Note color={C.teal}>转换使用约定，真正委托已有能力；这就是本例的适配器模式</Note><Text x={640} y={884} w={640} size={23} color={C.muted} center>IT小村 · 原创</Text></>;
 return <><Heading>回收同一关系：按约定使用，转换后真正委托</Heading><RoleStructure adapter focus={p<.3?'target':p<.65?'adapter':'sdk'}/><Note>业务方依赖目标约定，适配器转换并委托，服务实际处理</Note></>;
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 if(Number.isInteger(s.javaCardFrom)&&f>=s.javaCardFrom)return <JavaCodeCard card={javaCard}/>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.chapterTitle??'接口对不上，怎样接入新服务？'}</Text><Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>教学示例 · 订单17 · 不发送真实消息</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
