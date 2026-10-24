import React from 'react';
import {C} from './theme';
import {Text} from './objects';

// Opening preview only. These are observable chat states, not model reasoning.
export const RefundChat=({frame}:{frame:number})=>{
 const asking=frame>=120;
 const status=frame<9?'':frame<39?'正在查询订单…':frame<57?'订单已查询':frame<90?'订单已查询 · 正在查退款规则…':'订单已查询 · 退款规则已查询';
 const pending=(frame>=9&&frame<39)||(frame>=57&&frame<90);
 return <div style={{position:'absolute',left:130,top:275,width:1660,height:610,border:`1.5px solid ${C.edge}`,borderRadius:22,background:'#111E30',boxSizing:'border-box'}}>
  <Text x={36} y={18} w={460} size={34} weight={720}>退款咨询</Text>
  <Text x={810} y={26} w={430} size={27} color={C.muted}>订单 8124 · 教学示例</Text>
  <Text x={1270} y={29} w={350} size={25} color={C.muted}>先看这次变化</Text>
  <div style={{position:'absolute',left:0,right:0,top:86,borderTop:`1px solid ${C.edge}`}}/>

  <Text x={1235} y={100} w={365} size={24} color={C.muted}>你</Text>
  <div style={{position:'absolute',left:895,top:137,width:710,height:91,borderRadius:'18px 4px 18px 18px',background:'#244A71',border:'1px solid #41688C',boxSizing:'border-box'}}>
   <Text x={28} y={16} w={654} h={58} size={39} weight={600}>这单能申请退款吗？</Text>
  </div>

  {status&&<div style={{position:'absolute',left:60,top:253,height:44}}>
   {pending?<svg width={32} height={32} style={{position:'absolute',left:0,top:3,transform:`rotate(${frame*11}deg)`}}><circle cx={16} cy={16} r={11} fill="none" stroke={C.edge} strokeWidth={3}/><path d="M16 5a11 11 0 0 1 11 11" fill="none" stroke={C.blue} strokeWidth={3} strokeLinecap="round"/></svg>:<Text x={0} y={-1} w={35} size={29} color={C.teal}>✓</Text>}
   <Text x={48} y={0} w={1430} h={44} size={28} color={pending?C.blue:C.muted}>{status}</Text>
  </div>}

  {asking&&<>
   <Text x={62} y={318} w={360} size={24} color={C.teal}>AI 助手</Text>
   <div style={{position:'absolute',left:50,top:357,width:900,height:101,borderRadius:'4px 18px 18px 18px',background:'#173C42',border:`2px solid ${C.teal}`,boxSizing:'border-box'}}>
    <Text x={30} y={19} w={838} h={62} size={43} weight={650}>商品有没有使用过？</Text>
   </div>
  </>}

  <div style={{position:'absolute',left:36,top:507,width:1588,height:73,borderRadius:14,border:`1px solid ${C.edge}`,background:C.bg,boxSizing:'border-box'}}>
   <Text x={24} y={16} w={1260} h={42} size={27} color={C.muted}>输入你的回复…</Text>
   <div style={{position:'absolute',right:10,top:9,width:139,height:53,borderRadius:9,background:'#23364A'}}><Text x={10} y={5} w={119} h={43} size={28} color={C.muted} center>发送</Text></div>
  </div>
 </div>;
};
