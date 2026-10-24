import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
import {Shot,VIDEO,shots} from './data';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,a:number,n=30)=>{const v=clamp((f-a)/Math.max(1,n));return v*v*(3-2*v)};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const Txt:React.FC<{children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;alpha?:number;center?:boolean}>=({children,x=130,y=180,size=48,color=C.text,alpha=1,center=false})=><div style={{position:'absolute',left:x,top:y,color,fontSize:size,opacity:alpha,whiteSpace:'nowrap',fontWeight:600,lineHeight:1.35,transform:center?'translateX(-50%)':undefined}}>{children}</div>;
const Stock:React.FC<{value:number;owner?:string;color?:string;alpha?:number;scale?:number;old?:number;y?:number;x?:number}>=({value,owner='',color=C.text,alpha=1,scale=1,old,y=530,x=960})=><div data-stock={value} data-owner={owner} style={{position:'absolute',left:x-250,top:y-175,width:500,height:355,textAlign:'center',opacity:alpha,transform:`scale(${scale})`,transformOrigin:'center'}}>
 <div style={{fontSize:25,color:C.muted,letterSpacing:3}}>商品 7042 · 库存</div>
 <div style={{height:213,fontSize:184,fontFamily:MONO,fontWeight:650,lineHeight:1.12,color}}>{value}</div>
 <div style={{position:'absolute',left:45,right:45,top:262,borderTop:`2px solid ${owner?color:C.edge}`,height:35}}/>
 {owner&&<div style={{position:'absolute',top:279,left:0,right:0,color,fontSize:26}}>{owner}</div>}
 {old!==undefined&&<div style={{position:'absolute',left:0,right:0,top:-52,fontSize:25,color:C.muted}}>原确认库存 {old}</div>}
 </div>;
const Request:React.FC<{who:string;x:number;value?:number;state?:string;color?:string;alpha?:number;scale?:number;y?:number}>=({who,x,value,state='购买 1 件',color=C.blue,alpha=1,scale=1,y=365})=><div data-request={who} data-read={value} style={{position:'absolute',left:x-180,top:y,width:360,height:320,textAlign:'center',opacity:alpha,transform:`scale(${scale})`,transformOrigin:'center'}}>
 <div style={{fontSize:43,fontWeight:700,color}}>请求{who}</div>
 <div style={{height:110,fontSize:value===undefined?30:83,fontFamily:value===undefined?FONT:MONO,lineHeight:1.3,marginTop:35,color:value===undefined?C.muted:color}}>{value===undefined?'':value}</div>
 <div style={{fontSize:27,color:state.includes('缺货')?C.red:color,marginTop:14}}>{state}</div>
 </div>;
const Line:React.FC<{x1:number;x2:number;y?:number;p:number;color?:string;alpha?:number}>=({x1,x2,y=525,p,color=C.blue,alpha=1})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:alpha,pointerEvents:'none'}}><path d={`M${x1} ${y}H${x2}`} pathLength="1" stroke={color} strokeWidth="3" fill="none" strokeDasharray="1" strokeDashoffset={1-clamp(p)}/><circle cx={mix(x1,x2,clamp(p))} cy={y} r="7" fill={color} opacity={p>0&&p<1?1:0}/></svg>;
const Carry:React.FC<{value:string;x1:number;x2:number;p:number;y?:number;color?:string}>=({value,x1,x2,p,y=490,color=C.gold})=>p>0&&p<1?<Txt x={mix(x1,x2,p)} y={y-40*Math.sin(Math.PI*p)} center size={60} color={color}>{value}</Txt>:null;
const Pulse:React.FC<{f:number;x:number;y:number;color?:string}>=({f,x,y,color=C.blue})=><div style={{position:'absolute',left:x-18,top:y-18,width:36,height:36,border:`2px solid ${color}`,borderRadius:'50%',transform:`scale(${1+.2*Math.sin(f/12)})`,opacity:.6+.25*Math.sin(f/12)}}/>;
const Result:React.FC<{children:React.ReactNode;color?:string;alpha?:number;y?:number}>=({children,color=C.teal,alpha=1,y=780})=><Txt x={960} y={y} center size={38} color={color} alpha={alpha}>{children}</Txt>;

const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),d=s.durationInFrames,id=Number(s.id),s1=s.cueFrames?.sentences?.[1]??d*.5;
 if(id===1){const a=go(f,12,48),b=go(f,s1-15,48);return <>
  <Txt size={66}>最后 1 件，怎么都成功了？</Txt><Stock value={1}/>
  <Request who="甲" x={365} color={C.gold} state={a===1?'下单通过':'购买 1 件'}/><Request who="乙" x={1555} color={C.blue} state={b===1?'也通过了？':'购买 1 件'}/>
  <Line x1={540} x2={785} p={a} color={C.gold}/><Line x1={1380} x2={1135} p={b}/>
  <Result color={C.red} alpha={b}>货只有 1 件 · 两个请求都通过</Result>
 </>}
 if(id===2){const a=go(f,s1-12,25),b=go(f,s1+40,25);return <>
  <Txt>先看同一条库存记录</Txt><Stock value={1}/>
  <Request who="甲" x={365} color={C.gold} alpha={a}/><Request who="乙" x={1555} alpha={b}/>
 </>}
 if(id===3){const a=go(f,s1-10,45),b=go(f,s1+35,45);return <>
  <Txt>普通查询：都读到了 1</Txt><Stock value={1}/>
  <Request who="甲" x={365} color={C.gold} value={a===1?1:undefined} state={a===1?'读到的库存':'读取中'}/>
  <Request who="乙" x={1555} value={b===1?1:undefined} state={b===1?'读到的库存':'读取中'}/>
  <Line x1={785} x2={540} p={a} color={C.gold}/><Line x1={1135} x2={1380} p={b}/>
  <Carry value="1" x1={785} x2={540} p={a}/><Carry value="1" x1={1135} x2={1380} p={b} color={C.blue}/>
 </>}
 if(id===4){const calc=go(f,35,35),write=go(f,s1,45),done=write===1,focus=go(f,0,35)*(1-go(f,d-40,35));return <>
  <Txt>甲先写回自己的计算结果</Txt>
  <Request who="甲" x={mix(365,520,focus)} scale={mix(1,1.15,focus)} color={C.gold} value={calc===1?0:1} state={done?'通过 ✓':calc===1?'1 − 1 = 0':'读到 1'}/>
  <Request who="乙" x={1555} value={1} state="之前读到的 1" alpha={.35} scale={.8}/>
  <Stock x={mix(960,1100,focus)} value={done?0:1} color={done?C.teal:C.text}/><Line x1={mix(540,695,focus)} x2={mix(785,925,focus)} p={write} color={C.gold}/><Carry value="0" x1={mix(540,695,focus)} x2={mix(785,925,focus)} p={write}/>
  <Result alpha={done?1:0}>甲已通过 · 库存扣了 1 件</Result>
 </>}
 if(id===5){const calc=go(f,35,35),write=go(f,s1,45),done=write===1,focus=go(f,0,35)*(1-go(f,d-40,35));return <>
  <Txt>乙还在用旧值计算</Txt><Stock x={mix(960,820,focus)} value={0} color={done?C.red:C.teal}/>
  <Request who="甲" x={365} color={C.gold} value={0} state="已经通过 ✓" alpha={.35} scale={.8}/>
  <Request who="乙" x={mix(1555,1395,focus)} scale={mix(1,1.15,focus)} value={calc===1?0:1} color={C.red} state={done?'也被放行了':calc===1?'旧值 1 − 1 = 0':'旧读取结果'}/>
  <Line x1={mix(1380,1220,focus)} x2={mix(1135,995,focus)} p={write} color={C.red}/><Carry value="0" x1={mix(1380,1220,focus)} x2={mix(1135,995,focus)} p={write} color={C.red}/>
  <Result color={C.red} alpha={done?1:0}>再次写回 0 · 没有再扣 1 件</Result>
 </>}
 if(id===6){const at=s.cueFrames?.lostLabel??1,a=go(f,25,45),b=go(f,85,45);return <>
  {f>=at&&<Txt size={58} color={C.teal}>丢失更新</Txt>}
  <Stock value={0} color={C.red}/><Line x1={540} x2={785} p={a} color={C.gold} alpha={1-b*.7}/><Line x1={1380} x2={1135} p={b} color={C.red}/>
  <Request who="甲" x={365} color={C.gold} value={0} state="写回 0" alpha={1-b*.6}/><Request who="乙" x={1555} color={C.red} value={0} state="又写回 0" alpha={b}/>
  <Result color={C.red} alpha={go(f,s1,25)}>通过 2 次 · 库存只扣 1 次</Result>
 </>}
 if(id===7){const show=go(f,18,35),a=go(f,s1-10,35),b=go(f,s1+35,35);return <>
  <Txt>重来一次：起点仍是库存 1</Txt><Stock value={1} alpha={show}/>
  <Request who="甲" x={365} color={C.gold} state="甲的事务" alpha={a}/><Request who="乙" x={1555} state="乙的事务" alpha={b}/>
 </>}
 if(id===8){const at=s.cueFrames?.lockLabel??1,arrive=go(f,s1-8,40),read=go(f,s1+40,40);return <>
  {f>=at&&<Txt size={58} color={C.teal}>行锁</Txt>}
  <Stock value={1} owner={arrive===1?'甲持有 · 事务尚未结束':''} color={arrive===1?C.gold:C.text}/>
  <Request who="甲" x={365} color={C.gold} value={read===1?1:undefined} state={read===1?'加锁读到 1':'在事务里加锁读取'}/><Request who="乙" x={1555} alpha={.25}/>
  <Line x1={540} x2={785} p={arrive} color={C.gold}/><Carry value="1" x1={785} x2={540} p={read}/>
  <Txt x={960} y={805} center size={29} color={C.muted} alpha={go(f,at+45,25)}>SELECT stock FROM goods WHERE id=7042 FOR UPDATE;</Txt>
 </>}
 if(id===9){const approach=go(f,15,50);return <>
  <Txt>乙的加锁查询：先等，尚未返回</Txt><Stock value={1} owner="甲持有 · 事务尚未结束" color={C.gold}/>
  <Request who="甲" x={365} color={C.gold} value={1} state="正在检查和修改"/>
  <Request who="乙" x={1555} state={approach===1?'等待同一行 · 还没读到结果':'请求同一行'}/>
  <Line x1={1380} x2={1210} p={approach}/>{approach===1&&<Pulse f={f} x={1205} y={525}/>}
  <Result color={C.blue} alpha={go(f,s1,25)}>等待不是读取结果</Result>
 </>}
 if(id===10){const change=go(f,35,45),confirmAt=Math.max(125,s1+45),release=go(f,confirmAt,35),done=f>=confirmAt;return <>
  <Txt>{done?'甲提交：确认修改，释放锁':'甲检查有货，再扣成 0'}</Txt>
  <Stock value={change===1?0:1} old={!done&&change===1?1:undefined} owner={done?(release===1?'':'释放中'):'甲持有 · 本次修改待确认'} color={done?C.teal:C.gold}/>
  <Request who="甲" x={365} color={C.gold} value={change===1?0:1} state={done?'提交成功 ✓':'1 − 1 = 0'}/>
  <Request who="乙" x={1555} state="仍在等待查询返回" alpha={.65}/>
  <Line x1={540} x2={785} p={change} color={C.gold}/><Carry value="−1" x1={540} x2={785} p={change}/>
  <Line x1={1380} x2={1210} p={1} alpha={1-release}/>{!done&&<Pulse f={f} x={1205} y={525}/>}
  <Result alpha={release}>确认库存 0 · 锁已释放</Result>
 </>}
 if(id===11){const travel=go(f,12,40),back=go(f,60,50),ready=back===1;return <>
  <Txt>乙继续：加锁读到新的库存</Txt><Stock value={0} color={C.blue} owner={travel===1?'乙持有 · 重新检查':''}/>
  <Request who="甲" x={365} color={C.gold} state="甲已结束事务" alpha={.3*(1-go(f,15,60))}/>
  <Request who="乙" x={1555} value={ready?0:undefined} state={ready?'这次读到 0':'查询继续执行'}/>
  <Line x1={1380} x2={1135} p={travel}/><Line x1={1135} x2={1380} p={back}/><Carry value="0" x1={1135} x2={1380} p={back} color={C.blue}/>
  <Result color={C.blue} alpha={go(f,s1,25)}>用新结果检查，不能沿用旧值 1</Result>
 </>}
 if(id===12){const check=go(f,20,40),settle=go(f,s1,40);return <>
  <Txt>库存已经是 0，程序停止扣减</Txt><Stock value={0} color={C.teal} owner={settle===1?'':'乙检查后结束事务'}/>
  <Request who="甲" x={365} color={C.teal} state="甲 · 购买通过 ✓" alpha={go(f,s1-25,35)}/>
  <Request who="乙" x={1555} color={C.red} value={0} state={check===1?'缺货 · 不再扣减':'检查库存'}/>
  <Txt x={1555} y={715} center size={31} color={C.red} alpha={check}>0 不大于 0</Txt>
  <Result alpha={settle}>1 件货 · 只通过 1 次购买</Result>
 </>}
 if(id===13){const a=go(f,12,30),b=go(f,65,35),c=go(f,125,35),end=go(f,s1+12,35);return <>
  <Txt>关键：先拿到新值，再作决定</Txt>
  {[{x:420,t:'加锁读取',p:a},{x:960,t:'检查与修改',p:b},{x:1500,t:'结束事务',p:c}].map(q=><div key={q.x} style={{opacity:q.p*(1-end),transform:`translateY(${25*(1-q.p)}px)`}}><Txt x={q.x} y={460} center size={48} color={C.teal}>{q.t}</Txt></div>)}
  <Line x1={610} x2={770} y={495} p={b} alpha={1-end} color={C.teal}/><Line x1={1180} x2={1310} y={495} p={c} alpha={1-end} color={C.teal}/>
  <Txt x={960} y={450} center size={64} color={C.gold} alpha={end}>等到了，也要重新检查</Txt>
  <Result color={C.muted} alpha={end}>锁协调访问 · 程序判断库存</Result>
 </>}
 const change=go(f,28,35),old=go(f,90,35),brand=go(f,d-55,25);return <>
  <Txt size={56}>下一期：刚改的昵称，怎么又变回去了？</Txt>
  <Txt x={960} y={350} center size={28} color={C.muted} alpha={1-brand}>昵称（示例）</Txt>
  <Txt x={960} y={430} center size={116} color={old===1?C.gold:C.teal} alpha={1-brand}>{change===1&&old<1?'青禾':'阿青'}</Txt>
  <Result color={C.muted} alpha={old*(1-brand)}>改好了 → 一刷新，又读到旧值？</Result>
  <Txt x={960} y={495} center size={68} alpha={brand}>IT小村 · 原创</Txt>
 </>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{
 const f=useCurrentFrame(),sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 78% 10%, #1A425E55, transparent 62%)'}}/>
  <Txt x={100} y={62} size={23} color={C.muted}>数据库 · EP.17</Txt><Txt x={1715} y={60} size={25}>IT小村</Txt>
  <Txt x={1715} y={106} size={18} color={C.muted} center>同一数据库 · 示例数据</Txt>
  <Scene shot={shot}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.35,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
