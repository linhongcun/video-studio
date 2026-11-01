import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C} from './theme';
import {LAND_PATHS} from './landPaths';
import {Picture} from './Picture';

const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,a:number,n=42)=>{const t=clamp((f-a)/n);return t*t*(3-2*t)};
type Point={x:number;y:number};
const geo=(lon:number,lat:number):Point=>({x:210+((lon<55?lon+360:lon)-55)*7.5,y:290+(75-lat)*7.5});
// Fictional teaching locations, not a vendor's actual topology or measured route.
const user=geo(113,24),edge=geo(132,35),origin=geo(-125,38);
const imageAt=(p:Point):Point=>({x:p.x,y:p.y-90});
const otherEdges=[geo(104,2),geo(-155,21),geo(75,44)];
const Text:React.FC<{children:React.ReactNode;x:number;y:number;size?:number;color?:string;alpha?:number;center?:boolean}>=({children,x,y,size=30,color=C.text,alpha=1,center=false})=><div data-fit style={{position:'absolute',left:x,top:y,fontSize:size,fontWeight:650,lineHeight:1.4,color,opacity:alpha,zIndex:3,whiteSpace:'nowrap',transform:center?'translateX(-50%)':undefined}}>{children}</div>;
const Land:React.FC=()=><svg width="1920" height="1080" style={{position:'absolute',inset:0,zIndex:0}} aria-label="Natural Earth真实大陆轮廓，太平洋区域等距经纬投影">
 <defs><clipPath id="land-viewport"><rect x="130" y="315" width="1660" height="565" rx="20"/></clipPath></defs>
 <g clipPath="url(#land-viewport)"><rect x="130" y="315" width="1660" height="565" fill="#10273B"/>
 {[0,20,40,60].map(lat=><path key={'lat'+lat} d={`M130 ${geo(55,lat).y}H1790`} stroke="#326077" strokeOpacity=".13" fill="none"/>)}
 {[60,90,120,150,180,210,240].map(lon=><path key={'lon'+lon} d={`M${geo(lon,0).x} 315V880`} stroke="#326077" strokeOpacity=".13" fill="none"/>)}
 {LAND_PATHS.map((d,i)=><path key={i} d={d} fill="#263E50" stroke="#426073" strokeWidth="1.2" fillRule="evenodd"/>)}
 </g>
</svg>;
type Route='local-request'|'origin-request'|'origin-return'|'local-return';
const route=(name:Route):[Point,Point,Point,Point]=>{
 if(name==='local-request')return [user,{x:user.x+70,y:user.y+10},{x:edge.x-50,y:edge.y+50},edge];
 if(name==='origin-request')return [edge,{x:1040,y:390},{x:1330,y:390},origin];
 if(name==='origin-return')return [imageAt(origin),{x:1330,y:640},{x:1050,y:640},imageAt(edge)];
 return [imageAt(edge),{x:edge.x-30,y:edge.y-30},{x:user.x+40,y:user.y-10},imageAt(user)];
};
const point=(r:[Point,Point,Point,Point],t:number):Point=>{const q=1-t;return {x:q*q*q*r[0].x+3*q*q*t*r[1].x+3*q*t*t*r[2].x+t*t*t*r[3].x,y:q*q*q*r[0].y+3*q*q*t*r[1].y+3*q*t*t*r[2].y+t*t*t*r[3].y}};
const Path:React.FC<{name:Route;p:number;color?:string;image?:boolean;alpha?:number;history?:boolean}>=({name,p,color=C.blue,image=false,alpha=1,history=false})=>{
 const r=route(name),t=clamp(p),v=point(r,t),d=`M${r[0].x} ${r[0].y}C${r[1].x} ${r[1].y},${r[2].x} ${r[2].y},${r[3].x} ${r[3].y}`;
 return <><svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:alpha,zIndex:1,pointerEvents:'none'}}><path d={d} pathLength="1" fill="none" stroke={color} strokeWidth={history?2:4} strokeDasharray={history?'.014 .016':'1'} strokeDashoffset={history?0:1-t}/>{!image&&t>0&&t<1&&<circle cx={v.x} cy={v.y} r="9" fill={color}/>}</svg>{image&&t>0&&t<1&&<div style={{position:'absolute',inset:0,zIndex:2}}><Picture x={v.x} y={v.y} w={128} alpha={alpha}/></div>}</>;
};
const Marker:React.FC<{p:Point;active?:boolean;alpha?:number;who?:boolean}>=({p,active=false,alpha=1,who=false})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:alpha,zIndex:2,pointerEvents:'none'}}>
 {active&&<circle cx={p.x} cy={p.y} r="22" fill={C.teal} fillOpacity=".12" stroke={C.teal} strokeWidth="2"/>}
 {who?<g fill={C.text}><circle cx={p.x} cy={p.y-5} r="7"/><path d={`M${p.x-12} ${p.y+15}Q${p.x-12} ${p.y+3} ${p.x} ${p.y+3}Q${p.x+12} ${p.y+3} ${p.x+12} ${p.y+15}Z`}/></g>:<circle cx={p.x} cy={p.y} r="9" fill={active?C.teal:C.muted} stroke="#10273B" strokeWidth="3"/>}
</svg>;
const Cache:React.FC<{filled:boolean;alpha?:number}>=({filled,alpha=1})=>filled?<div style={{position:'absolute',inset:0,zIndex:2}}><Picture x={edge.x} y={imageAt(edge).y} w={128} alpha={alpha}/></div>:<div style={{position:'absolute',left:edge.x-64,top:imageAt(edge).y-44,width:128,height:88,border:`2px dashed ${C.muted}`,borderRadius:12,background:'#10273B',opacity:alpha,zIndex:2}}/>;
const World:React.FC<{id:number;f:number;s1:number;selected?:boolean;cache?:boolean;received?:boolean;edgeState?:string;sourceDim?:boolean;edgeCue?:number}>=({id,f,s1,selected=true,cache=false,received=false,edgeState='',sourceDim=false,edgeCue=0})=><>
 <Land/>
 <Text x={440} y={340} size={24} color={C.muted}>亚洲</Text><Text x={1545} y={340} size={24} color={C.muted}>北美洲</Text>
 <Text x={1220} y={750} size={23} color={C.muted}>太平洋</Text>
 {otherEdges.map((p,i)=><Marker key={i} p={p} alpha={id===3?go(f,35+i*18,25)*.5:.5}/>)}
 <Text x={1420} y={712} size={22} color={C.muted} alpha={id===3?go(f,70):1}>其他边缘 · 未检查</Text>
 <Marker p={origin} active={!sourceDim} alpha={sourceDim?.3:1}/><div style={{position:'absolute',inset:0,zIndex:2}}><Picture x={origin.x} y={imageAt(origin).y} w={150} alpha={sourceDim?.3:1}/></div>
 <Text x={origin.x} y={380} size={34} center color={sourceDim?C.muted:C.text}>远端源站</Text>
 <Marker p={user} who/><Text x={540} y={710} center size={33}>{id===7?'同地区另一访客':'用户'}</Text>
 {received&&<div style={{position:'absolute',inset:0,zIndex:2}}><Picture x={user.x} y={imageAt(user).y} w={128}/></div>}
 <Marker p={edge} active={selected} alpha={id===3?go(f,30,30):1}/>
 <Cache filled={cache} alpha={id===3?go(f,35,35):1}/>
 {(id!==4||f>=edgeCue)&&<Text x={edge.x+30} y={365} size={34} color={selected?C.teal:C.muted}>{id===3?'临近节点':'边缘节点'}</Text>}
 <Text x={edge.x+100} y={655} size={28} color={cache?C.teal:C.gold} alpha={id===3?go(f,s1+25):1}>{edgeState}</Text>
 <Text x={155} y={860} size={20} color={C.muted}>大陆轮廓：Natural Earth（公有领域）· 节点/路线为示例</Text>
</>;

export const GeoScene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,s1=s.cueFrames?.sentences?.[1]??d/2;
 const a=go(f,18,45),b=go(f,s1+8,50),c=go(f,s1+70,40);
 const cdnCue=s.cueFrames?.cdnLabel??1,edgeCue=s.cueFrames?.edgeLabel??1,originCue=s.cueFrames?.originLabel??s1;
 const heading=id===3?'地图上，找到合适的节点':id===4?'请求先到临近节点，检查副本':id===5?'没有副本，再向远端取图':id===6?'内容返回，只在选中节点按规则保存':id===7?'同地区再次请求：命中后直接返回':id===8?'这次少走的，是远端这段路':'回顾：CDN让可复用图片就近返回';
 const title=<Text x={130} y={175} size={51}>{heading}</Text>;
 if(id===3)return <>{title}{f>=cdnCue&&<Text x={130} y={250} size={39} color={C.teal}>CDN · 内容分发网络</Text>}
  <World id={id} f={f} s1={s1} selected={b===1} edgeState={b===1?'调度选中这个节点':''}/>
  <Path name="local-request" p={1} alpha={b*.5} color={C.teal} history/>
  <Text x={960} y={790} center size={29} alpha={c}>“近”看网络路径、时延与调度，不能只看直线距离</Text></>;
 if(id===4)return <>{title}<World id={id} f={f} s1={s1} edgeCue={edgeCue} selected={a===1} edgeState={b===1?'未命中：没有可用副本':'先检查图片缓存'} sourceDim/>
  <Path name="local-request" p={a}/><Text x={960} y={790} center size={31} color={C.gold} alpha={b}>没有可用副本，才继续这次远端取图</Text></>;
 if(id===5)return <>{title}<World id={id} f={f} s1={s1} edgeState="未命中 · 等待取图"/>
  <Path name="local-request" p={1} alpha={.25}/><Path name="origin-request" p={a}/>
  {f>=originCue&&<Text x={1160} y={350} center size={38} color={C.gold}>回源</Text>}
  <Text x={960} y={790} center size={30} color={C.gold} alpha={b}>本例没有命中，这次仍有远端传输</Text></>;
 if(id===6){const arriving=go(f,15,55),forward=go(f,70,50),saved=go(f,Math.max(125,s1+15),40);return <>{title}
  <World id={id} f={f} s1={s1} received={forward===1} cache={saved===1} edgeState={saved===1?'只在此节点：已存可复用副本':arriving===1?'接收并转发':'等待返回内容'}/>
  <Path name="origin-return" p={arriving} image color={C.teal}/><Path name="local-return" p={forward} image color={C.teal}/>
  <Text x={960} y={790} center size={30} color={C.teal} alpha={c}>源站内容经选中节点返回；其他节点没有凭空得到图片</Text></>}
 if(id===7)return <>{title}<World id={id} f={f} s1={s1} received={b===1} cache sourceDim edgeState={a===1?'命中 · 直接返回':'延续可使用的副本'}/>
  <Path name="local-request" p={a}/><Path name="local-return" p={b} image color={C.teal}/>
  <Text x={1370} y={635} center size={27} color={C.muted}>源站：本次没有取图请求</Text>
  <Text x={960} y={790} center size={31} color={C.teal} alpha={c}>同一地区 · 同一节点 · 命中后短路径返回</Text></>;
 if(id===8)return <>{title}<World id={id} f={f} s1={s1} received cache sourceDim edgeState="同一副本继续保留"/>
  <Path name="origin-request" p={1} history alpha={a*.22} color={C.muted}/><Path name="local-return" p={1} color={C.teal}/>
  <Text x={1220} y={430} center size={27} color={C.muted} alpha={a}>历史回源路径（本次未走）</Text>
  <Text x={960} y={790} center size={30} color={C.teal} alpha={b}>实际快多少，还要看网络与是否命中</Text></>;
 const returning=go(f,55,50),outro=go(f,d-75,25),brand=go(f,d-50,25);
 return <>{title}<div style={{opacity:1-outro}}><World id={id} f={f} s1={s1} received={returning===1} cache sourceDim edgeState="命中可复用副本"/>
  <Path name="local-request" p={a}/><Path name="local-return" p={returning} image color={C.teal}/>
  <Text x={960} y={790} center size={31} color={C.teal} alpha={b}>CDN：在合适的临近节点复用内容，省掉本次回源</Text></div>
  <Text x={960} y={480} center size={70} alpha={brand}>IT小村 · 原创</Text></>;
};
