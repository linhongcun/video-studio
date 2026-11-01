import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import {VIDEO} from '../data';

export const RemotionRoot=()=> <Composition id="Main" component={Main} {...VIDEO} defaultProps={{hideSubtitles:false,auditLayout:false}}/>;
