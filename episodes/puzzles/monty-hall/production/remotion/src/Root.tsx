import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import {VIDEO} from './data';
import {Cover,coverSizes} from './Cover';
export const RemotionRoot=()=> <>
 <Composition id="Main" component={Main} {...VIDEO} defaultProps={{hideSubtitles:false,auditLayout:false}}/>
 <Composition id="Cover16x9" component={Cover} {...coverSizes['16x9']} fps={30} durationInFrames={1} defaultProps={{size:'16x9',auditLayout:false}}/>
 <Composition id="Cover4x3" component={Cover} {...coverSizes['4x3']} fps={30} durationInFrames={1} defaultProps={{size:'4x3',auditLayout:false}}/>
 <Composition id="Cover3x4" component={Cover} {...coverSizes['3x4']} fps={30} durationInFrames={1} defaultProps={{size:'3x4',auditLayout:false}}/>
</>;
