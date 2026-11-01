import React from 'react';
import {C,FONT} from './theme';

/** Static series motifs: only the teaching objects carry motion. */
export const MysqlBackdrop=()=> <div data-mysql-canvas="true" aria-hidden="true" style={{position:'absolute',inset:0,width:1920,height:1080,pointerEvents:'none',background:C.bg}}>
 <div style={{position:'absolute',inset:0,background:`radial-gradient(ellipse at 82% 15%, ${C.teal}0D, transparent 64%)`}}/>
 <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  <g opacity=".12" fill="none" stroke={C.teal} strokeWidth="1">
   <path d="M1640 0L1920 280M1730 0L1920 190M1820 0L1920 100M0 850L230 1080M0 940L140 1080"/>
  </g>
  <g fill={C.teal} opacity=".12">{[0,1,2,3,4].flatMap(x=>[0,1,2,3].map(y=><circle key={`${x}-${y}`} cx={1780+x*27} cy={12+y*27} r="1.1"/>))}</g>
 </svg>
</div>;

export const MysqlHeader=({ep,scope}:{ep:string;scope:string})=><div data-mysql-header={ep} style={{position:'absolute',inset:0,pointerEvents:'none',fontFamily:FONT}}>
 <svg x="0" width="48" height="48" viewBox="0 0 64 64" style={{position:'absolute',left:110,top:53}} fill={C.surface} stroke={C.teal} strokeWidth="2.5">
  <path d="M5 14V47C5 61 59 61 59 47V14"/><ellipse cx="32" cy="14" rx="27" ry="10"/><path d="M5 30C5 44 59 44 59 30M5 45C5 59 59 59 59 45" fill="none"/>
 </svg>
 <div style={{position:'absolute',left:176,top:53,color:C.teal,fontSize:32,lineHeight:1.5,fontWeight:800,letterSpacing:1}}>MySQL</div>
 <div style={{position:'absolute',left:319,top:57,width:110,height:42,borderRadius:10,color:C.bg,background:C.teal,fontSize:24,lineHeight:'42px',textAlign:'center',fontWeight:800}}>{ep}</div>
 <div data-mysql-scope="true" style={{position:'absolute',left:459,top:64,color:C.muted,fontSize:22,lineHeight:1.5}}>{scope}</div>
 <div style={{position:'absolute',right:110,top:60,color:C.text,fontSize:25,lineHeight:1.4,fontWeight:600}}>IT小村</div>
 <div style={{position:'absolute',left:110,right:110,top:143,height:1,background:C.edge}}/>
</div>;
