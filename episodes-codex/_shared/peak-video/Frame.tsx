import React from 'react';
import style from './style-v1.json';
import {C,FONT} from './theme';

/** Exact-size transparent calibration canvas, with static cover-family corner lines. */
export const PeakBackdrop=()=> <g aria-hidden="true">
 <rect data-peak-canvas="true" width="1920" height="1080" fill="transparent"/>
 <g fill="none" strokeWidth="2" opacity=".22">
  <path d="M1828 0V122H1920M1868 145V260M38 705V915M132 1048H293" stroke={C.yellow}/>
  <path d="M1624 12H1808M1896 144V325M71 785V915M0 938H110V1080M132 1066H405" stroke={C.cyan}/>
 </g>
</g>;

/** No subject is added by default: technical names retain their original introduction. */
export const PeakHeader=({ep,title='',chapter=''}:{ep:number;title?:string;chapter?:string})=> {
 if(!Number.isInteger(ep)||ep<1)throw Error('PeakHeader requires a real episode number');
 return <g data-peak-header="true" fontFamily={FONT}>
  <g data-peak-mark="true" stroke={C.cyan} strokeWidth="5" fill="none" strokeLinecap="round">
   <path d="M121 21H177M121 43H162M121 65H177"/>
   <path d="M168 35L179 43L168 51"/>
  </g>
  <text x="199" y="60" fontSize="34" fill={C.cyan} fontWeight="800">{style.seriesLabel}</text>
  <rect x="650" y="22" width="127" height="47" rx="10" fill={C.cyan}/>
  <text x="713.5" y="55" fontFamily={style.fonts.brand} fontSize="26" fill={C.bg} fontWeight="750" textAnchor="middle">EP.{String(ep).padStart(2,'0')}</text>
  {title&&<text data-peak-subject="true" x="805" y="56" fontSize="26" fill={C.text} fontWeight="650">{title}</text>}
  {chapter&&<text data-peak-chapter="true" x={title?'1075':'805'} y="56" fontSize="24" fill={C.muted}>{chapter}</text>}
  <text x="1805" y="56" fontFamily={style.fonts.brand} fontSize="25" fill={C.muted} fontWeight="650" textAnchor="end">{style.brand}</text>
  <path d="M115 75H1805" fill="none" stroke={C.edge} strokeWidth="1.5"/>
 </g>;
};
