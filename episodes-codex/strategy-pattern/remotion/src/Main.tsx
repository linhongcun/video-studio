import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import {C,FONT} from './theme';
import {at,beat} from './motion';
import {Heading,Note,Reset,Text,Frame,Path} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;

const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??Math.max(1,Number(s.cueFrames?.sentences?.[0]??9)-2));
type Method='member'|'campaign';
const methodLabel=(method:string)=>method==='member'?'会员函数':'活动函数';
const methodRate=(method:string)=>method==='member'?'90%':'80%';

const Money:React.FC<{x:number;y?:number;label:string;amount?:string;detail?:string;color?:string;alpha?:number}>=({x,y=414,label,amount,detail,color=C.blue,alpha=1})=><div style={{position:'absolute',left:x-190,top:y,width:380,height:195,opacity:alpha}}>
 <Text x={0} y={0} w={380} size={29} color={C.muted} center>{label}</Text>
 <Text x={0} y={53} w={380} size={76} color={amount?color:C.muted} center weight={750}>{amount??'—'}</Text>
 {detail&&<Text x={0} y={153} w={380} size={27} color={C.muted} center>{detail}</Text>}
</div>;
const MethodCard:React.FC<{method?:Method;x?:number;y?:number;w?:number;formula?:boolean;alpha?:number;active?:boolean;label?:string}>=({method='member',x=960,y=383,w=570,formula=true,alpha=1,active=false,label})=><Frame x={x-w/2} y={y} w={w} h={220} color={C.teal} alpha={alpha}>
 <Text x={24} y={22} w={w-48} size={27} center color={C.muted}>{label??methodLabel(method)}</Text>
 <Text x={24} y={70} w={w-48} size={52} center color={C.teal} weight={750} mono>{method}</Text>
 {formula&&<Text x={24} y={151} w={w-48} size={30} center color={active?C.gold:C.text}>原金额 × {methodRate(method)}</Text>}
</Frame>;
const CallLine:React.FC<{method?:Method;x?:number;y?:number;size?:number;alpha?:number;highlight?:boolean;emphasis?:boolean}>=({method='member',x=240,y=330,size=52,alpha=1,highlight=true,emphasis=false})=><Text x={x} y={y} w={1450} size={size} mono alpha={alpha}>
 <span style={{color:C.text}}>checkout(</span><span style={{color:C.blue}}>10000</span><span>, </span><span style={{color:highlight?C.teal:C.text,fontWeight:750,textDecoration:emphasis?'underline':'none',textUnderlineOffset:8}}>{method}</span><span>)</span>
</Text>;
const CoreCode:React.FC<{method?:Method;binding?:number;amountBinding?:number;line?:number;result?:boolean;resultAlpha?:number;oldResult?:boolean;clear?:number;calculation?:boolean;invocation?:boolean;argumentFocus?:boolean}>=({method='member',binding=1,amountBinding=1,line=-1,result=false,resultAlpha=1,oldResult=false,clear=0,calculation=false,invocation=false,argumentFocus=false})=>{
 const amount=method==='member'?'9000':'8000',yuan=method==='member'?'90元':'80元';
 return <>
  <CallLine method={method} emphasis={argumentFocus}/>
  <Text x={240} y={460} w={1450} size={44} mono><span>def checkout(amount, </span><span style={{color:C.teal,fontWeight:750}}>pricing</span><span>):</span></Text>
  {line===0&&<div style={{position:'absolute',left:237,top:533,width:910,height:66,background:C.gold+'12',borderLeft:'3px solid '+C.gold}}/>}
  <Text x={240} y={535} w={1450} size={44} mono><span>    payable = </span><span style={{color:C.teal,fontWeight:750,textDecoration:line===0?'underline':'none',textUnderlineOffset:7}}>pricing</span><span>(</span><span style={{color:C.blue}}>amount</span><span>)</span></Text>
  {line===1&&<div style={{position:'absolute',left:237,top:608,width:910,height:66,background:C.gold+'12',borderLeft:'3px solid '+C.gold}}/>}
  <Text x={240} y={610} w={1450} size={44} mono color={line===1?C.gold:C.text}>    return payable</Text>
  <Path points={[[833,413],[833,433],[860,433],[860,450]]} color={C.teal} p={binding}/>
  <Path points={[[599,413],[599,433],[662,433],[662,450]]} color={C.blue} p={amountBinding}/>
  <Text x={240} y={721} w={1050} size={32} color={binding>0?C.teal:C.blue}>{invocation?<>pricing(amount) → {method}(<span style={{color:C.blue}}>10000</span>)</>:binding>0?<>本次 pricing 对应 {method} 函数</>:'amount 接收原金额10000分'}</Text>
  {calculation&&<Text x={240} y={777} w={1050} size={30} color={C.gold}>10000分 × {methodRate(method)} = {amount}分</Text>}
  {result&&<Money x={1535} y={486} label="调用后得到" amount={amount+'分'} detail={yuan} color={C.gold} alpha={resultAlpha}/>}
  {oldResult&&<Money x={1535} y={486} label="上一轮结果 · 将清空" amount="9000分" detail="90元" color={C.gold} alpha={1-clear}/>}
 </>;
};

const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='question'){
  const p=beat(s,f,'member'),q=beat(s,f,'campaign');
  return <><Heading>同样100元，为什么付的钱不同？</Heading>
   <Money x={370} label="同一笔示例订单" amount="100元"/>
   <Text x={725} y={414} w={410} size={36} center color={C.muted}>选择哪种计算办法？</Text>
   <Path points={[[570,505],[690,505]]} p={p} color={C.blue}/>
   <Text x={1230} y={383} w={510} size={48} color={C.teal} alpha={p}>会员九折 → <span style={{color:C.gold}}>90元</span></Text>
   <Text x={1230} y={536} w={510} size={48} color={C.teal} alpha={q}>活动八折 → <span style={{color:C.gold}}>80元</span></Text>
   <Note alpha={q}>原金额不变，变化的是计算应付金额的办法</Note>
  </>;
 }
 if(kind==='inline-rules'){
  const p=beat(s,f,'activity'),q=beat(s,f,'motive');
  return <><Heading>先看直接写法：计算办法都放在结算里</Heading>
   <Frame x={430} y={326} w={1060} h={426} label="结算" color={C.edge}>
    <Text x={40} y={102} w={980} size={43} center color={C.teal}>会员 → 原金额 × 90%</Text>
    <Text x={40} y={229} w={980} size={43} center color={C.teal} alpha={p}>活动 → 原金额 × 80%</Text>
   </Frame>
   <Note alpha={q}>两种办法需要各自维护时，考虑把它们独立出来</Note>
  </>;
 }
 if(kind==='member-method'){
  const p=beat(s,f,'input'),q=beat(s,f,'result');
  return <><Heading>{f<at(s,1,0)?'接下来，先单独看会员怎么算':'会员函数：收到原金额，算出应付金额'}</Heading><Reset>函数作用示例 · 这里只说明会员函数会做什么</Reset>
   <Money x={310} label="传入原金额" amount="100元"/>
   <MethodCard method="member" active={q>.2}/>
   <Path points={[[500,490],[675,490]]} p={p} color={C.blue}/>
   <Path points={[[1245,490],[1430,490]]} p={q} color={C.gold}/>
   <Money x={1620} label="返回应付金额" amount={q>=.99?'90元':undefined} color={C.gold}/>
   <Note>函数始终叫 member，90元是它执行后返回的结果</Note>
  </>;
 }
 if(kind==='two-strategies'){
  const visible=f>=termAt(s,'策略模式'),p=beat(s,f,'campaign');
  return <><Heading>{visible?'策略模式：把不同计算办法独立出来':'先把计算办法独立出来看'}</Heading>
   <MethodCard method="member" x={520} y={358} w={640} label={visible?'会员策略':'会员函数'}/>
   <MethodCard method="campaign" x={1400} y={358} w={640} alpha={p} label="活动策略"/>
   <Text x={350} y={671} w={1220} size={38} center color={C.teal} alpha={p}>它们都接收原金额，返回应付金额</Text>
   <Note alpha={p}>计算方法可以不同，结算使用的约定保持一致</Note>
  </>;
 }
 if(kind==='choose-function'){
  const p=beat(s,f,'selected'),q=beat(s,f,'explained');
  if(f<at(s,1,.03))return <><Heading>两种办法准备好了，接下来选一个给结算</Heading><Reset>开始一次新的结算 · 清空前面的函数作用示例结果</Reset><MethodCard method="member" x={520} y={358} w={640}/><MethodCard method="campaign" x={1400} y={358} w={640}/><Note>这次还没有计算应付金额</Note></>;
  return <><Heading>先选会员函数，再交给结算</Heading><Reset>新的结算 · 金额单位是分：10000分 = 100元</Reset>
   <CallLine y={395} size={66}/>
   <Text x={240} y={550} w={1450} size={39} color={C.teal} alpha={p}>member：这次选择的会员函数</Text>
   <Text x={240} y={642} w={1450} size={34} color={C.muted} alpha={q}>把这一行拆开看：先传入金额和要使用的函数</Text>
   <Note alpha={q}>member 后面没有括号，这一步交过去的是函数</Note>
  </>;
 }
 if(kind==='function-not-result'){
  const p=beat(s,f,'emphasis'),q=beat(s,f,'parameter');
  return <><Heading>交过去的是会员函数，本次结果尚未计算</Heading><Reset>沿用同一次调用 · 10000分 = 100元 · 先看传入的内容</Reset>
   <CallLine y={395} size={66} emphasis={p>.25}/>
   <Text x={240} y={550} w={1050} size={39} color={C.teal}>member：函数本身，没有跟调用括号</Text>
   <Text x={240} y={642} w={1050} size={34} color={C.muted} alpha={q}>函数也可以作为参数，交给结算</Text>
   <Money x={1590} y={556} label="应付金额" amount={undefined} detail="尚未计算" color={C.gold}/>
   <Note alpha={q}>函数可以像其他参数一样传进去；调用之后，才有结果</Note>
  </>;
 }
 if(kind==='parameter-binding'){
  const p=beat(s,f,'amount'),q=beat(s,f,'function');
  return <><Heading>同一个会员函数，在结算里由 pricing 参数代表</Heading><Reset>核心逻辑摘录 · 金额单位：分 · 完整校验见配套文章</Reset>
   <CoreCode method="member" amountBinding={p} binding={q}/>
   <Note alpha={q}>本次传入 member，所以调用 pricing 就是调用会员函数</Note>
  </>;
 }
 if(kind==='execute-member'){
  const p=beat(s,f,'invocation'),calculated=beat(s,f,'calculation'),q=beat(s,f,'returned'),computed=calculated>=.99,returned=q>=.99;
  return <><Heading>现在调用收到的函数，这时才得到90元</Heading><Reset>代码金额单位：分 · 10000分 = 100元</Reset>
   <CoreCode method="member" line={returned?1:0} result={returned} resultAlpha={q} calculation={computed} invocation={p>=.99}/>
   <Note>{returned?'返回9000分，也就是90元':'执行 pricing(amount)，此时实际运行 member'}</Note>
  </>;
 }
 if(kind==='switch-function'){
  const clear=beat(s,f,'cleared'),switching=beat(s,f,'replaced'),changed=switching>.5;
  return <><Heading>{f<at(s,1,0)?'会员这次算完了，接下来换活动办法':'清空90元，换活动函数，从原价100元重新算'}</Heading><Reset>只替换传入函数 · 仍使用10000分原金额 · 不叠加优惠</Reset>
   <CoreCode method={changed?'campaign':'member'} oldResult={clear<.99} clear={clear} binding={changed?switching:1}/>
   <Note>{changed?'现在 pricing 对应 campaign；下一步再执行':'先清空上一轮结果，再替换这次使用的函数'}</Note>
  </>;
 }
 if(kind==='execute-campaign'){
  const p=beat(s,f,'invocation'),calculated=beat(s,f,'calculation'),q=beat(s,f,'returned'),computed=calculated>=.99,returned=q>=.99;
  return <><Heading>调用方式不变，活动函数这次返回80元</Heading><Reset>再次使用原价100元：10000分，不使用上一轮90元</Reset>
   <CoreCode method="campaign" line={returned?1:0} result={returned} resultAlpha={q} calculation={computed} invocation={p>=.99}/>
   <Note>{returned?'返回8000分，也就是80元':'同样调用 pricing(amount)，这次实际运行 campaign'}</Note>
  </>;
 }
 if(kind==='pattern-recap'){
  const p=beat(s,f,'responsibility'),q=beat(s,f,'definition'),focus=q>.35?'method':p>.5?'checkout':'choice';
  return <><Heading>选办法、调用、具体计算，各有自己的位置</Heading><Reset>沿用刚才的核心逻辑 · 传入哪个函数，就使用哪个函数</Reset>
   <CoreCode method="campaign" result argumentFocus={focus==='choice'} line={focus==='checkout'?0:-1} invocation={focus==='method'}/>
   <Note alpha={q}>重点是结算能接收并使用可替换的办法</Note>
  </>;
 }
 if(kind==='when-to-use'){
  const p=beat(s,f,'member'),q=beat(s,f,'campaign');
  return <><Heading>最后，再看什么时候值得这样拆分</Heading>
   <Frame x={660} y={321} w={600} h={180} color={C.edge}><Text x={24} y={22} w={552} size={37} center>结算</Text><Text x={24} y={87} w={552} size={31} center color={C.teal}>沿用同一调用入口</Text></Frame>
   <MethodCard method="member" x={520} y={582} w={640} formula={false} label={p>.25?'会员办法 · 独立维护':'会员办法'}/>
   <MethodCard method="campaign" x={1400} y={582} w={640} formula={false} label={q>.25?'活动办法 · 独立维护':'活动办法'}/>
   <Path points={[[800,501],[800,540],[520,540],[520,582]]} color={p>.25?C.gold:C.edge}/><Path points={[[1120,501],[1120,540],[1400,540],[1400,582]]} color={q>.25?C.gold:C.edge}/>
   <Note alpha={q}>需要分别替换和维护时，独立办法让结算沿用同一入口</Note>
  </>;
 }
 const p=beat(s,f,'direct'),q=beat(s,f,'cost');
 if(f<at(s,1,.03))return <><Heading>简单稳定的判断，直接写也很合理</Heading><Frame x={430} y={344} w={1060} h={365} label="少量稳定规则" color={C.edge}><Text x={30} y={90} w={1000} size={43} center>会员 → 九折</Text><Text x={30} y={215} w={1000} size={43} center>活动 → 八折</Text></Frame><Note alpha={p}>规则长期不变时，直接判断往往更省事</Note></>;
 return <><Heading>拆分也有跳转成本，要结合实际变化决定</Heading><Reset>静止阅读示意 · 沿参数追到本次实际函数，不再次计算</Reset>
  <CoreCode method="campaign" result line={q<.5?0:-1} argumentFocus={q>=.5}/>
  <Note color={C.teal} alpha={q}>{q>.8?'看实际变化，再决定是否拆分':'查看 pricing 时，还要追到本次传入的 campaign 函数'}</Note>
  <Text x={640} y={884} w={640} size={23} center color={C.muted} alpha={q}>IT小村 · 原创</Text>
 </>;
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.chapterTitle??'两种办法，同一个结算'}</Text>
  <Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>示例订单 · 原价100元 · 每次只选一种优惠</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
