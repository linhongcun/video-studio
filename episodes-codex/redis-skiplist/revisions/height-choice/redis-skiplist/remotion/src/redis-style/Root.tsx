import React from 'react';
import {Composition} from 'remotion';
import storyboard from '@storyboard';
import {Main} from './Main';
const durationInFrames=(storyboard.scenes??[]).flatMap((s:any)=>s.shots??[]).reduce((n:number,s:any)=>n+Number(s.durationInFrames),0);
if(!Number.isInteger(durationInFrames)||durationInFrames<=0)throw Error('The actual voice-timed storyboard must exist before rendering.');
export const RemotionRoot=()=><Composition id="Main" component={Main} width={storyboard.meta.width} height={storyboard.meta.height} fps={storyboard.meta.fps} durationInFrames={durationInFrames} defaultProps={{hideSubtitles:false,auditLayout:false}}/>;
