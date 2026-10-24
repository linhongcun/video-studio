import React, {useLayoutEffect, useRef} from 'react';
import {C,FONT} from './theme';
import {ease,lerp,clamp} from './primitives';
export {ease,lerp,clamp};

export const Text:React.FC<{children:React.ReactNode;x:number;y:number;w:number;size?:number;color?:string;alpha?:number;center?:boolean;weight?:number;h?:number}>=({children,x,y,w,size=32,color=C.text,alpha=1,center=false,weight=550,h})=>{
 const ref=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{const e=ref.current;if(e&&e.clientWidth>0&&(e.scrollWidth>e.clientWidth+2||(h&&e.scrollHeight>e.clientHeight+2)))console.error('COPYFIT overflow',String(children),e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight);},[children,w,size,h]);
 return <div ref={ref} data-fit style={{position:'absolute',left:x,top:y,width:w,height:h,color,opacity:alpha,fontFamily:FONT,fontSize:size,fontWeight:weight,lineHeight:1.4,whiteSpace:'pre-line',textAlign:center?'center':'left',boxSizing:'border-box'}}>{children}</div>;
};
export const Title=({children,color=C.text,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><Text x={130} y={185} w={1650} size={47} color={color} alpha={alpha} weight={700}>{children}</Text>;
export const Note=({children,color=C.muted,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><div style={{opacity:alpha}}><div style={{position:'absolute',left:200,right:200,top:797,height:1,background:C.edge}}/><Text x={190} y={821} w={1540} size={30} color={color} center>{children}</Text></div>;
export const Reset=({children,alpha=1}:{children:React.ReactNode;alpha?:number})=><Text x={130} y={268} w={1610} size={24} color={C.gold} alpha={alpha}>{children}</Text>;

export const Actor=({x,name,caption='',lines=[],active=false,color=C.text,alpha=1,y=350,w=390,h=255}:{x:number;name:string;caption?:string;lines?:string[];active?:boolean;color?:string;alpha?:number;y?:number;w?:number;h?:number})=><div style={{position:'absolute',left:x-w/2,top:y,width:w,height:h,opacity:alpha}}>
 <div style={{position:'absolute',inset:0,borderTop:`3px solid ${active?color:C.edge}`,borderBottom:`2px solid ${active?color:C.edge}`,background:active?`linear-gradient(180deg, ${color}12, transparent 80%)`:'transparent'}}/>
 <Text x={10} y={21} w={w-20} size={34} color={active?color:C.text} center weight={650}>{name}</Text>
 {caption&&<Text x={10} y={75} w={w-20} size={23} color={C.muted} center>{caption}</Text>}
 {lines.map((line,i)=><Text key={i} x={12} y={119+i*43} w={w-24} size={29} color={color} center>{line}</Text>)}
</div>;

export const Graph=({model=[],program=[],tool=[],toolName='查询工具',toolCaption='访问实际数据',focus='',color=C.teal,alpha=1}:{model?:string[];program?:string[];tool?:string[];toolName?:string;toolCaption?:string;focus?:string;color?:string;alpha?:number})=><div style={{opacity:alpha}}>
 <Actor x={370} name="模型" caption="接收信息 · 生成下一步" lines={model} active={focus==='model'} color={focus==='model'?color:C.text}/>
 <Actor x={960} name="执行程序" caption="校验请求 · 执行调用" lines={program} active={focus==='program'} color={focus==='program'?color:C.text}/>
 <Actor x={1550} name={toolName} caption={toolCaption} lines={tool} active={focus==='tool'} color={focus==='tool'?color:C.text}/>
</div>;

export const Path=({x1,x2,y=700,p=1,color=C.blue,alpha=1,dashed=false}:{x1:number;x2:number;y?:number;p?:number;color?:string;alpha?:number;dashed?:boolean})=>{
 const end=lerp(x1,x2,clamp(p)),dir=x2>x1?1:-1;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}>
 <path d={`M ${x1} ${y} H ${end}`} stroke={color} strokeWidth={3} fill="none" strokeDasharray={dashed?'10 10':undefined}/>
 {p>.99&&<path d={`M ${end-dir*13} ${y-8} L ${end} ${y} L ${end-dir*13} ${y+8}`} stroke={color} strokeWidth={3} fill="none"/>}
 </svg>;
};

export const Packet=({children,x,y=660,w=340,color=C.gold,alpha=1}:{children:React.ReactNode;x:number;y?:number;w?:number;color?:string;alpha?:number})=><div style={{position:'absolute',left:x-w/2,top:y,width:w,minHeight:66,background:C.bg,border:`2px solid ${color}`,borderRadius:12,boxSizing:'border-box',opacity:alpha}}><Text x={12} y={12} w={w-24} size={28} center color={color}>{children}</Text></div>;

export const Transfer=({text,x1,x2,p,color=C.gold,y=700,alpha=1,w=340}:{text:string;x1:number;x2:number;p:number;color?:string;y?:number;alpha?:number;w?:number})=><>
 <Path x1={x1} x2={x2} y={y} color={color} p={Math.max(.01,p)} alpha={alpha}/>
 <Packet x={lerp(x1,x2,clamp(p))} y={y-34} w={w} color={color} alpha={alpha}>{text}</Packet>
</>;
export const Check=({x,y,color=C.teal,alpha=1}:{x:number;y:number;color?:string;alpha?:number})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M ${x-17} ${y} l 13 14 l 27 -30`} stroke={color} strokeWidth={5} strokeLinecap="round" fill="none"/></svg>;
export const Cross=({x,y,color=C.red,alpha=1}:{x:number;y:number;color?:string;alpha?:number})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M ${x-15} ${y-15} l30 30 m0 -30 l-30 30`} stroke={color} strokeWidth={5} strokeLinecap="round" fill="none"/></svg>;

export const Evidence=({x=1180,y=350,title,rows,highlight=-1,color=C.teal,alpha=1,w=590}:{x?:number;y?:number;title:string;rows:string[];highlight?:number;color?:string;alpha?:number;w?:number})=><div style={{position:'absolute',left:x,top:y,width:w,opacity:alpha}}>
 <Text x={0} y={0} w={w} size={27} color={C.muted}>{title}</Text>
 {rows.map((row,i)=><div key={row} style={{position:'absolute',left:0,top:59+i*68,width:w,height:58,borderLeft:`3px solid ${i===highlight?color:C.edge}`,background:i===highlight?`${color}10`:'transparent'}}><Text x={18} y={7} w={w-30} size={31} color={i===highlight?color:C.text}>{row}</Text></div>)}
</div>;
