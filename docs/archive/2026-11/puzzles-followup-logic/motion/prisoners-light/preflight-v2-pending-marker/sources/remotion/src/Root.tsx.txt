import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import {VIDEO} from './data';
export const RemotionRoot=()=> <Composition id="PrisonersLight" component={Main} {...VIDEO} defaultProps={{hideSubtitles:false,auditLayout:false}}/>;
