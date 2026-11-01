import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import storyboard from '@storyboard';
import {C,FONT} from './theme';
import {useLayoutAudit} from './LayoutAudit';
import {M,keyItem,clamp,ease,mix,progress,T,Head,Note,Pill,Arrow,BitArray,HashSlots,Trace,Directory} from './graphics';
declare const __HAS_VOICE_AUDIO__:boolean;
let offset=0;
export const shots:any[]=(storyboard.scenes??[]).flatMap((scene:any)=>scene.shots??[]).map((shot:any)=>{const result={...shot,id:String(shot.id).padStart(2,'0'),from:offset};offset+=Number(shot.durationInFrames);return result;});
/** Event clocks use the actual selected sentence envelopes, never wall time. */
export const sentenceSpan=(s:any,i:number):[number,number]=>{
 const voice=s.voice?.[i],sub=s.subtitles?.[i];
 const a=Number(s.cueFrames?.sentences?.[i]??voice?.localStart??sub?.from??(i?s.durationInFrames/2:0));
 const b=Number(voice?.localEnd??sub?.to??(i?s.durationInFrames-20:s.durationInFrames/2-8));
 return [a,Math.max(a+1,b)];
};
export const windowFor=(s:any,i:number,from=0,to=1):[number,number]=>{const [a,b]=sentenceSpan(s,i),length=b-a;return [a+length*from,b-length*(1-to)];};
export const stages=(f:number,a:number,b:number,positions:number[])=>positions.map((position,i)=>{const raw=(f-a)/Math.max(1,b-a)*positions.length-i;return {slot:i,position,raw,arrived:raw>=.68,started:raw>0,active:raw>=0&&raw<1,p:ease(raw/.68)};});
const run=(s:any,f:number,sentence:number,positions:number[],from=.04,to=.87)=>stages(f,...windowFor(s,sentence,from,to),positions);
const arrived=(steps:any[])=>steps.filter(v=>v.arrived).map(v=>v.position);
const focus=(steps:any[])=>steps.filter(v=>v.active).map(v=>v.position);
const traces=(steps:any[],color=C.gold)=><>{steps.filter(v=>v.started).map(v=><Trace key={v.slot} {...v} p={v.p} color={color} opacity={v.active?1:.22}/>)}</>;
const status=(text:string,color=C.teal,opacity=1,x=704,w=1000,y=792)=><Pill x={x} y={y} w={w} label={text} color={color} size={34} opacity={opacity}/>;
const normal=M.snapshots.after205 as number[];
const A=keyItem('sku101'),B=keyItem('sku205'),N=keyItem('sku001'),F=keyItem('sku067');
const heads:Record<string,[string,string,string]>={
 missing:['为什么先排除不存在的查询','不存在的商品编号，也要每次查数据库？','先看一次商品查询：没有这条记录，依然需要查找。'],
 bits:['为什么先排除不存在的查询','先留下0 / 1标记，不复制整条商品记录','格内存标记，格外标位置；0不是商品编号。'],
 hash:['同一编号怎样留下标记','同一个编号，用固定规则算出位置','这套教学实现用三路计算；相同输入和规则，位置不变。'],
 'insert-101':['同一编号怎样留下标记','加入101：只把三个位置设成1','先算位置，再逐个写入；抵达时才改变位值。'],
 'insert-205':['同一编号怎样留下标记','加入205：共享格子，1仍然是1','位置3被两个编号用到，但这个格子不做计数。'],
 'reject-001':['零与一为什么给出不同结论','看到任意一个0，就可以先排除','先探测位置12，再看位置2；不需要把三个位置都读完。'],
 'why-zero':['零与一为什么给出不同结论','加入时设过1，正确保留就不会碰到0','回看已加入的101：查询仍使用原来的三个位置。'],
 'false-positive':['零与一为什么给出不同结论','没加入的067，为什么三个位置全是1？','全1只说明允许继续查；还没有查到商品记录。'],
 'shared-marks':['零与一为什么给出不同结论','这三个1，可能来自别的编号','只在这里回看标记来源；位数组本身不保存来源。'],
 gate:['省下查询需要什么条件','过滤器负责排除，真实数据负责确认','两个独立请求，按同一套0 / 1规则依次处理。'],
 capacity:['省下查询需要什么条件','位数固定，标记越密，越容易误判','容量示意：另一个状态，不是前面四个编号的实测概率。'],
 'bad-delete':['省下查询需要什么条件','错误清位，会把别的编号一起抹掉','错误删除反例：下面不是普通布隆过滤器支持的操作。'],
 maintenance:['省下查询需要什么条件','数据新增了，标记也要一起维护','先展示未同步的危险，再把新增001正确加入标记。'],
};
const Meaning=({left,right}:any)=><><T x={550} y={787} size={39} anchor="middle" color={C.teal}>{left}</T><T x={1350} y={787} size={37} anchor="middle" color={C.muted}>{right}</T></>;
const QueryFooter=({label,color=C.teal,shown=false,pass=false,blocked=false,idlePhase='waiting',dbResult='',records=M.catalogInitially,unsafe=false}:any)=>{
 if(pass&&blocked)throw new Error('A query link cannot dispatch and block at once.');
 if(blocked&&!shown)throw new Error('An explicit rejection needs its visible result.');
 const phase=blocked?'blocked':pass?'dispatch':idlePhase;
 return <g data-query-link={phase}>
  {shown&&status(label,color,1,674,1020)}
  <g data-query-route="true">
   <Arrow x1={1215} y1={787} x2={1270} y2={787} color={pass?C.blue:C.edge} dashed={!pass}/>
   {blocked&&<path data-reject-mark="true" d="M1232 766L1252 808M1252 766L1232 808" stroke={unsafe?C.red:C.muted} strokeWidth={4}/>}
  </g>
  <Directory records={records} active={pass} result={dbResult} unsafe={unsafe}/>
 </g>;
};
const Missing=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1);
 const trip1=progress(f,a+(b-a)*.03,a+(b-a)*.38),back1=progress(f,a+(b-a)*.45,a+(b-a)*.68);
 const trip2=progress(f,c+(d-c)*.05,c+(d-c)*.42),back2=progress(f,c+(d-c)*.49,c+(d-c)*.74);
 const count=trip2===1?2:trip1===1?1:0,request=trip2>0?trip2:trip1,returnP=trip2>0?back2:back1;
 return <>
  <rect x={220} y={304} width={610} height={481} rx={28} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
  <T x={265} y={365} size={32}>商品查询</T><T x={780} y={365} size={23} color={C.muted} anchor="end">教学示意</T>
  <T x={267} y={435} size={27} color={C.muted}>商品编号</T>
  <rect x={265} y={459} width={352} height={98} rx={15} fill={C.bg} stroke={C.edge} strokeWidth={2}/>
  <T x={441} y={528} size={52} mono anchor="middle">{N.display}</T>
  <rect x={646} y={459} width={141} height={98} rx={15} fill={C.teal}/><T x={717} y={521} size={31} color={C.bg} anchor="middle" weight={750}>查询</T>
  <T x={525} y={665} size={39} color={returnP===1?C.red:C.muted} anchor="middle">{returnP===1?'未找到该商品':'查询商品目录'}</T>
  <T x={525} y={728} size={27} color={C.muted} anchor="middle">{trip2>0?'相同编号再次查询':'不存在，也需要查找'}</T>
  <Arrow x1={875} y1={498} x2={1275} y2={498} color={C.blue}/>
  {request>0&&request<1&&<circle cx={mix(887,1260,request)} cy={498} r={10} fill={C.text}/>}
  <Arrow x1={1275} y1={623} x2={875} y2={623} color={C.red} opacity={returnP}/>
  {returnP>0&&returnP<1&&<circle cx={mix(1260,887,returnP)} cy={623} r={10} fill={C.red}/>}
  <Directory y={562} active={request===1} result={returnP===1?'确认：没有001':''}/>
  <T x={1535} y={746} size={36} color={C.gold} anchor="middle">实际查库 {count} 次</T>
  <T x={960} y={858} size={33} color={C.teal} anchor="middle" opacity={progress(f,c,d)}>目标：先排除肯定没有的编号</T>
 </>;
};
const Bits=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),show=Math.max(1,Math.ceil(progress(f,a+(b-a)*.08,a+(b-a)*.58)*M.bitCount));
 const formal=f>=(s.cueFrames?.labels?.['位数组']??c);
 return <><T x={960} y={350} size={42} anchor="middle">每格只保留一个标记</T><Pill x={770} y={428} w={220} label="0：未置位" color={C.muted} size={30}/><Pill x={1150} y={428} w={220} label="1：已置位" color={C.teal} size={30}/><BitArray ones={[]} showCount={show} label={formal?'位数组 · 16个位置':'16个位置 · 从全0开始'}/><g opacity={progress(f,c,d)}><Meaning left="留下0 / 1标记" right="不保存整条商品记录"/></g></>;
};
const Hash=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),rows=run(s,f,0,A.positions,.03,.74),repeat=run(s,f,1,A.positions,.08,.82);
 const formal=f>=(s.cueFrames?.labels?.['哈希']??a),current=f<c?rows:repeat;
 return <><HashSlots item={A} active={current.find(v=>v.active)?.slot??-1} visible={Math.max(1,rows.filter(v=>v.started).length)} mode={formal?'哈希':'固定计算'}/>{traces(current)}<BitArray ones={[]} focus={focus(current)} label="16位 · 教学示例"/>{status(f<c?'计算出位置，不是查商品记录':'再算一次，仍是3、14、15',C.gold,progress(f,a+(b-a)*.7,b),960,1180)}</>;
};
const Insert=({s,f,item,base}:any)=>{
 const sentence=item.key===A.key?1:0,steps=run(s,f,sentence,item.positions,.08,.87),done=steps.every(v=>v.arrived);
 const ones=Array.from(new Set([...base,...arrived(steps)])).sort((a:any,b:any)=>a-b),share=item.key===B.key&&steps[1].arrived;
 const formal=item.key===B.key&&f>=(s.cueFrames?.labels?.['布隆过滤器']??sentenceSpan(s,1)[0]);
 return <><HashSlots item={item} active={steps.find(v=>v.active)?.slot??-1} checked={arrived(steps)} mode="算位置"/>{traces(steps)}<BitArray ones={ones} focus={focus(steps)} shared={share?[3]:[]} label="16位 · 教学示例"/>{done&&<g data-onset-term={formal?'布隆过滤器':undefined}>{status(formal?'布隆过滤器：多个编号共享0 / 1标记':share?'共享位置3：1仍然是1，不变成2':`${item.display}的三个位置都已设成1`,formal?C.teal:share?C.blue:C.teal,1,960,1240)}</g>}{share&&<T x={960} y={854} size={29} anchor="middle" color={C.muted}>格子里没有商品编号，也没有写入次数</T>}</>;
};
const Reject=({s,f}:any)=>{
 const steps=run(s,f,1,M.expected.negative001.checked,.04,.65),done=steps.every(v=>v.arrived),fail=done?M.expected.negative001.stopsAt:undefined;
 return <><HashSlots item={N} checked={arrived(steps)} failedAt={fail} active={steps.find(v=>v.active)?.slot??-1} mode="算位置"/>{traces(steps)}<BitArray ones={normal} focus={focus(steps)} zeroFocus={fail===undefined?[]:[fail]} label="16位 · 教学示例"/><QueryFooter shown={done} blocked={done} label="位置2是0 → 排除001" color={C.red} dbResult={done?'这次不查库':''}/></>;
};
const WhyZero=({s,f}:any)=>{
 const steps=run(s,f,0,A.positions,.08,.86),done=steps.every(v=>v.arrived),[c,d]=sentenceSpan(s,1);
 return <><HashSlots item={A} checked={arrived(steps)} active={steps.find(v=>v.active)?.slot??-1} mode="查同一位置"/>{traces(steps)}<BitArray ones={normal} focus={focus(steps)} label="16位 · 教学示例"/>{done&&status('加入过101 → 原来三个位置仍是1',C.teal,1,960,1280)}<T x={960} y={856} size={30} color={C.gold} anchor="middle" opacity={progress(f,c+(d-c)*.06,c+(d-c)*.5)}>前提：正确收录，标记被保留</T></>;
};
const FalsePositive=({s,f}:any)=>{
 const steps=run(s,f,0,F.positions,.10,.90),done=steps.every(v=>v.arrived),[c,d]=sentenceSpan(s,1),pass=done&&f>=c+(d-c)*.22,confirmed=f>=c+(d-c)*.66;
 return <><HashSlots item={F} checked={arrived(steps)} active={steps.find(v=>v.active)?.slot??-1} mode="算位置"/>{traces(steps)}<BitArray ones={normal} focus={focus(steps)} label="16位 · 教学示例"/><QueryFooter shown={done} blocked={false} idlePhase={done?'eligible':'waiting'} label="三位全1 → 可能存在067" color={C.gold} pass={pass} dbResult={confirmed?'确认：没有067':pass?'查询真实记录…':''}/>{pass&&!confirmed&&<circle cx={mix(1215,1270,progress(f,c+(d-c)*.22,c+(d-c)*.50))} cy={787} r={8} fill={C.blue}/>}</>;
};
const Shared=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),steps=stages(f,a+(b-a)*.04,a+(b-a)*.9,F.positions),explain=1-progress(f,c+(d-c)*.05,c+(d-c)*.48);
 return <><HashSlots item={F} checked={F.positions} mode="算位置"/><BitArray ones={normal} focus={focus(steps)} label="16位 · 只保存0 / 1"/>
  {steps.map(v=>{const owner=M.items.find((item:any)=>M.catalogInitially.includes(item.key)&&item.positions.includes(v.position));return <g key={v.slot} opacity={v.started?explain:0}><path d={`M${255+v.position*94} 690V713L${520+v.slot*440} 746`} stroke={owner.key===B.key?C.blue:C.teal} strokeWidth={3} fill="none"/><Pill x={520+v.slot*440} y={797} w={350} size={31} color={owner.key===B.key?C.blue:C.teal} label={`位置${v.position}来自${owner.display}`}/></g>;})}
  <g opacity={1-explain}>{status('位数组里没有“是谁写的”这条信息',C.gold,1,960,1440)}<T x={960} y={855} size={29} color={C.muted} anchor="middle">全1可能由别的编号共同留下</T></g>
 </>;
};
const Gate=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),switchAt=a+(b-a)*.48,negative=f<switchAt,item=negative?N:F;
 const steps=negative?stages(f,a+(b-a)*.02,a+(b-a)*.40,M.expected.negative001.checked):stages(f,switchAt,b-(b-a)*.04,F.positions),done=steps.every(v=>v.arrived),pass=!negative&&done;
 return <><HashSlots item={item} checked={arrived(steps)} active={steps.find(v=>v.active)?.slot??-1} failedAt={negative&&done?2:undefined} mode="独立查询"/>{traces(steps)}<BitArray ones={normal} focus={focus(steps)} zeroFocus={negative&&done?[2]:[]} label="16位 · 同一套判断规则"/><QueryFooter shown={done} blocked={negative&&done} label={negative?'001：看到0，先排除':'067：全1，继续查真实记录'} color={negative?C.red:C.gold} pass={pass} dbResult={negative?'不查库':f>=c+(d-c)*.35?'确认：没有067':pass?'继续确认…':''}/></>;
};
const Capacity=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),recover=progress(f,d-34,d-4),extra=Array.from({length:M.bitCount},(_,i)=>i).filter(i=>!normal.includes(i)),grow=Math.floor(progress(f,a+(b-a)*.08,b-(b-a)*.08)*extra.length),ones=recover===1?normal:[...normal,...extra.slice(0,grow)];
 return <><Pill x={960} y={349} w={1040} label={recover===1?'回到原来的101 / 205示例':'另一份容量示意 · 不执行查询'} color={C.gold} size={34}/><BitArray ones={ones} label={recover===1?'16位 · 原示例已恢复':'16位固定 · 这里只示意标记变密'}/><T x={960} y={785} size={38} anchor="middle" color={C.teal}>预计数量  ↔  空间  ↔  可接受的误判率</T><T x={960} y={852} size={29} anchor="middle" color={C.muted} opacity={progress(f,c,c+(d-c)*.30)}>四个教学编号，不能估算线上收益</T></>;
};
const BadDelete=({s,f}:any)=>{
 const [c,d]=sentenceSpan(s,1),reset=f>=s.durationInFrames-20,erase=stages(f,c+(d-c)*.02,c+(d-c)*.40,A.positions),query=stages(f,c+(d-c)*.45,c+(d-c)*.76,M.expected.wrongDeletion205.checked),querying=f>=c+(d-c)*.43&&!reset,item=querying?B:A;
 const ones=reset?normal:normal.filter(i=>!arrived(erase).includes(i)),error=querying&&query.every(v=>v.arrived),activeSteps=querying?query:erase,records=reset||f<c?M.catalogInitially:['sku205'];
 return <><HashSlots item={item} checked={querying?arrived(query):[]} failedAt={error?3:undefined} active={activeSteps.find(v=>v.active)?.slot??-1} mode={reset?'原状态':querying?'错误查询':'错误清位'}/>{!reset&&traces(activeSteps,C.red)}<BitArray ones={ones} focus={reset?[]:focus(activeSteps)} zeroFocus={error?[3]:[]} label={reset?'反例结束 · 位图与目录均恢复':'错误删除反例 · 不支持直接清位'}/><QueryFooter shown={reset||error||f<c} blocked={error} idlePhase={reset?'reset':'waiting'} label={reset?'已恢复101 / 205的原始状态':error?'205仍在目录，却被位置3的0错拦':'先看共享位，不能按编号直接清零'} color={reset?C.teal:C.red} records={records} dbResult={reset?'收录状态已恢复':error?'205真实存在':'目录仍有205'} unsafe={!reset}/></>;
};
const Maintenance=({s,f}:any)=>{
 const [a,b]=sentenceSpan(s,0),[c,d]=sentenceSpan(s,1),stale=run(s,f,0,M.expected.negative001.checked,.12,.78),write=run(s,f,1,N.positions,.04,.75),writing=f>=c,done=writing&&write.every(v=>v.arrived),ones=writing?Array.from(new Set([...normal,...arrived(write)])).sort((x:any,y:any)=>x-y):normal,current=writing?write:stale,error=!writing&&stale.every(v=>v.arrived);
 return <><HashSlots item={N} checked={arrived(current)} failedAt={error?2:undefined} active={current.find(v=>v.active)?.slot??-1} mode={writing?'同步标记':'未同步查询'}/>{traces(current,writing?C.gold:C.red)}<BitArray ones={ones} focus={focus(current)} zeroFocus={error?[2]:[]} label={done?'标记已同步 · 正确维护后用于拦截':writing?'新增001：按同一规则置位':'未同步反例 · 目录新增001，位图仍旧'}/><QueryFooter shown={done||error||writing} blocked={error} idlePhase={writing?'writing':'waiting'} label={done?'正确维护：零位可排除，全1再确认':writing?'正在同步标记，暂不执行拦截':'危险：旧标记的0不能证明目录不存在'} color={done?C.teal:writing?C.gold:C.red} records={[...M.catalogInitially,N.key]} pass={done} dbResult={done?'确认：001存在':writing?'已收录001':'001已在目录'} unsafe={!done}/></>;
};
export const Scene=({s,f}:any)=>{
 const type=s.visualType,[chapter,title,sub]=heads[type]??heads.missing;let content:any,state:any={},note='教学示例 · 16位 / 3路哈希不代表产品内部实现或性能数据';
 switch(type){
  case 'missing':content=<Missing s={s} f={f}/>;state={phase:'before-filter',catalog:M.catalogInitially};break;
  case 'bits':content=<Bits s={s} f={f}/>;state={ones:[]};break;
  case 'hash':content=<Hash s={s} f={f}/>;state={ones:[],mapping:A};break;
  case 'insert-101':{const steps=run(s,f,1,A.positions,.08,.87);state={ones:Array.from(new Set(arrived(steps))).sort((a:any,b:any)=>a-b),steps};content=<Insert s={s} f={f} item={A} base={[]}/>;break;}
  case 'insert-205':{const steps=run(s,f,0,B.positions,.08,.87);state={ones:Array.from(new Set([...M.snapshots.after101,...arrived(steps)])).sort((a:any,b:any)=>a-b),steps};content=<Insert s={s} f={f} item={B} base={M.snapshots.after101}/>;break;}
  case 'reject-001':content=<Reject s={s} f={f}/>;state={ones:normal,query:N.key,checked:arrived(run(s,f,1,M.expected.negative001.checked,.04,.65))};note='前提：相关编号已正确收录，标记未被错误清除';break;
  case 'why-zero':content=<WhyZero s={s} f={f}/>;state={ones:normal,query:A.key};note='结构不会漏掉已正确加入且标记仍被保留的编号';break;
  case 'false-positive':content=<FalsePositive s={s} f={f}/>;state={ones:normal,query:F.key,actuallyInserted:false};note='可能存在只是放行；是否真有商品，仍由目录数据库确认';break;
  case 'shared-marks':content=<Shared s={s} f={f}/>;state={ones:normal,explanationOverlayOnly:true};note='来源线仅用于讲解；真实位数组不保存编号与所有者';break;
  case 'gate':content=<Gate s={s} f={f}/>;state={ones:normal,queriesAreIndependent:true};note='正确维护范围内：任意0可排除，全1继续真实查询';break;
  case 'capacity':content=<Capacity s={s} f={f}/>;state={alternateIllustration:true,restoresOriginal:true};note='容量示意不估算误判率；空间和参数要按实际负载选取';break;
  case 'bad-delete':content=<BadDelete s={s} f={f}/>;state={invalidOperation:true,restoresBothBitsAndCatalog:true};note='普通布隆过滤器不能直接清位删除；共享位会影响其他编号';break;
  case 'maintenance':content=<Maintenance s={s} f={f}/>;state={newCatalogKey:N.key,requiresMaintenance:true};note='先正确维护标记，再用于排除；全1仍要确认真实记录';break;
  default:throw new Error('Unknown Bloom scene: '+type);
 }
 return <><Head chapter={chapter} title={title} sub={sub}/>{content}<Note>{note}</Note><g data-visual-state={JSON.stringify({type,frame:f,sentenceSpans:[sentenceSpan(s,0),sentenceSpan(s,1)],...state})}/></>;
};
const ShotView=({s,hideSubtitles=false,auditLayout=false}:any)=>{
 const f=useCurrentFrame();useLayoutAudit(auditLayout,'main',s.from+f);
 const caption=(s.subtitles??[]).find((c:any)=>f>=c.from&&f<(c.to!==undefined?c.to+1:c.from+(c.duration??0)));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}><svg data-audit-scene="true" width={1920} height={1080} viewBox="0 0 1920 1080"><Scene s={s} f={f}/></svg>{!hideSubtitles&&caption&&<div data-subtitle="true" style={{position:'absolute',left:115,right:115,bottom:49,textAlign:'center',fontFamily:FONT,fontSize:31,lineHeight:1.45,color:C.text}}>{caption.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:{hideSubtitles?:boolean;auditLayout?:boolean})=><AbsoluteFill style={{background:C.bg}}>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
