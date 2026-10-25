import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
import {Shot,VIDEO,shots} from './data';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
const DatabaseMark=createDatabaseIdentity(React);
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,a:number,n=35)=>{const v=clamp((f-a)/Math.max(1,n));return v*v*(3-2*v)};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
type Order={id:string;user:string};
const old:Order[]=[{id:'7042',user:'42'},{id:'7043',user:'17'},{id:'7044',user:'42'},{id:'7045',user:'86'},{id:'7046',user:'17'},{id:'7047',user:'86'}];
const a:Order={id:'7050',user:'42'},b:Order={id:'7051',user:'17'},again:Order={id:'7052',user:'42'};
const X=[420,960,1500],colors=[C.teal,C.blue,C.gold],names=['A库','B库','C库'];
const which=(o:Order)=>o.user==='42'?0:o.user==='17'?1:2;
const Txt:React.FC<{children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;alpha?:number;center?:boolean}>=({children,x=130,y=175,size=49,color=C.text,alpha=1,center=false})=><div style={{position:'absolute',left:x,top:y,color,fontSize:size,opacity:alpha,whiteSpace:'nowrap',lineHeight:1.35,fontWeight:600,transform:center?'translateX(-50%)':undefined}}>{children}</div>;
const Path:React.FC<{x1:number;y1:number;x2:number;y2:number;p:number;color?:string;alpha?:number}>=({x1,y1,x2,y2,p,color=C.teal,alpha=1})=>{const ym=(y1+y2)/2;return <svg width="1920" height="1080" style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M${x1} ${y1} C${x1} ${ym} ${x2} ${ym} ${x2} ${y2}`} pathLength="1" fill="none" stroke={color} strokeWidth="3" strokeDasharray="1" strokeDashoffset={1-clamp(p)}/></svg>};
const Token:React.FC<{o:Order;x:number;y:number;scale?:number;alpha?:number;color?:string;focus?:boolean;compact?:boolean;hideUser?:boolean}>=({o,x,y,scale=1,alpha=1,color=C.text,focus=false,compact=false,hideUser=false})=><div data-order={o.id} data-user={o.user} style={{position:'absolute',left:x-240,top:y-32,width:480,height:64,display:'flex',alignItems:'center',justifyContent:'space-around',fontFamily:MONO,fontSize:36,background:C.bg,borderBottom:`2px solid ${color}`,opacity:alpha,transform:`scale(${scale})`,transformOrigin:'center'}}>{!compact&&<span style={{color:C.muted,fontFamily:FONT,fontSize:23}}>订单</span>}<span style={{color}}>{o.id}</span>{!compact&&<span style={{fontFamily:FONT,fontSize:23,color:C.muted}}>用户</span>}<span style={{visibility:hideUser?'hidden':'visible',color:focus?C.gold:color,padding:'5px 12px',borderRadius:7,background:focus?'#8C641633':'transparent'}}>{o.user}</span></div>;
const Single:React.FC<{rows?:Order[];x?:number;y?:number;alpha?:number;scale?:number}>=({rows=old,x=960,y=345,alpha=1,scale=1})=><div style={{position:'absolute',left:x-450,top:y,width:900,height:440,opacity:alpha,transform:`scale(${scale})`,transformOrigin:'top center'}}><div style={{position:'relative',fontSize:32,color:C.teal,borderBottom:`2px solid ${C.teal}`,padding:'0 20px 20px 80px'}}><DatabaseMark size={44} style={{position:'absolute',left:20,top:-5}}/>一个库 · 订单表</div><div style={{display:'flex',justifyContent:'space-around',fontSize:23,color:C.muted,padding:'16px 0'}}><span>订单编号</span><span>用户编号</span></div>{rows.map((o,i)=><div key={o.id} style={{height:48,display:'flex',justifyContent:'space-around',alignItems:'center',fontFamily:MONO,fontSize:33,color:i===0?C.text:C.muted,borderBottom:`1px solid ${C.edge}`}}><span>{o.id}</span><span>{o.user}</span></div>)}</div>;
const Shard:React.FC<{n:number;rows:Order[];alpha?:number;y?:number;scale?:number;glow?:boolean}>=({n,rows,alpha=1,y=575,scale=1,glow=false})=><div data-shard={n} style={{position:'absolute',left:X[n]-195,top:y,width:390,height:285,opacity:alpha,transform:`scale(${scale})`,transformOrigin:'top center'}}>
 <div style={{position:'relative',fontSize:34,color:colors[n],fontWeight:700,textAlign:'center',paddingBottom:16,borderBottom:`${glow?3:1}px solid ${glow?colors[n]:C.edge}`}}><DatabaseMark size={44} style={{position:'absolute',left:6,top:-5}}/>{names[n]} <span style={{fontSize:22,color:C.muted,fontWeight:400}}>· 订单表（节选）</span></div>
 <div style={{display:'flex',justifyContent:'space-around',fontSize:20,color:C.muted,padding:'14px 0'}}>订单编号 <span>用户编号</span></div>
 {rows.map(o=><div key={o.id} style={{height:47,display:'flex',justifyContent:'space-around',alignItems:'center',fontFamily:MONO,fontSize:31,color:colors[n],borderBottom:`1px solid ${C.edge}`}}><span>{o.id}</span><span>{o.user}</span></div>)}
 </div>;
const Rule:React.FC<{f:number;at?:number;alpha?:number;user?:string}>=({f,at=0,alpha=1,user='42'})=><>
 <Txt x={960} y={450} center size={27} color={C.muted} alpha={alpha}>固定规则：用户 {user} → {names[user==='42'?0:user==='17'?1:2]}</Txt>
 <div style={{position:'absolute',left:950,top:500,width:20,height:20,borderRadius:'50%',background:C.teal,opacity:alpha*(.55+.3*Math.sin((f-at)/13))}}/>
 </>;
const Result:React.FC<{children:React.ReactNode;alpha?:number;color?:string;y?:number}>=({children,alpha=1,color=C.teal,y=795})=><Txt x={960} y={y} center size={36} color={color} alpha={alpha}>{children}</Txt>;
const Scene:React.FC<{s:Shot}>=({s})=>{
 const f=useCurrentFrame(),d=s.durationInFrames,id=Number(s.id),s1=s.cueFrames?.sentences?.[1]??d*.5;
 if(id===1){const progress=go(f,15,d*.7);return <>
  <Txt size={64}>订单太多，一个库忙不过来？</Txt><Single rows={old.slice(0,3)} y={450} scale={.85}/>
  {[0,1,2].map((i)=>{const p=go(f,10+i*28,75);return <Token key={i} o={old[i+3]} x={mix(340+i*540,960,p)} y={mix(325,420,p)} scale={.6} alpha={1-p*.65} color={C.gold}/>})}
  <Result alpha={progress} color={C.gold}>数据在增长 · 写入也集中在一处</Result>
 </>}
 if(id===2){const p=go(f,s1-12,60);return <>
  <Txt>{p<.2?'下单卡住，原因可能有很多':'这里只看：数据与写入集中'}</Txt><Single rows={old.slice(0,3+Math.floor(p*3))} y={345} scale={mix(.9,1,p)}/>
  <Result alpha={1-p} color={C.muted}>先确认瓶颈，再考虑拆分</Result>
 </>}
 if(id===3){const reveal=go(f,s1-10,55);return <>
  <Txt>先认识一条订单</Txt><Token o={old[0]} x={mix(960,690,reveal)} y={520} scale={1.25} focus color={C.teal}/>
  <Path x1={1050} y1={520} x2={1260} y2={520} p={reveal} color={C.gold}/>
  <Txt x={1350} y={365} center size={29} color={C.muted} alpha={reveal}>用户编号</Txt><Txt x={1350} y={440} center size={148} color={C.gold} alpha={reveal}>42</Txt>
  <Result alpha={reveal} color={C.muted}>订单 7042 属于用户 42</Result>
 </>}
 if(id===4){const p=go(f,8,d-65),n=Math.min(6,1+Math.floor(p*6));return <>
  <Txt>不同用户的订单，都写进这里</Txt><Single rows={old.slice(0,n)} y={340}/>
  {n<6&&<Token o={old[n]} x={mix(1590,960,(p*6)%1)} y={300} scale={.58} color={C.gold}/>}
  <Result alpha={go(f,s1,25)} color={C.gold}>同一个目标，持续累积</Result>
 </>}
 if(id===5){const at=s.cueFrames?.splitLabel??1,p=go(f,35,105);return <>
  {f>=at&&<Txt color={C.teal} size={58}>分库分表</Txt>}
  <Single rows={[]} y={305} alpha={1-p}/>
  {X.map((_,i)=><Shard key={i} n={i} rows={[]} alpha={p} y={575}/>)}
  {old.map((o,i)=>{const n=which(o),local=old.filter(q=>q.user===o.user).findIndex(q=>q.id===o.id);return <Token key={o.id} o={o} x={mix(960,X[n],p)} y={mix(484+i*48,713+local*47,p)} scale={mix(.95,.74,p)} compact={p>.3} color={p>.5?colors[n]:C.text}/>})}
  <Result alpha={go(f,s1+50,25)} color={C.muted} y={855}>各存一部分，不是复制三份</Result>
 </>}
 if(id===6){const p=go(f,15,35);return <>
  <Txt>每次新写入，都要找到目标</Txt><Token o={a} x={960} y={365} scale={1.05} alpha={p}/>
  <Txt x={960} y={285} center size={23} color={C.muted} alpha={p}>一条新订单</Txt>
  {X.map((x,n)=><React.Fragment key={n}><Path x1={960} y1={490} x2={x} y2={565} p={go(f,s1,50)} color={C.edge}/><Shard n={n} rows={[]} alpha={.5}/></React.Fragment>)}
  <Txt x={960} y={445} center size={46} color={C.gold} alpha={go(f,55,25)}>该去哪里？</Txt>
 </>}
 if(id===7){const at=s.cueFrames?.keyLabel??1,p=go(f,s1-12,55),route=go(f,s1+35,60);return <>
  {f>=at&&<Txt color={C.teal} size={58}>分片键</Txt>}
  <Token o={a} x={mix(960,540,p)} y={365} focus hideUser alpha={1-p}/>
  <Txt x={mix(1137,960,p)} y={mix(340,305,p)} center size={mix(36,100,p)} color={C.gold}><span style={{fontFamily:MONO}}>42</span></Txt>
  <Txt x={960} y={270} center size={24} color={C.muted} alpha={go(p*100,65,35)}>用户编号</Txt>
  <Rule f={f} alpha={route}/><Path x1={960} y1={520} x2={420} y2={575} p={route}/>
  <Shard n={0} rows={[]} alpha={route}/><Shard n={1} rows={[]} alpha={.2*route}/><Shard n={2} rows={[]} alpha={.2*route}/>
 </>}
 if(id===8||id===9||id===10){const o=id===9?b:id===10?again:a,n=which(o),p=go(f,s1-6,75),land=p===1,pre=id===8?[old[0]]:id===9?[old[1]]:[a];return <>
  <Txt>{id===10?'同一用户的新订单，仍走同一路径':`用户 ${o.user} → ${names[n]}`}</Txt>
  {X.map((_,j)=><Shard key={j} n={j} rows={j===n?(land?[...pre,o]:pre):j===0?[old[0],a].slice(id===8?0:1):[]} alpha={j===n?1:.18} glow={j===n&&land}/>)}
  <Rule f={f} user={o.user} alpha={(1-go(p*100,0,25))*(1-go(f,d-40,35))}/>
  <Path x1={960} y1={410} x2={X[n]} y2={713+pre.length*47} p={p} color={colors[n]}/>
  {!land&&<Token o={o} x={mix(960,X[n],p)} y={mix(365,713+pre.length*47,p)} scale={mix(1,.82,p)} compact={p>.85} color={colors[n]} focus/>}
  <Txt x={960} y={275} center size={28} color={C.muted} alpha={1-p}>{id===10?'又一条新订单':'当前写入'}</Txt>
 </>}
 if(id===11){const locate=go(f,15,60),back=go(f,s1,65),focus=go(f,s1+65,35),context=1-go(f,s1-10,10);return <>
  <Txt>查询用户 42，也按同一规则定位</Txt>
  <Txt x={960} y={325} center size={50} color={C.gold} alpha={1-go(back*100,50,50)}>用户 42 的订单</Txt>
  <Path x1={960} y1={410} x2={420} y2={575} p={locate} alpha={context}/>
  <Shard n={0} rows={[]} alpha={context} glow/><Shard n={1} rows={[]} alpha={.14*context}/><Shard n={2} rows={[]} alpha={.14*context}/>
  {[a,again].map((o,i)=><Token key={o.id} o={o} x={mix(420,960,back)} y={mix(723+i*47,470+i*95,back)} scale={mix(.74,1.1,back)} compact color={C.teal}/>)}
  <Txt x={960} y={350} center size={25} color={C.muted} alpha={focus}>查询结果节选 · 本段新增订单</Txt>
  <Txt x={833} y={400} center size={23} color={C.muted} alpha={focus}>订单编号</Txt><Txt x={1097} y={400} center size={23} color={C.muted} alpha={focus}>用户编号</Txt>
  <Result alpha={focus}>缩小范围，不必每次都访问所有库</Result>
 </>}
 if(id===12){const shift=go(f,s1-12,55);return <>
  <Txt>{shift<.4?'独立处理资源，才可能分担压力':'只拆表名，不会凭空增加资源'}</Txt>
  {X.map((x,n)=>{const p=go(f,30+n*10,70),o=old.find(q=>which(q)===n)!;return <React.Fragment key={n}><Shard n={n} rows={p===1?[o]:[]} alpha={1-go(shift*100,0,60)}/><Path x1={x} y1={350} x2={mix(x,960,shift)} y2={mix(575,640,shift)} p={p} color={colors[n]}/><Token o={o} x={mix(x,960,shift)} y={mix(350,520,p)} scale={.62} alpha={(1-p)*(1-shift)} color={colors[n]}/><Txt x={x} y={840} center size={25} color={colors[n]} alpha={1-shift}>处理资源 {n+1}</Txt></React.Fragment>})}
  <Txt x={960} y={710} center size={58} color={C.gold} alpha={go(shift*100,65,35)}>仍争抢同一份资源</Txt>
 </>}
 if(id===13){const query=go(f,s1+30,60);return <>
  <Txt>{query<.2?'分得开，不等于分得匀':'查询跨很多库，工作也会增加'}</Txt>
  {X.map((x,n)=><React.Fragment key={n}><Shard n={n} rows={n===0?[a,again]:[]} alpha={n===0?1:.35+query*.65} glow={n===0}/><Path x1={960} y1={370} x2={x} y2={575} p={query} color={colors[n]}/></React.Fragment>)}
  {[0,1,2].map(i=><Token key={i} o={{id:String(7060+i),user:'42'}} x={420} y={330+i*65} scale={.62} alpha={(1-query)*go(f,i*22,35)} color={C.gold}/>)}
  <Txt x={960} y={300} center size={34} color={C.muted} alpha={query}>另一种查询：统计所有用户</Txt>
  <Result color={C.gold} alpha={1-query}>一处更忙，仍可能成为瓶颈</Result>
 </>}
 const next=go(f,s1-12,40),brand=go(f,d-50,25);return <>
  <Txt size={52}>{next<.3?'先看瓶颈，再选分配规则':'下一期：两个订单，怎么撞成同一个号了？'}</Txt>
  <Txt x={960} y={410} center size={56} color={C.teal} alpha={1-next}>数据 → 规则 → 目标库</Txt>
  <Txt x={960} y={320} center size={25} color={C.muted} alpha={next*(1-brand)}>下期的另一组编号示例</Txt>
  <Txt x={600} y={440} center size={115} color={C.gold} alpha={next*(1-brand)}>1</Txt><Txt x={1320} y={440} center size={115} color={C.blue} alpha={next*(1-brand)}>1</Txt>
  <Txt x={600} y={590} center size={31} color={C.muted} alpha={next*(1-brand)}>订单甲</Txt><Txt x={1320} y={590} center size={31} color={C.muted} alpha={next*(1-brand)}>订单乙</Txt>
  <Txt x={960} y={475} center size={64} alpha={brand}>IT小村 · 原创</Txt>
 </>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{const f=useCurrentFrame(),sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 12%, #1A425E55, transparent 62%)'}}/>
 <Txt x={100} y={62} size={23} color={C.muted}>分布式 · EP.19</Txt><Txt x={1715} y={60} size={25}>IT小村</Txt><Txt x={1715} y={106} size={18} color={C.muted} center>订单与用户编号 · 示例数据</Txt>
 <Scene s={shot}/>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.35,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}</AbsoluteFill>;
