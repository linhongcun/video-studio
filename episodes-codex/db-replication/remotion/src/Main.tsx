import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,VIDEO,shots} from './data';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
const DatabaseMark=createDatabaseIdentity(React);
const DatabaseRole:React.FC<{children:React.ReactNode}>=({children})=><span style={{display:'inline-block',position:'relative'}}><DatabaseMark size={44} style={{position:'absolute',right:'calc(100% + 12px)',top:'50%',transform:'translateY(-50%)'}}/>{children}</span>;
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,a:number,n=35)=>{const p=clamp((f-a)/Math.max(1,n));return p*p*(3-2*p)};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const Text:React.FC<{children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;alpha?:number;center?:boolean}>=({children,x=130,y=180,size=48,color=C.text,alpha=1,center=false})=><div style={{position:'absolute',left:x,top:y,color,fontSize:size,fontWeight:600,whiteSpace:'nowrap',lineHeight:1.3,opacity:alpha,transform:center?'translateX(-50%)':undefined}}>{children}</div>;
const Data:React.FC<{role:string;value:string;x:number;y?:number;color?:string;alpha?:number;scale?:number;state?:string;old?:string}>=({role,value,x,y=500,color=C.text,alpha=1,scale=1,state='',old})=><div data-record={role} data-value={value} style={{position:'absolute',left:x-240,top:y-150,width:480,height:315,textAlign:'center',opacity:alpha,transform:`scale(${scale})`,transformOrigin:'center'}}>
 <div style={{fontSize:37,color,fontWeight:650}}>{role==='主库'||role==='从库'?<DatabaseRole>{role}</DatabaseRole>:role}</div><div style={{fontSize:22,color:C.muted,marginTop:13}}>用户 7042 · 昵称</div>
 <div style={{fontSize:96,fontWeight:700,lineHeight:1.3,color,marginTop:17}}>{value}</div>
 <div style={{margin:'12px 40px 0',height:2,background:color,opacity:.45}}/>
 {state&&<div style={{fontSize:25,color:state.includes('待')?C.gold:C.muted,marginTop:17}}>{state}</div>}
 {old&&<div style={{position:'absolute',left:0,right:0,top:-42,fontSize:24,color:C.muted}}>原确认：{old}</div>}
 </div>;
const Display:React.FC<{value?:string;alpha?:number;state?:string;color?:string;x?:number;y?:number;scale?:number}>=({value,alpha=1,state='',color=C.text,x=960,y=500,scale=1})=><div data-display={value} style={{position:'absolute',left:x-300,top:y-100,width:600,height:270,textAlign:'center',opacity:alpha,transform:`scale(${scale})`,transformOrigin:'center'}}>
 <div style={{fontSize:26,color:C.muted}}>当前显示 · 昵称</div><div style={{height:145,fontSize:112,fontWeight:750,color,marginTop:13}}>{value??'…'}</div><div style={{fontSize:27,color:state.includes('旧')?C.red:C.muted,marginTop:18}}>{state}</div>
 </div>;
const Route:React.FC<{x1:number;y1:number;x2:number;y2:number;p:number;color?:string;alpha?:number}>=({x1,y1,x2,y2,p,color=C.blue,alpha=1})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M${x1} ${y1}Q${(x1+x2)/2} ${(y1+y2)/2-55} ${x2} ${y2}`} pathLength="1" fill="none" stroke={color} strokeWidth="3" strokeDasharray="1" strokeDashoffset={1-clamp(p)}/></svg>;
const Move:React.FC<{text:string;x1:number;y1:number;x2:number;y2:number;p:number;color?:string;alpha?:number}>=({text,x1,y1,x2,y2,p,color=C.gold,alpha=1})=>p>0&&p<1?<Text x={mix(x1,x2,p)} y={mix(y1,y2,p)-55*Math.sin(Math.PI*p)} center size={43} color={color} alpha={alpha}><span data-moving-token style={{background:C.bg,padding:'2px 10px',borderRadius:6}}>{text}</span></Text>:null;
const Result:React.FC<{children:React.ReactNode;color?:string;alpha?:number;y?:number}>=({children,color=C.teal,alpha=1,y=790})=><Text x={960} y={y} center size={36} color={color} alpha={alpha}>{children}</Text>;
const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),d=s.durationInFrames,id=Number(s.id),s1=s.cueFrames?.sentences?.[1]??d*.5;
 if(id===1){const flip=go(f,s1-20,40);return <>
  <Text size={65}>刚改好的昵称，怎么又变回去了？</Text><Display value={flip===1?'阿青':'青禾'} color={flip===1?C.red:C.teal} state={flip===1?'刷新后：又是旧名字':'刚刚显示：保存成功'}/>
  <Route x1={1350} y1={540} x2={1190} y2={540} p={flip}/><Move text="刷新" x1={1450} y1={540} x2={1190} y2={540} p={flip} color={C.blue}/>
 </>}
 if(id===2){const want=go(f,s1-10,40);return <>
  <Text>同一个用户，同一条昵称记录</Text><Data role="本次教学记录" value="阿青" x={mix(960,650,want)}/><Text x={mix(1400,1280,want)} y={460} center size={90} color={C.gold} alpha={want}>青禾</Text><Text x={1280} y={610} center size={27} color={C.muted} alpha={want}>这次想改成</Text>
 </>}
 if(id===3){const at=s.cueFrames?.sourceLabel??1,p=go(f,15,55),request=go(f,s1+10,60);return <>
  {f>=at&&<Text size={58} color={C.teal}><DatabaseRole>主库</DatabaseRole></Text>}<Data role="接收本次修改" value="阿青" x={mix(960,470,p)} color={C.gold}/>
  <Route x1={1020} y1={560} x2={700} y2={510} p={request} color={C.gold}/><Move text="修改昵称" x1={1080} y1={560} x2={700} y2={510} p={request}/>
  <Result alpha={request}>本例：修改先到主库</Result>
 </>}
 if(id===4){const at=s.cueFrames?.replicaLabel??1,enter=go(f,10,45),copy=go(f,s1-20,60);return <>
  {f>=at&&<Text size={58} color={C.teal}>从库</Text>}<Data role="主库" value="阿青" x={470} color={C.gold} alpha={.6}/><Data role="从库" value={copy===1?'阿青':'…'} x={mix(1850,1450,enter)} color={C.blue} alpha={enter}/>
  <Route x1={710} y1={510} x2={1210} y2={510} p={copy} color={C.blue}/><Move text="阿青" x1={710} y1={510} x2={1210} y2={510} p={copy} color={C.blue}/>
  <Result color={C.blue} alpha={go(f,s1+50,30)}>可以把部分读取交给从库</Result>
 </>}
 if(id===5){const focus=go(f,0,35)*(1-go(f,d-40,35)),move=go(f,28,55),change=move===1,at=Math.min(d-45,s1+35),done=f>=at;return <>
  <Text>{done?'主库提交了这次修改':'把青禾写入主库'}</Text><Data role="主库" value={change?'青禾':'阿青'} x={mix(470,730,focus)} color={done?C.teal:C.gold} old={change&&!done?'阿青':undefined} state={done?'已提交':'本次修改 · 待确认'}/>
  <Data role="从库" value="阿青" x={mix(1450,1630,focus)} color={C.blue} alpha={.3} scale={.8}/>
  <Route x1={320} y1={720} x2={mix(470,730,focus)-210} y2={490} p={move} color={C.gold}/><Move text="青禾" x1={320} y1={720} x2={mix(470,730,focus)-210} y2={490} p={move}/>
  <Result alpha={done?1:0}>主库里的昵称已经更新</Result>
 </>}
 if(id===6){const ack=go(f,15,65),event=go(f,s1+25,100),lift=go(f,0,35);return <>
  <Text>保存成功，确认的是这次写入</Text><Data role="主库" value="青禾" x={470} y={mix(500,420,lift)} color={C.teal} scale={mix(1,.85,lift)}/><Data role="从库" value="阿青" x={1450} y={mix(500,420,lift)} color={C.blue} scale={mix(.8,.85,lift)} alpha={mix(.3,.45,lift)}/>
  <Display value={ack===1?'青禾':undefined} alpha={lift} y={720} scale={.72} color={C.teal} state={ack===1?'当前显示新名字':'等待保存结果'}/>
  <Route x1={600} y1={530} x2={800} y2={690} p={ack} color={C.teal}/><Move text="成功" x1={600} y1={530} x2={800} y2={690} p={ack} color={C.teal}/>
  <Route x1={700} y1={420} x2={1120} y2={420} p={event} color={C.gold} alpha={.5}/><Move text="更改" x1={700} y1={420} x2={1120} y2={420} p={event}/>
 </>}
 if(id===7){const ask=go(f,10,55),back=go(f,s1-10,60);return <>
  <Text>刷新，却读了尚未跟上的从库</Text><Data role="主库" value="青禾" x={470} y={420} color={C.teal} scale={.85} alpha={.35}/><Data role="从库" value="阿青" x={1450} y={420} color={C.blue} scale={.85}/>
  <Display value={back===1?'阿青':'青禾'} y={720} scale={.72} color={back===1?C.red:C.teal} state={back===1?'刷新读回旧名字':'这次从哪里读？'}/>
  <Route x1={1120} y1={730} x2={1340} y2={540} p={ask}/><Move text="查询" x1={1120} y1={730} x2={1340} y2={540} p={ask} color={C.blue}/>
  <Route x1={1340} y1={540} x2={1120} y2={730} p={back} color={C.red}/><Move text="阿青" x1={1340} y1={540} x2={1120} y2={730} p={back} color={C.red}/>
 </>}
 if(id===8){const focus=go(f,0,35),highlight=go(f,s1,35);return <>
  <Text>主库没有把这次修改撤销</Text><Data role="主库" value="青禾" x={mix(470,550,focus)} y={mix(420,500,focus)} color={C.teal} alpha={mix(.35,1,focus)} scale={mix(.85,1.12,focus)}/><Data role="从库" value="阿青" x={mix(1450,1370,focus)} y={mix(420,500,focus)} color={C.red} scale={mix(.85,1.12,focus)}/>
  <Result color={C.gold} alpha={highlight}>同一条记录 · 此时两边还不一样</Result>
 </>}
 if(id===9){const at=s.cueFrames?.delayLabel??1,travel=go(f,35,Math.min(170,d-60));return <>
  {f>=at&&<Text size={58} color={C.teal}>主从延迟</Text>}<Data role="主库" value="青禾" x={550} color={C.teal} scale={1.12}/><Data role="从库" value="阿青" x={1370} color={C.red} scale={1.12}/>
  <Route x1={780} y1={500} x2={1160} y2={500} p={travel} color={C.gold}/><Move text="更改" x1={780} y1={500} x2={1160} y2={500} p={travel}/>
  <Text x={1080} y={685} center size={28} color={C.gold} alpha={go(f,s1,30)}>更改还没有应用完成</Text>
 </>}
 if(id===10){const receive=go(f,10,50),applyAt=Math.min(d-45,s1+35),applied=f>=applyAt;return <>
  <Text>{applied?'应用完成，从库才更新':'接收更改，还要应用更改'}</Text><Data role="主库" value="青禾" x={550} color={C.teal} scale={1.12} alpha={.6}/><Data role="从库" value={applied?'青禾':'阿青'} x={1370} color={applied?C.teal:C.blue} scale={1.12} state={applied?'本次更改已应用':receive===1?'已接收 · 待应用':'正在接收'}/>
  <Route x1={1160} y1={500} x2={1200} y2={500} p={receive} color={C.gold}/><Move text="青禾" x1={1160} y1={500} x2={1200} y2={500} p={receive}/>
  {!applied&&receive===1&&<Text x={1370} y={735} center size={28} color={C.gold}>待应用：青禾</Text>}
 </>}
 if(id===11){const back=go(f,30,65),shrink=go(f,s1-10,40);return <>
  <Text>这次从已经跟上的从库读</Text><Data role="主库" value="青禾" x={550} y={mix(500,420,shrink)} color={C.teal} scale={mix(1.12,.75,shrink)} alpha={.6*(1-.8*shrink)}/><Data role="从库" value="青禾" x={1370} y={mix(500,420,shrink)} color={C.teal} scale={mix(1.12,.85,shrink)}/>
  <Display value={back===1?'青禾':undefined} y={720} scale={.72} color={C.teal} alpha={go(f,10,25)} state={back===1?'这次读到新名字':'读取中'}/>
  <Route x1={1130} y1={570} x2={1120} y2={730} p={back} color={C.teal}/><Move text="青禾" x1={1130} y1={570} x2={1120} y2={730} p={back} color={C.teal}/>
 </>}
 if(id===12){const ask=go(f,18,50),back=go(f,85,55),hint=go(f,s1+10,30);return <>
  <Text>刚改后，要立刻核对：新查询定向主库</Text><Data role="主库" value="青禾" x={470} y={420} color={C.teal} scale={.85}/><Data role="从库" value="阿青" x={1450} y={420} color={C.blue} scale={.85} alpha={.3}/>
  <Display value={back===1?'青禾':undefined} y={720} scale={.72} color={C.teal} state={back===1?'本次读取拿到新名字':'另一个示例 · 重新读取'}/>
  <Route x1={800} y1={690} x2={580} y2={540} p={ask}/><Move text="新查询" x1={800} y1={690} x2={580} y2={540} p={ask} color={C.blue}/>
  <Route x1={580} y1={540} x2={800} y2={690} p={back} color={C.teal}/><Move text="青禾" x1={580} y1={540} x2={800} y2={690} p={back} color={C.teal}/>
  <Text x={960} y={280} center size={27} color={C.muted} alpha={hint}>本例：主库已提交 · 新查询 · 无旧缓存</Text>
 </>}
 if(id===13){const first=go(f,15,45),second=go(f,s1,40),out=1-go(f,d-30,25);return <>
  <Text>先分清写到哪里，再决定从哪里读</Text>
  <Text x={960} y={400} center size={60} color={C.gold} alpha={first*out}>修改 → 主库</Text>
  <Text x={960} y={520} center size={52} color={C.teal} alpha={first*out}>刚改后的新查询 → 同一主库</Text>
  <Text x={960} y={720} center size={33} color={C.blue} alpha={second*out}>普通读取，可按需求分给从库</Text>
 </>}
 const row=go(f,20,40),grow=go(f,65,75),brand=go(f,d-55,25);return <>
  <Text size={55}>下一期：订单太多，一个数据库装不下怎么办？</Text>
  <div style={{opacity:1-brand}}>{[0,1,2,3].map(i=><div key={i} style={{position:'absolute',left:600,top:340+i*100,width:720,height:70,borderBottom:`2px solid ${C.edge}`,opacity:go(f,20+i*25,30),transform:`translateY(${(1-row)*35}px)`}}><span style={{fontSize:33,color:C.muted}}>订单 {7042+i}</span><span style={{fontSize:32,color:C.teal,float:'right'}}>新增记录</span></div>)}</div>
  <Text x={960} y={790} center size={33} color={C.gold} alpha={grow*(1-brand)}>记录越来越多</Text><Text x={960} y={500} center size={68} alpha={brand}>IT小村 · 原创</Text>
 </>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{const f=useCurrentFrame(),sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 10%, #194B6550, transparent 63%)'}}/>
 <Text x={100} y={62} size={23} color={C.muted}>数据库 · EP.18</Text><Text x={1715} y={60} size={25}>IT小村</Text><Text x={1690} y={106} center size={18} color={C.muted}>同一条昵称记录 · 示例数据</Text>
 <Scene shot={shot}/>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.3,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
