import React from 'react';
import {C} from './theme';
import {T} from './primitives';
import {World,Progress,Layout,DOORS,stateAt,selectorAt,ease,mix,clamp} from './monty-model';
const Star=({x,y,size=24}:any)=>{const points=Array.from({length:10},(_,i)=>{const a=-Math.PI/2+i*Math.PI/5,r=i%2?size*.44:size;return`${x+Math.cos(a)*r},${y+Math.sin(a)*r}`;}).join(' ');return <polygon data-prize-icon="true" points={points} fill={C.gold}/>;};
export const DoorRow=({world,progress,layout,alpha=1,analysis=false,showResult=true,emphasis=0}:{world:World;progress:Progress;layout:Layout;alpha?:number;analysis?:boolean;showResult?:boolean;emphasis?:number})=>{
 const state=stateAt(world,progress),l=layout,header=mix(72,48,l.small),bodyY=l.y-l.height/2+header,bodyH=l.height-header,selector=selectorAt(world,progress.swap,l),playerLabelSize=mix(28,21,l.small);
 return <g opacity={alpha} data-world={world.id} data-world-state={JSON.stringify({...state,analysis,layout:l,selector})}>
  {DOORS.map(d=>{
   const x=l.xs[d-1],y=l.y-l.height/2,host=d===world.host?progress.host:0,final=d===world.target?progress.reveal:0,open=Math.max(host,final),isPrize=d===world.prize,contentAlpha=ease((open-.72)/.28),openBy=host>0?'host':final>0?'player':null;
   const clipId=`cover-${world.id}-${d}`;
   return <g key={d} data-door={`${world.id}-door-${d}`} data-door-number={d} data-open-by={openBy??''} data-open-progress={open} data-is-prize={isPrize?'true':'false'}>
    <rect data-door-body="true" x={x-l.width/2} y={y} width={l.width} height={l.height} rx={mix(20,12,l.small)} fill={C.bg} stroke={host===1?C.muted:C.edge} strokeWidth={2}/>
    <path d={`M ${x-l.width/2} ${bodyY} H ${x+l.width/2}`} stroke={C.edge} strokeWidth={1}/>
    <T x={x} y={y+header*.68} size={mix(34,24,l.small)} anchor="middle" color={C.text}>{d}号门</T>
    <g opacity={contentAlpha} data-revealed-content={contentAlpha>.98?(isPrize?'prize':'empty'):'pending'}>
     {isPrize?<><Star x={x-mix(76,42,l.small)} y={bodyY+bodyH*.5} size={mix(32,14,l.small)}/><T x={x+mix(35,18,l.small)} y={bodyY+bodyH*.5+mix(14,9,l.small)} size={mix(40,27,l.small)} color={C.gold} anchor="middle" weight={700}>奖品</T></>:<T x={x} y={bodyY+bodyH*.62} size={mix(56,31,l.small)} color={C.muted} anchor="middle">空</T>}
    </g>
    <clipPath id={clipId}><rect x={x-l.width/2+2} y={bodyY+1} width={(l.width-4)*(1-open)} height={Math.max(0,bodyH-3)} rx={mix(13,7,l.small)}/></clipPath>
    <rect x={x-l.width/2+2} y={bodyY+1} width={(l.width-4)*(1-open)} height={Math.max(0,bodyH-3)} rx={mix(13,7,l.small)} fill={C.surface}/>
    <T x={x} y={bodyY+bodyH*.58} size={mix(34,26,l.small)} color={C.muted} anchor="middle" alpha={1-ease(open/.16)}>未开</T>
    {analysis&&d===world.prize&&<rect data-analysis-prize-mark="true" x={x-l.width/2-4} y={y-4} width={l.width+8} height={l.height+8} rx={mix(24,16,l.small)} fill="none" stroke={C.gold} strokeWidth={2} strokeDasharray="5 6" opacity={.8}/>}
   </g>;
  })}
  {progress.pick>0&&<g opacity={progress.pick} data-player-selector="true" data-selector-stage={selector.stage}>
   <rect data-selector-body="true" x={selector.x-selector.w/2} y={selector.y-selector.h/2} width={selector.w} height={selector.h} rx={mix(23,14,l.small)} fill={selector.stage==='travel'?C.bg:'none'} stroke={C.teal} strokeWidth={mix(4,3,l.small)}/>
   <rect x={selector.x-playerLabelSize*2-8} y={selector.labelY-playerLabelSize*1.2} width={playerLabelSize*4+16} height={playerLabelSize*1.6} rx={5} fill={C.bg}/><T x={selector.x} y={selector.labelY} size={playerLabelSize} color={C.teal} anchor="middle">玩家选择</T>
  </g>}
  {progress.host>0&&progress.host<1&&<g data-host-action="true"><T x={mix(l.xs[world.host-1],1530,l.small)} y={mix(l.y-l.height/2-55,l.y-22,l.small)} size={mix(28,23,l.small)} color={C.gold} anchor="middle">主持人开{world.host}号</T>{l.small<.5&&<path d={`M ${l.xs[world.host-1]} ${l.y-l.height/2-42} V ${l.y-l.height/2-9}`} stroke={C.gold} strokeWidth={3}/>}</g>}
  {!analysis&&progress.pick===1&&<T x={l.xs[world.initial-1]} y={l.y-l.height/2-36} size={27} color={C.teal} anchor="middle">初选1号</T>}
  {analysis&&<g opacity={l.small}><T x={190} y={l.y-13} size={29} color={C.gold}>奖品初始在{world.prize}号</T><T x={190} y={l.y+25} size={22} color={C.muted}>初选1号 · {world.prize===world.initial?'最初选对':'最初选错'}</T></g>}
  {analysis&&showResult&&state.resultCommitted&&<T x={1530} y={l.y+10} size={30} color={state.result==='win'?C.teal:C.red} anchor="middle">换门{state.result==='win'?'赢':'输'}</T>}
 </g>;
};
