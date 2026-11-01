import React from 'react';
import {Composition} from 'remotion';
import {Main,MechanismPreview,MechanismSequence,getStages} from './Main';
import {VIDEO,hasMeasuredBody} from './data';
export const RemotionRoot=()=> <>
 {hasMeasuredBody&&<Composition id="Main" component={Main} {...VIDEO}/>}
 <Composition id="MechanismPreview" component={MechanismPreview} width={1920} height={1080} fps={30} durationInFrames={90} defaultProps={{shotId:'03',stage:1}}/>
 <Composition id="MechanismSequence" component={MechanismSequence} width={1920} height={1080} fps={30} durationInFrames={270} defaultProps={{shotId:'07'}} calculateMetadata={({props})=>({durationInFrames:getStages(props.shotId).length*45})}/>
</>;
