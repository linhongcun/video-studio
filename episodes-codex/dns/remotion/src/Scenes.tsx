import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C} from './theme';
import config from '../../production.json';
import {T,Node,Link,Packet,Page,Result,go,mix} from './Primitives';
export const SceneTitle:React.FC<{shot:Shot;frame:number}>=({shot:s,frame:f})=>{
 const id=Number(s.id);let title=config.shots[id-1][1];for(const[term,n,key]of config.terms)if(n===id&&f>=(s.cueFrames?.[key]??1))title=term as string;
 return <><T size={53}>{title}</T>{(id===2||id===3)&&<T x={960} y={880} center size={21} color={C.muted}>保留域名与文档地址：图解示例，非真实公开解析结果</T>}{id===11&&<T x={130} y={260} size={27} color={C.gold}>重置示例：另一个时点，缓存尚未到期</T>}{id===5&&f<70&&<T x={130} y={260} size={27} color={C.gold}>切回本次主线：本地没有可用答案</T>}{id===12&&f>=s.durationInFrames-65&&<T x={960} y={880} center size={23}>IT小村 · 原创</T>}</>;
};
const Box:React.FC<{x:number;y:number;title:string;value:string;active?:boolean;color?:string;w?:number}>=({x,y,title,value,active=true,color=C.blue,w=300})=><div style={{position:'absolute',left:x-w/2,top:y-55,width:w,height:130,border:`2px solid ${active?color:C.edge}`,borderRadius:12,background:C.surface,opacity:active?1:.35,textAlign:'center',paddingTop:17}}><div style={{fontSize:32,fontWeight:650,color:active?color:C.muted}}>{title}</div><div style={{fontSize:23,color:C.muted,marginTop:13}}>{value}</div></div>;
const Route:React.FC<{x1:number;y1:number;x2:number;y2:number;p:number;text?:string;color?:string;offset?:number}>=({x1,y1,x2,y2,p,text,color=C.gold,offset=0})=>{
 const dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy),px=-dy/len*offset,py=dx/len*offset;
 return <><svg width={1920} height={900} style={{position:'absolute',inset:0}}><path d={`M${x1+px} ${y1+py}L${x2+px} ${y2+py}`} stroke={C.edge} strokeWidth={2}/><path d={`M${x1+px} ${y1+py}L${mix(x1,x2,p)+px} ${mix(y1,y2,p)+py}`} stroke={color} strokeWidth={4}/>{p>0&&p<1&&<circle cx={mix(x1,x2,p)+px} cy={mix(y1,y2,p)+py} r={9} fill={color}/>}</svg>{p>0&&p<1&&text&&<T x={mix(x1,x2,p)+px} y={mix(y1,y2,p)+py-35} size={24} center color={color}>{text}</T>}</>;
};
/** All server identities retain these coordinates through shots05–09. */
const QueryNetwork:React.FC<{id:number;f:number;b:number}>=({id,f,b})=>{
 const current=id>=6&&id<=8?id-6:-1,qa=go(f,18,52),answer=go(f,b+12,60),toResolver=go(f,70,40),back=go(f,18,60);
 const labels=['根服务器','顶级域服务器','权威服务器'],ys=[350,535,720],received=answer===1,done=id===9;
 return <>
  <Box x={270} y={500} w={280} title="客户端" value={done&&back===1?'拿到示例地址':'等待同一个查询'} color={C.blue}/>
  <Box x={835} y={500} w={340} title="递归解析器" value={id===5?(f>=155?'自身缓存：未命中':'先检查自己的缓存'):done?'保留一份可用缓存':id===8&&received?'已取得地址记录':received?'已收到下一步指引':'替客户端继续查询'} color={C.gold}/>
  <T x={270} y={650} size={22} center color={C.muted}>本地无可用答案</T><T x={835} y={650} size={22} center color={C.muted}>{done?'通常缓存本次回答':'不把查询交给客户端继续'}</T>
  {ys.map((y,i)=><Box key={y} x={1600} y={y} w={300} title={labels[i]} value={i===2?'本例：返回地址记录':'返回下一步指引'} active={current===i} color={i===2?C.teal:C.blue}/>)}
  {id===5&&<Route x1={425} y1={490} x2={645} y2={490} p={toResolver} text="查询" color={C.blue}/>}
  {id>=6&&id<=8&&<><Route x1={1020} y1={485} x2={1430} y2={ys[current]-10} p={qa} text="询问" color={C.blue} offset={-18}/><Route x1={1430} y1={ys[current]+18} x2={1020} y2={535} p={answer} text={id===8?'示例地址':'下层指引'} color={id===8?C.teal:C.gold} offset={-18}/></>}
  {done&&<Route x1={645} y1={540} x2={425} y2={540} p={back} text="203.0.113.10" color={C.teal}/>}
  <Result y={835} color={current===2?C.teal:C.gold} alpha={id===5?go(f,155,25):done?go(f,80,25):answer}>{id===5?'本次：解析器缓存也没有可用答案':done?'答案返回客户端，随后才能连接':id===8?(received?'这次才拿到地址记录':'地址记录正在返回解析器'):(received?'指引已回到解析器，再由解析器问下一组':'指引正在返回解析器')}</Result>
 </>;
};
export const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),b=s.cueFrames?.sentences?.[1]??s.durationInFrames*.5,p=go(f,b+12,70);
 if(id===1)return <><Page url="https://shop.example" loading/><T x={960} y={835} center size={30} color={C.gold} alpha={p}>目标地址：还不知道</T></>;
 if(id===2||id===3||id===12)return null;
 if(id===4){const hit=go(f,100,35);return <><Node x={390} label="客户端" value={hit===1?'直接复用可用地址':'同一个示例域名'} color={C.blue}/><Node x={1520} label="本地缓存" value={f>=65?'已有可用答案':'检查已有记录'} color={C.teal}/><Link x1={590} x2={1320} p={go(f,35,30)}/><Link x1={1320} x2={590} y={650} p={hit}/><Packet text="可用地址" x1={1320} x2={590} p={hit} y={580} color={C.teal}/><Result color={C.teal} alpha={go(f,100,25)}>本地已有可用记录，就不必向外逐级查询</Result></>}
 if(id>=5&&id<=9)return <QueryNetwork id={id} f={f} b={b}/>;
 if(id===10){const count=Math.max(0,60-Math.floor(go(f,65,110)*60));return <><Node x={480} label="解析器缓存记录" value="203.0.113.10（示例）" color={count?C.teal:C.muted}/><T x={1350} y={355} size={130} center color={count?C.gold:C.red} mono>{count}</T><T x={1350} y={535} center size={30} color={C.muted}>示例有效期 · 秒（快进）</T><Result color={count?C.teal:C.red}>{count?'有效期内，可按规则复用':'本条记录已到期，按规则重新查询'}</Result></>}
 if(id===11){const q=go(f,75,35),a=go(f,130,55);return <><Node x={390} label="客户端" value={a===1?'快速拿到地址':'再次查询同一个名字'} color={C.blue}/><Node x={1520} label="解析器缓存" value="这次：缓存尚未到期" color={C.teal}/><Link x1={590} x2={1320} p={q}/><Link x1={1320} x2={590} y={650} p={a}/><Packet text="直接返回可用答案" x1={1320} x2={590} p={a} y={580} color={C.teal}/><Result color={C.gold} alpha={go(f,185,25)}>省去逐级询问，网页内容仍要继续获取</Result></>}
 return null;
};
