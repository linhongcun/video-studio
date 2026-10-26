import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import storyboard from '@storyboard';
import {C,FONT} from './theme';
import {M,item,clamp,ease,progress,T,Head,Note,Pill,BitRow,HashFlow,Result,Members} from './graphics';
import {useLayoutAudit} from './LayoutAudit';
import type {MainProps,Shot,Stage} from './types';
declare const __HAS_VOICE_AUDIO__:boolean;
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((c:any)=>c.shots??[]).map((s:any)=>{const result={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=Number(s.durationInFrames);return result;});
export const sentenceSpan=(s:Shot,i:number):[number,number]=>{
 const a=Number(s.cueFrames?.sentences?.[i]??s.voice?.[i]?.localStart??s.subtitles?.[i]?.from??(i?s.durationInFrames/2:0));
 const b=Number(s.voice?.[i]?.localEnd??s.subtitles?.[i]?.to??(i?s.durationInFrames-20:s.durationInFrames/2-8));return[a,Math.max(a+1,b)];
};
type Operation={key:string;position:number;slot:number;kind:'write'|'read'|'clear'};
/** Each operation has one path. Arrival completes at72% of its slot, followed by a readable hold. */
export const operationStages=(s:Shot,f:number,sentence:number,ops:Operation[],from=.06,to=.96):Stage[]=>{
 const [a,b]=sentenceSpan(s,sentence),start=a+(b-a)*from,end=a+(b-a)*to;
 return ops.map((o,i)=>{const raw=(f-start)/Math.max(1,end-start)*ops.length-i;return{...o,raw,p:ease(raw/.72),arrived:raw>=.72,active:raw>=0&&raw<1,started:raw>0};});
};
const op=(key:string,kind:'write'|'read'|'clear',slot=0,comparison=false):Operation=>({key,position:item(key)[comparison?'comparisonPositions':'singlePositions'][slot],kind,slot});
const current=(rows:Stage[])=>rows.find(v=>v.active)??[...rows].reverse().find(v=>v.started)??rows[0];
const completed=(rows:Stage[])=>rows.filter(v=>v.arrived);
const onesAfter=(base:number[],rows:Stage[])=>Array.from(new Set([...base,...completed(rows).map(v=>v.position)])).sort((a,b)=>a-b);
const normal=M.snapshots.afterB as number[];
const Flow=({step,formal=true,comparison=false,phase,showPosition}:any)=><HashFlow element={step.key} position={step.position} slot={step.slot} mode={step.kind} formal={formal} ruleLabel={comparison?`固定规则${step.slot===0?'①':'②'}`:undefined} phase={phase??step.p} showPosition={showPosition??step.p>=.38} color={step.kind==='clear'?C.red:C.gold}/>;
const headers:Record<string,[string,string,string]>={
 goal:['用标记判断是否加入过','只留下0和1，还能判断加入过吗？','直接看元素与标记，不保存元素内容。'],
 bits:['用标记判断是否加入过','八个格子，分清位值和位置编号','格子里面是0或1；格子外面是位置编号。'],
 'insert-a':['一次计算怎样留下标记','加入A：一次计算，标记一个位置','先看同一规则怎样定位，再把位置3从0改成1。'],
 'insert-b':['一次计算怎样留下标记','B也落在3：碰撞后，1仍然是1','两次加入共享一个格子；它没有变成2。'],
 'query-zero':['为什么零与一结论不同','D落在7：这里的0足以排除','如果D被正确加入过，位置7当时就应当被设成1。'],
 'query-one':['为什么零与一结论不同','C落在3：这里的1证明不了C加入过','演示中只插入A和B，没有插入C。'],
 'unsafe-delete':['共享标记的边界与取舍','错误清位，会把B一起错排除','错误操作反例：普通布隆过滤器不支持直接清位删除。'],
 'extra-position':['共享标记的边界与取舍','另建8格对照：每个元素用两个位置','这是另一份数组；先重加A和B，不能直接用旧标记查询。'],
 tradeoff:['共享标记的边界与取舍','抓住核心：0可排除，1只代表可能存在','位置次数、空间和预计元素数量要一起选择。'],
};
const Goal=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1);
 return <><T x={440} y={390} size={96} mono anchor="middle" weight={750}>A</T><T x={440} y={295} size={30} anchor="middle" color={C.muted}>待判断的元素</T><T x={1190} y={367} size={47} anchor="middle" color={C.gold}>有没有被加入过？</T><BitRow ones={[]} label="8个位 · 初始全0"/><Result kind="question" label={f<c?'只留下标记，不保存元素本身':'压缩了信息，还能判断得多准确？'} color={f<c?C.muted:C.gold} opacity={progress(f,a+(b-a)*.1,a+(b-a)*.6)}/></>;
};
const Bits=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),formal=f>=(s.cueFrames?.labels?.['位数组']??c),show=Math.max(1,Math.ceil(progress(f,a+(b-a)*.05,a+(b-a)*.65)*M.bitCount));
 return <><T x={960} y={364} size={50} anchor="middle">每个格子，只能放0或1</T><BitRow ones={[]} showCount={show} label={formal?'位数组 · 格内存值，格外编号':'8个位 · 全部从0开始'}/><Result kind="explanation" label={f<c?'里面：0或1':'外面：位置0—7；里面：保存的位值'} color={C.muted}/></>;
};
const InsertA=({s,f}:any)=>{
 const [c]=sentenceSpan(s,1),mapping=operationStages(s,f,0,[op('A','read')],.12,.94),writing=operationStages(s,f,1,[op('A','write')],.12,.97),rows=f<c?mapping:writing,step=current(rows),done=f>=c&&writing[0].arrived,formal=f>=(s.cueFrames?.labels?.['哈希']??sentenceSpan(s,0)[0]);
 return <><Flow step={step} formal={formal}/><BitRow ones={done?M.snapshots.afterA:[]} focus={step.started?[step.position]:[]} label="一次计算 · 8个位"/>{done&&<Result kind="written" label="加入A：把3号位从0改成1"/>}</>;
};
const InsertB=({s,f}:any)=>{
 const rows=operationStages(s,f,0,[op('B','write')],.08,.95),step=current(rows),done=step.arrived,formal=f>=(s.cueFrames?.labels?.['布隆过滤器']??sentenceSpan(s,1)[0]);
 return <><Flow step={step}/><BitRow ones={normal} focus={step.started?[step.position]:[]} label="和A共用3号位 · 1仍然是1"/><Members keys={done?M.inserted:['A']}/>{done&&<Result kind="shared" label={formal?'布隆过滤器：共享标记，不保存元素':'A和B都写3；1仍然是1'} color={formal?C.teal:C.blue}/>}</>;
};
const QueryZero=({s,f}:any)=>{
 const rows=operationStages(s,f,0,[op('D','read')],.16,.98),step=current(rows),done=step.arrived;
 return <><Flow step={step}/><BitRow ones={normal} focus={step.started?[step.position]:[]} zeroFocus={done?[step.position]:[]} label="同一规则查询 · 标记仍为原状态"/><Members keys={M.inserted}/>{done&&<Result kind="absent" label="D读到0 → 确定未加入" color={C.red}/>}</>;
};
const QueryOne=({s,f}:any)=>{
 const rows=operationStages(s,f,0,[op('C','read')],.12,.97),step=current(rows),done=step.arrived,[c]=sentenceSpan(s,1);
 return <><Flow step={step}/><BitRow ones={normal} focus={step.started?[step.position]:[]} label="同一规则查询 · 3号位已经是1"/><Members keys={M.inserted} label="演示中只加入"/>{done&&<Result kind="possible" label={f<c?'C读到1 → 只能说可能存在':'C没有加入；这个1来自A和B'} color={C.gold}/>}</>;
};
const UnsafeDelete=({s,f}:any)=>{
 const [c]=sentenceSpan(s,1),clearing=operationStages(s,f,1,[op('A','clear')],.03,.35),querying=operationStages(s,f,1,[op('B','read')],.43,.86),reset=f>=s.durationInFrames-24,isQuery=f>=sentenceSpan(s,1)[0]+(sentenceSpan(s,1)[1]-sentenceSpan(s,1)[0])*.40,step=current(isQuery?querying:clearing),cleared=clearing[0].arrived,error=!reset&&querying[0].arrived;
 return <><Flow step={step} phase={reset?0:step.p} showPosition={reset||step.p>=.38}/><BitRow ones={reset?normal:cleared?M.snapshots.wronglyClearedA:normal} focus={!reset&&step.started?[step.position]:[]} zeroFocus={error?[M.wrongDeletion.clearedPosition]:[]} label={reset?'反例结束 · 已恢复正常标记':'错误清位反例 · 不是支持的删除方法'}/><Members keys={reset||f<c?M.inserted:M.wrongDeletion.remainingTruth} label="演示中的真实成员"/>{reset?<Result kind="reset" label="撤销错误操作，恢复单位置示例"/>:error?<Result kind="invalid-reject" label="B仍在，却因为共享位被清零而错排除" color={C.red}/>:<Result kind="invalid-operation" label="错误尝试：删除A时直接清零3号位" color={C.red}/>}</>;
};
export const comparisonOperations={write:[op('A','write',0,true),op('A','write',1,true),op('B','write',0,true),op('B','write',1,true)],read:[op('C','read',0,true),op('C','read',1,true)]};
const ExtraPosition=({s,f}:any)=>{
 const [c]=sentenceSpan(s,1),writes=operationStages(s,f,0,comparisonOperations.write,.08,.96),reads=operationStages(s,f,1,comparisonOperations.read,.08,.90),reading=f>=c,step=current(reading?reads:writes),ones=onesAfter(M.comparison.snapshots.empty,writes),aDone=writes.slice(0,2).every(v=>v.arrived),bDone=writes.slice(2).every(v=>v.arrived),keys=bDone?M.comparison.inserted:aDone?['A']:[],done=reading&&reads.every(v=>v.arrived);
 if(reading&&!bDone)throw new Error('Cannot query the rebuilt filter before both A and B are completely inserted.');
 return <><Flow step={step} comparison/><BitRow ones={ones} focus={step.started?[step.position]:[]} zeroFocus={done?[M.comparison.queries.C.stopsAt]:[]} label="另一份8位数组 · 每个元素2个位置"/><Members keys={keys} label={reading?'重建完成后才查询':'这份新数组已加入'}/>{done?<Result kind="absent" label="C检查3和5；5为0 → 排除这次误判" color={C.red}/>:reading?<Result kind="checking" label="A和B已完整重建；现在查询C" color={C.gold}/>:<Result kind="rebuilding" label={`${step.key}：重新写第${step.slot+1}个位置${step.position}`} color={C.blue}/>}</>;
};
const Tradeoff=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),second=f>=c,split=c+(d-c)*.48,positive=f>=split,rows=positive?operationStages(s,f,1,[op('C','read')],.50,.96):operationStages(s,f,1,[op('D','read')],.06,.45),step=current(rows);
 return <>{second?<Flow step={step}/>:<><Pill x={475} y={347} w={370} label="空间" size={38}/><Pill x={960} y={347} w={440} label="预计元素数量" size={38} color={C.blue}/><Pill x={1450} y={347} w={370} label="位置次数" size={38} color={C.gold}/></>}<BitRow ones={normal} focus={second&&step.started?[step.position]:[]} zeroFocus={second&&!positive&&step.arrived?[step.position]:[]} label="回到单位置示例 · 没有改变原标记"/>{second&&step.arrived?<Result kind={positive?'possible':'absent'} label={positive?'C读到1：也只代表可能存在':'D读到0：可以排除'} color={positive?C.gold:C.red}/>:second?<Result kind="checking" label={`按同一规则查询${step.key}`} color={C.gold}/>:<Result kind="tradeoff" label="位置不是越多越好，要与空间和数量一起选择" color={C.muted}/>}</>;
};
export const Scene=({s,f}:any)=>{
 const [chapter,title,sub]=headers[s.visualType]??headers.goal;let content:any,note='教学示例 · 8格标记，只保存0或1';
 switch(s.visualType){
  case 'goal':content=<Goal s={s} f={f}/>;note='元素是判断对象；格子只留下0和1';break;
  case 'bits':content=<Bits s={s} f={f}/>;break;
  case 'insert-a':content=<InsertA s={s} f={f}/>;break;
  case 'insert-b':content=<InsertB s={s} f={f}/>;note='A/B是演示操作的回看，不是位数组保存的元素名单';break;
  case 'query-zero':content=<QueryZero s={s} f={f}/>;note='前提：元素正确加入，规则固定，标记被正确保留';break;
  case 'query-one':content=<QueryOne s={s} f={f}/>;note='1可能由其他元素留下；本例C从未被加入';break;
  case 'unsafe-delete':content=<UnsafeDelete s={s} f={f}/>;note='清除共享位会误伤其他元素；反例结束后恢复原状态';break;
  case 'extra-position':content=<ExtraPosition s={s} f={f}/>;note='另一份重建对照 · 只说明这次查询，不报告误判率';break;
  case 'tradeoff':content=<Tradeoff s={s} f={f}/>;note='正确加入并保留标记时：0可排除；全1只代表可能存在';break;
  default:throw new Error('Unknown core Bloom scene '+s.visualType);
 }
 return <><Head chapter={chapter} title={title} sub={sub}/>{content}<Note>{note}</Note><g data-visual-state={JSON.stringify({type:s.visualType,frame:f,sentenceSpans:[sentenceSpan(s,0),sentenceSpan(s,1)]})}/></>;
};
const ShotView=({s,hideSubtitles=false,auditLayout=false}:any)=>{
 const f=useCurrentFrame();useLayoutAudit(auditLayout,'main',s.from+f);
 const caption=(s.subtitles??[]).find((c:any)=>f>=c.from&&f<(c.to!==undefined?c.to+1:c.from+(c.duration??0)));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}><svg data-audit-scene="true" width={1920} height={1080} viewBox="0 0 1920 1080"><Scene s={s} f={f}/></svg>{!hideSubtitles&&caption&&<div data-subtitle="true" style={{position:'absolute',left:115,right:115,bottom:49,textAlign:'center',fontFamily:FONT,fontSize:31,lineHeight:1.45,color:C.text}}>{caption.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:MainProps)=><AbsoluteFill style={{background:C.bg}}>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
