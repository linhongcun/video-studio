import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,NODE_VALUES} from './data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
// Only measured sentence starts are used in production; fractional windows describe
// animation beats within a sentence, not inferred word-level recognition.
const at=(s:Shot,i:number,p:number)=>{
 const start=Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
 const end=Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-12);
 return start+(end-start)*p;
};
const phase=(s:Shot,f:number,i=0,a=.1,b=.7)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const cue=(s:Shot,f:number,term:string,i:number)=>f>=Number(s.cueFrames?.labels?.[term]??s.cueFrames?.sentences?.[i]??0);
const T=({x,y,children,size=34,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='反转链表',color=C.text}:any)=><g><T x={120} y={101} size={27} color={C.muted}>{kicker}</T><T x={120} y={184} size={54} color={color} weight={760}>{title}</T>{sub&&<T x={120} y={245} size={31} color={C.muted}>{sub}</T>}</g>;
const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={896} size={34} color={color} alpha={alpha} anchor="middle">{children}</T>;
type Target=-1|1|2|3|4;
const X:Record<number,number>={'-1':250,1:620,2:1000,3:1380,4:1740};
const targetName=(n:Target)=>n===-1||n===4?'None':String(n);
type Pointer={target:Target;pos?:number;alpha?:number};
type BoardProps={links?:Target[];changing?:number;changeTo?:Target;changeProgress?:number;prev?:Pointer;cur?:Pointer;nxt?:Pointer;spot?:number;spotAlpha?:number;saved?:Target;savedAlpha?:number;headAlpha?:number;idAlpha?:number;nullCaption?:boolean;linkAlpha?:number[]};
const RefArrow=({source,target,draw=1,alpha=1,color=C.muted}:any)=>{
 const sx=X[source],tx=X[target],right=tx>sx,start=sx+(right?110:-110),end=tx+(target===-1||target===4?(right?-70:70):(right?-110:110));
 const restingEnd=mix(start,end,clamp(draw));
 return <path data-next-source={source} data-next-target={targetName(target)} d={`M ${start} 545 H ${restingEnd}`} stroke={color} strokeWidth={4} fill="none" opacity={alpha} markerEnd={draw>.04?'url(#ref-head)':undefined}/>;
};
const Role=({kind,pointer}:{kind:'prev'|'cur'|'nxt';pointer:Pointer})=>{
 const pos=pointer.pos??X[pointer.target],a=pointer.alpha??1;
 const approachingNull=clamp((pos-X[3])/(X[4]-X[3]));
 // Route beside the fixed identity label, then approach the plain None text.
 if(kind==='cur')return <g opacity={a} data-pointer="cur" data-target={targetName(pointer.target)}><T x={pos+30} y={344} anchor="middle" size={34} color={C.gold}>当前 cur</T><path d={`M ${pos+30} 363 H ${pos+90-60*approachingNull} V ${451+62*approachingNull}`} stroke={C.gold} strokeWidth={3} fill="none" markerEnd="url(#gold-head)"/></g>;
 if(kind==='prev')return <g opacity={a} data-pointer="prev" data-target={targetName(pointer.target)}><path d={`M ${pos-38} 675 V 621`} stroke={C.teal} strokeWidth={3} fill="none" markerEnd="url(#teal-head)"/><T x={pos-38} y={722} anchor="middle" size={34} color={C.teal}>前驱 prev</T></g>;
 return <g opacity={a} data-pointer="nxt" data-target={targetName(pointer.target)}><path d={`M ${pos+48} 780 V 649 H ${pos+65} V 621`} stroke={C.blue} strokeWidth={3} fill="none" strokeDasharray="8 6" markerEnd="url(#blue-head)"/><T x={pos+48} y={827} anchor="middle" size={34} color={C.blue}>临时 nxt</T></g>;
};
const Board=({links=[2,3,4],changing,changeTo,changeProgress=0,prev,cur,nxt,spot=-1,spotAlpha=0,saved,savedAlpha=0,headAlpha=1,idAlpha=1,nullCaption=false,linkAlpha=[1,1,1]}:BoardProps)=>{
 return <g data-linked-list="fixed-original-nodes">
  {([-1,4] as Target[]).map(n=><g key={n} data-empty-reference={n===-1?'left':'right'}><T x={X[n]} y={553} anchor="middle" mono size={36} color={C.muted}>None</T><T x={X[n]} y={598} anchor="middle" size={27} color={C.muted}>空值</T></g>)}
  {NODE_VALUES.map((n,i)=>{
   const old=links[i],active=changing===n&&changeTo!==undefined,p=active?changeProgress:0;
   const shown=active&&p>=1?changeTo!:old;
   return <g key={n} data-original-node={n} data-next-at-rest={active&&p>0&&p<1?'changing':targetName(shown)}>
    <T x={X[n]} y={436} anchor="middle" size={28} color={C.muted} alpha={idAlpha}>原节点 {n}</T>
    <rect x={X[n]-110} y={465} width={220} height={152} rx={21} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <T x={X[n]} y={534} anchor="middle" size={61} mono>{n}</T>
    <path d={`M ${X[n]-84} 553 H ${X[n]+84}`} stroke={C.edge} strokeWidth={1.5}/>
    <T x={X[n]} y={596} anchor="middle" size={29} color={C.muted} mono>{active&&p>0&&p<1?'next':`next → ${targetName(shown)}`}</T>
    {n===spot&&<rect x={X[n]-110} y={465} width={220} height={152} rx={21} fill={C.gold+'06'} stroke={C.gold} strokeWidth={3} opacity={spotAlpha}/>}
    {active?<><RefArrow source={n} target={old} draw={1-clamp(p/.35)} alpha={p<.35?linkAlpha[i]:0}/><RefArrow source={n} target={changeTo} draw={clamp((p-.35)/.65)} alpha={p>.35?1:0} color={C.teal}/></>:<RefArrow source={n} target={old} alpha={linkAlpha[i]} color={old<n?C.teal:C.muted}/>}
   </g>;
  })}
  {saved!==undefined&&<g opacity={savedAlpha} data-preserved-entrance={targetName(saved)}>{saved===-1||saved===4?<path d={`M ${X[saved]-62} 568 H ${X[saved]+62}`} stroke={C.blue} strokeWidth={4}/>:<rect x={X[saved]-119} y={456} width={238} height={170} rx={27} fill="none" stroke={C.blue} strokeWidth={3} strokeDasharray="9 7"/>}</g>}
  <g opacity={headAlpha} data-head="original-node-1"><T x={350} y={337} anchor="middle" size={31} color={C.muted}>入口 head</T><path d="M 350 354 V 397 H 520 V 452" stroke={C.muted} strokeWidth={2} fill="none" markerEnd="url(#ref-head)"/></g>
  {prev&&<Role kind="prev" pointer={prev}/>} {cur&&<Role kind="cur" pointer={cur}/>} {nxt&&<Role kind="nxt" pointer={nxt}/>}
  {nullCaption&&<T x={960} y={873} anchor="middle" size={27} color={C.muted}>左右的 None 都表示空引用，不是额外节点</T>}
 </g>;
};
const pointer=(target:Target,alpha=1):Pointer=>({target,alpha});
const moving=(from:Target,to:Target,p:number):Pointer=>({target:p>=1?to:from,pos:mix(X[from],X[to],p)});
const Step=({label,alpha=1,color=C.gold}:any)=><g opacity={alpha}><rect x={630} y={758} width={660} height={83} rx={17} fill={C.surface} stroke={color} strokeWidth={1.5}/><T x={960} y={811} anchor="middle" size={35} color={color}>{label}</T></g>;
const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 if(t==='problem'){
  const walk=phase(s,f,1,.08,.8),spot=walk>=1?-1:Math.min(3,Math.floor(walk*4))+1;
  return <><Head kicker="LeetCode 206 · 先看题目" title="反转连接，还要保留每个原节点" sub="单向链表 · 每个节点保存值与 next 引用"/><Board spot={spot<=3?spot:-1} spotAlpha={walk<1?1:0}/><T x={960} y={738} anchor="middle" size={39} color={C.gold} alpha={p}>沿 next：1 → 2 → 3 → None</T><Note alpha={q}>head 是入口 · None 表示没有下一个节点</Note></>;
 }
 if(t==='output'){
  // This is the required output preview; shot 03 explicitly restores the input.
  const preview=phase(s,f,0,.1,.8),target=preview>=1;
  return <><Head kicker="LeetCode 206 · 题目目标预览" title="原节点不变，让连接全部反向" sub="要求：不交换值，不新建节点，返回反转后的头"/><g opacity={1-preview}><Board/></g><g opacity={preview}><Board links={[-1,1,2]}/></g><Step label="返回原节点 3 · 它是新的入口" alpha={p} color={C.teal}/><Note alpha={q}>{target?'目标：3 → 2 → 1 → None':'先看输出目标，还未开始执行算法'}</Note></>;
 }
 if(t==='derive-order'){
  const visit=phase(s,f,0,.05,.75),goals=phase(s,f,0,.4,.88),inspectionAlpha=phase(s,f,1,.02,.08);
  const move=phase(s,f,1,.4,.62),arrived=move===0||move===1,current=move===1?3:2,needed=current-1;
  const currentX=mix(X[2],X[3],move),neededX=mix(X[1],X[2],move);
  return <><Head kicker="思路推导 · 恢复原链" title="原链向后访问，目标却要指回刚走过的节点" sub="先分析需要记住什么 · 原 next 还没有修改"/><Board/>
   <g opacity={visit}><T x={1040} y={337} anchor="middle" size={31} color={C.gold}>原连接的访问顺序：1 → 2 → 3</T><path d="M 620 377 H 1380" pathLength={1} stroke={C.gold} strokeWidth={3} strokeDasharray="1" strokeDashoffset={1-visit} fill="none" markerEnd={visit>.95?'url(#gold-head)':undefined}/></g>
   <g opacity={goals} data-analysis-goal="unapplied-back-links">{[[2,1],[3,2]].map(([from,to])=><path key={from} d={`M ${X[from]-28} 630 V 675 H ${X[to]+28} V 630`} stroke={C.teal} strokeWidth={3} strokeDasharray="9 7" fill="none" markerEnd="url(#teal-head)"/>)}<T x={960} y={735} anchor="middle" size={28} color={C.muted}>虚线只标目标中的回指关系</T></g>
   <g opacity={inspectionAlpha} data-analysis-needed-entrance={needed}>
    <rect x={currentX-114} y={461} width={228} height={160} rx={24} fill="none" stroke={C.gold} strokeWidth={3}/><rect x={neededX-118} y={457} width={236} height={168} rx={27} fill="none" stroke={C.teal} strokeWidth={3}/>
    <g opacity={arrived?1:0}><T x={neededX} y={794} anchor="middle" size={31} color={C.teal}>需要记住 {needed}</T><T x={currentX} y={849} anchor="middle" size={31} color={C.gold}>走到 {current} 时，要指回 {needed}</T></g>
   </g><Note color={C.muted}>这里只分析做法，正式处理仍从原链开始</Note>
  </>;
 }
 if(t==='save')return <><Head kicker="开始执行 · 恢复原链" title="改掉连接前，先保住后半段入口" sub="回到输入：1 → 2 → 3 → None"/><Board spot={1} spotAlpha={p} saved={2} savedAlpha={q*.7}/><Step label="修改 1.next 之前，怎样还能访问到 2？" alpha={q}/><Note alpha={q}>要保存的是原后继的入口，不是复制一个新节点</Note></>;
 if(t==='roles'){
  const prevOn=cue(s,f,'前驱指针',0),curOn=cue(s,f,'当前指针',1);
  return <><Head kicker="准备第一轮" title="把已完成段和当前节点分开记住" sub="开始时，还没有任何节点完成反转"/><Board prev={prevOn?pointer(-1):undefined} cur={curOn?pointer(1):undefined} spot={1} spotAlpha={q}/><Note alpha={q}>已完成段为空 · 本轮处理原节点 1</Note></>;
 }
 if(t==='save-first'){
  const introduced=cue(s,f,'临时指针',0),assigned=q>0;
  return <><Head kicker="第一轮 · 先保存" title="先记住：原来的下一站是节点 2" sub="此时还没有修改 1.next"/><Board prev={pointer(-1)} cur={pointer(1)} nxt={assigned?pointer(2,q):undefined} spot={1} spotAlpha={1} saved={2} savedAlpha={q}/>{introduced&&!assigned&&<T x={1048} y={827} size={34} anchor="middle" color={C.blue}>临时 nxt · 待保存</T>}<Note alpha={q} color={C.blue}>临时指针指向原节点 2，原连接仍然保留</Note></>;
 }
 if(t==='reverse-first')return <><Head kicker="第一轮 · 再反转" title="把 1.next 改为空，入口 2 仍在" sub="当前节点 1 指向前驱所指的空值"/><Board changing={1} changeTo={-1} changeProgress={p} prev={pointer(-1)} cur={pointer(1)} nxt={pointer(2)} spot={1} spotAlpha={1} saved={2} savedAlpha={q}/><Note alpha={q} color={C.blue}>nxt 仍能访问到 2 → 3 → None</Note></>;
 if(t==='move-first')return <><Head kicker="第一轮 · 最后移动" title="先更新前驱，再继续处理节点 2" sub="连接已经改好，接着依次移动两个角色"/><Board links={[-1,3,4]} prev={moving(-1,1,p)} cur={moving(1,2,q)} nxt={pointer(2)} saved={2} savedAlpha={1}/><Note alpha={q} color={C.teal}>完成段：1 → None · 待处理：2 → 3 → None</Note></>;
 if(t==='second-round')return <><Head kicker="第二轮 · 先保存，再反转" title="先保存 3，再让节点 2 指回 1" sub="当前节点仍是 2，前驱仍是 1"/><Board links={[-1,3,4]} changing={2} changeTo={1} changeProgress={q} prev={pointer(1)} cur={pointer(2)} nxt={moving(2,3,p)} spot={2} spotAlpha={1} saved={3} savedAlpha={p}/><Note alpha={q} color={C.teal}>2 → 1 → None 已连接好，3 的入口也仍在</Note></>;
 if(t==='move-second')return <><Head kicker="第二轮 · 最后移动" title="前驱来到 2，当前再来到 3" sub="保存、反转都已完成，才开始移动"/><Board links={[-1,1,4]} prev={moving(1,2,p)} cur={moving(2,3,q)} nxt={pointer(3)} saved={3} savedAlpha={1}/><Note alpha={q} color={C.teal}>完成段：2 → 1 → None · 待处理：3</Note></>;
 if(t==='save-last')return <><Head kicker="第三轮 · 先保存" title="最后一个节点，原后继是空值" sub="先看 3.next：后面已经没有节点"/><Board links={[-1,1,4]} prev={pointer(2)} cur={pointer(3)} nxt={moving(3,4,q)} spot={3} spotAlpha={1} saved={4} savedAlpha={q}/><Note alpha={q} color={C.blue}>临时指针记为空 · None 不是第四个节点</Note></>;
 if(t==='reverse-last')return <><Head kicker="第三轮 · 再反转" title="让节点 3 指回节点 2" sub="原节点的身份、位置和值全程保持不变"/><Board links={[-1,1,4]} changing={3} changeTo={2} changeProgress={p} prev={pointer(2)} cur={pointer(3)} nxt={pointer(4)} spot={3} spotAlpha={1}/><Note alpha={q} color={C.teal}>连接已经成为：3 → 2 → 1 → None</Note></>;
 if(t==='move-last')return <><Head kicker="第三轮 · 最后移动" title="前驱到 3，当前再来到空值" sub="先完成连接，再依次更新指针"/><Board links={[-1,1,2]} prev={moving(2,3,p)} cur={moving(3,4,q)} nxt={pointer(4)}/><Note alpha={q} color={C.teal}>当前为空：已经没有待处理节点</Note></>;
 if(t==='code'){
  const exit=phase(s,f,1,.04,.3),returned=phase(s,f,1,.5,.83);
  return <><Head kicker="把停止和返回写进程序" title="当前为空时停止，返回完成段的头" sub="连接反转完了，最后确认谁才是新的入口"/><g opacity={exit}><T x={900} y={333} anchor="middle" mono size={38} color={C.gold}>while cur:</T><T x={900} y={380} anchor="middle" size={29} color={C.muted}>cur 为空，退出循环</T></g><Board links={[-1,1,2]} prev={pointer(3)} cur={pointer(4)} nxt={pointer(4)}/><g opacity={returned}><rect x={647} y={756} width={626} height={88} rx={17} fill={C.surface} stroke={C.teal} strokeWidth={2}/><T x={960} y={813} anchor="middle" mono size={38} color={C.teal}>return prev  →  原节点 3</T></g><Note alpha={returned}>head 仍指向原节点 1 · 返回值才给出新头</Note></>;
 }
 return <><Head kicker="回收结论" title="先保存后反转，始终保留下一步入口" sub="只改 next，不交换值，不创建新节点" color={C.teal}/>
  {[['① 保存原后继',C.blue],['② 反转 next',C.teal],['③ 依次移动',C.gold]].map(([label,color],i)=><g key={label}><rect x={205+i*520} y={292} width={470} height={83} rx={17} fill={C.surface} stroke={color} strokeWidth={2}/><T x={440+i*520} y={345} anchor="middle" size={35} color={color}>{label}</T>{i<2&&<T x={700+i*520} y={345} anchor="middle" size={31} color={C.muted}>→</T>}</g>)}
  <Board links={[-1,1,2]} headAlpha={0}/><g><path d="M 1380 690 V 628" stroke={C.teal} strokeWidth={3} fill="none" markerEnd="url(#teal-head)"/><T x={1380} y={744} anchor="middle" size={36} color={C.teal}>返回值 · 新头 3</T></g><path d="M 620 690 V 628" stroke={C.muted} strokeWidth={2} fill="none" markerEnd="url(#ref-head)"/><T x={620} y={744} anchor="middle" size={32} color={C.muted}>传入的 head 仍指向 1</T><Note alpha={q}>接下来是完整代码，需要细看请暂停</Note>
 </>;
};
const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null;
 const card=codeCardFrom!==null&&f>=codeCardFrom,sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  <defs><radialGradient id="lc206-bg"><stop offset="0" stopColor="#173B55" stopOpacity=".22"/><stop offset="1" stopColor={C.bg} stopOpacity="0"/></radialGradient>{[['ref-head',C.muted],['teal-head',C.teal],['gold-head',C.gold],['blue-head',C.blue]].map(([id,color])=><marker key={id} id={id} markerWidth="11" markerHeight="11" refX="9" refY="5.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M 1 1 L 9 5.5 L 1 10" fill="none" stroke={color} strokeWidth="2.5"/></marker>)}</defs>
  <ellipse cx="1440" cy="280" rx="950" ry="700" fill="url(#lc206-bg)"/>
  {card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}
  <T x={1790} y={91} size={25} color={C.muted} anchor="end">IT小村</T>
  <T x={120} y={1020} size={22} color={C.muted} alpha={.65}>{card?'LeetCode 206 · Python 3':'LeetCode 206 · 教学示例'}</T>
 </svg>{!hideSubtitles&&!card&&subtitle&&<div style={{position:'absolute',left:180,right:180,bottom:65,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
