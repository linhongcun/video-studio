import React from 'react';
import {C,FONT,MONO} from './theme';
import {Txt,Chip,Line,LocalBoundary,MovingChip,ease,lerp} from './primitives';
export {Txt,Chip,Line,LocalBoundary,MovingChip,ease,lerp};
export const TITLE_Y=190;
export const Title=({children,color=C.text,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><Txt x={130} y={TITLE_Y} size={46} color={color} alpha={alpha}>{children}</Txt>;
export const Note=({children,color=C.muted,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><>
 <div style={{position:'absolute',left:230,right:230,top:795,height:1,background:C.edge,opacity:alpha}}/>
 <Txt x={960} y={823} width={1600} center size={31} color={color} alpha={alpha}>{children}</Txt>
</>;
export const Reset=({children='重新演示 · 从库存 4 开始'}:{children?:React.ReactNode})=><Txt x={130} y={276} size={23} color={C.gold}>{children}</Txt>;
export const Order=({x=520,y=405,exists=false,state='尚未提交',color=C.text,alpha=1,detail='',pending=false}:{x?:number;y?:number;exists?:boolean;state?:string;color?:string;alpha?:number;detail?:string;pending?:boolean})=><div style={{position:'absolute',left:x-235,top:y,width:470,textAlign:'center',opacity:alpha,fontFamily:FONT}}>
 <div style={{fontSize:26,color:C.muted}}>订单记录</div>
 <div style={{fontFamily:MONO,fontSize:94,fontWeight:700,lineHeight:'135px',height:135,color}}>{exists||pending?'8124':'—'}</div>
 <div style={{height:2,background:color,margin:'0 20px 20px',opacity:(exists||pending)?0.8:0.3}}/>
 <div style={{fontSize:31,lineHeight:1.5,color}}>{state}</div>
 {detail&&<div style={{fontSize:23,color:C.muted,lineHeight:1.6,marginTop:13}}>{detail}</div>}
</div>;
export const Stock=({x=1400,y=405,value=4,state='原库存',color=C.text,alpha=1,detail='',units=true}:{x?:number;y?:number;value?:number|string;state?:string;color?:string;alpha?:number;detail?:string;units?:boolean})=><div style={{position:'absolute',left:x-235,top:y,width:470,textAlign:'center',opacity:alpha,fontFamily:FONT}}>
 <div style={{fontSize:26,color:C.muted}}>商品 7042 · 可用库存</div>
 <div style={{fontFamily:MONO,fontSize:108,fontWeight:700,lineHeight:'135px',height:135,color}}>{value}</div>
 <div style={{height:2,background:color,margin:'0 20px 20px',opacity:.65}}/>
 <div style={{fontSize:31,lineHeight:1.5,color}}>{state}</div>
 {detail&&<div style={{fontSize:23,color:C.muted,lineHeight:1.6,marginTop:13}}>{detail}</div>}
 {units&&typeof value==='number'&&<div style={{display:'flex',gap:13,justifyContent:'center',marginTop:22}}>{Array.from({length:Math.max(4,value)},(_,n)=>n).map(n=><div key={n} style={{width:27,height:8,borderRadius:5,background:n<value?color:C.edge}}/>)}</div>}
</div>;
export const SplitBoundaries=({left='订单库 · 独立提交',right='库存库 · 独立提交',colorLeft=C.edge,colorRight=C.edge,p=1}:{left?:string;right?:string;colorLeft?:string;colorRight?:string;p?:number})=><>
 <LocalBoundary x={235} y={365} w={570} h={385} label={left} color={colorLeft} p={p}/>
 <LocalBoundary x={1115} y={365} w={570} h={385} label={right} color={colorRight} p={p}/>
</>;
export const Cross=({x,y,alpha=1,color=C.red}:{x:number;y:number;alpha?:number;color?:string})=><svg style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}} width={1920} height={1080}><path d={`M${x-17} ${y-17}L${x+17} ${y+17}M${x+17} ${y-17}L${x-17} ${y+17}`} stroke={color} strokeWidth={5} strokeLinecap="round"/></svg>;
export const Check=({x,y,alpha=1,color=C.teal}:{x:number;y:number;alpha?:number;color?:string})=><svg style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}} width={1920} height={1080}><path d={`M${x-17} ${y}L${x-4} ${y+14}L${x+22} ${y-15}`} stroke={color} strokeWidth={5} strokeLinecap="round" fill="none"/></svg>;
