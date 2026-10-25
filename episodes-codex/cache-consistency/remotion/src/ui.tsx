import React,{useLayoutEffect,useRef} from 'react';
import {C,FONT,MONO} from './theme';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
const DatabaseMark=createDatabaseIdentity(React);
export const clamp=(v:number)=>Math.min(1,Math.max(0,v));
export const go=(f:number,a:number,n=30)=>{const t=clamp((f-a)/n);return t*t*(3-2*t)};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
type TextProps={children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;alpha?:number;center?:boolean;w?:number};
export const Txt:React.FC<TextProps>=({children,x=130,y=160,size=50,color=C.text,alpha=1,center=false,w})=>{
 const ref=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{const e=ref.current;if(e&&w&&e.scrollWidth>w+2)console.error('COPYFIT overflow',String(children),e.scrollWidth,w)},[children,w]);
 return <div ref={ref} style={{position:'absolute',left:x,top:y,width:w,color,fontSize:size,opacity:alpha,fontWeight:600,lineHeight:1.35,whiteSpace:'nowrap',transform:center?'translateX(-50%)':undefined,textAlign:center?'center':undefined}}>{children}</div>
};
export const Result:React.FC<{children:React.ReactNode;alpha?:number;color?:string}>=({children,alpha=1,color=C.teal})=><Txt x={960} y={782} size={38} center color={color} alpha={alpha} w={1660}>{children}</Txt>;
export const Record:React.FC<{x:number;label:string;database?:boolean;value?:number|string;detail?:string;color?:string;alpha?:number;focus?:number;empty?:boolean}>=({x,label,database=false,value,detail='',color=C.text,alpha=1,focus=0,empty=false})=><div data-record={label} data-value={value} style={{position:'absolute',left:x-195,top:325,width:390,height:365,textAlign:'center',opacity:alpha,transform:`scale(${1+.05*focus})`,transformOrigin:'center'}}>
 <div style={{fontSize:33,color:focus?color:C.muted}}><span style={{position:'relative'}}>{database&&<DatabaseMark size={44} style={{position:'absolute',right:'calc(100% + 10px)',top:'50%',transform:'translateY(-50%)'}}/>}{label}</span></div>
 <div style={{height:160,marginTop:30,fontFamily:MONO,fontSize:value==='等待'?62:112,lineHeight:1.3,color:empty?C.muted:color}}>{empty?'—':value??''}</div>
 <div style={{position:'absolute',left:22,right:22,top:245,borderTop:`2px solid ${focus?color:C.edge}`}}/>
 <div style={{position:'absolute',top:266,left:-25,right:-25,fontSize:27,color:empty?C.muted:color}}>{detail}</div>
 </div>;
export const Link:React.FC<{x1:number;x2:number;p:number;color?:string;y?:number;value?:string;alpha?:number}>=({x1,x2,p,color=C.blue,y=520,value,alpha=1})=><>
 <svg width={1920} height={1080} style={{position:'absolute',inset:0,opacity:alpha,pointerEvents:'none'}}><path d={`M${x1} ${y} H${x2}`} pathLength={1} stroke={color} strokeWidth={3} fill="none" strokeDasharray={1} strokeDashoffset={1-clamp(p)}/><circle cx={mix(x1,x2,p)} cy={y} r={7} fill={color} opacity={p>0&&p<1?1:0}/></svg>
 {p>0&&p<1&&value&&<div style={{position:'absolute',left:mix(x1,x2,p)-65,top:y>=700?y-65-6*Math.sin(Math.PI*p):y-100-35*Math.sin(Math.PI*p),width:130,textAlign:'center',fontSize:47,color,background:C.bg,borderRadius:10,fontFamily:MONO,opacity:alpha}}>{value}</div>}
 </>;
export const DotFlow:React.FC<{f:number;x1:number;x2:number;start?:number;count?:number;y?:number;color?:string}>=({f,x1,x2,start=0,count=3,y=520,color=C.blue})=><>{Array.from({length:count},(_,i)=>{const p=clamp((f-start-i*30)/70);return p>0&&p<1?<div key={i} style={{position:'absolute',left:mix(x1,x2,p)-12,top:y-12,width:24,height:24,borderRadius:'50%',background:color,boxShadow:`0 0 18px ${color}66`}}/>:null})}</>;
export const Status:React.FC<{x:number;y?:number;children:React.ReactNode;color?:string;alpha?:number}>=({x,y=700,children,color=C.muted,alpha=1})=><Txt x={x} y={y} size={28} center color={color} alpha={alpha}>{children}</Txt>;
export const SeriesHeader:React.FC<{ep:number}>=({ep})=><><Txt x={100} y={60} size={23} color={C.muted}>后台缓存 · EP.{String(ep).padStart(2,'0')}</Txt><Txt x={1715} y={60} size={25}>IT小村</Txt><Txt x={1690} y={109} size={20} color={C.muted}>示例数据</Txt></>;
