import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,shots} from './data';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
const DatabaseMark=createDatabaseIdentity(React);
declare const __HAS_VOICE_AUDIO__:boolean;
const cap=(n:number)=>Math.max(0,Math.min(1,n));
const ease=(f:number,start:number,len=32)=>{const t=cap((f-start)/len);return t*t*(3-2*t)};
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
const Text:React.FC<{children:React.ReactNode;x?:number;y?:number;w?:number;size?:number;color?:string;alpha?:number;center?:boolean}>=({children,x=130,y=180,w=1660,size=58,color=C.text,alpha=1,center=false})=><div ref={e=>{if(e&&e.scrollWidth>e.clientWidth+2)console.error('COPYFIT overflow',String(children));}} style={{position:'absolute',left:center?x-w/2:x,top:y,width:w,fontSize:size,lineHeight:1.35,fontWeight:600,color,opacity:alpha,textAlign:center?'center':'left',whiteSpace:'nowrap'}}>{children}</div>;
const Node:React.FC<{label:string;detail?:string;x:number;y:number;color?:string;alpha?:number;progress?:number;database?:boolean}>=({label,detail='',x,y,color=C.blue,alpha=1,progress,database=false})=><div style={{position:'absolute',left:x-165,top:y-65,width:330,height:130,border:`2px solid ${color}`,borderRadius:20,background:C.surface,opacity:alpha,textAlign:'center'}}>
 <div style={{fontSize:40,fontWeight:650,marginTop:15,color}}>{database?<span style={{display:'inline-flex',alignItems:'center',gap:8}}><DatabaseMark size={44}/><span>{label}</span></span>:label}</div><div style={{fontSize:23,color:C.muted,marginTop:5}}>{detail}</div>
 {progress!==undefined&&<div style={{position:'absolute',left:15,right:15,bottom:9,height:4,background:C.edge}}><div style={{width:cap(progress)*100+'%',height:4,background:color}}/></div>}
</div>;
const Link:React.FC<{x1:number;y1:number;x2:number;y2:number;color?:string;p?:number;alpha?:number;dashed?:boolean}>=({x1,y1,x2,y2,color=C.edge,p=1,alpha=1,dashed=false})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,opacity:alpha}}><path d={`M${x1} ${y1} L${x2} ${y2}`} pathLength={1} stroke={color} strokeWidth={3} fill="none" strokeDasharray={dashed?'.025 .02':'1'} strokeDashoffset={dashed?0:1-cap(p)}/></svg>;
const Packet:React.FC<{label:string;x1:number;y1:number;x2:number;y2:number;p:number;color?:string;hold?:boolean}>=({label,x1,y1,x2,y2,p,color=C.gold,hold=false})=>p>0&&(p<1||hold)?<div style={{position:'absolute',left:lerp(x1,x2,cap(p))-43,top:lerp(y1,y2,cap(p))-25,width:86,height:50,borderRadius:14,background:color,color:C.bg,display:'flex',justifyContent:'center',alignItems:'center',fontWeight:800,fontSize:25,boxShadow:`0 0 24px ${color}33`}}>{label}</div>:null;
const appY=[345,535,725];
const Layout:React.FC<{bad?:boolean;failing?:boolean;recovered?:boolean;alpha?:number}>=({bad=false,failing=false,recovered=false,alpha=1})=><div style={{opacity:alpha}}>
 <Link x1={465} y1={535} x2={685} y2={535}/>
 {appY.map((y,i)=><Link key={y} x1={1015} y1={535} x2={1315} y2={y} color={bad&&i===1?C.red:C.edge} dashed={bad&&i===1}/>)}
 <Node label="浏览器请求" detail="同一个访问入口" x={300} y={535}/><Node label="分配入口" detail="每次选择一个实例" x={850} y={535} color={C.teal}/>
 {appY.map((y,i)=><Node key={y} label={'应用'+['甲','乙','丙'][i]} detail={bad&&i===1?'暂停接收新请求':failing&&i===1?'没有回应':recovered&&i===1?'已恢复 · 同一套程序':'同一套程序'} x={1480} y={y} color={(bad||failing)&&i===1?C.red:recovered&&i===1?C.teal:C.blue} alpha={bad&&i===1?.5:1}/>) }
</div>;
const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,s1=s.cueFrames?.sentences?.[1]??d/2;
 const finish=(txt:string,a=1,color=C.teal)=><Text x={960} y={820} center w={1660} size={33} color={color} alpha={a}>{txt}</Text>;
 if(id===1){return <>
  <Text size={64}>一台服务器忙不过来，怎么办？</Text>
  <Link x1={430} y1={535} x2={1280} y2={535}/><Node label="应用甲" detail="正在处理请求 0" x={1480} y={535} progress={.15+.6*ease(f,0,d-1)}/>
  {[0,1,2,3,4].map((i)=><Packet key={i} label={String(i+1)} x1={330-i*40} y1={535} x2={1195-i*108} y2={535} p={ease(f,12+i*26,70)} hold color={i>1?C.gold:C.blue}/>)}
  <Text x={1450} y={665} center w={530} size={30} color={C.gold}>仍在处理</Text>
  {finish('新的请求继续到达，等待变长',ease(f,s1,30),C.gold)}
 </>}
 if(id===2){const next=ease(f,60,45),shift=ease(f,110,50);return <>
  <Text size={64}>请求来了，程序还没处理完</Text>
  <Link x1={430} y1={535} x2={1315} y2={535}/>
  <Node label="应用甲" detail={next===1?'正在处理请求 1':f>=57?'刚完成请求 0':'正在处理请求 0'} x={1480} y={535} progress={next===1?.1+.7*ease(f,110,110):.75+.25*ease(f,12,45)}/>
  {next===0?<Packet label="1" x1={1195} y1={535} x2={1195} y2={535} p={1} hold color={C.blue}/>:<Packet label="1" x1={1195} y1={535} x2={1315} y2={535} p={next} color={C.blue}/>}
  {[1,2,3,4].map(i=>{const x=lerp(1195-i*108,1195-(i-1)*108,shift);return <Packet key={i} label={String(i+1)} x1={x} y1={535} x2={x} y2={535} p={1} hold color={i===1?C.blue:C.gold}/>})}
  {[6,7].map((n,i)=><Packet key={n} label={String(n)} x1={330-i*40} y1={535} x2={763-i*108} y2={535} p={ease(f,120+i*36,60)} hold/>)}
  <Text x={1450} y={665} center w={530} size={30} color={C.gold}>{next===1?'下一个开始处理':'依次处理'}</Text>
  {finish('处理完一个，再接下一个；新的请求仍在增加',ease(f,s1+20,30),C.gold)}
 </>}
 if(id===3){const settle=ease(f,15,55);return <><Text>增加实例，运行同样的程序</Text>
  <Node label="应用甲" detail="同一套网站程序" x={1480} y={lerp(535,345,settle)} color={C.blue}/>
  <Node label="应用乙" detail="同一套网站程序" x={1480} y={535} color={C.blue} alpha={ease(f,70,38)}/>
  <Node label="应用丙" detail="同一套网站程序" x={1480} y={725} color={C.blue} alpha={ease(f,115,38)}/>
  <Text x={690} y={480} center w={950} size={44} color={C.gold} alpha={ease(f,s1,30)}>每个请求，应该交给谁？</Text>
 </>}
 if(id===4){const enter=ease(f,25,42),send=ease(f,s1+15,52);return <>
  {f>=(s.cueFrames?.balanceLabel??1)&&<Text color={C.teal}>负载均衡</Text>}
  <Layout/><Link x1={465} y1={535} x2={685} y2={535} color={C.gold} p={enter}/><Packet label="请求" x1={465} y1={535} x2={685} y2={535} p={enter}/>
  <Link x1={1015} y1={535} x2={1315} y2={345} color={C.gold} p={send}/><Packet label="请求" x1={1015} y1={535} x2={1315} y2={345} p={send}/>
  {finish('入口接住请求，再选一个实例',ease(f,s1+72,30))}
 </>}
 if(id===5){const start=Math.max(35,s1);return <><Text>轮流分配：同一请求只交给一个实例</Text><Layout/>
  {appY.map((y,i)=>{const p=ease(f,start+i*48,42);return <React.Fragment key={i}><Link x1={1015} y1={535} x2={1315} y2={y} color={[C.gold,C.blue,C.teal][i]} p={p}/><Packet label={String(i+1)} x1={1015} y1={535} x2={1315} y2={y} p={p} color={[C.gold,C.blue,C.teal][i]}/><Text x={1760} y={y-24} center w={140} size={34} color={[C.gold,C.blue,C.teal][i]} alpha={p===1?1:0}>收到 {i+1}</Text></React.Fragment>})}
  {finish('轮流分配是本例规则，实际还可以按权重、连接数等选择',ease(f,start+155,22),C.muted)}
 </>}
 if(id===6){const process=ease(f,18,55),back=ease(f,s1+5,52),last=ease(f,s1+60,42);return <><Text>处理完成，结果回到对应的浏览器</Text><Layout alpha={.75}/>
  <Node label="应用丙" detail={process===1?'请求 3 已完成':'正在处理请求 3'} x={1480} y={725} color={C.teal} progress={process}/>
  <Link x1={1315} y1={725} x2={1015} y2={535} color={C.teal} p={back}/><Packet label="结果3" x1={1315} y1={725} x2={1015} y2={535} p={back} color={C.teal}/>
  <Link x1={685} y1={535} x2={465} y2={535} color={C.teal} p={last}/><Packet label="结果3" x1={685} y1={535} x2={465} y2={535} p={last} color={C.teal}/>
  {finish('请求与结果一一对应',last===1?1:0)}
 </>}
 if(id===7){const fail=ease(f,15,35),req=ease(f,s1,60);return <><Text>乙不回应，分过去的请求也会等待</Text><Layout failing={fail===1}/>
  <Link x1={1015} y1={535} x2={1280} y2={535} color={C.red} p={req}/><Packet label="请求4" x1={1015} y1={535} x2={1250} y2={535} p={req} color={C.red} hold/>
  <Text x={1480} y={635} center w={400} size={30} color={C.red} alpha={req}>没有成功响应</Text>
  {finish('实例数量变多，也需要识别故障',ease(f,s1+75,22),C.red)}
 </>}
 if(id===8){const a=ease(f,s1+5,35),b=ease(f,s1+67,35),n=b===1?2:a===1?1:0;return <>
  {f>=(s.cueFrames?.healthLabel??1)&&<Text color={C.teal}>健康检查</Text>}<Layout failing bad={n===2}/>
  <Link x1={1015} y1={535} x2={1315} y2={535} color={C.red} dashed/>
  <Packet label="探测1" x1={1015} y1={535} x2={1315} y2={535} p={a} color={C.gold}/><Packet label="探测2" x1={1015} y1={535} x2={1315} y2={535} p={b} color={C.gold}/>
  <Text x={1750} y={515} center w={260} size={28} color={C.red}>失败 {n} / 2</Text>
  {finish('示例配置：连续 2 次失败，暂停接收新请求',b===1?1:.6,C.gold)}
 </>}
 if(id===9){return <><Text>暂停乙，新请求改选甲或丙</Text><Layout bad/>
  {[0,2].map((i,k)=>{const p=ease(f,25+k*68,50);return <React.Fragment key={i}><Link x1={1015} y1={535} x2={1315} y2={appY[i]} color={C.teal} p={p}/><Packet label={'新'+(k+1)} x1={1015} y1={535} x2={1315} y2={appY[i]} p={p} color={C.teal}/></React.Fragment>})}
  {finish('此前失败的请求，不会因此自动成功',ease(f,s1,28),C.gold)}
 </>}
 if(id===10){const a=ease(f,25,35),b=ease(f,85,35),ready=b===1,req=ease(f,Math.max(135,s1+20),50);return <><Text>先确认恢复，再接收新的请求</Text><Layout bad={!ready} recovered={ready}/>
  <Packet label="检查1" x1={1015} y1={535} x2={1315} y2={535} p={a} color={C.teal}/><Packet label="检查2" x1={1015} y1={535} x2={1315} y2={535} p={b} color={C.teal}/>
  <Text x={1750} y={515} center w={260} size={28} color={C.teal}>通过 {ready?2:a===1?1:0} / 2</Text>
  {ready&&<><Link x1={1015} y1={535} x2={1315} y2={535} color={C.gold} p={req}/><Packet label="新请求" x1={1015} y1={535} x2={1315} y2={535} p={req} color={C.gold}/></>}
  {finish('示例配置：连续 2 次成功后恢复分配',ready?1:.4)}
 </>}
 if(id===11){const focus=ease(f,s1-5,45);return <><Text>实例增加，性能不一定按倍数增加</Text>
  {[0,1,2].map((i)=><React.Fragment key={i}><Node label={'应用'+['甲','乙','丙'][i]} detail="同一套网站程序" x={450} y={345+i*185} alpha={1-focus*.4}/><Link x1={615} y1={345+i*185} x2={1220} y2={530} color={C.gold} p={focus}/><Packet label="查询" x1={615} y1={345+i*185} x2={1120-i*95} y2={530} p={ease(f,s1+10+i*20,45)} hold/></React.Fragment>)}
  <Node label="同一个数据库" detail="仍可能成为瓶颈" x={1440} y={530} color={C.gold} alpha={focus} database/>
  {finish('处理能力取决于整条链路，不承诺快 3 倍',focus,C.gold)}
 </>}
 const a=ease(f,20,45),b=ease(f,70,45),c=ease(f,125,45),end=ease(f,d-55,35);return <>
  <div style={{opacity:1-end}}><Text>更多实例，加上清楚的分配规则</Text><Layout recovered/>
   <Packet label="请求" x1={465} y1={535} x2={685} y2={535} p={a}/><Packet label="请求" x1={1015} y1={535} x2={1315} y2={345} p={b}/><Packet label="结果" x1={1315} y1={345} x2={465} y2={535} p={c} color={C.teal}/>
   {finish('增加实例 → 分配请求 → 避开故障',ease(f,s1,30))}</div>
  <Text x={960} y={470} center size={72} alpha={end}>IT小村 · 原创</Text>
 </>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const View:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{const f=useCurrentFrame(),sub=shot.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 10%,#1A425E44,transparent 65%)'}}/>
 <Text x={100} y={62} size={23} color={C.muted}>浏览器与网络 · EP.06</Text><Text x={1715} y={60} w={180} size={25}>IT小村</Text>
 <Scene shot={shot}/><Text x={130} y={880} size={19} color={C.muted}>抽象过程示意 · 路径、数量与配置均为教学示例</Text>
 {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',justifyContent:'center',alignItems:'center',textAlign:'center',fontSize:38,lineHeight:1.35,background:C.bg+'F7'}}>{sub.text}</div>}
 </AbsoluteFill>};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><View shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
