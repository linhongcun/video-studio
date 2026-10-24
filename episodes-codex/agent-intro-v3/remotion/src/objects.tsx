import React,{useLayoutEffect,useRef} from 'react';
import {C,FONT} from './theme';
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(f:number,start:number,len=36)=>{const p=clamp((f-start)/Math.max(1,len));return p*p*(3-2*p);};
export const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
export const Text:React.FC<{children:React.ReactNode;x:number;y:number;w:number;size?:number;color?:string;alpha?:number;center?:boolean;weight?:number;h?:number}>=({children,x,y,w,size=36,color=C.text,alpha=1,center=false,weight=550,h})=>{
 const ref=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{const e=ref.current;if(e&&e.clientWidth>0&&(e.scrollWidth>e.clientWidth+2||(h&&e.scrollHeight>e.clientHeight+2)))console.error('COPYFIT overflow',String(children),e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight);},[children,w,size,h]);
 return <div ref={ref} data-fit style={{position:'absolute',left:x,top:y,width:w,height:h,fontFamily:FONT,fontSize:size,lineHeight:1.4,fontWeight:weight,color,opacity:alpha,whiteSpace:'pre-line',textAlign:center?'center':'left',boxSizing:'border-box'}}>{children}</div>;
};
export const Title=({children,alpha=1,color=C.text}:{children:React.ReactNode;alpha?:number;color?:string})=><Text x={130} y={157} w={1660} size={55} weight={720} alpha={alpha} color={color}>{children}</Text>;
export const Note=({children,alpha=1,color=C.muted}:{children:React.ReactNode;alpha?:number;color?:string})=><Text x={150} y={826} w={1620} size={31} alpha={alpha} color={color} center>{children}</Text>;
export const Arrow=({x1,x2,y=560,p=1,color=C.teal,alpha=1}:{x1:number;x2:number;y?:number;p?:number;color?:string;alpha?:number})=>{
 const end=lerp(x1,x2,clamp(p)),dir=x2>x1?1:-1;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M${x1} ${y}H${end}`} stroke={color} strokeWidth={3} fill="none"/>{p>.98&&<path d={`M${end-dir*13} ${y-9}L${end} ${y}L${end-dir*13} ${y+9}`} stroke={color} strokeWidth={3} fill="none"/>}</svg>;
};
export const Packet=({children,x,y=682,w=400,color=C.gold,alpha=1}:{children:React.ReactNode;x:number;y?:number;w?:number;color?:string;alpha?:number})=><div style={{position:'absolute',left:x-w/2,top:y,width:w,minHeight:71,border:`2px solid ${color}`,background:C.bg,borderRadius:12,opacity:alpha,boxSizing:'border-box'}}><Text x={15} y={13} w={w-30} size={30} color={color} center>{children}</Text></div>;
export const Transit=({text,x1,x2,p,y=718,color=C.gold,alpha=1,w=420}:{text:string;x1:number;x2:number;p:number;y?:number;color?:string;alpha?:number;w?:number})=><><Arrow x1={x1} x2={x2} y={y} p={p} color={color} alpha={alpha}/><Packet x={lerp(x1,x2,clamp(p))} y={y-36} w={w} color={color} alpha={alpha}>{text}</Packet></>;
export const Node=({x,name,lines=[],active=false,color=C.teal,alpha=1,w=410,y=370,h=260}:{x:number;name:string;lines?:string[];active?:boolean;color?:string;alpha?:number;w?:number;y?:number;h?:number})=><div style={{position:'absolute',left:x-w/2,top:y,width:w,height:h,opacity:alpha,borderTop:`3px solid ${active?color:C.edge}`,borderBottom:`2px solid ${active?color:C.edge}`,background:active?`linear-gradient(180deg,${color}13,transparent)`:'transparent'}}><Text x={14} y={24} w={w-28} size={37} weight={650} center color={active?color:C.text}>{name}</Text>{lines.map((line,i)=><Text key={i} x={14} y={112+i*50} w={w-28} size={31} center color={active?color:C.text}>{line}</Text>)}</div>;
export const Tick=({x,y,color=C.teal,alpha=1}:{x:number;y:number;color?:string;alpha?:number})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={`M${x-15} ${y}l12 13l25 -29`} stroke={color} strokeWidth={5} fill="none" strokeLinecap="round"/></svg>;
export const Fact:React.FC<{children:React.ReactNode;y:number;color?:string;alpha?:number;fresh?:boolean}>=({children,y,color=C.text,alpha=1,fresh=false})=><div style={{position:'absolute',left:130,top:y,width:600,height:78,opacity:alpha,borderLeft:`3px solid ${fresh?color:C.edge}`,background:fresh?`${color}10`:'transparent'}}><Text x={20} y={15} w={560} size={33} color={color}>{children}</Text></div>;
export const StateBoard=({known,missing,next,active=false,highlight=-1,color=C.teal,missingColor=C.gold,alpha=1}:{known:string[];missing:string;next:string;active?:boolean;highlight?:number;color?:string;missingColor?:string;alpha?:number})=><div style={{opacity:alpha}}>
 <Text x={130} y={327} w={600} size={27} color={C.muted}>已经拿到</Text>
 {known.map((line,i)=><Fact key={i} y={395+i*95} color={i===highlight?color:C.text} fresh={i===highlight}>{line}</Fact>)}
 <Text x={825} y={327} w={345} size={27} color={C.muted} center>还缺什么</Text>
 <Text x={800} y={455} w={395} size={43} color={missingColor} center weight={650}>{missing}</Text>
 <Text x={1310} y={327} w={465} size={27} color={C.muted} center>下一步选什么</Text>
 <div style={{position:'absolute',left:1300,top:421,width:480,minHeight:188,borderTop:`3px solid ${active?color:C.edge}`,borderBottom:`2px solid ${active?color:C.edge}`,background:active?`${color}0B`:'transparent'}}><Text x={20} y={48} w={440} size={55} color={active?color:C.muted} center weight={700}>{next}</Text></div>
</div>;
