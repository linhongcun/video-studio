import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
import {Shot,VIDEO,shots} from './data';
import {TIME,IDS} from './sample-data';
import {MethodsScene} from './Methods';
declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const go=(f:number,a:number,n=30)=>{const v=clamp((f-a)/Math.max(1,n));return v*v*(3-2*v)};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const Txt:React.FC<{children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;alpha?:number;center?:boolean;mono?:boolean}>=({children,x=130,y=180,size=48,color=C.text,alpha=1,center=false,mono=false})=><div style={{position:'absolute',left:x,top:y,color,fontSize:size,opacity:alpha,whiteSpace:'nowrap',fontWeight:600,lineHeight:1.35,fontFamily:mono?MONO:FONT,transform:center?'translateX(-50%)':undefined}}>{children}</div>;
const Line:React.FC<{x1:number;x2:number;y?:number;p:number;color?:string;alpha?:number}>=({x1,x2,y=590,p,color=C.teal,alpha=1})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:alpha,pointerEvents:'none'}}><path d={`M${x1} ${y}H${x2}`} pathLength="1" fill="none" stroke={color} strokeWidth="3" strokeDasharray="1" strokeDashoffset={1-clamp(p)}/><circle cx={mix(x1,x2,clamp(p))} cy={y} r="7" fill={color} opacity={p>0&&p<1?1:0}/></svg>;
const Order:React.FC<{who:string;id:string;x:number;y?:number;scale?:number;color?:string;alpha?:number;label?:string}>=({who,id,x,y=380,scale=1,color=C.text,alpha=1,label=''})=><div data-order={who} data-id={id} style={{position:'absolute',left:x-260,top:y,width:520,height:300,textAlign:'center',opacity:alpha,transform:`scale(${scale})`,transformOrigin:'center'}}>
 <div style={{fontSize:29,color:C.muted}}>{who}</div><div style={{fontFamily:/^\d+$/.test(id)?MONO:FONT,fontSize:/^\d+$/.test(id)?(id.length>10?45:110):72,fontWeight:650,color,marginTop:24,lineHeight:1.15}}>{id}</div>
 <div style={{borderTop:`2px solid ${color===C.text?C.edge:color}`,margin:'26px 20px 15px'}}/>
 {label&&<div style={{fontSize:25,color:C.muted}}>{label}</div>}
 </div>;
const Field:React.FC<{name:string;value:string;x:number;y:number;width:number;color:string;alpha?:number;scale?:number}>=({name,value,x,y,width,color,alpha=1,scale=1})=><div data-field={name} data-value={value} style={{position:'absolute',left:x-width/2,top:y,width,height:160,textAlign:'center',opacity:alpha}}>
 <div style={{fontSize:28*scale,color:C.muted}}>{name}</div><div style={{fontFamily:MONO,fontSize:(value.length>5?55:79)*scale,color,fontWeight:650,marginTop:23,lineHeight:1.1}}>{value}</div><div style={{position:'absolute',left:0,right:0,top:145*scale,borderTop:`2px solid ${color}`}}/>
 </div>;
const Fields:React.FC<{time?:string;worker?:string;seq?:string;y?:number;focus?:number;alpha?:number;scale?:number;reveal?:number}>=({time=TIME.toString(),worker='007',seq='000',y=390,focus=-1,alpha=1,scale=1,reveal=3})=><>
 {[{name:'时间',value:time,x:570,w:650,color:C.teal},{name:'机器编号',value:worker,x:1120,w:320,color:C.gold},{name:'序号',value:seq,x:1500,w:320,color:C.blue}].map((q,i)=><Field key={q.name} name={q.name} value={q.value} x={960+(q.x-960)*scale} y={y} width={q.w*scale} scale={scale} color={q.color} alpha={alpha*(i<reveal?(focus<0||focus===i?1:.52):0)}/>)}
 </>;
const LongId:React.FC<{value:string;y?:number;alpha?:number;color?:string;label?:string;size?:number}>=({value,y=690,alpha=1,color=C.teal,label='组合后的整数',size=68})=><><Txt x={960} y={y-43} size={25} center color={C.muted} alpha={alpha}>{label}</Txt><Txt x={960} y={y} center mono size={size} color={color} alpha={alpha}>{value}</Txt></>;
const Result:React.FC<{children:React.ReactNode;alpha?:number;color?:string;y?:number}>=({children,alpha=1,color=C.teal,y=805})=><Txt x={960} y={y} size={34} center color={color} alpha={alpha}>{children}</Txt>;

const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),d=s.durationInFrames,id=Number(s.id),s1=s.cueFrames?.sentences?.[1]??d*.5;
 if(id===16||id===17)return <MethodsScene shot={s}/>;
 if(id===1){const p=go(f,25,55);return <>
  <Txt size={63}>两个订单，怎么撞成同一个号了？</Txt>
  <Order who="甲的订单" id="42" x={520} color={C.red}/><Order who="乙的订单" id="42" x={1400} color={C.red}/>
  <Line x1={760} x2={1160} p={p} color={C.red}/><Result color={C.red} alpha={go(f,s1-15,35)}>同一个号，匹配到两笔不同订单</Result>
 </>}
 if(id===2){const a=go(f,10,40),b=go(f,s1-10,40);return <>
  <Txt>订单分开存，编号也各自生成</Txt>
  <Order who="库甲 · 订单表" id="41" x={520} alpha={a} color={C.gold} label="各自的上一笔编号"/>
  <Order who="库乙 · 订单表" id="41" x={1400} alpha={b} color={C.blue} label="各自的上一笔编号"/>
 </>}
 if(id===3){const at=s.cueFrames?.autoLabel??1,p=go(f,35,45),q=go(f,s1,45);return <>
  {f>=at&&<Txt size={58} color={C.teal}>自增 ID</Txt>}
  <Order who="同一张表" id={q===1?'43':p===1?'42':'41'} x={960} color={C.teal} scale={1.25} label="每来一条，编号往后增加"/>
  <Line x1={560} x2={1360} y={760} p={go(f,s1-20,50)} color={C.teal}/>
  <Result alpha={go(f,s1+40,30)}>配合唯一约束 · 范围是本表</Result>
 </>}
 if(id===4){const p=go(f,s1,50);return <>
  <Txt>库甲：上一笔 41，下一笔 42</Txt>
  <Order who="库甲 · 上一笔" id="41" x={mix(960,480,p)} scale={mix(1.15,.62,p)} alpha={1-.6*p}/>
  <Order who="库甲 · 新订单" id="42" x={mix(1510,1110,p)} color={C.gold} alpha={p} scale={mix(.65,1.2,p)} label="本表没有重复"/>
  <Line x1={720} x2={870} p={p} color={C.gold}/>
 </>}
 if(id===5){const p=go(f,s1,40),compare=go(f,s1+40,45);return <>
  <Txt>库乙也从自己的 41 继续往后</Txt>
  <Order who="库甲 · 已生成" id="42" x={520} color={compare>.9?C.red:C.gold} alpha={.45+.55*compare} scale={.9}/>
  <Order who="库乙 · 新订单" id={p===1?'42':'41'} x={1400} color={compare>.9?C.red:C.blue} scale={1.12} label={p===1?'本表也没有重复':'上一笔编号'}/>
  <Line x1={770} x2={1150} p={compare} color={C.red}/><Result color={C.red} alpha={compare}>本地都没重复 · 跨库却相同</Result>
 </>}
 if(id===6){const p=go(f,s1-12,50);return <>
  <Txt>本表唯一，不等于所有库共同唯一</Txt>
  <Order who="库甲的订单" id="42" x={mix(520,650,p)} y={mix(380,340,p)} color={C.red}/>
  <Order who="库乙的订单" id="42" x={mix(1400,1270,p)} y={mix(380,580,p)} color={C.red}/>
  <Line x1={500} x2={1420} y={780} p={1-p} color={C.muted}/><Result color={C.red} alpha={p} y={830}>统一使用订单号时，必须考虑所有生成位置</Result>
 </>}
 if(id===7){const at=s.cueFrames?.snowLabel??1;return <>
  {f>=at&&<Txt size={58} color={C.teal}>雪花算法</Txt>}
  <Fields reveal={f<s1?1:f<s1+45?2:3} alpha={go(f,at+10,25)}/>
  <Result alpha={go(f,s1+70,30)} color={C.muted}>字段示意 · 时间 / 机器编号 / 同毫秒序号</Result>
 </>}
 if(id===8){const p=go(f,s1+20,45),changed=p===1;return <>
  <Txt>先只改变时间</Txt>
  <LongId value={IDS.base} y={310} size={33} color={C.muted} label="上一个编号" alpha={p}/>
  <Fields time={(changed?TIME+1n:TIME).toString()} focus={0}/>
  <LongId value={changed?IDS.time:IDS.base} alpha={go(f,35,25)}/>
  <Result alpha={p}>机器与序号不变 · 时间前进，结果不同</Result>
 </>}
 if(id===9){const p=go(f,s1-10,45);return <>
  <Txt>同一毫秒：靠机器编号区分</Txt>
  <Txt x={160} y={365} size={30} color={C.gold}>甲</Txt><Fields y={315} scale={.78} focus={1}/>
  <LongId value={IDS.base} y={485} size={56} label="甲生成的编号" color={C.gold}/>
  <Txt x={160} y={660} size={30} color={C.gold} alpha={p}>乙</Txt><Fields y={610} scale={.78} worker="009" focus={1} alpha={p}/>
  <LongId value={IDS.worker} y={780} size={56} label="乙生成的编号" color={C.gold} alpha={p}/>
 </>}
 if(id===10){const p=go(f,s1+15,45),changed=p===1;return <>
  <Txt>同机、同毫秒：让序号往后增加</Txt>
  <LongId value={IDS.base} y={310} size={33} color={C.muted} label="同毫秒的上一笔" alpha={p}/>
  <Fields seq={changed?'001':'000'} focus={2}/><LongId value={changed?IDS.sequence:IDS.base} color={C.blue}/>
  <Result alpha={p} color={C.blue}>000 → 001 · 区分连续两次请求</Result>
 </>}
 if(id===11){const p=go(f,20,60),out=go(f,s1-20,45);return <>
  <Txt>按规则组合成整数</Txt><Fields y={mix(330,410,p)} scale={mix(1.1,.85,p)}/>
  <svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:out}}>{[570,1120,1500].map((x,i)=><g key={x}><path d={`M${x} 585Q${x} 650 960 655`} pathLength="1" strokeDasharray="1" strokeDashoffset={1-out} fill="none" stroke={[C.teal,C.gold,C.blue][i]} strokeWidth="3"/><circle cx={mix(x,960,out*out)} cy={mix(585,655,out)} r="7" fill={[C.teal,C.gold,C.blue][i]} opacity={out>0&&out<1?1:0}/></g>)}</svg>
  <LongId value={IDS.base} y={710} alpha={out}/><Result color={C.muted} alpha={go(f,s1+45,25)} y={840}>字段示意，不是十进制直接拼接</Result>
 </>}
 if(id===12){const stage=f<s1*.65?0:f<s1+25?1:2;const labels=['机器编号不能重复','时间往回走，要按实现处理','序号用尽，不能直接绕回'];return <>
  <Txt>不重复，需要正确维护前提</Txt>
  <Txt x={960} y={420} center size={62} color={[C.gold,C.teal,C.blue][stage]}>{labels[stage]}</Txt>
  {stage===0?<><Txt x={660} y={595} center mono size={90} color={C.gold}>007</Txt><Txt x={1260} y={595} center mono size={90} color={C.gold}>009</Txt><Line x1={810} x2={1110} y={650} p={go(f,15,40)} color={C.gold}/></>:stage===1?<Result color={C.red} y={630}>不能倒着继续复用之前的组合</Result>:<Result color={C.blue} y={630}>按规则等待下一毫秒等处理</Result>}
 </>}
 if(id===13){const p=go(f,Math.min(75,s1-10),45);return <>
  <Txt>反例：误用了同一个生成器编号</Txt>
  <Txt x={150} y={370} size={26} color={C.red}>甲</Txt><Fields y={315} scale={.78} focus={1}/><LongId value={IDS.base} y={485} size={56} color={C.red} label="相同时间、编号、序号"/>
  <Txt x={150} y={665} size={26} color={C.red} alpha={p}>乙</Txt><Fields y={610} scale={.78} focus={1} alpha={p}/><LongId value={IDS.base} y={780} size={56} color={C.red} label="相同组合，仍会撞号" alpha={p}/>
 </>}
 if(id===14){const focus=f<d*.3?0:f<d*.55?1:2,settle=go(f,s1+20,35);return <>
  <Txt>三种差异，各管一件事</Txt><Fields focus={focus}/>
  <Result color={[C.teal,C.gold,C.blue][focus]} y={700}>{['不同毫秒 → 时间区分','不同生成器 → 编号区分','同机同毫秒 → 序号区分'][focus]}</Result>
  <Result alpha={settle} color={C.muted} y={820}>前提正确维护，才能分别生成不冲突的编号</Result>
 </>}
 const p=go(f,35,45),brand=go(f,d-55,25);return <>
  <Txt size={58}>下一期：下单成功了，库存怎么没扣？</Txt>
  <Order who="订单库" id="订单已创建" x={520} color={C.teal} alpha={1-brand} label="编号已解决"/>
  <Order who="库存库" id="库存未扣" x={1400} color={C.red} alpha={1-brand} label="另一个库还没完成"/>
  <Line x1={790} x2={1090} p={p} color={C.red} alpha={1-brand}/><Result color={C.red} alpha={p*(1-brand)}>两个库，如何把这件事做完整？</Result>
  <Txt x={960} y={490} center size={68} alpha={brand}>IT小村 · 原创</Txt>
 </>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{
 const f=useCurrentFrame(),sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 78% 10%, #22435D66, transparent 65%)'}}/>
  <Txt x={100} y={62} size={23} color={C.muted}>分布式 · EP.20</Txt><Txt x={1715} y={60} size={25}>IT小村</Txt><Txt x={1715} y={106} center size={18} color={C.muted}>示例数据 · 字段示意</Txt>
  <Scene shot={shot}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.35,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
