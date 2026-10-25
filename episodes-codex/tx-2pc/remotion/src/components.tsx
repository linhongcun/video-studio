import React from 'react';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
import {C,FONT,MONO} from './theme';
import {Txt,Chip,Line,MovingChip,ease,lerp} from './primitives';
export {Txt,Chip,Line,MovingChip,ease,lerp};
export const Title=({children,alpha=1,color=C.text}:{children:React.ReactNode;alpha?:number;color?:string})=><Txt x={130} y={184} size={47} color={color} alpha={alpha}>{children}</Txt>;
export const Reset=({children}:{children:React.ReactNode})=><Txt x={130} y={264} size={23} color={C.gold}>{children}</Txt>;
export const Note=({children,color=C.muted,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><>
 <div style={{position:'absolute',left:200,right:200,top:806,height:1,background:C.edge,opacity:alpha}}/>
 <Txt x={960} y={834} width={1600} size={32} center color={color} alpha={alpha}>{children}</Txt>
</>;
export const Coordinator=({state,color=C.blue,visible=true,detail='协调者 · 可靠记录'}:{state:string;color?:string;visible?:boolean;detail?:string})=><div style={{position:'absolute',left:660,top:304,width:600,textAlign:'center',opacity:visible?1:0}}>
 <div style={{color:C.muted,fontSize:23,lineHeight:1.25,marginBottom:8}}>{detail}</div>
 <div style={{background:C.bg,border:`2px solid ${color}`,borderRadius:12,height:52,display:'flex',justifyContent:'center',alignItems:'center',fontSize:27,color}}>{state}</div>
</div>;
export type Mode='empty'|'working'|'prepared'|'committed'|'rejected'|'aborted';
const DatabaseMark=createDatabaseIdentity(React);
export const Participant=({kind,mode='empty',durable=false,alpha=1,pulse=0,wait=false}:{kind:'order'|'stock';mode?:Mode;durable?:boolean;alpha?:number;pulse?:number;wait?:boolean})=>{
 const order=kind==='order',x=order?180:1140,w=600;
 const done=mode==='committed',pending=mode==='prepared'||mode==='working';
 const color=done?C.teal:mode==='rejected'?C.red:pending?C.gold:C.text;
 const value=order?(pending||done?'8124':'—'):(done?'3':'4');
 const state=done?(order?'订单已保存':'库存已保存'):(mode==='rejected'?'本地处理拒绝':mode==='aborted'?(order?'无本单记录':'原库存未改变'):pending?(mode==='prepared'?(durable?'准备就绪 · 等最终决定':'正在可靠保存本地状态'):'修改已就位 · 等准备完成'):(order?'尚无本单记录':'已保存库存'));
 return <div style={{position:'absolute',left:x,top:524,width:w,height:250,textAlign:'center',fontFamily:FONT,opacity:alpha,borderTop:`2px solid ${color}`,borderBottom:`1px solid ${C.edge}`,background:`linear-gradient(180deg,${color}${pulse>0?'18':'08'},transparent)`}}>
  <div style={{position:'absolute',left:0,right:0,top:-44,height:44,fontSize:24,color:C.muted,background:C.bg,display:'flex',alignItems:'center',justifyContent:'center',gap:10}}><DatabaseMark size={44}/><span>{order?'订单库 · 记录 8124':'库存库 · 商品 7042 · 已保存值'}</span></div>
  <div style={{fontFamily:MONO,fontWeight:700,fontSize:order?92:100,color:!order&&pending?C.text:color,lineHeight:'130px',height:130}}>{value}</div>
  <div style={{fontSize:28,color,lineHeight:1.5}}>{state}</div>
  {!order&&pending&&!wait&&!wait&&<div style={{marginTop:15,fontSize:26,color:C.gold}}>本次拟改为 3 · 尚未确认</div>}
  {order&&pending&&!wait&&<div style={{marginTop:15,fontSize:25,color:C.muted}}>已确认记录：无</div>}
  {wait&&<div style={{marginTop:15,fontSize:25,color:C.gold}}>{order?'本单未确认 · 占用仍保留':'拟改 3 · 等决定，占用仍保留'}</div>}
 </div>;
};
export const Token=({x1,y1,x2,y2,p,text,color=C.gold,alpha=1,width=230}:{x1:number;y1:number;x2:number;y2:number;p:number;text:string;color?:string;alpha?:number;width?:number})=><>
 <Line x1={x1} y1={y1+28} x2={x2} y2={y2+28} p={p} color={color} alpha={alpha}/>
 <MovingChip x1={x1} y1={y1} x2={x2} y2={y2} p={p} width={width} color={color} alpha={alpha}>{text}</MovingChip>
</>;
export const Cross=({x,y,color=C.red}:{x:number;y:number;color?:string})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d={`M${x-16} ${y-16}L${x+16} ${y+16}M${x+16} ${y-16}L${x-16} ${y+16}`} fill="none" stroke={color} strokeWidth={5}/></svg>;
