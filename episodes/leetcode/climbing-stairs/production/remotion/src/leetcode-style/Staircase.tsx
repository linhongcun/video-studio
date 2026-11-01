import React from 'react';
import {C,FONT,MONO} from './theme';

export type StairGeometry={x:number;baseY:number;width:number;rise:number;steps:number};
export const clamp=(p:number)=>Math.max(0,Math.min(1,p));
export const smooth=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
export const foot=(g:StairGeometry,step:number)=>({x:g.x+(step-.5)*g.width,y:g.baseY-step*g.rise});
export const MAIN_STAIRS:StairGeometry={x:405,baseY:782,width:177,rise:61,steps:6};
const Text=({x,y,children,size=25,color=C.text,anchor='middle',mono=false,...rest}:any)=><text x={x} y={y} fill={color} fontFamily={mono?MONO:FONT} fontSize={size} textAnchor={anchor} {...rest}>{children}</text>;

/** A literal side elevation: footprints land on the horizontal tread. */
export const Staircase=({geometry:g,counts,focus={},target=0,dimCountsBefore=0,labelOffset=0,showOrigin=true,showUnknown=true,terminalLabel='终点',countSize=27,numberSize=20}: {
 geometry:StairGeometry;counts?:(number|null)[];focus?:Record<number,string>;target?:number;dimCountsBefore?:number;labelOffset?:number;showOrigin?:boolean;showUnknown?:boolean;terminalLabel?:string;countSize?:number;numberSize?:number;
})=>{
 const endX=g.x+g.steps*g.width;
 let shape=`M ${g.x-g.width} ${g.baseY} H ${g.x}`;
 for(let i=1;i<=g.steps;i++)shape+=` V ${g.baseY-i*g.rise} H ${g.x+i*g.width}`;
 shape+=` V ${g.baseY+19} H ${g.x-g.width} Z`;
 return <g data-literal-staircase={g.steps} data-label-offset={labelOffset}>
  <path d={shape} fill={C.surface} stroke={C.edge} strokeWidth={2.5} strokeLinejoin="round"/>
  <path d={`M ${g.x-g.width-28} ${g.baseY+20} H ${endX+30}`} stroke={C.edge} strokeWidth={2}/>
  {Array.from({length:g.steps},(_,i)=>{
   const k=i+1,p=foot(g,k),x=g.x+i*g.width,color=focus[k]??(target===k?C.gold:C.edge),dim=k<dimCountsBefore ? .2 : 1;
   return <g key={k} data-physical-step={k+labelOffset} data-method-count={counts?.[i]??'not-computed'}>
    <rect x={x+1.5} y={p.y+1.5} width={g.width-3} height={Math.min(g.rise-3,58)} fill={focus[k]?focus[k]+'0B':C.surface}/>
    <path d={`M ${x} ${p.y} H ${x+g.width}`} stroke={focus[k]??(target===k?C.gold:C.muted)} strokeWidth={focus[k]||target===k?5:3}/>
    <Text x={x+12} y={p.y+21} size={numberSize} anchor="start" color={C.muted}>第{k+labelOffset}阶</Text>
    {counts&&<g opacity={dim}>{counts[i]!==null&&counts[i]!==undefined?<Text x={p.x+23} y={p.y+49} size={countSize} color={focus[k]??(target===k?C.gold:C.text)}><tspan fontFamily={MONO}>{counts[i]}</tspan>种</Text>:showUnknown&&<Text x={p.x+23} y={p.y+49} size={Math.min(countSize,23)} color={C.muted}>待算</Text>}</g>}
   </g>;
  })}
  {showOrigin&&<><Text x={foot(g,0).x} y={g.baseY+53} size={23} color={C.muted}>起点 · 0阶</Text><path d={`M ${foot(g,0).x} ${g.baseY-6} v 12`} stroke={C.muted} strokeWidth={3}/></>}
  {terminalLabel&&<g data-terminal={g.steps+labelOffset}><path d={`M ${endX-20} ${g.baseY-g.steps*g.rise-5} v -75`} stroke={C.teal} strokeWidth={3}/><path d={`M ${endX-20} ${g.baseY-g.steps*g.rise-80} h -45 l 12 13 l -12 13 h 45 Z`} fill={C.teal}/><Text x={endX-28} y={g.baseY-g.steps*g.rise-94} size={23} color={C.teal}>{terminalLabel}</Text></g>}
 </g>;
};

export const Walker=({x,y,color=C.gold,scale=1,moving=0,alpha=1}:{x:number;y:number;color?:string;scale?:number;moving?:number;alpha?:number})=>{
 const swing=Math.sin(moving*Math.PI*2)*7;
 return <g transform={`translate(${x} ${y}) scale(${scale})`} opacity={alpha} data-walker-foot={`${x},${y}`}>
  <ellipse cx="0" cy="1" rx="17" ry="3" fill={color} opacity=".2"/><circle cx="1" cy="-61" r="10" fill={color}/>
  <path d={`M 0 -44 L -2 -24 M -1 -39 L ${-15-swing*.4} -28 M -1 -39 L ${14+swing*.4} -33 M -2 -24 L ${-11+swing} -12 L -11 -1 M -2 -24 L ${11-swing} -11 L 11 -1`} stroke={color} strokeWidth="6.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
  <path d="M -16 -1 h 9 M 7 -1 h 10" stroke={C.text} strokeWidth="3" strokeLinecap="round"/>
 </g>;
};
export const hopCurve=(g:StairGeometry,from:number,to:number)=>{
 const a=foot(g,from),b=foot(g,to),c={x:(a.x+b.x)/2,y:b.y-(to-from)*g.rise/2-28};
 return {a,b,c,d:`M ${a.x} ${a.y} Q ${c.x} ${c.y}, ${b.x} ${b.y}`};
};
/** The trajectory clears each riser; a two-step hop has no middle landing. */
export const Hop=({geometry:g,from,to,progress,color=C.teal,showWalker=true,scale=1,alpha=1,trail=true}:{geometry:StairGeometry;from:number;to:number;progress:number;key?:string|number;color?:string;showWalker?:boolean;scale?:number;alpha?:number;trail?:boolean})=>{
 const {a,b,c,d}=hopCurve(g,from,to),raw=clamp(progress),p=smooth((raw-.10)/.68),one=1-p;
 const x=one*one*a.x+2*one*p*c.x+p*p*b.x,y=one*one*a.y+2*one*p*c.y+p*p*b.y;
 return <g opacity={alpha} data-hop={`${from}-${to}`} data-hop-progress={raw}>
  {trail&&<path d={d} fill="none" stroke={color} strokeWidth={4} strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1-p} opacity={.85}/>}
  {p>=1&&<ellipse cx={b.x} cy={b.y-1} rx={12} ry={3} fill={color}/>}
  {showWalker&&<Walker x={x} y={y} color={color} scale={scale} moving={raw>.1&&raw<.78?raw*2:0}/>}
 </g>;
};
export const Route=({geometry:g,path,progress=1,lastColor=C.gold,highlightLast=false,walkerScale=1,alpha=1}:{geometry:StairGeometry;path:number[];progress?:number;lastColor?:string;highlightLast?:boolean;walkerScale?:number;alpha?:number})=>{
 let step=0;const total=clamp(progress)*path.length,current=Math.min(path.length-1,Math.floor(total));
 return <g opacity={alpha} data-walking-route={path.join(',')}>
  {path.map((stride,i)=>{const from=step,to=step+stride;step=to;const local=clamp(total-i),last=i===path.length-1,color=highlightLast&&last?lastColor:C.blue;return <Hop key={i} geometry={g} from={from} to={to} progress={local} color={color} showWalker={i===current} scale={walkerScale} alpha={local>0||i===current?1:0}/>;})}
 </g>;
};
