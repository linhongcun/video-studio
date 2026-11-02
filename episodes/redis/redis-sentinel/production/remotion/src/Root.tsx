import React from 'react';
import {Composition} from 'remotion';
import {Main,MechanismPreview,MechanismSequence,VIDEO} from './Main';
import model from '../../model.json';
export const RemotionRoot=()=> <>
 <Composition id="Main" component={Main} {...VIDEO}/>
 <Composition id="MechanismPreview" component={MechanismPreview} width={1920} height={1080} fps={30} durationInFrames={90} defaultProps={{shotId:'08',stage:0,progress:1}}/>
 <Composition id="MechanismSequence" component={MechanismSequence} width={1920} height={1080} fps={30} durationInFrames={300} defaultProps={{shotId:'08'}} calculateMetadata={({props})=>({durationInFrames:(model.shots as any)[String(props.shotId)].length*60})}/>
</>;
