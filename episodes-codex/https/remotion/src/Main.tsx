import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,shots} from './data';
import config from '../../production.json';
import {T} from './Primitives';
import {Scene} from './Scenes';
import {createBranchNavigator} from '../../../_shared/branch-map';
import {navigationSpec} from './branch-map';
import {Result,CaptionlessBrand,go} from './Primitives';
const Navigator=createBranchNavigator(React);
declare const __HAS_VOICE_AUDIO__:boolean;
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot, captions})=>{
 const f=useCurrentFrame();const sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 const id=Number(shot.id),d=shot.durationInFrames;
 let title=config.shots[id-1][1];for(const[term,n,key]of config.terms)if(n===id&&f>=(shot.cueFrames?.[key]??1))title=term as string;
 if(id===6)title='另看核验失败：停止正常发送';
 if(id===7)title='回到核验通过的正常情景';
 if(id===11)title='机制回顾：保护到两个端点为止';
 if(id===12)title='回看：身份与数据，两处不同判断';
 const foreground=<><T size={id===11||id===12?50:57}>{title}</T>
  {id===11&&<><T x={960} y={820} center size={31} color={C.teal}>保护范围：两端之间的传输</T><Result y={865} color={C.gold} alpha={go(f,Number(shot.cueFrames?.sentences?.[1]??d/2),35)}>网站信誉、服务端存储，仍需另外判断</Result></>}
  {id===12&&<><Result y={800} color={C.muted} alpha={go(f,Number(shot.cueFrames?.sentences?.[1]??d/2),35)}>加密网址，不是网站信誉保证</Result><CaptionlessBrand alpha={go(f,d-65,40)}/></>}
 </>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 78% 10%, #1A425E55, transparent 62%)'}}/>
 <T x={100} y={60} size={23} color={C.muted}>浏览器与网络 · EP.{String(config.ep).padStart(2,'0')}</T><T x={1715} y={58} size={25}>IT小村</T>
 <T x={1715} y={102} size={18} color={C.muted} center>教学示意 · 示例数据</T>
 {id<4?<Scene shot={shot}/>:<Navigator spec={navigationSpec(shot,f)} shotId={shot.id} frame={f} durationInFrames={d} foreground={foreground}><Scene shot={shot} hideTitle/></Navigator>}
 {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
 </AbsoluteFill>;
