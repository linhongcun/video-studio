import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame} from 'remotion';
import solution from '../../../solution.json';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
import {EpisodeHeader} from './EpisodeHeader';
import {LeetcodeBackdrop} from '../../../../_shared/leetcode-video/Frame';
import {Terrain} from './Terrain';
import {SHOTS,FINAL,INITIAL,event,observedStep,sentence,span,clamp,Shot,TraceEvent} from '../data';
declare const __HAS_VOICE_AUDIO__:boolean;
const titles:Record<string,string>={
 problem:'这些凹处，能留下多少水？',example:'数出所有留下的水',
 'lower-wall':'第四列：水位由哪边决定？','submerged-bar':'矮柱能淹过，不同凹处水位不同',
 'reuse-highest':'相同的柱子，反复查找了很多次','left-pass':'向右扫：记住见过的最高柱',
 'right-pass':'向左扫：准备另一侧','name-method':'给两组最高值起名字',
 'depth-rule':'水位减去柱高，得到水深','edge-zero':'先说明边缘为什么没有水',
 'fill-left':'从第二列开始，一列一列相加','fill-right':'高柱加零，右边小凹处加一',
 implementation:'把同一条规则写成程序',closing:'两遍准备，一遍把水加起来'};
const chapterNames:Record<string,string>={problem:'先看哪里能留水',derive:'为什么要记住左右高点',scan:'两遍准备，再逐列加水',code:'把水深写成程序'};
const Tx=({x,y,children,size=32,color=C.text,weight=500,anchor='start'}:{x:number;y:number;children:React.ReactNode;size?:number;color?:string;weight?:number;anchor?:'start'|'middle'|'end'})=><text x={x} y={y} fontFamily={FONT} fontSize={size} fill={color} fontWeight={weight} textAnchor={anchor}>{children}</text>;
const Line=({y,children,color=C.muted,size=28}:{y:number;children:React.ReactNode;color?:string;size?:number})=><Tx x={1388} y={y} color={color} size={size}>{children}</Tx>;
const Pill=({text,x=150,y=252,color=C.gold}:{text:string;x?:number;y?:number;color?:string})=><g><rect x={x} y={y-31} width={text.length*24+38} height={47} rx={8} fill={C.surface} stroke={color} strokeOpacity={.5}/><Tx x={x+18} y={y} size={24} color={color}>{text}</Tx></g>;
const Arrow=({from,to,y,color=C.gold}:{from:number;to:number;y:number;color?:string})=><g><path d={`M ${from} ${y} H ${to}`} stroke={color} strokeWidth={5}/><path d={`M ${to} ${y} l ${to>from?-18:18} -11 v 22 Z`} fill={color}/></g>;
const EdgeArrows=({left=false,right=false}:{left?:boolean;right?:boolean})=><g>{left&&<><Arrow from={185} to={91} y={488} color={C.red}/><Tx x={75} y={540} size={23} color={C.red}>左侧敞开</Tx></>}{right&&<><Arrow from={1240} to={1321} y={703} color={C.red}/><Tx x={1200} y={900} size={23} color={C.red}>右侧敞开</Tx></>}</g>;
const splitCaption=(text:string)=>{
 const result:string[]=[];
 let remaining=text;
 while(remaining.length>38){
  const part=remaining.slice(0,38);let cut=-1;
  for(const token of ['，','、','；','。']){const found=part.lastIndexOf(token);if(found>=22)cut=Math.max(cut,found+1);}
  if(cut<0)cut=38;
  result.push(remaining.slice(0,cut));remaining=remaining.slice(cut);
 }
 if(remaining)result.push(remaining);
 return result;
};
const Captions=({shot,local}:{shot:Shot;local:number})=>{
 const sub=shot.subtitles?.find(item=>local>=item.from&&local<(item.to===undefined?item.from+(item.duration??0):item.to+1));
 if(!sub)return null;
 const lines=splitCaption(sub.text);
 return <g data-subtitle={sub.text}><rect x={80} y={930} width={1760} height={130} rx={14} fill={C.bg} fillOpacity={.97}/>{lines.map((line,i)=><g key={i}><Tx x={960} y={lines.length===1?1009:979+i*49} size={35} anchor="middle">{line}</Tx></g>)}</g>;
};
const FillPanel=({target,snapshot,committed}:{target:TraceEvent;snapshot:TraceEvent;committed:boolean})=><g data-total={snapshot.total} data-source-event={snapshot.index}>
 <Line y={365} color={C.gold}>第{target.i+1}列 · {committed?'确认':'计算中'}</Line>
 <Line y={426}>左右最高</Line>
 <Line y={477} size={35}><tspan fill={C.gold}>{target.left[target.i]}</tspan><tspan fill={C.muted}> 与 </tspan><tspan fill={C.teal}>{target.right[target.i]}</tspan><tspan fill={C.muted}> → </tspan><tspan fill={C.blue}>{target.level}</tspan></Line>
 <Line y={551}>水位 − 柱高 = 水深</Line>
 <Line y={609} size={37} color={C.text}>{target.level} − {target.height[target.i]} = {target.depth}</Line>
 <path d="M 1388 657 H 1765" stroke={C.edge} strokeWidth={2}/>
 <Line y={712} size={27}>已计入的蓝水</Line>
 <Line y={790} size={70} color={C.blue}>{snapshot.total}<tspan fontSize={28}> 格</tspan></Line>
 <Line y={851} size={23} color={committed?C.teal:C.gold}>{committed?`本列加${target.depth}，已确认`:'金框：待加入，尚未计数'}</Line>
</g>;
const Artwork=({shot,local}:{shot:Shot;local:number})=>{
 const type=shot.visualType,s2=sentence(shot,1),second=local>=s2;
 const duration=shot.durationInFrames-(shot.codeCardFrom!==undefined?shot.durationInFrames-shot.codeCardFrom:0);
 const p=span(local,12,duration-22);
 const zero=INITIAL.water;
 if(type==='implementation'){
  const selected=second?[15,16,17]:[3,4,8,12,15,16,17];
  return <g>
   <Pill text="同源程序节选 · Python下标从0开始"/>
   <rect x={137} y={302} width={998} height={520} rx={16} fill={C.surface} stroke={C.edge}/>
   {selected.map((n,i)=><g key={n}><text x={173} y={358+i*57} fill={second?C.gold:C.text} fontSize={28} fontFamily={MONO} xmlSpace="preserve">{solution.lines[n].trimStart()}</text></g>)}
   <g transform="translate(1110 390) scale(.51)"><Terrain x={0} water={FINAL.water} showColumns={false}/></g>
   <Tx x={1194} y={877} size={25} color={C.muted}>画面第3列 ↔ Python i=2</Tx>
   {second&&<><Tx x={170} y={867} size={29} color={C.gold}>三遍扫描 · 时间 O(n)</Tx><Tx x={600} y={867} size={29} color={C.teal}>两个数组 · 辅助空间 O(n)</Tx></>}
  </g>;
 }
 if(type==='left-pass'||type==='right-pass'){
  const left=type==='left-pass',step=observedStep(left?1:8,left?7:14,p);
  const prior=step.target.index===(left?1:8)?step.target.i:event(step.target.index-1).i;
  const moving=prior+(step.target.i-prior)*clamp(step.fraction/.34);
  return <g>
   <Pill text={left?'正式执行 · 预览水已清空':'正式执行 · 保留左侧记录'}/>
   <Terrain snapshot={step.snapshot} active={step.target.i} activeX={moving} showLeft showRight={!left}/>
   <Arrow from={left?155:1268} to={left?1268:155} y={279} color={left?C.gold:C.teal}/>
   <Line y={376} color={left?C.gold:C.teal}>{left?'从左向右':'从右向左'}</Line>
   <Line y={442}>正在检查第{step.target.i+1}列</Line>
   <Line y={512}>柱高 {step.target.height[step.target.i]}</Line>
   <Line y={590}>本列比较后的记录</Line>
   <Line y={672} size={69} color={left?C.gold:C.teal}>{step.committed?step.target.highest:"…"}</Line>
   <Line y={754} size={25}>先比较，再留下记录</Line>
   <Line y={810} size={24}>{left?'L：左边见过的最高柱':'R：右边见过的最高柱'}</Line>
   {!left&&second&&<Line y={866} size={26} color={C.gold}>两组都包含当前柱</Line>}
  </g>;
 }
 if(type==='fill-left'||type==='fill-right'||type==='edge-zero'){
  const first=type==='edge-zero'?15:type==='fill-left'?16:19,last=type==='edge-zero'?15:type==='fill-left'?18:21;
  const step=type==='fill-right'?(second?observedStep(21,21,span(local,s2,s2+Math.min(100,duration-s2-22))):observedStep(19,20,span(local,12,s2-12))):observedStep(first,last,type==='edge-zero'?span(local,0,Math.max(90,s2-12)):span(local,12,s2-10));
  const preview=Math.min(step.target.depth??0,Math.floor(span(step.fraction,0,.58)*(step.target.depth??0))+1);
  return <g>
   <Pill text={type==='edge-zero'&&second?'末列边界只作预览 · 执行仍在第1列':'正式执行 · 每列先算，再确认加入'}/>
   <Terrain snapshot={step.snapshot} water={step.snapshot.water} showLeft showRight active={step.target.i} ghost={!step.committed?{i:step.target.i,depth:step.target.depth??0,count:preview}:null} level={{value:step.target.level??0,from:step.target.i,to:step.target.i}}/>
   <FillPanel {...step}/>
   {type==='edge-zero'&&<><EdgeArrows left right={second}/><Tx x={188} y={894} size={25} color={C.red}>{second?'第1列无左挡柱；第7列无右挡柱，都加0':'第1列无左侧阻挡 → 加0'}</Tx></>}
   {type==='fill-right'&&step.target.index===21&&step.committed&&<Tx x={940} y={893} size={34} color={C.teal}>扫描结束 · 返回8</Tx>}
  </g>;
 }
 const preview=['example','lower-wall','submerged-bar','closing'].includes(type);
 let water=preview?FINAL.water:zero;
 let focus:number[]=[],active:number|null=null;
 if(type==='lower-wall'){focus=[0,1,2,3,4];active=3;}
 if(type==='submerged-bar'){focus=second?[4,5,6]:[0,1,2,3,4];active=second?5:2;}
 if(type==='depth-rule'){water=zero.map((_,i)=>i===2?1:0);focus=[2];active=2;}
 const showRecords=['name-method','depth-rule'].includes(type);
 return <g>
  <Pill text={type==='problem'?'原题：每柱宽1 · 非负高度':type==='example'?'题意预览 · 尚未执行程序':type==='closing'?'结果回收 · 所有蓝水共8格':type==='name-method'?'准备完成 · 尚未开始加水':type==='depth-rule'?'规则说明 · 这一格不提前计入总量':'思路分析 · 原柱子保持不动'}/>
  <Terrain water={water} active={active} snapshot={showRecords?event(14):undefined} showLeft={showRecords} showRight={showRecords} focus={focus} dim={focus.length>0} level={type==='lower-wall'?{value:3,from:0,to:3,label:'水位3'}:type==='submerged-bar'?{value:second?1:3,from:second?5:0,to:second?5:3,label:second?'水位1':'水位3'}:type==='depth-rule'?{value:3,from:2,to:2}:undefined}/>
  {type==='problem'&&<>
   <Line y={389} color={C.blue}>雨后留下的水</Line><Line y={455}>所有凹处相加</Line><Line y={539}>返回一个整数</Line>
   <rect x={1390} y={618} width={100} height={100} fill="#267CA8" stroke="#7DDDF0" strokeWidth={3}/><Line y={775} size={25}>一格 = 一单位水量</Line>
  </>}
  {type==='example'&&<>
   <Line y={389}>左边 7格</Line><Line y={455}>右边 1格</Line><Line y={559} size={66} color={C.blue}>共8格</Line><Line y={664} size={25}>灰柱不是水</Line><Line y={721} size={25}>流出去的不计入</Line>
   <EdgeArrows left={second} right={second}/>
   <Tx x={545} y={895} anchor="middle" size={29} color={C.blue}>左盆：3 + 1 + 3 = 7</Tx><Tx x={1134} y={895} anchor="middle" size={29} color={C.blue}>右盆：1</Tx>
  </>}
  {type==='lower-wall'&&<>
   <Line y={381}>左边最高 3</Line><Line y={442}>右边最高 4</Line><Line y={552} size={32} color={C.blue}>{second?'较矮的一侧决定':'该看哪一边？'}</Line><Line y={632} size={66} color={C.blue}>{second?'水位3':'3 或 4'}</Line>
   {second&&<><path d="M 216 342 H 858" stroke={C.red} strokeWidth={3} strokeDasharray="10 8"/><path d="M 755 405 C 610 405 330 407 225 433 L 87 433" fill="none" stroke={C.red} strokeWidth={4}/><path d="M 87 433 l 20 -10 v 20 Z" fill={C.red}/><Tx x={385} y={386} size={25} color={C.red}>超过3，先从左边流走</Tx></>}
  </>}
  {type==='submerged-bar'&&<>
   <Line y={384} color={C.blue}>{second?'右边小凹处':'矮柱上方也能存水'}</Line><Line y={459}>{second?'左高4，右高1':'高2的柱子被淹过'}</Line><Line y={568} size={57} color={C.blue}>{second?'水位1':'水位3'}</Line><Line y={680} size={26}>{second?'每处看自己的两侧':'更远的高3柱挡水'}</Line>
   {!second&&<><path d="M 560 505 C 495 494 354 463 220 454" fill="none" stroke={C.gold} strokeWidth={4}/><Tx x={390} y={581} size={25} color={C.gold}>柱顶以上1格水</Tx></>}
  </>}
  {type==='reuse-highest'&&<>
   <Line y={383}>{second?'往右：记住见过最高':'第2列、第4列'}</Line><Line y={449}>{second?'反向：再准备另一侧':'都会再经过相同柱子'}</Line><Line y={553} color={C.gold}>{second?'每个方向只走一遍':'重复寻找太多'}</Line>
   {!second&&<><path d="M 390 333 Q 318 302 220 333 M 720 368 Q 475 286 220 333" fill="none" stroke={C.gold} strokeWidth={4} strokeDasharray="12 7"/><path d="M 390 333 Q 560 281 876 333 M 720 368 Q 806 295 876 333" fill="none" stroke={C.teal} strokeWidth={4} strokeDasharray="12 7"/><Tx x={450} y={897} size={27} color={C.muted}>同一排柱子被反复查找</Tx></>}
   {second&&<><Arrow from={155} to={1268} y={280}/><Arrow from={1268} to={155} y={325} color={C.teal}/><Tx x={430} y={897} size={27} color={C.gold}>保留“见过的最高高度”</Tx></>}
  </>}
  {type==='name-method'&&<>
   {local>=(shot.cueFrames?.labels?.['前缀最高值']??0)&&<><Line y={380} size={34} color={C.gold}>前缀最高值</Line><Line y={438} size={25}>从左到当前列</Line></>}
   {local>=(shot.cueFrames?.labels?.['后缀最高值']??s2)&&<><Line y={550} size={34} color={C.teal}>后缀最高值</Line><Line y={608} size={25}>从右到当前列</Line></>}
   <Line y={753} size={25}>两组均包含当前柱</Line><Tx x={453} y={894} size={27} color={C.muted}>第3列的记录：L3 / R4</Tx>
  </>}
  {type==='depth-rule'&&<>
   <Line y={379} color={C.blue}>第3列 · 规则说明</Line><Line y={456}>水位 3</Line><Line y={520}>柱高 2</Line><Line y={614} size={52} color={C.gold}>3 − 2 = 1</Line><Line y={692} size={27}>只在柱顶上放1格</Line><Line y={774} size={25}>水位与水深分开看</Line>
   <path d="M 643 456 h 21 M 654 456 V 564 M 643 564 h 21" stroke={C.gold} strokeWidth={4}/><Tx x={668} y={520} size={26} color={C.gold}>水深1</Tx>
  </>}
  {type==='closing'&&<>
   <Line y={381}>左右较低处定水位</Line><Line y={447}>减去柱高</Line><Line y={513}>各列相加</Line><Line y={640} size={82} color={C.blue}>8<tspan fontSize={30}> 格水</tspan></Line><Line y={765} size={29} color={C.gold}>完整程序 · 暂停查看</Line>
   <Tx x={545} y={896} anchor="middle" size={28} color={C.blue}>左盆水位3 · 7格</Tx><Tx x={1134} y={896} anchor="middle" size={28} color={C.blue}>右盆水位1 · 1格</Tx>
  </>}
 </g>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=>{
 const frame=useCurrentFrame();
 const shot=SHOTS.find(item=>frame>=item.from&&frame<item.from+item.durationInFrames)??SHOTS[SHOTS.length-1];
 const local=frame-shot.from;
 const card=shot.codeCardFrom!==undefined&&local>=shot.codeCardFrom;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <LeetcodeBackdrop/>
  {__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
  <svg width={1920} height={1080} viewBox="0 0 1920 1080">
   <rect width={1920} height={1080} fill={C.bg}/>
   {card?<CodeCard/>:<>
    <EpisodeHeader detail={chapterNames[shot.chapterId]}/>
    <Tx x={145} y={204} size={51} weight={750}>{titles[shot.visualType]??'接雨水'}</Tx>
    <path d="M 1341 314 V 878" stroke={C.edge} strokeWidth={2}/>
    <Artwork shot={shot} local={local}/>
    {!hideSubtitles&&<Captions shot={shot} local={local}/>}
   </>}
  </svg>
 </AbsoluteFill>;
};
