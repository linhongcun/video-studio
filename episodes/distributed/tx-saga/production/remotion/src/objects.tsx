import React from 'react';
import {C,FONT,MONO} from './theme';
import {Txt,Chip,Line,LocalBoundary,MovingChip,ease,lerp} from './primitives';
export {Txt,Chip,Line,LocalBoundary,MovingChip,ease,lerp};
export const Title=({children,color=C.text,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><Txt x={130} y={190} size={46} color={color} alpha={alpha}>{children}</Txt>;
export const Reset=({children}:{children:React.ReactNode})=><Txt x={130} y={278} size={23} color={C.gold}>{children}</Txt>;
export const Note=({children,color=C.muted,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><>
 <div style={{position:'absolute',left:230,right:230,top:797,height:1,background:C.edge,opacity:alpha}}/>
 <Txt x={960} y={823} width={1600} center size={31} color={color} alpha={alpha}>{children}</Txt>
</>;
export const Account=({value=1000,state='账户初始余额',color=C.text,alpha=1,history='none',pendingRefund=false,mark=false,x=520}:{value?:number;state?:string;color?:string;alpha?:number;history?:'none'|'debit'|'refund';pendingRefund?:boolean;mark?:boolean;x?:number})=><div style={{position:'absolute',left:x-250,top:370,width:500,textAlign:'center',opacity:alpha,fontFamily:FONT}}>
 <div style={{fontSize:25,color:C.muted}}>账户余额 · 元</div>
 <div style={{fontFamily:MONO,fontSize:108,fontWeight:700,height:132,lineHeight:'132px',color}}>{value}</div>
 <div style={{height:2,background:color,margin:'0 22px 15px',opacity:.6}}/>
 <div style={{fontSize:31,lineHeight:1.45,color}}>{state}</div>
 {history!=='none'&&<div style={{margin:'23px 45px 0',borderTop:`1px solid ${C.edge}`,paddingTop:10,fontSize:23,lineHeight:1.5,color:C.muted,textAlign:'left',display:'flex',justifyContent:'space-between'}}><span>原扣款 · 已提交</span><span style={{fontFamily:MONO}}>−200</span></div>}
 {(history==='refund'||pendingRefund)&&<div style={{margin:'4px 45px 0',fontSize:23,lineHeight:1.5,color:pendingRefund?C.gold:C.teal,textAlign:'left',display:'flex',justifyContent:'space-between'}}><span>{pendingRefund?'新退款 · 待执行':'新退款 · 已提交'}</span><span style={{fontFamily:MONO}}>＋200</span></div>}
 {mark&&<div style={{fontSize:19,lineHeight:1.6,color:C.teal,marginTop:7}}>R8124 · 已处理，重复不再退款</div>}
</div>;
export const Stock=({value=4,state='可用库存',alpha=1,color=C.text}:{value?:number;state?:string;alpha?:number;color?:string})=><div style={{position:'absolute',left:1150,top:370,width:500,textAlign:'center',opacity:alpha,fontFamily:FONT}}>
 <div style={{fontSize:25,color:C.muted}}>商品7042 · 可用库存</div>
 <div style={{fontFamily:MONO,fontSize:108,fontWeight:700,height:132,lineHeight:'132px',color}}>{value}</div>
 <div style={{height:2,background:color,margin:'0 22px 15px',opacity:.6}}/>
 <div style={{fontSize:31,lineHeight:1.45,color}}>{state}</div>
 <div style={{display:'flex',gap:13,justifyContent:'center',marginTop:25}}>{[0,1,2,3].map(i=><div key={i}style={{width:34,height:9,borderRadius:5,background:i<value?color:C.edge}}/>)}</div>
</div>;
export const Cross=({x=1400,y=700,color=C.red,alpha=1}:{x?:number;y?:number;color?:string;alpha?:number})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M${x-17} ${y-17}L${x+17} ${y+17}M${x+17} ${y-17}L${x-17} ${y+17}`} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round"/></svg>;
export const Check=({x=960,y=700,color=C.teal}:{x?:number;y?:number;color?:string})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d={`M${x-18} ${y}L${x-4} ${y+14}L${x+22} ${y-15}`} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round"/></svg>;
