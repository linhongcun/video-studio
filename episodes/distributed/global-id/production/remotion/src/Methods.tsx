import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C,FONT,MONO} from './theme';

const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,start:number,duration=30)=>{
 const p=clamp((f-start)/Math.max(1,duration));return p*p*(3-2*p);
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
const Heading:React.FC<{children:React.ReactNode;color?:string}>=({children,color=C.teal})=><Text y={180} size={58} color={color}>{children}</Text>;

// Both values are valid v4 examples. Their generation order deliberately differs
// from the byte/prefix order used in the following InnoDB primary-key diagram.
const UUID_A='b8d21c40-32b4-4e38-a5d2-73034bc45071';
const UUID_B='35a7f930-7065-4f25-8cc4-8f85ac6781b6';
const LocalGeneration:React.FC<{frame:number;onset:number}>=({frame,onset})=>{
 const rows=[
  {name:'节点甲 · 先生成',y:405,color:C.teal,id:UUID_A,start:onset+15},
  {name:'节点乙 · 后生成',y:625,color:C.blue,id:UUID_B,start:onset+73},
 ];
 return <>
  <Text y={282} size={34} color={C.muted}>各节点自己生成，不必逐次向中心取号</Text>
  {rows.map(row=>{
   const progress=go(frame,row.start,37),ready=go(frame,row.start+31,20);
   return <div key={row.name} data-uuid-node={row.name} data-generated-id={row.id}>
    <Text x={150} y={row.y-15} size={35} color={row.color}>{row.name}</Text>
    <Text x={150} y={row.y+46} size={26} color={C.muted}>本地随机生成</Text>
    <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
     <path d={`M480 ${row.y+38}H665`} pathLength="1" stroke={row.color} strokeWidth="3"
      fill="none" strokeDasharray="1" strokeDashoffset={1-progress}/>
     <circle cx={mix(480,665,progress)} cy={row.y+38} r="8" fill={row.color} opacity={progress>0&&progress<1?1:0}/>
    </svg>
    <Text x={705} y={row.y+5} size={36} color={row.color} mono alpha={ready}>{row.id}</Text>
   </div>;
  })}
  <Text x={960} y={795} size={35} center color={C.gold} alpha={go(frame,onset+113,25)}>可靠随机源 · 碰撞概率极低</Text>
 </>;
};

type Key={value:string;color?:string;alpha?:number;position?:number};
const Leaf:React.FC<{
 x:number;y?:number;width?:number;height?:number;title:string;keys:Key[];
 color?:string;fontSize?:number;gap?:number;
}>=({x,y=430,width=520,height=330,title,keys,color=C.edge,fontSize=43,gap=58})=><div data-index-leaf={title} style={{position:'absolute',left:x-width/2,top:y,width,height,border:`2px solid ${color}`,borderRadius:10,background:C.surface}}>
 <div style={{fontSize:27,color:C.muted,textAlign:'center',marginTop:14}}>{title}</div>
 <div style={{position:'absolute',left:25,right:25,top:62,borderTop:`1px solid ${C.edge}`}}/>
 {keys.map((key,i)=><div key={key.value} style={{position:'absolute',left:0,right:0,top:78+(key.position??i)*gap,fontFamily:MONO,fontSize,fontWeight:650,textAlign:'center',lineHeight:1.2,color:key.color??C.text,opacity:key.alpha??1}}>{key.value}</div>)}
</div>;
const IndexInsertion:React.FC<{frame:number;from:number;to:number}>=({frame,from,to})=>{
 const span=Math.max(120,to-from);
 const a=go(frame,from+12,span*.18),b=go(frame,from+span*.48,span*.18);
 return <>
  <Text y={282} size={33} color={C.muted}>MySQL · InnoDB 主键叶页 · UUID 前缀示意</Text>
  <Text x={960} y={345} size={31} center>先生成 b8…，后生成 35…，插入位置却不同</Text>
  <Leaf x={560} title="较小键值所在的叶页" color={b>0?C.blue:C.edge} keys={[
   {value:'28…'}, {value:'35…',color:C.blue,alpha:b===1?1:0},
   {value:'42…',position:1+b}, {value:'59…',position:2+b},
  ]}/>
  <Leaf x={1360} title="较大键值所在的叶页" color={a>0?C.teal:C.edge} keys={[
   {value:'ac…'}, {value:'b8…',color:C.teal,alpha:a===1?1:0},
   {value:'d6…',position:1+a}, {value:'f1…',position:2+a},
  ]}/>
  <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
   <path d="M850 695H1070" fill="none" stroke={C.edge} strokeWidth="2"/>
   {[{p:a,x:1360,color:C.teal},{p:b,x:560,color:C.blue}].map((q,i)=><path key={i} d={`M960 395Q${q.x} 400 ${q.x} 595`} pathLength="1" fill="none" stroke={q.color} strokeWidth="3" strokeDasharray="1" strokeDashoffset={1-q.p} opacity={q.p>0&&q.p<1?.75:0}/>)}
  </svg>
  {a>0&&a<1&&<Text x={mix(960,1360,a)} y={mix(355,565,a)} size={43} mono center color={C.teal}>b8…</Text>}
  {b>0&&b<1&&<Text x={mix(960,560,b)} y={mix(355,565,b)} size={43} mono center color={C.blue}>35…</Text>}
  <Text x={960} y={810} size={34} center color={C.gold} alpha={go(frame,from+span*.73,24)}>不按生成顺序递增，插入可能分散到多个页</Text>
 </>;
};
const IndexCost:React.FC<{frame:number;from:number;to:number}>=({frame,from,to})=>{
 const span=Math.max(120,to-from),split=go(frame,from+span*.42,span*.28);
 const leftX=mix(560,400,split),leftWidth=mix(520,420,split);
 const newX=mix(870,970,split),newWidth=mix(20,420,split),pageY=mix(430,445,split);
 return <>
  <Text y={282} size={34} color={C.muted}>访问更分散，空间不足时还可能分裂</Text>
  <Text x={960} y={345} size={31} center color={C.gold}>多个叶页的访问，会影响索引页缓存利用</Text>
  <Leaf x={leftX} y={pageY} width={leftWidth} height={mix(330,290,split)} title={split<.5?'原叶页 · 空间已满（示意）':'分裂后 · 左页'} color={C.blue} keys={[{value:'28…'},{value:'35…',color:C.blue}]}/>
  <div style={{position:'absolute',inset:0,opacity:split}}>
   <Leaf x={newX} y={pageY} width={newWidth} height={mix(330,290,split)} title={split<.5?'':'分裂后 · 右页'} color={C.blue} keys={[{value:'48…',position:1,color:C.gold,alpha:clamp((split-.45)/.4)}]}/>
  </div>
  <Leaf x={mix(1360,1560,split)} y={pageY} width={mix(520,340,split)} height={mix(330,290,split)} title={split<.6?'另一个叶页':'原高位页 · 不变'} fontSize={mix(43,36,split)} gap={mix(58,44,split)} color={C.teal} keys={[{value:'ac…'},{value:'b8…',color:C.teal},{value:'d6…'},{value:'f1…'}]}/>
  <svg width="1920" height="1080" style={{position:'absolute',inset:0}}><path d={`M${leftX+leftWidth/2+10} 680H${newX-newWidth/2-10}`} fill="none" stroke={C.edge} strokeWidth="2" opacity={split}/></svg>
  <Text x={mix(560,970,split)} y={mix(624,523,split)} size={43} mono center>42…</Text>
  <Text x={mix(560,970,split)} y={mix(682,639,split)} size={43} mono center>59…</Text>
  <Text x={leftX} y={390} size={27} center color={C.gold} alpha={go(frame,from+15,25)*(1-split)}>再插入 48…（示例）</Text>
  <Text x={960} y={815} size={33} center color={C.gold}>空间不足时才可能发生，并非每次插入都会分裂</Text>
 </>;
};
const UuidScene:React.FC<{shot:Shot}>=({shot})=>{
 const frame=useCurrentFrame(),sentences=shot.cueFrames?.sentences??[];
 const onset=shot.cueFrames?.uuidLabel??1;
 const indexAt=sentences[1]??Math.floor(shot.durationInFrames*.36);
 const costAt=sentences[2]??Math.floor(shot.durationInFrames*.72);
 return <>
  {frame>=onset&&<Heading>UUID · 随机版本（v4）</Heading>}
  {frame<indexAt?<LocalGeneration frame={frame} onset={onset}/>:frame<costAt?<IndexInsertion frame={frame} from={indexAt} to={costAt}/>:<IndexCost frame={frame} from={costAt} to={shot.durationInFrames}/>}
 </>;
};

const Counter:React.FC<{x:number;y?:number;name:string;value:string;color?:string;alpha?:number;status?:string;valueSize?:number}>=({x,y=410,name,value,color=C.gold,alpha=1,status='',valueSize=84})=><div style={{position:'absolute',left:x-210,top:y,width:420,height:260,opacity:alpha,borderTop:`3px solid ${color}`,borderBottom:`2px solid ${color}`,background:C.surface,textAlign:'center'}}>
 <div style={{fontSize:29,color:C.muted,marginTop:18}}>{name}</div>
 <div style={{fontSize:valueSize,fontWeight:650,fontFamily:MONO,color,lineHeight:1.2,marginTop:18}}>{value}</div>
 {status&&<div style={{fontSize:27,color,marginTop:15}}>{status}</div>}
</div>;
const RedisNormal:React.FC<{frame:number;onset:number;to:number}>=({frame,onset,to})=>{
 const start=onset+12,step=Math.max(17,(to-start-15)/6);
 const reqA=go(frame,start,step),valueA=frame>=start+step;
 const retA=go(frame,start+step*1.3,step*1.1);
 const reqB=go(frame,start+step*3,step),valueB=frame>=start+step*4;
 const retB=go(frame,start+step*4.3,step*1.1);
 const routes=[
  {name:'节点甲',x:340,edge:500,center:750,request:reqA,reply:retA,value:'1001',color:C.teal},
  {name:'节点乙',x:1580,edge:1420,center:1170,request:reqB,reply:retB,value:'1002',color:C.blue},
 ];
 return <>
  <Text y={282} size={34} color={C.muted}>同一个计数器，正常时集中递增取号</Text>
  {routes.map(row=><div key={row.name}>
   <Text x={row.x} y={390} size={42} center color={row.color}>{row.name}</Text>
   <Text x={(row.edge+row.center)/2} y={383} size={25} center color={C.muted}>取一个号</Text>
   <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
    <path d={`M${row.edge} 460H${row.center}`} fill="none" stroke={C.edge} strokeWidth="2"/>
    <circle cx={mix(row.edge,row.center,row.request)} cy="460" r="9" fill={row.color} opacity={row.request>0&&row.request<1?1:0}/>
    <path d={`M${row.center} 575H${row.edge}`} fill="none" stroke={row.color} strokeWidth="2" opacity={row.reply>0?.55:0}/>
   </svg>
   <Text x={row.x} y={550} size={76} mono center color={row.color} alpha={row.reply===1?1:0}>{row.value}</Text>
  </div>)}
  <Counter x={960} name="共享计数器 · 示例" value={valueB?'1002':valueA?'1001':'1000'} status="原子 +1"/>
  {routes.map(row=>row.reply>0&&row.reply<1&&<Text key={row.name} x={mix(row.center,row.x,row.reply)} y={545} size={41} mono center color={row.color}>{row.value}</Text>)}
  <Text x={960} y={810} size={32} center color={C.muted} alpha={go(frame,start+step*5.4,12)}>已发出：1001 → 1002</Text>
 </>;
};
const RedisFailover:React.FC<{frame:number;from:number;to:number}>=({frame,from,to})=>{
 const span=Math.max(150,to-from),elapsed=frame-from;
 const stopped=elapsed>=span*.35,promoted=elapsed>=span*.53,reissued=elapsed>=span*.73;
 const blocked=go(frame,from+10,span*.23);
 return <>
  <Text y={282} size={34} color={C.muted}>异步复制尚未到达，主从切换可能让计数回退</Text>
  <Counter x={490} name={stopped?'旧主 · 故障后停发':'旧主'} value="1002" color={stopped?C.muted:C.gold} status={stopped?'停止发号':'已发过 1001、1002'}/>
  <Counter x={1430} name={promoted?'副本升为新主':'副本'} value={reissued?'1001':'1000'} color={reissued?C.red:C.blue} status={promoted?'从旧计数继续 +1':'仍保留较旧计数'}/>
  <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
   <path d="M710 495H1210" stroke={C.edge} strokeWidth="3" strokeDasharray="12 10"/>
   <circle cx={mix(730,965,blocked)} cy="495" r="10" fill={C.gold} opacity={promoted?0:1}/>
   <path d="M975 472L1000 517M1000 472L975 517" stroke={C.red} strokeWidth="4" opacity={blocked}/>
  </svg>
  <Text x={960} y={370} size={28} center color={C.gold}>更新未送达</Text>
  <Text x={960} y={730} size={37} center color={reissued?C.red:C.muted}>{reissued?'1001 已发过，再次取到就重复了':'历史已发：1001、1002'}</Text>
  <Text x={960} y={818} size={29} center color={C.muted}>示例：异步复制不等于故障后计数一定保留</Text>
 </>;
};
const RedisReservedRange:React.FC<{frame:number;from:number;conditionAt:number;to:number}>=({frame,from,conditionAt,to})=>{
 const preconditions=frame>=conditionAt;
 const span=Math.max(100,conditionAt-from),jump=go(frame,from+span*.55,span*.25);
 const confirmed=go(frame,conditionAt+12,Math.max(24,(to-conditionAt)*.32));
 const issued=frame>=conditionAt+(to-conditionAt)*.62;
 const oldAlpha=preconditions?1:.75;
 return <>
  <Text y={282} size={34} color={C.muted}>{preconditions?'上界记录可靠，且旧主已停发，才能继续':'事先预留号段的方案（示意）'}</Text>
  <div style={{position:'absolute',left:610,top:345,width:700,height:155,border:`2px solid ${preconditions?C.gold:C.edge}`,borderRadius:10,background:C.surface,textAlign:'center'}}>
   <div style={{fontSize:29,color:C.muted,marginTop:10}}>独立可靠记录 · 在旧主使用前写下</div>
   <div style={{fontSize:53,fontWeight:650,fontFamily:MONO,color:C.gold,marginTop:8}}>预留上界 1200</div>
  </div>
  <Counter x={490} y={550} name="旧主预留：1001—1200" value="1001…1200" valueSize={48} color={C.muted} alpha={oldAlpha} status="旧主已停止发号"/>
  <Counter x={1430} y={550} name="新主" value={issued?'1201':jump===1?'1200':'1000'} color={issued?C.teal:C.blue} status={issued?'下一次 +1 → 1201':jump===1?'越过整段，再继续':'准备越过旧预留段'}/>
  <svg width="1920" height="1080" style={{position:'absolute',inset:0}}>
   <path d="M725 675H1195" stroke={C.gold} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1-jump}/>
   <path d="M1175 663L1195 675L1175 687" fill="none" stroke={C.gold} strokeWidth="3" opacity={jump}/>
  </svg>
  <Text x={960} y={570} size={29} center color={C.gold}>跳过 1001—1200</Text>
  {preconditions&&<>
   <Text x={960} y={515} size={28} center color={C.teal} alpha={confirmed}>可靠上界 ✓　旧主停发 ✓</Text>
  </>}
  <Text x={960} y={840} size={29} center color={C.muted}>示例方案，不是 Redis 默认保证</Text>
 </>;
};
const RedisScene:React.FC<{shot:Shot}>=({shot})=>{
 const frame=useCurrentFrame(),s=shot.cueFrames?.sentences??[],d=shot.durationInFrames;
 const onset=shot.cueFrames?.redisLabel??1;
 const failureAt=s[1]??Math.floor(d*.22),reserveAt=s[2]??Math.floor(d*.48),conditionAt=s[3]??Math.floor(d*.70),snowAt=s[4]??Math.floor(d*.9);
 if(frame>=snowAt)return <>
  <Heading color={C.gold}>接下来，详细看雪花算法</Heading>
  <Text x={960} y={465} size={88} color={C.gold} center>雪花算法</Text>
 </>;
 return <>
  {frame>=onset&&<Heading color={C.blue}>Redis 自增</Heading>}
  {frame<failureAt?<RedisNormal frame={frame} onset={onset} to={failureAt}/>:frame<reserveAt?<RedisFailover frame={frame} from={failureAt} to={reserveAt}/>:<RedisReservedRange frame={frame} from={reserveAt} conditionAt={conditionAt} to={snowAt}/>}
 </>;
};

export const MethodsScene:React.FC<{shot:Shot}>=({shot})=>Number(shot.id)===16?<UuidScene shot={shot}/>:<RedisScene shot={shot}/>;
