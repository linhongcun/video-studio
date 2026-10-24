import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,shots} from './data';
declare const __HAS_VOICE_AUDIO__:boolean;
const cap=(n:number)=>Math.max(0,Math.min(1,n));
const ease=(f:number,start:number,len=35)=>{const t=cap((f-start)/len);return t*t*(3-2*t)};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const Text:React.FC<{children:React.ReactNode;x?:number;y?:number;w?:number;size?:number;color?:string;alpha?:number;center?:boolean}>=({children,x=130,y=180,w=1660,size=58,color=C.text,alpha=1,center=false})=><div ref={e=>{if(e&&e.scrollWidth>e.clientWidth+2)console.error('COPYFIT overflow',String(children));}} style={{position:'absolute',left:center?x-w/2:x,top:y,width:w,fontSize:size,color,opacity:alpha,lineHeight:1.35,fontWeight:600,textAlign:center?'center':'left',whiteSpace:'nowrap'}}>{children}</div>;
const ImageTile:React.FC<{x:number;y:number;scale?:number;alpha?:number;progress?:number;label?:string}>=({x,y,scale=1,alpha=1,progress=1,label=''})=><div style={{position:'absolute',left:x-125,top:y-85,width:250,height:170,transform:`scale(${scale})`,transformOrigin:'center',opacity:alpha}}>
 <div style={{position:'absolute',inset:0,borderRadius:14,background:C.surface,border:`2px solid ${C.teal}`,overflow:'hidden'}}>
  <svg width={250} height={170} style={{clipPath:`inset(${100-cap(progress)*100}% 0 0 0)`}}><rect width={250} height={170} fill="#164153"/><circle cx={185} cy={42} r={22} fill={C.gold}/><path d="M0 170 L70 68 L150 170 Z" fill="#2B8D94"/><path d="M70 170 L163 84 L250 170 Z" fill={C.teal}/></svg>
 </div>{label&&<div style={{position:'absolute',left:-120,right:-120,top:190,textAlign:'center',fontSize:26,color:C.muted}}>{label}</div>}
</div>;
const Link:React.FC<{x1:number;y1:number;x2:number;y2:number;color?:string;alpha?:number;p?:number}>=({x1,y1,x2,y2,color=C.edge,alpha=1,p=1})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,opacity:alpha}}><path d={`M${x1} ${y1} L${x2} ${y2}`} stroke={color} strokeWidth={3} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1-cap(p)}/></svg>;
const Moving:React.FC<{f:number;start:number;x1:number;y1:number;x2:number;y2:number;label?:string;color?:string;len?:number}>=({f,start,x1,y1,x2,y2,label='图片',color=C.teal,len=55})=>{const p=ease(f,start,len);return p>0&&p<1?<div style={{position:'absolute',left:mix(x1,x2,p)-50,top:mix(y1,y2,p)-25,width:100,height:50,borderRadius:12,background:color,color:C.bg,display:'flex',alignItems:'center',justifyContent:'center',fontSize:25,fontWeight:800}}>{label}</div>:null};
const Endpoint:React.FC<{x:number;y:number;title:string;detail?:string;color?:string;alpha?:number}>=({x,y,title,detail='',color=C.blue,alpha=1})=><div style={{position:'absolute',left:x-185,top:y-70,width:370,height:140,border:`2px solid ${color}`,borderRadius:20,background:C.surface,opacity:alpha,textAlign:'center'}}><div style={{fontSize:42,fontWeight:650,color,marginTop:19}}>{title}</div><div style={{fontSize:24,color:C.muted,marginTop:6}}>{detail}</div></div>;
const BrowserArea:React.FC<{cache?:boolean;image?:boolean;networkAlpha?:number}>=({cache=false,image=false,networkAlpha=1})=><>
 <div style={{position:'absolute',left:130,top:335,width:1050,height:445,borderRadius:24,border:`2px solid ${C.edge}`}}/>
 <Text x={175} y={353} size={29} color={C.muted}>浏览器内部</Text>
 <Text x={420} y={430} center w={400} size={34}>页面里的图片</Text>
 <ImageTile x={420} y={600} alpha={image?1:.16}/>
 {cache&&<><Text x={930} y={430} center w={400} size={34} color={C.teal}>本地副本</Text><ImageTile x={930} y={600} scale={.8}/></>}
 <Link x1={1185} y1={540} x2={1395} y2={540} alpha={networkAlpha}/><Endpoint x={1590} y={540} title="网站" detail="同一张图片" alpha={networkAlpha}/>
</>;
const Scene:React.FC<{shot:Shot}>=({shot:s})=>{const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,s1=s.cueFrames?.sentences?.[1]??d/2;
 const result=(t:string,a=1,color=C.teal)=><Text x={960} y={820} center size={36} color={color} alpha={a}>{t}</Text>;
 if(id===1){const first=ease(f,15,100),second=ease(f,38,18);return <><Text size={60}>同一个网页，第二次打开为什么快这么多？</Text>
  <ImageTile x={580} y={550} scale={1.6} progress={first}/><ImageTile x={1360} y={550} scale={1.6} progress={second}/>
  <Text x={580} y={340} center w={600} size={42} color={C.gold}>第一次</Text><Text x={1360} y={340} center w={600} size={42} color={C.teal}>第二次</Text>
  {result('还是这张图片，等待却少了',second)}
 </>}
 if(id===2){const focus=ease(f,25,45);return <><Text>先只追踪页面里的同一张图片</Text>
  <div style={{position:'absolute',left:300,top:340,width:1320,height:410,border:`2px solid ${C.edge}`,borderRadius:20,opacity:1-focus*.5}}/>
  {[0,1,2].map(i=><div key={i} style={{position:'absolute',left:380,top:400+i*90,width:520-i*70,height:15,background:C.edge,opacity:1-focus*.8}}/>)}
  <ImageTile x={mix(1300,960,focus)} y={540} scale={mix(1,1.6,focus)} label="同一个图片资源"/>
  {result('整页还可能有其他独立请求',ease(f,s1,30),C.muted)}
 </>}
 if(id===3){const request=ease(f,25,45),download=ease(f,s1+5,80);return <><Text>第一次：本地没有可用副本</Text><BrowserArea/>
  <Link x1={1185} y1={540} x2={1395} y2={540} color={C.gold} p={request}/><Moving f={f} start={25} x1={1185} y1={540} x2={1395} y2={540} label="请求" color={C.gold} len={45}/>
  <Link x1={1395} y1={600} x2={560} y2={600} color={C.teal} p={download}/><Moving f={f} start={s1+5} x1={1395} y1={600} x2={560} y2={600} len={80}/><ImageTile x={420} y={600} progress={download} alpha={download}/>
  {result('图片内容从网站传回来',download===1?1:.3)}
 </>}
 if(id===4){const save=ease(f,s1+5,65);return <>
  {f>=(s.cueFrames?.cacheLabel??1)&&<Text color={C.teal}>浏览器缓存</Text>}
  <BrowserArea image/>
  <ImageTile x={930} y={600} scale={.8} alpha={save}/><Text x={930} y={430} center w={400} size={34} color={C.teal} alpha={save}>本地副本</Text>
  <Moving f={f} start={s1+5} x1={560} y1={600} x2={805} y2={600} len={65}/>
  <Text x={930} y={715} center w={420} size={26} color={C.gold} alpha={save}>连同缓存规则一起保存</Text>
  {result('允许存储，才保存相应响应',ease(f,35,35),C.muted)}
 </>}
 if(id===5||id===6||id===9){const expiry=id===9,age=expiry?61:id===6?20:0,progress=ease(f,20,70),shown=Math.round(expiry?mix(20,61,progress):age*progress),isStale=expiry&&shown>=60;return <>
  <Text>{id===5?'示例规则：允许 60 秒内直接复用':expiry?(isStale?'示例期限已到，需要联系网站':'时间快进：20 秒 → 61 秒'):'时间快进：20 秒后再次需要它'}</Text>
  <ImageTile x={470} y={520} scale={1.25}/>
  <Text x={470} y={735} center w={550} size={30} color={C.teal}>同一份本地图片</Text>
  <Text x={1230} y={380} center w={850} size={34} color={C.muted}>教学设置 · 有效期 60 秒</Text>
  <div style={{position:'absolute',left:840,top:520,width:720,height:14,borderRadius:7,background:C.edge}}><div style={{height:14,width:Math.min(1,shown/60)*720,borderRadius:7,background:isStale?C.gold:C.teal}}/></div>
  <div style={{position:'absolute',left:840+Math.min(1.03,shown/60)*720-4,top:493,width:8,height:68,background:isStale?C.gold:C.teal}}/>
  <Text x={840} y={575} w={250} size={29} color={C.muted}>0 秒</Text><Text x={1560} y={575} center w={250} size={29} color={C.muted}>60 秒</Text>
  {id!==5&&<Text x={1230} y={665} center w={800} size={46} color={isStale?C.gold:C.teal}>{Math.round(shown)} 秒 · {isStale?'不能按原期限直接用':'仍在示例有效期内'}</Text>}
  {id===5?result('期限由网站规则等条件决定，不是统一的 60 秒',ease(f,s1,30),C.muted):expiry?result('通常需要联系网站确认或更新',isStale?ease(f,s1,30):0,C.gold):result('请求匹配、规则允许，才能直接复用',ease(f,s1,30))}
 </>}
 if(id===7){const p=ease(f,20,70);return <><Text>这次，图片直接从本地进入页面</Text><BrowserArea cache networkAlpha={.25}/>
  <Link x1={805} y1={600} x2={560} y2={600} color={C.teal} p={p}/><Moving f={f} start={20} x1={805} y1={600} x2={560} y2={600} len={70}/><ImageTile x={420} y={600} alpha={p===1?1:0}/>
  <Text x={1495} y={670} center w={600} size={29} color={C.muted} alpha={ease(f,s1,30)}>这张图片没有发出网络请求</Text>
  {result('短路径：本地副本 → 页面',p===1?1:0)}
 </>}
 if(id===8){const other=ease(f,s1+12,65);return <><Text>少等一次请求，少传一次图片内容</Text><BrowserArea cache image networkAlpha={.55}/>
  <Link x1={805} y1={600} x2={560} y2={600} color={C.teal}/>
  <Text x={960} y={810} center size={34} color={C.teal}>本地复用的是这张图片</Text>
  <Moving f={f} start={s1+12} x1={1185} y1={420} x2={1395} y2={420} label="其他资源" color={C.blue} len={65}/>
  <Text x={1450} y={340} center w={600} size={29} color={C.blue} alpha={other}>其他资源仍可能联网</Text>
 </>}
 const brand=ease(f,d-55,35);return <>
  <div style={{opacity:1-brand}}><Text>是否更快，取决于能不能复用</Text><BrowserArea cache image networkAlpha={.2}/>
   <Link x1={805} y1={600} x2={560} y2={600} color={C.teal} p={ease(f,s1,50)}/><Moving f={f} start={s1} x1={805} y1={600} x2={560} y2={600} len={50}/>
   {result('副本仍在 + 请求匹配 + 规则允许',ease(f,25,35))}</div>
  <Text x={960} y={470} center size={72} alpha={brand}>IT小村 · 原创</Text>
 </>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const View:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{const f=useCurrentFrame(),sub=shot.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 10%,#1A425E44,transparent 65%)'}}/>
 <Text x={100} y={62} size={23} color={C.muted}>浏览器与网络 · EP.07</Text><Text x={1715} y={60} w={180} size={25}>IT小村</Text>
 <Scene shot={shot}/><Text x={130} y={880} size={19} color={C.muted}>同一张图片的过程示意 · 时间与规则均为教学示例</Text>
 {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',justifyContent:'center',alignItems:'center',textAlign:'center',fontSize:38,lineHeight:1.35,background:C.bg+'F7'}}>{sub.text}</div>}
 </AbsoluteFill>};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><View shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
