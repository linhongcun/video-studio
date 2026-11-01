import React from 'react';
import {C,FONT} from './theme';
import {HEIGHT,TraceEvent} from './data';
export type TerrainProps={x?:number;baseline?:number;unit?:number;pitch?:number;barWidth?:number;water?:number[];snapshot?:TraceEvent;active?:number|null;activeX?:number|null;showLeft?:boolean;showRight?:boolean;showHeights?:boolean;showColumns?:boolean;ghost?:{i:number;depth:number;count:number}|null;focus?:number[];level?:{value:number;from:number;to:number;color?:string;label?:string};dim?:boolean};
/** All water rectangles begin strictly above the physical grey column. */
export const Terrain=({x=150,baseline=780,unit=108,pitch=164,barWidth=164,water=HEIGHT.map(()=>0),snapshot,active=null,activeX=null,showLeft=false,showRight=false,showHeights=true,showColumns=true,ghost=null,focus=[],level,dim=false}:TerrainProps)=>{
 const cx=(i:number)=>x+i*pitch+barWidth/2;
 return <g data-terrain="fixed-original-columns" data-unit-pixels={unit} fontFamily={FONT}>
  {[1,2,3,4].map(h=><g key={h}><path d={`M ${x-22} ${baseline-h*unit} H ${x+6*pitch+barWidth+12}`} stroke={C.edge} strokeWidth={1.5} opacity={.4}/><text x={x-39} y={baseline-h*unit+8} fill={C.muted} fontSize={21} textAnchor="end">{h}</text></g>)}
  {HEIGHT.map((height,i)=>{
   const focused=!dim||focus.length===0||focus.includes(i);
   const visibleWater=water[i]??0;
   const lKnown=snapshot&&snapshot.index>=i+1;
   const rKnown=snapshot&&snapshot.index>=14-i;
   return <g key={i} opacity={focused?1:.40} data-column={i+1} data-original-height={height} data-committed-water={visibleWater}>
    {Array.from({length:visibleWater},(_,k)=><g key={'w'+k} data-water-unit={`${i},${height+k+1}`}><rect x={x+i*pitch} y={baseline-(height+k+1)*unit} width={barWidth} height={unit} fill="#267CA8"/><rect x={x+i*pitch+3} y={baseline-(height+k+1)*unit+3} width={barWidth-6} height={unit-6} fill="#48B4D4" fillOpacity={.30} stroke="#7DDDF0" strokeOpacity={.5} strokeWidth={2}/></g>)}
    {height>0&&<g><rect x={x+i*pitch} y={baseline-height*unit} width={barWidth} height={height*unit} rx={3} fill="#778696"/><rect x={x+i*pitch+7} y={baseline-height*unit+7} width={barWidth-14} height={height*unit-7} fill="#93A1AE" fillOpacity={.32}/><path d={`M ${x+i*pitch+5} ${baseline-height*unit+4} H ${x+i*pitch+barWidth-5}`} stroke="#BAC5CF" strokeWidth={5}/></g>}
    {showHeights&&<text x={cx(i)} y={height>0?baseline-height*unit+45:baseline+29} textAnchor="middle" fill={height>0?'#F3F6F8':C.muted} fontSize={33} fontWeight={700}>{height}</text>}
    {ghost?.i===i&&Array.from({length:Math.min(ghost.depth,ghost.count)},(_,k)=><rect key={'g'+k} x={x+i*pitch+4} y={baseline-(height+k+1)*unit+4} width={barWidth-8} height={unit-8} rx={3} fill="none" stroke={C.gold} strokeWidth={4} strokeDasharray="12 7" data-pending-water="not-yet-committed"/>)}
    {showLeft&&lKnown&&<g data-left-record={snapshot.left[i]}><path d={`M ${cx(i)-57} ${baseline-snapshot.left[i]*unit} h 49`} stroke={C.gold} strokeWidth={4}/><rect x={cx(i)-62} y={baseline-snapshot.left[i]*unit-34} width={60} height={29} rx={6} fill={C.bg}/><text x={cx(i)-32} y={baseline-snapshot.left[i]*unit-11} textAnchor="middle" fill={C.gold} fontSize={22} fontWeight={700}>L{snapshot.left[i]}</text></g>}
    {showRight&&rKnown&&<g data-right-record={snapshot.right[i]}><path d={`M ${cx(i)+8} ${baseline-snapshot.right[i]*unit} h 49`} stroke={C.teal} strokeWidth={4}/><rect x={cx(i)+2} y={baseline-snapshot.right[i]*unit-34} width={60} height={29} rx={6} fill={C.bg}/><text x={cx(i)+32} y={baseline-snapshot.right[i]*unit-11} textAnchor="middle" fill={C.teal} fontSize={22} fontWeight={700}>R{snapshot.right[i]}</text></g>}
    {showColumns&&<text x={cx(i)} y={baseline+77} textAnchor="middle" fill={active===i?C.gold:C.muted} fontSize={24}>第{i+1}列</text>}
   </g>;
  })}
  {level&&<g data-water-level={level.value}><path d={`M ${x+level.from*pitch-6} ${baseline-level.value*unit} H ${x+level.to*pitch+barWidth+6}`} stroke={level.color??C.blue} strokeWidth={4} strokeDasharray="13 9"/>{level.label&&<text x={x+level.from*pitch+12} y={baseline-level.value*unit-45} fill={level.color??C.blue} fontSize={25}>{level.label}</text>}</g>}
  <path d={`M ${x-25} ${baseline+4} H ${x+6*pitch+barWidth+24}`} stroke="#C1C7CA" strokeWidth={5}/>
  {(active!==null||activeX!==null)&&<g data-current-column={active===null?'moving':active+1}><rect x={x+(activeX??active??0)*pitch-7} y={baseline-4*unit-10} width={barWidth+14} height={4*unit+26} rx={9} fill="none" stroke={C.gold} strokeWidth={3} strokeDasharray="12 8"/><path d={`M ${x+(activeX??active??0)*pitch+barWidth/2} ${baseline-4*unit-38} l -12 -19 h 24 Z`} fill={C.gold}/></g>}
 </g>;
};
