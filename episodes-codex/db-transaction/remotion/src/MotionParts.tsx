import React from 'react';
import {C,FONT,MONO} from './theme';
import {Shot} from './data';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
const DatabaseMark=createDatabaseIdentity(React);
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const linear=(f:number,start:number,len=24)=>clamp((f-start)/Math.max(1,len));
export const ease=(v:number)=>{v=clamp(v);return v*v*(3-2*v)};
export const go=(f:number,start:number,len=30)=>ease(linear(f,start,len));
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const fmt=(v:number)=>v.toLocaleString('en-US');
export const sent=(s:Shot,i:number,fallback:number)=>Number(s.cueFrames?.sentences?.[i]??fallback);
export const mark=(s:Shot,key:string)=>Number(s.cueFrames?.[key]??1);
export const Text:React.FC<{children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;opacity?:number;center?:boolean;weight?:number}>=({children,x=130,y=165,size=46,color=C.text,opacity=1,center=false,weight=600})=><div style={{position:'absolute',left:x,top:y,color,opacity,fontSize:size,fontWeight:weight,lineHeight:1.35,whiteSpace:'nowrap',transform:center?'translateX(-50%)':undefined}}>{children}</div>;
export const Term:React.FC<{name:string;f:number;at:number}>=({name,f,at})=>f>=at?<div data-term={name} style={{position:'absolute',left:130,top:165,width:500,height:80,fontSize:58,fontWeight:700,color:C.teal,lineHeight:1.2}}>{name}</div>:null;
export const Check:React.FC<{x:number;y:number;p:number;color?:string}>=({x,y,p,color=C.teal})=><svg style={{position:'absolute',left:x-25,top:y-25}} width="50" height="50" viewBox="0 0 50 50"><path d="m9 26 10 10 23-25" pathLength="1" stroke={color} strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1" strokeDashoffset={1-clamp(p)}/></svg>;
export const Cross:React.FC<{x:number;y:number;p?:number;color?:string}>=({x,y,p=1,color=C.red})=><svg style={{position:'absolute',left:x-23,top:y-23,opacity:clamp(p),transform:`scale(${.8+.2*clamp(p)})`}} width="46" height="46" viewBox="0 0 46 46"><path d="m10 10 26 26M36 10 10 36" stroke={color} strokeWidth="4" strokeLinecap="round"/></svg>;
export const Path:React.FC<{d:string;p:number;color?:string;width?:number;opacity?:number;dash?:boolean}>=({d,p,color=C.teal,width=3,opacity=1,dash=false})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity,pointerEvents:'none'}}><path d={d} pathLength="1" fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeDasharray={dash?'.015 .014':'1'} strokeDashoffset={dash?0:1-clamp(p)} opacity={dash?clamp(p):1}/></svg>;
export const Balance:React.FC<{x:number;y:number;owner:string;value:number;old?:number;p?:number;scale?:number;opacity?:number;color?:string;state?:string}>=({x,y,owner,value,old=value,p=1,scale=1,opacity=1,color=C.text,state=''})=><div data-balance={owner} style={{position:'absolute',left:x-250,top:y-130,width:500,height:260,transform:`scale(${scale})`,transformOrigin:'center',opacity,textAlign:'center'}}>
 <div style={{fontSize:31,fontWeight:500,color:C.muted,lineHeight:1.3}}>{owner}</div>
 <div style={{position:'absolute',left:0,top:43,width:500,height:158,overflow:'hidden',fontSize:132,fontFamily:MONO,fontWeight:650,lineHeight:1.15,letterSpacing:-5,color}}>
 {old!==value&&<div style={{position:'absolute',left:0,right:0,top:-180*clamp(p),opacity:1}}>{fmt(old)}</div>}
 <div style={{position:'absolute',left:0,right:0,top:old===value?0:180*(1-clamp(p)),opacity:1}}>{fmt(value)}</div></div>
 {state&&<div style={{position:'absolute',left:0,right:0,top:211,fontSize:25,color:color===C.text?C.muted:color,lineHeight:1.3}}>{state}</div>}
 </div>;
export const Anchor:React.FC<{x:number;y:number;value:number;opacity?:number;label?:string}>=({x,y,value,opacity=1,label='已确认'})=><div style={{position:'absolute',left:x-160,top:y-60,width:320,textAlign:'center',opacity}}><div style={{fontSize:23,color:C.muted,marginBottom:8}}>{label}</div><div style={{fontSize:54,fontFamily:MONO,color:C.text,lineHeight:1.15,letterSpacing:-2}}>{fmt(value)}</div></div>;
export const Op:React.FC<{text:string;x:number;y:number;color?:string;opacity?:number;scale?:number}>=({text,x,y,color=C.gold,opacity=1,scale=1})=><div style={{position:'absolute',left:x-100,top:y-42,width:200,textAlign:'center',color,opacity,fontFamily:MONO,fontSize:60,fontWeight:650,lineHeight:1.2,transform:`scale(${scale})`,letterSpacing:-2}}>{text}</div>;
export const Operate:React.FC<{f:number;start:number;len?:number;x:number;y:number;text:string;color?:string;gutter?:boolean}>=({f,start,len=50,x,y,text,color=C.gold,gutter=false})=>{const p=go(f,start,len),q=gutter?{x:mix(x-420,x-320,p),y:y-5}:{x:mix(x-270,x,p),y:y-180-55*Math.sin(Math.PI*p)};return <>
 <Path d={gutter?`M${x-410} ${y-5}H${x-200}`:`M${x-270} ${y-180} Q${x-100} ${y-290} ${x} ${y-180}`} p={linear(f,start,len)} color={color} opacity={.4*(1-go(f,start+len,25))}/>
 {f>=start&&<Op text={text} x={q.x} y={q.y} color={color} opacity={go(f,start,10)*(1-go(f,start+len-6,22))} scale={1-.18*p}/>}
 </>};
export const Scope:React.FC<{p:number;x?:number;y?:number;w?:number;h?:number;label?:string;opacity?:number}>=({p,x=370,y=330,w=1180,h=380,label='同一数据库',opacity=1})=><>
 <Path d={`M${x+80} ${y}H${x+28}Q${x} ${y} ${x} ${y+28}V${y+h-28}Q${x} ${y+h} ${x+28} ${y+h}H${x+w-28}Q${x+w} ${y+h} ${x+w} ${y+h-28}V${y+28}Q${x+w} ${y} ${x+w-28} ${y}H${x+w-80}`} p={p} color={C.teal} width={2} opacity={opacity*.55}/>
 <div style={{position:'absolute',left:960,top:y-37,height:44,display:'inline-flex',alignItems:'center',gap:12,transform:'translateX(-50%)',opacity:go(p,0,1)*opacity,color:C.teal,fontSize:27,fontWeight:600,lineHeight:1.35,whiteSpace:'nowrap'}}><DatabaseMark size={44}/><span>{label}</span></div></>;
