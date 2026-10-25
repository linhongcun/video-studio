import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C,FONT,MONO} from './theme';

const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,start:number,duration=30)=>{
 const p=clamp((f-start)/Math.max(1,duration));
 return p*p*(3-2*p);
};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;

const Text:React.FC<{
 children:React.ReactNode;x?:number;y:number;size?:number;color?:string;
 alpha?:number;center?:boolean;mono?:boolean;
}>=({children,x=130,y,size=40,color=C.text,alpha=1,center=false,mono=false})=><div
 style={{position:'absolute',left:x,top:y,fontSize:size,color,opacity:alpha,
  fontFamily:mono?MONO:FONT,fontWeight:600,lineHeight:1.35,whiteSpace:'nowrap',
  transform:center?'translateX(-50%)':undefined}}
>{children}</div>;

/** An overview of examples, rather than an exhaustive list or a ranking. */
const MethodOverview:React.FC<{frame:number;formalNames?:boolean;selected?:boolean;alpha?:number}>=({frame,formalNames=false,selected=false,alpha=1})=>{
 const branches=[
  {x:430,label:formalNames?'UUIDv4':'本地生成',color:C.teal},
  {x:960,label:formalNames?'Redis 自增':'集中取号',color:C.blue},
  {x:1490,label:'雪花算法',color:C.gold},
 ];
 return <div data-method-overview style={{position:'absolute',inset:0,opacity:alpha}}>
  <Text x={960} y={340} size={35} center>分布式 ID 的不同做法</Text>
  <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
   {branches.map((b,i)=>{
    const reveal=go(frame,10+i*13,28);
    return <path key={b.x} d={`M960 405V445H${b.x}V505`} pathLength="1"
     fill="none" stroke={selected&&i!==2?C.edge:b.color} strokeWidth={selected&&i===2?4:2}
     strokeDasharray="1" strokeDashoffset={1-reveal} opacity={selected&&i!==2?.55:.8}/>;
   })}
  </svg>
  {branches.map((b,i)=>{
   const reveal=go(frame,22+i*13,24),muted=selected&&i!==2;
   return <div key={b.x} style={{opacity:reveal}}>
    <Text x={b.x} y={540} size={selected&&i===2?59:48} color={muted?C.muted:b.color} center>{b.label}</Text>
    {i===2&&<Text x={b.x} y={640} size={28} color={C.gold} center>{selected?'本期展开':'经典方案之一'}</Text>}
    {selected&&i===2&&<div style={{position:'absolute',left:b.x-155,top:626,width:310,borderTop:`3px solid ${C.gold}`}}/>}
   </div>;
  })}
  <Text x={960} y={795} size={28} center color={C.muted}>常见示例 · 不止这些实现方式</Text>
 </div>;
};

const LocalGeneration:React.FC<{frame:number;onset:number}>=({frame,onset})=>{
 const rows=[
  {name:'节点甲',y:405,color:C.teal,id:'cc86a3b0-a8b7-4afd-9182-87ccf1b36e73',start:onset+15},
  {name:'节点乙',y:625,color:C.blue,id:'f6f75624-cf42-4379-b60c-455df2bdbd9a',start:onset+73},
 ];
 return <>
  <Text y={282} size={34} color={C.muted}>各节点在本地生成，不必逐次向中心取号</Text>
  {rows.map(row=>{
   const progress=go(frame,row.start,37),ready=go(frame,row.start+31,20);
   return <div key={row.name} data-uuid-node={row.name} data-generated-id={row.id}>
    <Text x={150} y={row.y-15} size={39} color={row.color}>{row.name}</Text>
    <Text x={150} y={row.y+46} size={26} color={C.muted}>本地随机生成</Text>
    <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
     <path d={`M430 ${row.y+38}H620`} pathLength="1" stroke={row.color} strokeWidth="3"
      fill="none" strokeDasharray="1" strokeDashoffset={1-progress}/>
     <circle cx={mix(430,620,progress)} cy={row.y+38} r="8" fill={row.color} opacity={progress>0&&progress<1?1:0}/>
    </svg>
    <Text x={665} y={row.y+5} size={37} color={row.color} mono alpha={ready}>{row.id}</Text>
   </div>;
  })}
  <Text x={960} y={795} size={35} center color={C.gold} alpha={go(frame,onset+113,25)}>可靠随机源 · 碰撞概率极低</Text>
 </>;
};

const UuidScene:React.FC<{shot:Shot}>=({shot})=>{
 const frame=useCurrentFrame();
 const onset=shot.cueFrames?.uuidLabel??shot.cueFrames?.sentences?.[1]??Math.floor(shot.durationInFrames*.5);
 const focus=go(frame,onset,24);
 return <>
  {frame<onset?<Text y={180} size={58}>分布式 ID，有很多实现方式</Text>:<Text y={180} size={58} color={C.teal}>UUID · 随机版本（v4）</Text>}
  {frame<onset+24&&<MethodOverview frame={frame} alpha={1-focus}/>}
  {frame>=onset&&<div style={{position:'absolute',inset:0,opacity:focus}}><LocalGeneration frame={frame} onset={onset}/></div>}
 </>;
};

const RedisDetail:React.FC<{frame:number;onset:number;warningAt:number}>=({frame,onset,warningAt})=>{
 const start=onset+12,step=Math.max(17,(warningAt-start-15)/6);
 const reqA=go(frame,start,step),valueA=frame>=start+step;
 const retA=go(frame,start+step*1.3,step*1.1);
 const reqB=go(frame,start+step*3,step),valueB=frame>=start+step*4;
 const retB=go(frame,start+step*4.3,step*1.1);
 const warning=go(frame,warningAt,25);
 const routes=[
  {name:'节点甲',x:340,edge:500,center:780,request:reqA,reply:retA,value:'1001',color:C.teal},
  {name:'节点乙',x:1580,edge:1420,center:1140,request:reqB,reply:retB,value:'1002',color:C.blue},
 ];
 return <>
  <Text y={282} size={34} color={C.muted}>同一个计数器，集中分配编号</Text>
  {routes.map(row=><div key={row.name} data-redis-client={row.name}>
   <Text x={row.x} y={390} size={42} center color={row.color}>{row.name}</Text>
   <Text x={(row.edge+row.center)/2} y={383} size={25} center color={C.muted}>取一个号</Text>
   <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
    <path d={`M${row.edge} 460H${row.center}`} fill="none" stroke={C.edge} strokeWidth="2"/>
    <circle cx={mix(row.edge,row.center,row.request)} cy="460" r="9" fill={row.color} opacity={row.request>0&&row.request<1?1:0}/>
    <path d={`M${row.center} 575H${row.edge}`} fill="none" stroke={row.color} strokeWidth="2" opacity={row.reply>0?.55:0}/>
   </svg>
   <Text x={row.x} y={550} size={76} mono center color={row.color} alpha={row.reply===1?1:0}>{row.value}</Text>
  </div>)}
  <div data-redis-counter style={{position:'absolute',left:780,top:410,width:360,height:260,
   borderTop:`3px solid ${C.gold}`,borderBottom:`2px solid ${C.gold}`,background:C.surface,textAlign:'center'}}>
   <div style={{fontSize:27,color:C.muted,marginTop:18}}>共享计数器 · 示例</div>
   <div style={{fontSize:88,fontWeight:650,fontFamily:MONO,color:C.gold,lineHeight:1.2,marginTop:19}}>{valueB?'1002':valueA?'1001':'1000'}</div>
   <div style={{fontSize:28,color:C.gold,marginTop:12}}>原子 +1</div>
  </div>
  {routes.map(row=>row.reply>0&&row.reply<1&&<Text key={row.name} x={mix(row.center,row.x,row.reply)} y={545} size={41} mono center color={row.color}>{row.value}</Text>)}
  <Text x={960} y={788} size={36} center color={C.red} alpha={warning}>故障恢复后，必须防止计数回退</Text>
 </>;
};

const RedisScene:React.FC<{shot:Shot}>=({shot})=>{
 const frame=useCurrentFrame();
 const sentences=shot.cueFrames?.sentences??[];
 const onset=shot.cueFrames?.redisLabel??1;
 const warningAt=sentences[1]??Math.floor(shot.durationInFrames*.43);
 const focusAt=sentences[2]??Math.floor(shot.durationInFrames*.8);
 const back=go(frame,focusAt,30);
 const detailAlpha=1-clamp(back*2),overviewAlpha=clamp(back*2-1);
 return <>
  {frame<focusAt
   ?frame>=onset&&<Text y={180} size={58} color={C.blue}>Redis 自增</Text>
   :<Text y={180} size={58} color={C.gold}>下面，聚焦雪花算法</Text>}
  <div style={{position:'absolute',inset:0,opacity:detailAlpha,transform:`scale(${mix(1,.87,back)})`,transformOrigin:'960px 500px'}}>
   <RedisDetail frame={frame} onset={onset} warningAt={warningAt}/>
  </div>
  {overviewAlpha>0&&<MethodOverview frame={frame-focusAt+55} formalNames selected alpha={overviewAlpha}/>}
 </>;
};

export const MethodsScene:React.FC<{shot:Shot}>=({shot})=>Number(shot.id)===16?<UuidScene shot={shot}/>:<RedisScene shot={shot}/>;
