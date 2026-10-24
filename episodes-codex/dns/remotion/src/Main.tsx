import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,shots} from './data';
import config from '../../production.json';
import {T} from './Primitives';
import {Scene,SceneTitle} from './Scenes';
import {createBranchNavigator} from '../../../_shared/branch-map';
import {navigationSpec} from './branch-map';
const Navigator=createBranchNavigator(React);
declare const __HAS_VOICE_AUDIO__:boolean;
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot, captions})=>{
 const f=useCurrentFrame();const sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 78% 10%, #1A425E55, transparent 62%)'}}/>
 <T x={100} y={60} size={23} color={C.muted}>浏览器与网络 · EP.{String(config.ep).padStart(2,'0')}</T><T x={1715} y={58} size={25}>IT小村</T>
 <T x={1715} y={102} size={18} color={C.muted} center>教学示意 · 示例数据</T>
 <Navigator spec={navigationSpec(shot,f)} shotId={shot.id} frame={f} durationInFrames={shot.durationInFrames} foreground={<SceneTitle shot={shot} frame={f}/>}><Scene shot={shot}/></Navigator>
 {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
 </AbsoluteFill>;
