import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import {C,FONT} from './theme';
import {at} from './motion';
import {Heading,Note,Reset,Text,Frame,Rule,Token,Travel,Path,Result,Code,clamp,ease,lerp} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;

const phase=(s:Shot,f:number,i:number,a=.06,b=.75)=>ease(f,at(s,i,a),at(s,i,b)-at(s,i,a));
const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??Math.max(1,Number(s.cueFrames?.sentences?.[0]??9)-2));
const names=['普通规则','会员规则','活动规则','新客规则'];
const formulas=['原价','×90%','×80%','−10元'];
const ruleY=(index:number,four=false)=>four?326+index*105:326+index*150;
const RuleBank=({selected=1,rate=80,four=false,alpha=1,changed=false,newAlpha=1,calculation}:{selected?:number;rate?:number;four?:boolean;alpha?:number;changed?:boolean;newAlpha?:number;calculation?:string})=><div style={{opacity:alpha}}>
 <Text x={1320} y={278} w={460} size={23} color={C.muted}>独立计算 · 每次只选一种</Text>
 {names.slice(0,four?4:3).map((name,i)=><Rule key={name} x={1320} y={ruleY(i,four)} w={460} name={name} formula={i===2?'×'+rate+'%':formulas[i]} active={i===selected} changed={changed&&i===2} color={changed&&i===2?C.gold:i===3?C.blue:C.teal} alpha={i===3?newAlpha:1} detail={i===selected?calculation:undefined}/>)}
</div>;
const Caller=({selected='会员',alpha=1,extra=false,highlight=false}:{selected?:string;alpha?:number;extra?:boolean;highlight?:boolean})=><Frame x={140} y={343} w={340} h={184} label="调用方" color={highlight?C.gold:C.edge} alpha={alpha}>
 <Text x={20} y={65} w={300} size={34} center color={C.gold} weight={650}>{selected?'选择：'+selected:'等待选择'}</Text>
 <Text x={20} y={126} w={300} size={21} center color={highlight?C.gold:C.muted}>{extra?'可选项已加入新客':'选择责任保留在这里'}</Text>
</Frame>;
const Checkout=({amount='',waiting=true,alpha=1,focus=false}:{amount?:string;waiting?:boolean;alpha?:number;focus?:boolean})=><Frame x={620} y={400} w={500} h={350} label="结算" color={focus?C.teal:C.edge} alpha={alpha}>
 <Text x={24} y={75} w={452} size={30} center>读取原金额</Text>
 <Text x={24} y={127} w={452} size={30} center color={C.teal}>调用收到的规则</Text>
 <div style={{position:'absolute',left:30,top:220,width:440,height:110,borderTop:`2px solid ${waiting?C.edge:C.teal}`}}>
  <Text x={0} y={9} w={440} size={22} center color={C.muted}>应付金额</Text>
  <Text x={0} y={43} w={440} size={47} center color={waiting?C.muted:C.teal} weight={750}>{waiting?'等待返回':amount+' 元'}</Text>
 </div>
</Frame>;
const selectionPoints:[[number,number],[number,number]]=[[480,436],[620,436]];
const inputPoints:[number,number][]=[[300,680],[545,680],[545,590],[620,590]];
const callPoints=(selected=1,four=false):[number,number][]=>[[1120,535],[1220,535],[1220,ruleY(selected,four)+51],[1320,ruleY(selected,four)+51]];
const returnPoints=(selected=1,four=false):[number,number][]=>[[1320,ruleY(selected,four)+81],[1250,ruleY(selected,four)+81],[1250,780],[870,780],[870,715]];
const Whole=({selected=1,rate=80,amount='',waiting=true,caller=true,four=false,changed=false,newAlpha=1,selection=true,orderVisible=true,calculation}:{selected?:number;rate?:number;amount?:string;waiting?:boolean;caller?:boolean;four?:boolean;changed?:boolean;newAlpha?:number;selection?:boolean;orderVisible?:boolean;calculation?:string})=><>
 {caller&&<Caller selected={selected>=0?names[selected].replace('规则',''):''} extra={four&&selected===3} highlight={four&&selected===3}/>}
 <Checkout amount={amount} waiting={waiting} focus/>
 <RuleBank selected={selected} rate={rate} four={four} changed={changed} newAlpha={newAlpha} calculation={calculation}/>
 {caller&&selection&&<Path points={selectionPoints} color={selected>=0?C.gold:C.edge} dashed={selected<0}/>}
 <Text x={140} y={586} w={340} size={22} color={C.muted} center>本次重新计算</Text>
 {orderVisible&&<Token text="原价 100 元" x={300} y={680} color={C.blue} w={290}/>}
</>;
const oldRules=[['普通','原金额'],['会员','金额 × 90%'],['活动','金额 × 80%']];
const Old=({count=3,scope=false,request=false,amount='',alpha=1,showResult=true}:{count?:number;scope?:boolean;request?:boolean;amount?:string;alpha?:number;showResult?:boolean})=><div style={{opacity:alpha}}>
 <Frame x={380} y={337} w={1160} h={411} label="结算函数 · 计算规则写在内部" color={scope?C.gold:C.edge}/>
 <Text x={414} y={487} w={280} size={38} color={C.blue} center>读取金额</Text>
 {oldRules.slice(0,count).map(([name,formula],i)=><div key={name} style={{position:'absolute',left:760,top:404+i*107,width:660,height:88,borderLeft:`4px solid ${request&&i===2?C.gold:C.edge}`,background:request&&i===2?`${C.gold}12`:C.surface}}>
  <Text x={22} y={19} w={230} size={31} color={request&&i===2?C.gold:C.text}>{name}时</Text>
  <Text x={275} y={19} w={360} size={31} color={request&&i===2?C.gold:C.muted}>{formula}</Text>
 </div>)}
 <Token text="100 元" x={210} y={569} color={C.blue} w={220}/>
 <Path points={[[320,569],[380,569]]} color={C.blue}/>
 {showResult&&<Token text={amount?amount+' 元':'待计算'} x={1700} y={569} color={amount?C.teal:C.muted} w={230}/>}
 {showResult&&<Path points={[[1540,569],[1585,569]]} color={C.muted}/>}
</div>;

const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='hook'){
  const p=phase(s,f,0,.03,.75),q=phase(s,f,1,.05,.7);
  return <><Heading>改活动价，又要动结算？</Heading><Old scope={q>.12} request showResult={false}/>
   <Token text="活动：八折 → 七五折" x={1670} y={300} color={C.gold} w={440}/>
   <Text x={420} y={762} w={1080} size={26} center color={C.gold} alpha={q}>普通、会员、活动，都挤在同一个修改范围里</Text>
  </>;
 }
 if(kind==='monolith'){
  const p=phase(s,f,0,.08,.8),q=phase(s,f,1,.06,.75);
  return <><Heading>最初：一笔订单，原价结算</Heading><Reset>回看最初版本 · 同一100元示例订单</Reset><Old count={1} amount={q>.98?'100':''}/>
   {q<.99?<Travel points={[[210,569],[600,569],[600,448],[1090,448],[1460,448],[1460,569],[1700,569]]} p={q} text="100 元" color={C.teal} alpha={p}/>:null}
   <Note alpha={p}>没有优惠时，直接返回原金额</Note>
  </>;
 }
 if(kind==='new-rule'){
  const p=phase(s,f,0,.03,.8),q=phase(s,f,1,.03,.8),index=Math.min(2,Math.floor(q*3));
  const code=['if kind == "ordinary":','    return total_cents','if kind == "member":','    return total_cents * 90 // 100','if kind == "campaign":','    return total_cents * 80 // 100'];
  return <><Heading>优惠增加，分支也写进结算</Heading><Reset>核心分支摘录 · 金额单位为分 · 各选一次，不叠加</Reset>
   <Frame x={130} y={330} w={920} h={435} label="结算函数内的具体算法" color={C.edge}/>
   <Code lines={code.slice(0,p<.35?2:p<.7?4:6)} x={165} y={405} w={850} size={32} active={q>.05?index*2:-1}/>
   {['普通','会员','活动'].map((name,i)=><div key={name} style={{opacity:i===0?1:i===1?clamp(p*3-1):clamp(p*3-2)}}><Rule x={1210} y={340+i*145} w={510} name={name} formula={['100 元','90 元','80 元'][i]} active={index===i&&q>.02} color={C.gold}/></div>)}
   <Note>原金额仍是100元，当前每次只执行一个分支</Note>
  </>;
 }
 if(kind==='extract'){
  const p=phase(s,f,0,.06,.98),q=phase(s,f,1,.05,.68),base=at(s,0,.06),end=at(s,1,.55),progress=ease(f,base,end-base);
  return <><Heading>把会变化的算法，逐个抽出来</Heading>
   <Frame x={380} y={337} w={lerp(1160,740,progress)} h={411} label={progress>.7?'结算 · 保留共同流程':'结算函数 · 原来的位置'} color={C.edge}/>
   <Text x={414} y={487} w={280} size={38} color={C.blue} center>读取金额</Text>
   {oldRules.map(([name,formula],i)=>{const move=ease(f,base+i*13,Math.max(1,end-base-i*13));return <Rule key={name} x={lerp(760,1320,move)} y={lerp(404+i*107,ruleY(i),move)} w={lerp(660,460,move)} name={name+'规则'} formula={['原价','×90%','×80%'][i]} active={move>.02&&move<.98} color={C.teal}/>;})}
   <Text x={675} y={489} w={420} size={32} color={C.teal} center alpha={q}>调用收到的规则</Text>
   <Path points={[[1120,535],[1220,535],[1220,527],[1320,527]]} p={q} color={C.teal}/>
   <Note alpha={p}>具体计算移出去，结算保留统一调用的位置</Note>
  </>;
 }
 if(kind==='contract'){
  const p=phase(s,f,0,.03,.9),q=phase(s,f,1,.04,.8),current=Math.min(2,Math.floor(p*3)),y=ruleY(current)+51;
  return <><Heading>每一种规则，都遵守相同的约定</Heading><Reset>各次独立计算 · 输入相同，返回的应付金额可以不同</Reset>
   <Token text="原金额 100 元" x={330} y={535} color={C.blue} w={330}/>
   {names.slice(0,3).map((name,i)=><Rule key={name} x={750} y={ruleY(i)} w={500} name={name} formula={['100 元','90 元','80 元'][i]} active={i===current}/>)}
   <Path points={[[495,535],[650,535],[650,y],[750,y]]} color={C.blue}/>
   <Path points={[[1250,y],[1360,y],[1360,535],[1470,535]]} color={C.teal}/>
   <Token text={['100','90','80'][current]+' 元'} x={1615} y={535} color={C.teal} w={290}/>
   <Text x={250} y={755} w={1420} size={33} center color={C.teal} alpha={q}>原金额 → 计算规则 → 应付金额</Text>
   <Note alpha={q}>共同的是输入与输出约定，不是具体算法</Note>
  </>;
 }
 if(kind==='strategy'){
  const visible=f>=termAt(s,'策略模式'),p=phase(s,f,0,.05,.85),q=phase(s,f,1,.06,.75);
  return <><Heading>{visible?'策略模式：算法独立，主流程委托其中一种':'把可替换的算法交给结算'}</Heading>
   <Whole caller={false} selected={1}/><Path points={callPoints(1)} p={p} color={C.teal}/>
   <Token text="本例：函数" x={870} y={334} color={C.teal} alpha={q} w={360}/>
   <Note alpha={q}>先理解调用关系，不必先建一大批类</Note>
  </>;
 }
 if(kind==='select'){
  const p=phase(s,f,0,.05,.72),q=phase(s,f,1,.03,.7);
  return <><Heading>调用方先选择，再把规则交给结算</Heading><Whole selected={p>.65?1:-1} selection={false}/>
   <Travel points={selectionPoints} p={p} text="会员" color={C.gold} w={120} endInset={60} alpha={p<.99?1:0}/>
   {p>=.99&&<Path points={selectionPoints} color={C.gold}/>}
   <Path points={callPoints(1)} p={q} color={C.muted} dashed/>
   <Note alpha={q} color={C.gold}>规则选择仍然存在，责任在调用方</Note>
  </>;
 }
 if(kind==='call'){
  const p=phase(s,f,0,.05,.8),q=phase(s,f,1,.05,.8);
  return <><Heading>同一个100元，只进入选中的会员规则</Heading><Whole selected={1} orderVisible={false}/>
   {p<.99?<Travel points={inputPoints} p={p} text="100 元" color={C.blue} w={220}/>:<Path points={inputPoints} color={C.blue}/>}
   {f>=at(s,1,.05)&&(q<.99?<Travel endInset={110} points={callPoints(1)} p={q} text="100 元" color={C.teal} w={220}/>:<Path points={callPoints(1)} color={C.teal}/>)}
   <Note>普通规则、活动规则都没有执行</Note>
  </>;
 }
 if(kind==='return'){
  const p=phase(s,f,0,.04,.65),q=phase(s,f,1,.04,.78),done=q>=.99;
  return <><Heading>会员规则算完，结果才回到结算</Heading><Whole selected={1} amount="90" waiting={!done} calculation={p>.35?'100 × 90% = 90':undefined}/><Path points={callPoints(1)} color={C.muted} dashed/>
   {f>=at(s,1,.04)&&!done&&<Travel endInset={65} points={returnPoints(1)} p={q} text="90 元" color={C.teal} w={220}/>}
   <Note alpha={p}>结算接收应付金额，具体九折算法留在规则里</Note>
  </>;
 }
 if(kind==='switch'){
  const selected=phase(s,f,0,.04,.4)>.5?2:-1,input=phase(s,f,0,.45,.95),call=phase(s,f,1,.03,.4),ret=phase(s,f,1,.45,.85),done=ret>=.99;
  return <><Heading>只换活动规则，仍然从100元重新计算</Heading><Reset>清空上一结果 · 这次选活动 · 不与会员优惠叠加</Reset><Whole selected={selected} amount="80" waiting={!done} orderVisible={false}/>
   {input<.99?<Travel points={inputPoints} p={input} text="100 元" color={C.blue} alpha={f>=at(s,0,.45)?1:0}/>:<Path points={inputPoints} color={C.blue}/>}
   {f>=at(s,1,.03)&&f<at(s,1,.45)&&<Travel endInset={110} points={callPoints(2)} p={call} text="100 元" color={C.teal}/>}
   {f>=at(s,1,.45)&&!done&&<Travel endInset={65} points={returnPoints(2)} p={ret} text="80 元" color={C.teal}/>}
   <Note>调用方式没变，计算结果来自这次选中的规则</Note>
  </>;
 }
 if(kind==='change'){
  const changed=phase(s,f,0,.05,.75)>.5,call=phase(s,f,1,.03,.35),ret=phase(s,f,1,.42,.85),done=ret>=.99;
  return <><Heading>活动从八折改七五折，只修改活动规则</Heading><Reset>同一100元示例订单 · 重新计算 · 会员和结算保留原样</Reset><Whole selected={2} rate={changed?75:80} amount="75" waiting={!done} changed={changed}/>
   <Text x={1340} y={754} w={420} size={24} color={C.gold} center>{changed?'本次只改这里：75%':'旧活动规则：80%'}</Text>
   {f>=at(s,1,.03)&&f<at(s,1,.42)&&<Travel endInset={110} points={callPoints(2)} p={call} text="100 元" color={C.teal}/>}
   {f>=at(s,1,.42)&&!done&&<Travel endInset={65} points={returnPoints(2)} p={ret} text="75 元" color={C.gold}/>}
   <Note color={C.gold}>{done?'75元来自新规则的重新计算，不是在80元上再打折':f>=at(s,1,.03)?'正在从100元重新计算，等待结果返回':changed?'新规则已配置，等待从100元重新计算':'原活动规则八折，先修改活动算法'}</Note>
  </>;
 }
 if(kind==='compare'){
  const p=phase(s,f,0,.03,.7),q=phase(s,f,1,.03,.7);
  return <><Heading>减少算法对主流程的牵连，约定仍要维护</Heading><Reset>对比本次改动范围 · 不承诺结算永远不改</Reset>
   <Frame x={150} y={342} w={690} h={365} label="原来：具体规则在结算内部" color={p>.25?C.gold:C.edge}>
    {['普通算法','会员算法','活动算法：80% → 75%'].map((text,i)=><Text key={text} x={34} y={86+i*77} w={620} size={31} color={i===2?C.gold:C.muted}>{text}</Text>)}
   </Frame>
   <Frame x={1000} y={342} w={770} h={365} label="现在：规则独立，结算统一调用" color={C.edge}>
    <Text x={32} y={91} w={260} size={33} color={C.muted}>结算：不改</Text>
    <div style={{position:'absolute',left:365,top:75,width:365,height:220,border:`2px solid ${C.gold}`,borderRadius:12}}>
     <Text x={15} y={23} w={331} size={28} center>活动规则</Text><Text x={15} y={91} w={331} size={42} center color={C.gold}>80% → 75%</Text><Text x={15} y={162} w={331} size={24} center color={C.gold}>本次修改</Text>
    </div>
   </Frame>
   <Token text="共同调用约定" x={510} y={770} color={C.blue} alpha={q} w={470}/>
   <Token text="选择和注册：仍要维护" x={1360} y={770} color={C.gold} alpha={q} w={650}/>
  </>;
 }
 if(kind==='add'){
  const p=phase(s,f,0,.04,.75),registered=phase(s,f,1,.03,.3),call=phase(s,f,1,.35,.57),ret=phase(s,f,1,.63,.88),done=ret>=.99;
  return <><Heading>新增规则，也要新增调用方的可选项</Heading><Reset>另一次独立计算 · 示例100元减10元，得到90元</Reset><Whole selected={registered>.5?3:-1} rate={75} four newAlpha={p} amount="90" waiting={!done}/>
   <Text x={1320} y={755} w={460} size={25} color={C.blue} center alpha={p}>新增：新客规则函数</Text>
   <Token text="加入“新客”可选项" x={310} y={558} color={C.gold} alpha={registered} w={380}/>
   {f>=at(s,1,.35)&&f<at(s,1,.63)&&<Travel endInset={110} points={callPoints(3,true)} p={call} text="100 元" color={C.blue}/>}
   {f>=at(s,1,.63)&&!done&&<Travel endInset={65} points={returnPoints(3,true)} p={ret} text="90 元" color={C.blue}/>}
   <Note>新增实现与选择入口都要处理，结算仍通过同一约定调用</Note>
  </>;
 }
 if(kind==='code'){
  const q=phase(s,f,1,.04,.8),active=f<at(s,1,.04)?3:q<.45?9:q<.8?3:6;
  const lines=[
   'def checkout(total_cents: int, pricing: Pricing) -> int:',
   '    if type(total_cents) is not int or total_cents < 0:',
   '        raise ValueError("total_cents must be a non-negative integer")',
   '    payable = pricing(total_cents)',
   '    if type(payable) is not int or not 0 <= payable <= total_cents:',
   '        raise ValueError("pricing must return integer cents within [0, total]")',
   '    return payable',
   '',
   '# 外部选择：活动新规则（金额单位为分）',
   'checkout(10_000, select_rule("campaign"))  # 7500 分 = 75 元',
  ];
  return <><Heading>沿着函数参数，找到实际执行的规则</Heading><Reset>可暂停阅读 · 核心调用摘录，完整可运行实现见配套文章</Reset>
   <Code lines={lines} x={150} y={315} w={1620} size={28} active={active}/>
   <Note>外部选择 → 函数参数 → 统一调用 → 返回结果</Note>
  </>;
 }
 if(kind==='boundary'){
  const p=phase(s,f,0,.03,.7),q=phase(s,f,1,.03,.7);
  return <><Heading>规则值得独立变化时，再多拆这一层</Heading>
   <Frame x={160} y={338} w={700} h={390} label="简单而稳定" color={q>.35?C.edge:C.teal} alpha={1-q*.45}>
    <Text x={30} y={83} w={640} size={38} center>两条长期不变的判断</Text>
    <Text x={30} y={166} w={640} size={34} center color={C.teal} alpha={p}>直接写清楚，往往更省事</Text>
    <Text x={30} y={272} w={640} size={26} center color={C.muted}>不为套模式制造额外结构</Text>
   </Frame>
   <Frame x={1020} y={338} w={740} h={390} label="算法确实分别变化" color={q>.35?C.gold:C.edge} alpha={.45+q*.55}>
    <Text x={30} y={83} w={680} size={38} center>独立修改 · 独立验证</Text>
    <Text x={30} y={166} w={680} size={33} center color={C.gold}>结算 → 规则 → 返回</Text>
    <Text x={30} y={272} w={680} size={26} center color={C.muted} alpha={q}>代价：拆分、装配与跳转阅读</Text>
   </Frame>
   <Note color={C.gold} alpha={q}>先确认变化和收益，再决定是否承担间接层的成本</Note>
  </>;
 }
 const p=phase(s,f,0,.04,.84),q=phase(s,f,1,.04,.82),done=q>=.8;
 return <><Heading>选择在外，计算独立</Heading><Whole selected={2} rate={75} amount="75" waiting={!done}/>
  {p<.4?<Travel points={selectionPoints} p={p/.4} text="活动规则" color={C.gold} alpha={1-q}/>:<Path points={callPoints(2)} p={clamp((p-.4)/.6)} color={C.teal}/>}
  {q>.05&&q<.8&&<Travel endInset={65} points={returnPoints(2)} p={q/.8} text="75 元" color={C.teal}/>}
  <Note color={C.teal}>结算有统一入口，选择与算法各有自己的位置</Note>
  <Text x={620} y={882} w={680} size={23} color={C.muted} center alpha={q}>IT小村 · 原创</Text>
 </>;
};

const chapterNames:Record<string,string>={why:'为什么改一条规则要看整段',delegate:'把算法交给可替换的规则',change:'规则改变时，究竟改哪里',boundary:'什么时候值得多拆这一层'};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1360} size={25} color={C.muted}>设计模式 · {chapterNames[s.chapterId]??s.chapterTitle??'策略'}</Text>
  <Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>示例订单 · 原价100元 · 每次只选一种优惠</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:`${C.bg}F8`,borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
