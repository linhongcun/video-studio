import React from 'react';
import {Text} from './objects';
import {C,PAGE} from './theme';

// This is the taught consultation function, not a shell around the mechanism.
export const Chat=({compact=false,user='你',state='preparing',showState=true,showReply=false,replyAlpha=1}:{compact?:boolean;user?:string;state?:'preparing'|'success'|'denied';showState?:boolean;showReply?:boolean;replyAlpha?:number})=>{
 const w=compact?1120:1660,questionW=compact?840:1050,qx=w-questionW-45;
 const answer=state==='denied'?'当前用户没有读取权限，未查询订单。':'这笔订单已签收 3 天。';
 return <div style={{position:'absolute',left:130,top:282,width:w,height:598,border:`1.5px solid ${C.edge}`,borderRadius:22,background:PAGE.bg,boxSizing:'border-box'}}>
  <Text x={35} y={20} w={470} size={34} weight={720}>退款咨询</Text>
  <Text x={w-535} y={28} w={490} size={26} color={C.muted}>订单 8124 · 教学示例</Text>
  <div style={{position:'absolute',left:0,right:0,top:86,borderTop:`1px solid ${C.edge}`}}/>
  <Text x={w-350} y={104} w={300} size={24} color={C.muted}>{user}</Text>
  <div style={{position:'absolute',left:qx,top:144,width:questionW,height:88,borderRadius:'18px 4px 18px 18px',background:'#244A71',border:'1px solid #41688C'}}>
   <Text x={24} y={17} w={questionW-48} h={57} size={compact?37:40} weight={600}>帮我查一下，这单签收几天了？</Text>
  </div>
  {showState&&<Text x={48} y={262} w={w-96} size={27} color={state==='denied'?C.red:state==='success'?C.teal:C.gold}>{state==='preparing'?'助手状态：准备查询订单 8124':state==='success'?'查询结果已交回助手':'程序返回：读取权限未通过'}</Text>}
  {showReply&&<div style={{opacity:replyAlpha}}>
   <Text x={49} y={326} w={300} size={24} color={state==='denied'?C.red:C.teal}>AI 助手</Text>
   <div style={{position:'absolute',left:45,top:366,width:state==='denied'?w-90:Math.min(1010,w-90),height:94,borderRadius:'4px 18px 18px 18px',background:state==='denied'?'#3D2632':'#173C42',border:`1.5px solid ${state==='denied'?C.red:C.teal}`}}>
    <Text x={24} y={18} w={state==='denied'?w-138:Math.min(962,w-138)} h={59} size={state==='denied'?37:43} weight={650}>{answer}</Text>
   </div>
  </div>}
  <div style={{position:'absolute',left:35,right:35,top:505,height:65,borderRadius:13,border:`1px solid ${PAGE.border}`,background:PAGE.field}}>
   <Text x={24} y={13} w={w-315} h={43} size={27} color={C.muted}>输入你的问题…</Text>
   <div style={{position:'absolute',right:9,top:8,width:123,height:49,borderRadius:8,background:'#23364A'}}><Text x={8} y={4} w={107} size={27} color={C.muted} center>发送</Text></div>
  </div>
 </div>;
};
