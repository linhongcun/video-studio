import React from 'react';
import {C,FONT,MONO} from './theme';
import {Cell,GRID,LAND,TraceEvent,INITIAL,contains,equalCell,componentAt,scanAt,displayCell} from './data';
export const ISLAND_COLORS=['#74AF76','#61D9AD','#EFCA76','#CB9DE6'];
export type MapGeometry={x:number;y:number;cell:number};
export const MAP:MapGeometry={x:225,y:330,cell:127};
export const center=(cell:Cell,g:MapGeometry=MAP)=>({x:g.x+(cell[1]+.5)*g.cell,y:g.y+(cell[0]+.5)*g.cell});
const Text=({x,y,children,size=23,color=C.text,anchor='middle',mono=false,...rest}:any)=><text x={x} y={y} fill={color} fontFamily={mono?MONO:FONT} fontSize={size} textAnchor={anchor} {...rest}>{children}</text>;
const land=(r:number,c:number)=>GRID[r]?.[c]==='1';
const shore=(cell:Cell,g:MapGeometry,inset:number,color:string)=>{
 const [r,c]=cell,x=g.x+c*g.cell,y=g.y+r*g.cell,size=g.cell;
 return <g key={cell.join(',')}>
  <rect x={x+inset} y={y+inset} width={size-2*inset} height={size-2*inset} rx={22} fill={color}/>
  {land(r,c+1)&&<rect x={x+size/2} y={y+inset} width={size/2+1} height={size-2*inset} fill={color}/>}
  {land(r,c-1)&&<rect x={x-1} y={y+inset} width={size/2+1} height={size-2*inset} fill={color}/>}
  {land(r+1,c)&&<rect x={x+inset} y={y+size/2} width={size-2*inset} height={size/2+1} fill={color}/>}
  {land(r-1,c)&&<rect x={x+inset} y={y-1} width={size-2*inset} height={size/2+1} fill={color}/>}
 </g>;
};
export const NeighborArrow=({from,to,geometry:g=MAP,color=C.gold,alpha=1,blocked=false}: {from:Cell;to:Cell;geometry?:MapGeometry;color?:string;alpha?:number;blocked?:boolean})=>{
 const a=center(from,g),b=center(to,g),dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy),ux=dx/length,uy=dy/length;
 const start={x:a.x+ux*g.cell*.30,y:a.y+uy*g.cell*.30},end={x:Math.max(g.x-8,Math.min(g.x+5*g.cell+8,b.x-ux*g.cell*.28)),y:Math.max(g.y-8,Math.min(g.y+4*g.cell+8,b.y-uy*g.cell*.28))};
 const angle=Math.atan2(dy,dx)*180/Math.PI;
 return <g opacity={alpha} data-four-neighbor={`${from.join(',')}->${to.join(',')}`}>
  <path d={`M ${start.x} ${start.y} L ${end.x} ${end.y}`} stroke={color} strokeWidth={5} strokeLinecap="round" fill="none"/>
  {blocked?<g transform={`translate(${end.x} ${end.y})`}><path d="M -8 -8 L 8 8 M 8 -8 L -8 8" stroke={color} strokeWidth={4} strokeLinecap="round"/></g>:<path d="M -11 -7 L 0 0 L -11 7" transform={`translate(${end.x} ${end.y}) rotate(${angle})`} stroke={color} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" fill="none"/>}
 </g>;
};
export const DiagonalGap=({from,to,geometry:g=MAP,alpha=1}: {from:Cell;to:Cell;geometry?:MapGeometry;alpha?:number})=>{
 const a=center(from,g),b=center(to,g),x=(a.x+b.x)/2,y=(a.y+b.y)/2;
 return <g opacity={alpha} data-diagonal-not-connected={`${from.join(',')}->${to.join(',')}`}>
  <path d={`M ${a.x+g.cell*.28} ${a.y+g.cell*.28} L ${x-13} ${y-13} M ${x+13} ${y+13} L ${b.x-g.cell*.28} ${b.y-g.cell*.28}`} stroke={C.red} strokeWidth={3} strokeDasharray="6 7"/>
  <circle cx={x} cy={y} r={20} fill="#15394E" stroke={C.red} strokeWidth={2}/><path d={`M ${x-8} ${y-8} l 16 16 M ${x+8} ${y-8} l -16 16`} stroke={C.red} strokeWidth={3.5} strokeLinecap="round"/>
 </g>;
};
/** Terrain is immutable; only ownership/state overlays change. */
export const IslandMap=({geometry:g=MAP,snapshot=INITIAL,previewComponents=false,previewIds,showScan=false,showState=true,showCoordinates=true,showGrid=true,showNeighbor=true,focusCells=[],showNumbers=false}: {
 geometry?:MapGeometry;snapshot?:TraceEvent;previewComponents?:boolean;previewIds?:number[];showScan?:boolean;showState?:boolean;showCoordinates?:boolean;showGrid?:boolean;showNeighbor?:boolean;focusCells?:Cell[];showNumbers?:boolean;
})=>{
 const scan=showScan?scanAt(snapshot):null,cols=GRID[0].length,rows=GRID.length;
 const color=(cell:Cell)=>{const id=componentAt(cell);return (previewComponents||previewIds?.includes(id)||contains(snapshot.seen,cell))&&id?ISLAND_COLORS[id]:ISLAND_COLORS[0];};
 return <g data-sea-land-map="immutable-original-grid" data-trace-event={snapshot.index}>
  <rect x={g.x-26} y={g.y-26} width={cols*g.cell+52} height={rows*g.cell+52} rx={28} fill="#10394F" stroke="#315F73" strokeWidth={2}/>
  {GRID.flatMap((row,r)=>row.map((value,c)=>value==='0'?<g key={`water-${r}-${c}`} opacity={.27}><path d={`M ${g.x+c*g.cell+g.cell*.25} ${g.y+r*g.cell+g.cell*.45} q ${g.cell*.1} ${g.cell*.045}, ${g.cell*.2} 0 t ${g.cell*.2} 0`} fill="none" stroke="#69ADBD" strokeWidth={2}/><path d={`M ${g.x+c*g.cell+g.cell*.37} ${g.y+r*g.cell+g.cell*.57} h ${g.cell*.25}`} fill="none" stroke="#69ADBD" strokeWidth={1.5}/></g>:null))}
  {LAND.map(cell=>shore(cell,g,10,'#CDB783'))}
  {LAND.map(cell=>shore(cell,g,15,color(cell)))}
  {LAND.map(cell=>{const p=center(cell,g);return <path key={`terrain-${cell}`} d={`M ${p.x-22} ${p.y+9} q 16 -17, 32 -3 t 19 -4`} fill="none" stroke="#153D2D" strokeWidth={2} opacity={.22}/>;})}
  {showGrid&&<g opacity={.17}>{Array.from({length:cols+1},(_,i)=><path key={`col-${i}`} d={`M ${g.x+i*g.cell} ${g.y} v ${rows*g.cell}`} stroke="#ACD2D5" strokeWidth={1.5}/>)}{Array.from({length:rows+1},(_,i)=><path key={`row-${i}`} d={`M ${g.x} ${g.y+i*g.cell} h ${cols*g.cell}`} stroke="#ACD2D5" strokeWidth={1.5}/>)}</g>}
  {showCoordinates&&<g>{Array.from({length:cols},(_,i)=><Text key={`column-${i}`} x={g.x+(i+.5)*g.cell} y={g.y-11} size={21} color={C.muted}>{i+1}</Text>)}{Array.from({length:rows},(_,i)=><Text key={`row-${i}`} x={g.x-13} y={g.y+(i+.5)*g.cell+7} size={21} anchor="end" color={C.muted}>{i+1}</Text>)}</g>}
  {showNumbers&&GRID.flatMap((row,r)=>row.map((value,c)=>{const p=center([r,c],g);return <Text key={`digit-${r}-${c}`} x={p.x} y={p.y+12} size={31} mono color={value==='1'?'#173C2C':'#96B6C3'}>{value}</Text>;}))}
  {focusCells.map(cell=>{const p=center(cell,g);return <rect key={`focus-${cell}`} x={p.x-g.cell*.42} y={p.y-g.cell*.42} width={g.cell*.84} height={g.cell*.84} rx={16} stroke={C.gold} strokeWidth={4} fill="none"/>;})}
  {showState&&LAND.map(cell=>{
   const p=center(cell,g),known=contains(snapshot.seen,cell),pending=contains(snapshot.stack,cell),expanded=contains(snapshot.expanded,cell),active=equalCell(snapshot.active,cell),owner=ISLAND_COLORS[componentAt(cell)]??C.teal;
   return <g key={`state-${cell}`} data-cell={cell.join(',')} data-owned={known} data-pending={pending} data-expanded={expanded} data-active={active}>
    {known&&<g transform={`translate(${p.x+g.cell*.25} ${p.y-g.cell*.25})`}><circle r={12} fill="#17392F" stroke={owner} strokeWidth={1.5}/><path d="M -6 0 l 4 4 l 8 -9" stroke={owner} strokeWidth={3} fill="none" strokeLinecap="round" strokeLinejoin="round"/></g>}
    {pending&&<rect x={p.x-g.cell*.36} y={p.y-g.cell*.36} width={g.cell*.72} height={g.cell*.72} rx={15} fill="none" stroke={C.gold} strokeWidth={3} strokeDasharray="8 6"/>}
    {active&&<rect x={p.x-g.cell*.40} y={p.y-g.cell*.40} width={g.cell*.80} height={g.cell*.80} rx={19} fill="none" stroke={C.text} strokeWidth={4.5}/>}
    {expanded&&<circle cx={p.x-g.cell*.25} cy={p.y+g.cell*.25} r={5} fill="#17392F"/>}
   </g>;
  })}
  {scan&&<g data-outer-scan={displayCell(scan)}>{(()=>{const p=center(scan,g),d=g.cell*.49,k=21;return <><path d={`M ${p.x-d} ${p.y-d+k} v -${k} h ${k} M ${p.x+d-k} ${p.y-d} h ${k} v ${k} M ${p.x+d} ${p.y+d-k} v ${k} h -${k} M ${p.x-d+k} ${p.y+d} h -${k} v -${k}`} stroke={C.blue} strokeWidth={4} fill="none"/><circle cx={p.x-d} cy={p.y-d} r={5} fill={C.blue}/></>;})()}</g>}
  {showNeighbor&&snapshot.from&&snapshot.cell&&snapshot.reason!=='boundary'&&['neighbor_check','mark','push'].includes(snapshot.action)&&<NeighborArrow from={snapshot.from} to={snapshot.cell} geometry={g} color={snapshot.reason==='water'||snapshot.reason==='boundary'?C.red:snapshot.reason==='seen'?C.gold:C.text} blocked={snapshot.reason==='water'||snapshot.reason==='boundary'||snapshot.reason==='seen'}/>}
 </g>;
};
