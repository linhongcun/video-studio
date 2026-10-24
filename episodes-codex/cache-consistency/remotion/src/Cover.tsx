import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{const q=covers.sizes[size],wide=size==='16x9',portrait=size==='3x4',x=q.content.x,w=q.content.w;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 15%,#17556D88,transparent 65%)'}}/>
 <div style={{position:'absolute',left:q.watermarkZone.x,top:q.watermarkZone.y,fontSize:27,color:C.muted}}>IT小村 / 后台缓存 · EP.09</div>
 <div style={{position:'absolute',left:x,top:portrait?230:200,width:w,fontWeight:800,fontSize:wide?108:portrait?85:70,lineHeight:1.4,letterSpacing:-2}}>后台已改179，<br/><span style={{color:C.gold}}>页面还显示199？</span></div>
 <div style={{position:'absolute',left:x,top:portrait?570:490,fontSize:wide?34:27,color:C.muted}}>同一商品，两份数据</div>
 <div style={{position:'absolute',left:x,top:portrait?715:590,width:w,height:portrait?390:235,borderTop:`2px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,display:'flex',justifyContent:'space-around',alignItems:'center'}}>
 {[['应用','199',C.blue],['临时副本','199',C.gold],['原记录','179',C.teal]].map(([a,b,c])=><div key={a} style={{textAlign:'center'}}><div style={{fontSize:wide?31:24,color:C.muted}}>{a}</div><div style={{fontSize:wide?112:portrait?85:76,fontFamily:MONO,color:c,marginTop:25}}>{b}</div></div>)}
 </div>
 <div style={{position:'absolute',left:x,top:portrait?1230:875,fontSize:portrait?25:21,color:C.muted}}>示例数据 · 同一商品7042</div>
 </AbsoluteFill>;
};
