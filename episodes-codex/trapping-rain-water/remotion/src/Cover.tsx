import React from 'react';
import {Terrain} from './Terrain';
import {FINAL} from './data';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Vertical=()=> <g fontFamily={FONT}>
 <text x={125} y={112} fill={C.muted} fontSize={32}>IT小村 · 算法图解</text>
 <text x={125} y={230} fill={C.gold} fontSize={43} fontWeight={650}>LC.42</text>
 <text x={120} y={373} fill={C.text} fontSize={108} fontWeight={800}>接雨水</text>
 <text x={125} y={466} fill={C.muted} fontSize={42}>每列能留下多少水？</text>
 <Terrain x={130} baseline={1025} unit={104} pitch={118} barWidth={118} water={FINAL.water} showColumns={false} showHeights/>
 <path d="M 130 713 H 602" stroke={C.blue} strokeWidth={3} strokeDasharray="10 8"/>
 <path d="M 721 921 H 944" stroke={C.blue} strokeWidth={3} strokeDasharray="10 8"/>
 <text x={125} y={1177} fill={C.blue} fontSize={43} fontWeight={650}>左盆7格 + 右盆1格 = 8</text>
</g>;
export const Cover=({size='16x9'}:{size?:keyof typeof coverSizes})=>{
 const dimensions=coverSizes[size];
 return <svg {...dimensions} viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}>
  <rect width="100%" height="100%" fill={C.bg}/>
  {size==='16x9'?<g fontFamily={FONT}>
   <text x={180} y={133} fill={C.muted} fontSize={31}>IT小村 · 算法图解</text>
   <text x={180} y={294} fill={C.gold} fontSize={44}>LC.42</text>
   <text x={172} y={454} fill={C.text} fontSize={126} fontWeight={800}>接雨水</text>
   <text x={180} y={548} fill={C.muted} fontSize={43}>每列能留下多少水？</text>
   <text x={180} y={735} fill={C.blue} fontSize={60} fontWeight={700}>左盆7格 + 右盆1格</text>
   <text x={180} y={823} fill={C.blue} fontSize={73} fontWeight={750}>= 8格水</text>
   <g transform="translate(1020 122) scale(.66)"><Terrain x={0} baseline={1080} unit={144} pitch={170} barWidth={170} water={FINAL.water} showColumns={false}/></g>
  </g>:size==='4x3'?<g transform="translate(315 0) scale(.75)"><Vertical/></g>:<Vertical/>}
 </svg>;
};
