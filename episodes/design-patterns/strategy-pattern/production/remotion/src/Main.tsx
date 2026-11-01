import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import {C,FONT,MONO} from './theme';
import javaCard from './java-card.json';
import {at,beat} from './motion';
import {Heading,Note,Reset,Text,Frame,Path,clamp,lerp} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;

type Pricing='member'|'campaign';
const label=(pricing:string)=>pricing==='member'?'会员定价':'活动定价';
const rate=(pricing:string)=>pricing==='member'?'90%':'80%';
const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??0);
const RequestPath:[number,number][]=[[415,568],[960,568],[960,652]];
const ReturnPath:[number,number][]=[[960,652],[960,568],[1505,568],[1505,538]];

const Selection:React.FC<{pricing?:Pricing;waiting?:boolean;alpha?:number;active?:boolean;previous?:boolean;review?:boolean}>=({pricing='member',waiting=false,alpha=1,active=false,previous=false,review=false})=><Text x={220} y={276} w={1480} size={29} color={C.muted} center alpha={alpha}>
 <span style={{color:active?C.gold:C.muted}}>{review?'回看会员90元、活动80元；当前选择：':previous?'上次选择：':'选择：'}</span><span style={{color:C.teal,fontWeight:700,textDecoration:active?'underline':'none',textUnderlineOffset:7}}>{waiting?'本次尚未决定':label(pricing)}</span>{!waiting&&!review&&' · 决定本次采用谁'}
</Text>;
const Settlement:React.FC<{output?:string;outputAlpha?:number;mixed?:boolean;scope?:boolean;delegate?:boolean;suppressPricing?:boolean;continued?:boolean;focus?:'read'|'pricing'|'result'|'whole';alpha?:number}>=({output,outputAlpha=1,mixed=false,scope=false,delegate=false,suppressPricing=false,continued=false,focus,alpha=1})=><div style={{opacity:alpha}}>
 <Frame x={150} y={330} w={1620} h={276} label="结算流程" color={scope||focus==='whole'?C.gold:C.edge}/>
 {[415,960,1505].map((x,i)=><div key={x} style={{position:'absolute',left:x-210,top:393,width:420,height:160,borderTop:'2px solid '+((focus==='read'&&i===0)||(focus==='pricing'&&i===1)||(focus==='result'&&i===2)?C.gold:'transparent'),background:((focus==='read'&&i===0)||(focus==='pricing'&&i===1)||(focus==='result'&&i===2))?C.gold+'08':'transparent'}}/>)}
 <Text x={220} y={408} w={390} size={31} center>读取原价</Text>
 <Text x={220} y={471} w={390} size={54} center color={C.blue} weight={750}>100元</Text>
 <Text x={730} y={408} w={460} size={31} center color={delegate?C.teal:C.text}>{delegate?'按约定使用当前策略':'定价'}</Text>
 {mixed?<>
  <Text x={730} y={455} w={460} size={31} center color={C.teal}>会员定价 · 九折</Text>
  <Text x={730} y={507} w={460} size={31} center color={C.teal}>活动定价 · 八折</Text>
 </>:!suppressPricing&&<Text x={730} y={482} w={460} size={27} center color={C.muted}>{delegate?'具体定价交给所选策略':'这项职责仍由结算发起'}</Text>}
 <Text x={1310} y={408} w={390} size={31} center>显示应付</Text>
 <Text x={1310} y={471} w={390} size={output?54:34} center color={output?C.gold:C.muted} weight={750} alpha={output?outputAlpha:1}>{output??'等待本次结果'}</Text>
 <Path points={[[620,430],[715,430]]} color={C.edge}/><Path points={[[1205,430],[1295,430]]} color={C.edge}/>
 {continued&&<Text x={1320} y={555} w={370} size={24} center color={C.gold}>使用返回金额，流程继续</Text>}
</div>;
const Contract:React.FC<{alpha?:number;active?:boolean}>=({alpha=1,active=false})=><>
 <Path points={[[960,606],[960,652]]} color={active?C.gold:C.teal} alpha={alpha}/>
 <Text x={1005} y={614} w={690} size={24} color={active?C.gold:C.teal} alpha={alpha}>约定：接收原价，交回应付金额</Text>
</>;
const CurrentPricing:React.FC<{pricing?:Pricing;computed?:boolean;detail?:boolean;active?:boolean;pending?:boolean;alpha?:number;alternative?:boolean}>=({pricing='member',computed=false,detail=true,active=false,pending=false,alpha=1,alternative=true})=><div style={{opacity:alpha}}>
 <Frame x={510} y={652} w={900} h={151} color={active?C.gold:C.teal}/>
 <Text x={535} y={671} w={850} size={34} center color={C.teal} weight={700}>当前定价策略：{label(pricing)}</Text>
 {detail&&<Text x={535} y={728} w={850} size={34} center>{computed?<><span style={{color:C.blue}}>100元</span> × {rate(pricing)} = <span style={{color:C.gold}}>{pricing==='member'?'90元':'80元'}</span></>:pending?'本次尚未定价':pricing==='member'?'接收原价，负责九折定价':'接收原价，负责八折定价'}</Text>}
 {alternative&&<Text x={1450} y={710} w={300} size={23} color={C.muted} center>备选：{label(pricing==='member'?'campaign':'member')}</Text>}
</div>;
const PreparedPricing:React.FC<{results?:number;maintenance?:boolean;named?:boolean;alpha?:number}>=({results=0,maintenance=false,named=true,alpha=1})=><div style={{opacity:alpha}}>
 {(['member','campaign'] as Pricing[]).map((pricing,i)=><div key={pricing} style={{opacity:maintenance&&i===1?.45:1}}>
  <Frame x={i===0?300:1010} y={652} w={610} h={151} color={maintenance&&i===0?C.gold:C.teal}/>
  <Text x={i===0?320:1030} y={673} w={570} size={33} center color={C.teal} weight={700}>{label(pricing)}{named?'策略':''}</Text>
  {maintenance&&i===0?<Frame x={335} y={723} w={540} h={62} color={C.gold}><Text x={10} y={10} w={520} size={28} center color={C.gold}>本例可独立维护的九折细节</Text></Frame>:<Text x={i===0?320:1030} y={733} w={570} size={32} center color={results>.1?C.gold:C.text}>{results>.1?(pricing==='member'?'100元 → 90元':'100元 → 80元'):(pricing==='member'?'负责九折定价':'负责八折定价')}</Text>}
 </div>)}
</div>;
const AmountTravel:React.FC<{points:[number,number][];p:number;text:string;color:string;endInset?:number}>=({points,p,text,color,endInset=35})=>{
 let total=0;const lengths:number[]=[];for(let i=1;i<points.length;i++){total+=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lengths.push(total);}let x=points[0][0],y=points[0][1],dist=clamp(p)*Math.max(0,total-endInset);
 for(let i=1;i<points.length;i++){const previous=i===1?0:lengths[i-2],ratio=clamp((dist-previous)/Math.max(1,lengths[i-1]-previous));x=lerp(points[i-1][0],points[i][0],ratio);y=lerp(points[i-1][1],points[i][1],ratio);if(ratio<1)break;}
 const opacity=1-clamp((p-.9)/.1);
 return <><Path points={points} p={p} color={color}/><div style={{position:'absolute',left:x-90,top:y-22,width:180,height:44,border:'2px solid '+color,borderRadius:9,background:C.bg,opacity,boxSizing:'border-box'}}><Text x={8} y={0} w={160} size={29} center color={color}>{text}</Text></div></>;
};

const CheckoutUI:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const progress=beat(s,f,'campaign'),changed=progress>0,done=progress>=.99;
 const price=changed?(done?'80元':'计算中'):'90元';
 const accent=(which:Pricing)=>which===(changed?'campaign':'member')?C.gold:C.edge;
 return <><Heading>换一种优惠，结算怎样照常继续？</Heading>
  <Frame x={180} y={315} w={1560} h={492} label="结算页 · 教学示意" color={C.blue}/>
  <Text x={235} y={390} w={610} size={27} color={C.muted}>商品清单</Text>
  <Text x={235} y={439} w={610} size={39} weight={700}>示例商品 × 1</Text>
  <Text x={235} y={509} w={610} size={29} color={C.muted}>商品原价</Text>
  <Text x={235} y={558} w={610} size={70} color={C.blue} weight={750}>100元</Text>
  <Text x={235} y={705} w={610} size={26} color={C.muted}>本例每次只选一种优惠，不叠加</Text>
  <div style={{position:'absolute',left:900,top:385,width:2,height:360,background:C.edge}}/>
  <Text x={960} y={380} w={705} size={29}>选择本次定价办法</Text>
  {(['member','campaign'] as Pricing[]).map((which,i)=>{const selected=which===(changed?'campaign':'member');return <div key={which} style={{position:'absolute',left:960,top:438+i*92,width:705,height:75,border:'2px solid '+accent(which),background:selected?C.gold+'09':C.bg,borderRadius:12,boxSizing:'border-box'}}>
   <div style={{position:'absolute',left:24,top:24,width:23,height:23,border:'2px solid '+(selected?C.gold:C.muted),borderRadius:20,boxSizing:'border-box'}}>{selected&&<div style={{position:'absolute',left:4,top:4,width:11,height:11,borderRadius:12,background:C.gold}}/>}</div>
   <Text x={67} y={13} w={420} size={31} color={selected?C.gold:C.text}>{which==='member'?'会员优惠 · 九折':'活动优惠 · 八折'}</Text>
   {changed&&which==='campaign'&&progress<.5&&<div style={{position:'absolute',right:22,top:18,color:C.gold,fontSize:25}}>已改选</div>}
  </div>;})}
  <Text x={960} y={664} w={300} size={30} color={C.muted}>本次应付</Text>
  <Text x={1280} y={649} w={385} size={56} color={C.gold} center weight={750}>{price}</Text>
  <Note>{changed?(done?'页面改选活动后，应付80元；接下来展开背后的设计':'改选后先重新计算，不沿用会员90元结果'):'先看用户在结算页做什么，再进入内部职责'}</Note>
 </>;
};

const RoleDiagram:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const progress=beat(s,f,'roles'),started=f>=at(s,1,0);
 const current=!started?'none':progress<.22?'client':progress<.47?'context':progress<.7?'strategy':'concrete';
 const ink=(which:string)=>current===which?C.gold:C.teal;
 return <><Heading>对照结构图，把各方职责逐一对上</Heading>
  <Text x={160} y={267} w={1580} size={27} color={C.muted} center>同一个结算功能 · 业务对象与代码角色对应</Text>
  <Path points={[[490,520],[650,520]]} color={current==='client'?C.gold:C.edge}/>
  <Path points={[[1130,520],[1200,520],[1200,420],[1310,420]]} color={current==='context'?C.gold:C.edge}/>
  <Path points={[[1365,644],[1365,578],[1420,578],[1420,517]]} color={current==='concrete'?C.gold:C.edge} dashed/>
  <Path points={[[1635,644],[1635,578],[1660,578],[1660,517]]} color={current==='concrete'?C.gold:C.edge} dashed/>
  <Frame x={150} y={390} w={340} h={260} color={ink('client')} label="选择方"/>
  <Text x={174} y={457} w={292} size={29}>决定本次采用谁</Text>
  <Text x={174} y={548} w={292} size={24} color={C.muted}>Client · main</Text>
  <Frame x={650} y={390} w={480} h={260} color={ink('context')} label="结算上下文"/>
  <Text x={678} y={451} w={424} size={30}>读取原价
委托定价，显示应付</Text>
  <Text x={678} y={554} w={424} size={25} color={C.muted}>Context · Checkout</Text>
  <Frame x={1310} y={330} w={450} h={187} color={ink('strategy')} label="抽象定价约定"/>
  <Text x={1334} y={391} w={402} size={29}>原价 → 应付金额</Text>
  <Text x={1334} y={447} w={402} size={24} color={C.muted}>Strategy · PricingStrategy</Text>
  <Frame x={1240} y={644} w={260} h={151} color={ink('concrete')} label="会员定价"/>
  <Text x={1260} y={704} w={220} size={30} color={C.text}>负责九折</Text>
  <Text x={1260} y={752} w={220} size={21} color={C.muted}>MemberPricing</Text>
  <Frame x={1510} y={644} w={260} h={151} color={ink('concrete')} label="活动定价"/>
  <Text x={1530} y={704} w={220} size={30} color={C.text}>负责八折</Text>
  <Text x={1530} y={752} w={220} size={21} color={C.muted}>CampaignPricing</Text>
  <Text x={494} y={477} w={152} size={22} color={C.muted} center>配置</Text>
  <Text x={1138} y={438} w={165} size={22} color={C.muted} center>按约定使用</Text>
  <Note color={started?C.teal:C.muted}>{!started?'先认清结构，再沿同一关系看一次计算':current==='client'?'选择方配置本次采用谁，不承担九折或八折细节':current==='context'?'结算通过共同约定使用所选策略':current==='strategy'?'抽象策略说明各方共同依赖的定价约定':'具体策略各自计算；接下来先选会员，看一次委托'}</Note>
 </>;
};

const JavaCodeCard:React.FC=()=>{
 const ref=useRef<HTMLPreElement>(null),card=javaCard as {title?:string;subtitle?:string;lines:string[]};
 useLayoutEffect(()=>{const e=ref.current;if(e&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))console.error('COPYFIT Java key-code card',e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight);},[]);
 return <AbsoluteFill data-java-card style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <Text x={130} y={55} w={1300} size={25} color={C.muted}>设计模式 · 策略模式</Text><Text x={1690} y={55} w={150} size={25}>IT小村</Text>
  <Text x={130} y={124} w={1660} size={47} weight={750}>{card.title??'Java关键代码 · 节选'} <span style={{color:C.gold}}> · {card.subtitle??'暂停查看'}</span></Text>
  <pre ref={ref} data-fit style={{position:'absolute',left:150,top:217,width:1620,height:750,margin:0,padding:'15px 22px',boxSizing:'border-box',borderLeft:'3px solid '+C.teal,background:C.surface,fontFamily:MONO,fontSize:26,lineHeight:1.24,whiteSpace:'pre',overflow:'hidden'}}>{card.lines.join('\n')}</pre>
  <Text x={130} y={999} w={1660} size={25} color={C.muted} center>同一原价100元，会员90元、活动80元 · 本例优惠二选一</Text>
 </AbsoluteFill>;
};

const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='checkout-ui')return <CheckoutUI s={s} f={f}/>;
 if(kind==='mixed-pricing'){
  const p=beat(s,f,'details'),q=beat(s,f,'maintenance');
  return <><Heading>结算页背后，共同步骤与定价细节先写在同一处</Heading>
   <Settlement mixed={p>.1} scope={q>.2} focus={q>.2?'pricing':undefined}/>
   <Note alpha={q}>维护一种定价办法时，也要进入这段共同流程</Note>
  </>;
 }
 if(kind==='separate-pricing'){
  const p=beat(s,f,'separate'),finish=beat(s,f,'retained');
  return <><Heading>{f<at(s,1,0)?'接下来，把会变化的定价做法分开':'做法独立，读取原价和显示应付的位置保留'}</Heading>
   <Settlement suppressPricing focus={p>.05&&p<.99?'pricing':undefined}/>
   <Frame x={300} y={652} w={1320} h={151} color={C.teal} alpha={p}/>
   {(['member','campaign'] as Pricing[]).map((pricing,i)=>{const w=lerp(460,570,p);return <div key={pricing} style={{position:'absolute',left:lerp(730,i===0?320:1030,p),top:lerp(i===0?455:507,704,p),width:w,height:48,background:C.bg}}><Text x={0} y={0} w={w} size={31} center color={C.teal}>{label(pricing)} · {pricing==='member'?'九折':'八折'}</Text></div>;})}
   <Text x={730} y={482} w={460} size={27} center color={C.teal} alpha={finish}>定价职责保留，具体做法分开</Text>
   <Note alpha={finish}>结算仍要定价，具体怎么算交给独立办法</Note>
  </>;
 }
 if(kind==='shared-contract'){
  const visible=f>=termAt(s,'策略模式'),p=beat(s,f,'contract'),q=beat(s,f,'examples');
  return <><Heading>{visible?'策略模式：独立的做法，按共同约定替换使用':'独立的定价办法怎样配合结算？'}</Heading><Reset>共同约定与作用示例 · 本镜没有开始新的结算</Reset>
   <Settlement delegate/>
   <Contract alpha={p} active={q>.2}/>
   <PreparedPricing results={q} named={visible}/>
   <Note alpha={q}>接收的都是原价，交回的都是应付金额；结果可以不同</Note>
  </>;
 }
 if(kind==='role-structure')return <RoleDiagram s={s} f={f}/>;
 if(kind==='member-delegation'){
  const request=beat(s,f,'request'),calculation=beat(s,f,'calculation'),returned=beat(s,f,'returned'),used=beat(s,f,'used');
  const computed=calculation>=.99,done=returned>=.99;
  return <><Heading>结算交出定价任务，会员策略交回应付金额</Heading><Selection pricing="member"/>
   <Settlement delegate output={done?'90元':undefined} continued={used>.3} focus={used>.3?'result':request>.1?'pricing':'read'}/><Contract/>
   <CurrentPricing pricing="member" computed={computed} active={request>.4&&!done}/>
   {f>=at(s,0,.1)&&request<.99&&<AmountTravel points={RequestPath} p={request} text="100元" color={C.blue}/>}
   {f>=at(s,1,.28)&&!done&&<AmountTravel points={ReturnPath} p={returned} text="90元" color={C.gold} endInset={40}/>}
   <Note>{used>.3?'结算使用返回的90元，继续原有流程':'具体九折留在会员策略内部，结算按约定使用它'}</Note>
  </>;
 }
 if(kind==='swap-strategy'){
  const clear=beat(s,f,'cleared'),selection=beat(s,f,'selection'),request=beat(s,f,'request'),calculation=beat(s,f,'calculation'),returned=beat(s,f,'returned'),used=beat(s,f,'used');
  const changed=selection>=.99,pricing:Pricing=changed?'campaign':'member',done=returned>=.99;
  return <><Heading>先清空90元，再从原价100元改用活动策略</Heading><Selection pricing={pricing} active={selection>.1&&selection<.99}/>
   <Settlement delegate output={done?'80元':clear<.99?'90元':undefined} outputAlpha={done?1:1-clear} continued={used>.3} focus={used>.3?'result':request>.1?'pricing':undefined}/><Contract/>
   <CurrentPricing pricing={pricing} computed={done||calculation>=.99||clear<.1} pending={clear>=.99&&!changed} active={request>.3&&!done}/>
   {f>=at(s,1,.04)&&request<.99&&<AmountTravel points={RequestPath} p={request} text="100元" color={C.blue}/>}
   {f>=at(s,1,.51)&&!done&&<AmountTravel points={ReturnPath} p={returned} text="80元" color={C.gold} endInset={40}/>}
   <Note>{used>.3?'活动交回80元，结算仍按原来的步骤继续':changed?'本次改选活动，重新使用100元原价，会员不执行':'先结束会员这次结果，再选择另一种定价办法'}</Note>
  </>;
 }
 if(kind==='stable-collaboration'){
  const p=beat(s,f,'steps'),q=beat(s,f,'contract'),focus=p<.33?'read':p<.66?'pricing':'result';
  return <><Heading>步骤保留，定价通过同一个约定交给策略</Heading><Selection pricing="campaign" review/>
   <Settlement delegate output="80元" focus={q>.1?'pricing':focus}/><Contract active={q>.2}/><CurrentPricing pricing="campaign" detail={q<.4}/>
   <Note alpha={q}>结算依赖共同计价约定，具体九折、八折分别留在策略内部</Note>
  </>;
 }
 if(kind==='maintenance-boundary'){
  const p=beat(s,f,'scope');
  return <><Heading>{f<at(s,1,0)?'两种策略能替换，再看怎样分别维护':'本例共同约定不变时，维护会员策略内部细节'}</Heading>
   <Selection pricing="campaign" previous alpha={p>.2?.4:1}/>
   <Settlement delegate output="80元" alpha={p>.2?.45:1}/><Contract active={p>.2}/>
   {p>.2?<PreparedPricing maintenance/>:<CurrentPricing pricing="campaign" detail={false}/>}
   <Note>{p>.2?'仅圈定会员策略内部；活动策略和共同流程保留原样':'本镜展示维护范围，不重新选择或计算金额'}</Note>
  </>;
 }
 if(kind==='cost-boundary'){
  const focus=beat(s,f,'reading'),direct=beat(s,f,'direct');
  if(f>=at(s,1,.04))return <><Heading>只有少量长期稳定判断，直接处理也合理</Heading><Settlement mixed/><Note alpha={direct}>拆分与协作也有维护成本，按实际变化选择结构</Note></>;
  return <><Heading>选择与协作仍需维护，阅读也要多追踪一层</Heading><Selection pricing="campaign" active={focus<.3}/>
   <Settlement delegate output="80元" focus={focus<.45?'pricing':undefined}/><Contract active={focus>=.3&&focus<.65}/><CurrentPricing pricing="campaign" active={focus>=.65}/>
   <Note>阅读时：从结算的定价职责，追到当前策略的具体做法</Note>
  </>;
 }
 const p=beat(s,f,'roles'),q=beat(s,f,'idea');
 return <><Heading>变化独立，策略可换，共同步骤保留</Heading><Selection pricing="campaign" active={p<.33}/>
  <Settlement delegate output="80元" focus={p>.66?'whole':undefined}/><Contract active={q>.2}/><CurrentPricing pricing="campaign" active={p>=.33&&p<=.66}/>
  <Note color={C.teal} alpha={q}>选择决定采用谁，策略负责怎么算，结算按共同约定使用它</Note>
  <Text x={640} y={885} w={640} size={23} center color={C.muted} alpha={q}>IT小村 · 原创</Text>
 </>;
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 if(Number.isInteger(s.javaCardFrom)&&f>=s.javaCardFrom)return <JavaCodeCard/>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.chapterTitle??'同一流程，不同策略'}</Text><Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>{s.visualType==='checkout-ui'?'结算功能 · 教学示意':'示例订单 · 原价100元 · 每次只选一种定价办法'}</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
