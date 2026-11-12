import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {PuzzleCanvas,PuzzleHeader} from '../../../../../../../../_shared/puzzles-video/Frame';
import protocol from '../../model-data.json';
import {C,FONT,MONO} from './theme';
import {shots,Shot} from './data';
import {Layout,Point,ease,planMoves,moveLayout} from './motion';
declare const __HAS_VOICE_AUDIO__:boolean;

type Node=typeof protocol.nodes[number];
const node=(prefix:string):Node=>{const n=protocol.nodes.find(n=>n.prefix===prefix);if(!n)throw Error('Unknown weighing '+prefix);return n;};
const all=Array.from({length:12},(_,i)=>i+1);
const ballId=(value:string)=>parseInt(value,10);
const ids=(cases:string[])=>[...new Set(cases.map(ballId))];
const clamped=(f:number,a:number,b:number)=>Math.max(0,Math.min(1,(f-a)/Math.max(1,b-a)));
const at=(a:number,b:number,p:number)=>a+(b-a)*p;
const windows=(s:Shot)=>({a:s.voice[0].localStart,b:s.voice[0].localEnd,c:s.voice[1].localStart,e:s.voice[1].localEnd});
const subset=(layout:Layout,visible:number[])=>Object.fromEntries(visible.map(id=>[id,layout[id]])) as Layout;
const inGroup=(balls:number[],cx:number):Layout=>{
  const points=balls.length<=3?balls.map((_,i)=>({x:cx+(i-(balls.length-1)/2)*190,y:535})):balls.map((_,i)=>({x:cx+(i%2?145:-145),y:i<2?440:635}));
  return Object.fromEntries(balls.map((id,i)=>[id,points[i]]));
};
const outside=(balls:number[]):Layout=>{
  const points=balls.length===1?[{x:1625,y:535}]:balls.length===3?[{x:1530,y:440},{x:1720,y:440},{x:1625,y:635}]:balls.map((_,i)=>({x:i%2?1720:1530,y:i<2?440:635}));
  return Object.fromEntries(balls.map((id,i)=>[id,points[i]]));
};
const layout=(left:number[],right:number[],off:number[])=>({...inGroup(left,440),...inGroup(right,1100),...outside(off)});
const first=layout([1,2,3,4],[5,6,7,8],[9,10,11,12]);
const second=layout([1,2,5],[3,6,9],[4,7,8]);
const last=layout([1],[2],[6]);
const balanced=layout([9,10,11],[1,2,3],[12]);
const initial=Object.fromEntries(all.map((id,i)=>[id,{x:310+(i%6)*260,y:i<6?420:650}])) as Layout;
const firstMoves=planMoves(initial,first,[1,2,5,6,7,8,12,3,4,9,10,11]);
const secondVisible=Object.keys(second).map(Number);
const secondMoves=planMoves(subset(first,secondVisible),second,[1,2,5,6,9,4,7,3,8]);
const lastMoves=planMoves(subset(second,[1,2,6]),last,[6,2,1]);
const balancedVisible=Object.keys(balanced).map(Number);
const balancedMoves=planMoves(subset(first,balancedVisible),balanced,[1,2,3,9,10,11,12]);

const T=({x,y,children,size=36,color=C.text,anchor='start',weight=600,alpha=1,width=1660,mono=false,...rest}:any)=><text data-text data-max-width={width} x={x} y={y} fill={color} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} opacity={alpha} {...rest}>{children}</text>;
const Head=({title,sub}:any)=><PuzzleHeader number="P06" kicker="12个球称三次" title={title} sub={sub}/>;
const Panel=({x,y,w,h,children,alpha=1,color=C.edge}:any)=><g opacity={alpha}><rect x={x} y={y} width={w} height={h} rx={22} fill={C.surface} fillOpacity={.45} stroke={color} strokeWidth={2}/>{children}</g>;
const Result=({children,color=C.text,alpha=1}:any)=><g opacity={alpha}><rect x={120} y={790} width={1680} height={84} rx={18} fill={C.surface} stroke={C.edge}/><T x={960} y={846} size={37} color={color} anchor="middle" width={1620}>{children}</T></g>;
const Ball=({id,p,cases,normal=false,answer=false,focus=false,alpha=1,hideLabel=false,radius=46}: {key?:number;id:number;p:Point;cases:string[];normal?:boolean;answer?:boolean;focus?:boolean;alpha?:number;hideLabel?:boolean;radius?:number})=>{
  const own=cases.filter(c=>ballId(c)===id);
  const kind=answer?'偏轻 · 确认':normal?'正常':own.length===1?(own[0].endsWith('H')?'可能重':'可能轻'):'轻重未知';
  const color=answer||normal?C.teal:focus?C.coral:C.violet;
  return <g transform={`translate(${p.x} ${p.y})`} opacity={alpha} data-ball={id} data-ball-status={kind} data-candidate-cases={own.join(',')} data-ball-normal={normal} data-ball-answer={answer}>
    <circle r={radius} fill={C.surface} stroke={color} strokeWidth={answer?5:3}/>
    <T x={0} y={16} size={45} weight={750} anchor="middle" width={100}>{id}</T>
    {!hideLabel&&<T x={0} y={radius+44} size={29} color={color} anchor="middle" width={176}>{kind}</T>}
  </g>;
};
const Balls=({positions,cases,normal=[],answer,focus=[],hideLabels=false,alphas={}}:{positions:Layout;cases:string[];normal?:number[];answer?:number;focus?:number[];hideLabels?:boolean;alphas?:Record<number,number>})=><g data-visible-balls={Object.keys(positions).join(',')} data-current-candidates={cases.join(',')}>
  {Object.entries(positions).map(([key,p])=>{const id=Number(key);return <Ball key={id} id={id} p={p} cases={cases} normal={normal.includes(id)} answer={answer===id} focus={focus.includes(id)} hideLabel={hideLabels} alpha={alphas[id]??1}/>;})}
</g>;
const Board=({positions,cases,left,right,off=[],normal=[],answer,focus=[],moving=false,alphas={},result}:{positions:Layout;cases:string[];left:number[];right:number[];off?:number[];normal?:number[];answer?:number;focus?:number[];moving?:boolean;alphas?:Record<number,number>;result?:string})=><g data-comparison-left={left.join(',')} data-comparison-right={right.join(',')} data-comparison-off={off.join(',')} data-placement-state={moving?'moving':'settled'} data-weighing-result={result??'not-submitted'}>
  <Panel x={120} y={350} w={620} h={405} color={result==='L'?C.coral:C.edge}/>
  <Panel x={780} y={350} w={620} h={405} color={result==='R'?C.coral:C.edge}/>
  {!!off.length&&<Panel x={1450} y={350} w={350} h={405}/>}
  {!moving&&<><T x={440} y={325} anchor="middle" size={31} color={C.muted} width={600}>左边{left.length?` · ${left.length}个`:''}</T><T x={1100} y={325} anchor="middle" size={31} color={C.muted} width={600}>右边{right.length?` · ${right.length}个`:''}</T>{!!off.length&&<T x={1625} y={325} anchor="middle" size={31} color={C.muted} width={330}>留在外面</T>}</>}
  <Balls positions={positions} cases={cases} normal={normal} answer={answer} focus={focus} hideLabels={moving} alphas={alphas}/>
</g>;

const Scene=({s,f}:{s:Shot;f:number})=>{
  const q=parseInt(s.id,10),{a,b,c,e}=windows(s);
  const root=node(''),left=node('L');
  if(q===1)return <><Head title="12个球，3次找出异常" sub="恰有1个异常 · 轻重未知 · 其余11个同重 · 使用等臂天平"/><Balls positions={initial} cases={root.candidates} hideLabels/>
    <Result color={f>=c?C.coral:C.muted}>{f>=c?'最多3称：找出球号，也要判断轻重':'只用这12个球，没有额外的正常球'}</Result></>;
  if(q===2){
    const p=clamped(f,a+5,b-12),movement=moveLayout(initial,firstMoves,p),submitted=f>=at(c,e,.48);
    return <><Head title="先分三组，4个对4个" sub="第1称 · 两边球数相同"/><Board positions={movement.positions} cases={submitted?left.candidates:root.candidates} normal={submitted?[9,10,11,12]:[]} left={[1,2,3,4]} right={[5,6,7,8]} off={[9,10,11,12]} moving={!movement.settled} result={submitted?'L':undefined}/><Result alpha={movement.settled?1:0} color={submitted?C.coral:C.muted}>{submitted?'第1称：左边重':'9—12号先留在外面'}</Result></>;
  }
  if(q===3){const focus=f<c?(f<at(a,b,.5)?[1,2,3,4]:[5,6,7,8]):[9,10,11,12];return <><Head title="左边重，还不能锁定哪一组" sub="第1称已结束 · 1—4可能重，5—8可能轻"/><Board positions={first} cases={left.candidates} normal={[9,10,11,12]} left={[1,2,3,4]} right={[5,6,7,8]} off={[9,10,11,12]} focus={focus} result="L"/><Result color={f>=c?C.teal:C.text}>{f>=c?'9—12号都正常，可用来作参照':'左边有重球，或者右边有轻球'}</Result></>;}
  if(q===4){
    const start=a+20,end=b-12,p=clamped(f,start,end),movement=moveLayout(subset(first,secondVisible),secondMoves,p),alpha=1-ease(clamped(f,a,a+20));
    return <><Head title="第2称：换一组来比" sub="第一称左重 · 9号已经确定正常"/><Board positions={movement.positions} cases={left.candidates} normal={[9]} left={[1,2,5]} right={[3,6,9]} off={[4,7,8]} moving={!movement.settled}/>{alpha>0&&<Balls positions={subset(first,[10,11,12])} cases={[]} normal={[10,11,12]} hideLabels alphas={{10:alpha,11:alpha,12:alpha}}/>}<Result alpha={movement.settled?1:0} color={f>=c?C.teal:C.text}>{f>=c?'重球让本侧重；轻球让对面重；9号补齐数量':'左边1、2、5号　对　右边3、6、9号'}</Result></>;
  }
  if(q===5){
    const submitted=f>=c+10,fade=clamped(f,c+10,c+35),p=clamped(f,c+35,e-12),movement=moveLayout(subset(second,[1,2,6]),lastMoves,p),selected=node('LL');
    const positions=submitted?{...second,...movement.positions}:second;
    const alphas=Object.fromEntries(secondVisible.filter(id=>![1,2,6].includes(id)).map(id=>[id,1-fade]));
    return <><Head title={submitted?'第2称还是左重，只剩三颗':'如果左重，哪些球会造成它？'} sub={submitted?'下一步：第3称1号对2号，6号留在外面':'第2称 · 先看左重意味着什么'}/><Board positions={positions} cases={submitted?selected.candidates:left.candidates} normal={submitted?secondVisible.filter(id=>![1,2,6].includes(id)):[9]} left={p>0?[1]:[1,2,5]} right={p>0?[2]:[3,6,9]} off={p>0?[6]:[4,7,8]} focus={[1,2,6]} moving={submitted&&!movement.settled} alphas={submitted?alphas:{}} result={submitted&&p===0?'L':undefined}/><Result alpha={submitted&&!movement.settled?0:1} color={submitted?C.coral:C.text}>{submitted?'第2称左重 → 只剩1号重、2号重、6号轻':'1、2号偏重，或6号偏轻，都会让左边重'}</Result></>;
  }
  if(q===6){const confirmed=f>=at(c,e,.6);return <><Head title={confirmed?'第3称平衡，6号偏轻':'第3称：1号对2号'} sub={confirmed?'主例结束 · 三次称重完成':'它俩只可能偏重；6号仍可能偏轻'}/><Board positions={last} cases={confirmed?['6L']:node('LL').candidates} normal={confirmed?[1,2]:[]} answer={confirmed?6:undefined} left={[1]} right={[2]} off={[6]} result={confirmed?'B':undefined}/><Result color={confirmed?C.teal:C.text}>{confirmed?'1、2号正常 → 留在外面的6号偏轻':'不平衡：较重的那个异常；平衡：6号偏轻'}</Result></>;}
  if(q===7){const n=node('LR');return <><Head title="第二称的另一个结果：右重" sub="首称左重 → 第二称右重 · 第3称：3号对正常9号"/><Board positions={layout(n.left,n.right,[5])} cases={n.candidates} normal={[9]} left={n.left} right={n.right} off={[5]}/><Result color={f>=c?C.teal:C.text}>{f>=c?'3号较重 → 3号偏重；平衡 → 5号偏轻':'只剩：3号可能重，5号可能轻'}</Result></>;}
  if(q===8){const n=node('LB');return <><Head title="第二称若平衡，检查盘外球" sub="首称左重 → 第二称平衡 · 第3称：7号对8号"/><Board positions={layout(n.left,n.right,[4])} cases={n.candidates} left={n.left} right={n.right} off={[4]}/><Result color={f>=c?C.teal:C.text}>{f>=c?'7、8号谁轻就是谁；平衡 → 4号偏重':'只剩：4号可能重，7、8号可能轻'}</Result></>;}
  if(q===9){const n=node('R');return <><Head title="第一称若右重，轻重反过来" sub="另一路：第一称右重 · 称球组合保持不变"/><Board positions={subset(first,[1,2,3,4,5,6,7,8])} cases={n.candidates} left={[1,2,3,4]} right={[5,6,7,8]}/>{f>=c&&<Panel x={1450} y={350} w={350} h={405}><T x={1625} y={455} anchor="middle" size={32} color={C.coral} width={320}>左重 ↔ 右重</T><T x={1625} y={555} anchor="middle" size={32} color={C.violet} width={320}>偏重 ↔ 偏轻</T><T x={1625} y={655} anchor="middle" size={32} color={C.teal} width={320}>平衡保持</T></Panel>}<Result color={f>=c?C.teal:C.text}>{f>=c?'左右重结果、答案轻重，同时对调':'1—4号可能轻；5—8号可能重'}</Result></>;}
  if(q===10){const p=clamped(f,c+20,e-12),movement=moveLayout(subset(first,balancedVisible),balancedMoves,p),fade=1-ease(clamped(f,c,c+20)),n=node('B');return <><Head title={f<c?'第一称平衡，就有正常参照':'第2称：9、10、11号，对正常球'} sub="另一路：第一称平衡 · 1—8号全部正常"/><Board positions={f<c?first:movement.positions} cases={n.candidates} normal={f<c?[1,2,3,4,5,6,7,8]:[1,2,3]} left={f<c?[1,2,3,4]:[9,10,11]} right={f<c?[5,6,7,8]:[1,2,3]} off={f<c?[9,10,11,12]:[12]} moving={f>=c&&!movement.settled} result={f<c?'B':undefined}/>{f>=c&&fade>0&&<Balls positions={subset(first,[4,5,6,7,8])} cases={[]} normal={[4,5,6,7,8]} hideLabels alphas={{4:fade,5:fade,6:fade,7:fade,8:fade}}/>}<Result alpha={f>=c&&!movement.settled?0:1} color={f<c?C.teal:C.text}>{f<c?'异常在9—12号里，轻重仍未知':'右边全正常，可以判断左边的轻重'}</Result></>;}
  if(q===11){
    const p=clamped(f,c,e),lastStage=p>=.43,heavy=p<.74,phase=f<c?'BB':!lastStage?'B':heavy?'BL':'BR',n=node(phase),off=phase==='BB'?[12].filter(id=>!n.left.includes(id)):phase==='B'?[12]:[11];
    const title=phase==='BB'?'第二称平衡：最后比较12号':phase==='B'?'第二称不平衡：方向也知道了':heavy?'已知偏重：找较重的那个':'已知偏轻：找较轻的那个';
    const msg=phase==='BB'?'12号对正常球，重就是偏重，轻就是偏轻':phase==='B'?(p<.22?'左组较重 → 9、10、11中有重球':'左组较轻 → 9、10、11中有轻球'):p>.9?'9、10号平衡 → 11号异常，沿用已知轻重':heavy?'9、10号不平衡 → 较重的那个异常':'9、10号不平衡 → 较轻的那个异常';
    return <><Head title={title} sub="第一称平衡后的处理 · 第3称确定球号和轻重"/><Board positions={layout(n.left,n.right,off)} cases={n.candidates} normal={phase==='BB'?[1]:phase==='B'?[1,2,3]:[]} left={n.left} right={n.right} off={off}/><Result color={phase==='BB'?C.teal:C.text}>{msg}</Result></>;
  }
  if(q===12)return <><Head title="每次记住：谁可疑，可能轻还是重" sub="三次称重，确定球号和轻重"/><Ball id={6} p={{x:960,y:440}} cases={['6L']} answer radius={64}/><T x={960} y={650} anchor="middle" size={49} color={C.teal}>左重 → 左重 → 平衡 → 6号偏轻</T>{f>=c&&<><Panel x={360} y={720} w={550} h={132}><T x={635} y={802} size={43} anchor="middle" width={520}>谁还可疑</T></Panel><Panel x={1010} y={720} w={550} h={132}><T x={1285} y={802} size={43} anchor="middle" width={520}>可能轻，还是重</T></Panel></>}</>;
  throw Error('Unknown simple P06 shot '+s.id);
};

const ShotView=({s,hideSubtitles,auditLayout}:{s:Shot;hideSubtitles:boolean;auditLayout:boolean})=>{
  const f=useCurrentFrame(),ref=useRef<SVGSVGElement>(null);
  const caption=s.subtitles?.find(q=>f>=q.from&&f<(q.to!==undefined?q.to+1:q.from+(q.duration??0)));
  useLayoutEffect(()=>{if(!auditLayout||!ref.current)return;ref.current.querySelectorAll<SVGTextElement>('[data-max-width]').forEach(el=>{const width=Number(el.dataset.maxWidth);if(width&&el.getBBox().width>width+2)console.error('COPYFIT',s.id,f,el.textContent,el.getBBox().width,width);});},[auditLayout,s.id,f]);
  return <AbsoluteFill data-shot={s.id} data-local-frame={f} style={{background:C.bg,fontFamily:FONT,color:C.text,overflow:'hidden'}}><svg ref={ref} width={1920} height={1080} viewBox="0 0 1920 1080" data-audit-scene><PuzzleCanvas/><Scene s={s} f={f}/><T x={1795} y={83} size={26} color={C.muted} anchor="end">IT小村</T></svg>{!hideSubtitles&&caption&&<div data-subtitle style={{position:'absolute',left:140,right:140,top:910,minHeight:100,maxHeight:150,display:'flex',alignItems:'center',justifyContent:'center',fontSize:32,lineHeight:1.45,textAlign:'center',background:C.bg+'F5',padding:'0 18px',borderRadius:14,boxSizing:'border-box'}}>{caption.text}</div>}</AbsoluteFill>;
};
export type MainProps={hideSubtitles?:boolean;showSubtitles?:boolean;auditLayout?:boolean};
export const Main=({hideSubtitles=false,showSubtitles=true,auditLayout=false}:MainProps)=><AbsoluteFill style={{background:C.bg}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles||!showSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
