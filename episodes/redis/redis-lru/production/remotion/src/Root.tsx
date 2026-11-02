import React from 'react';
import {Composition} from 'remotion';
import board from '@storyboard';
import {Main} from './Main';
export const Root=()=> <Composition id="Main" component={Main} durationInFrames={board.meta.durationInFrames} fps={30} width={1920} height={1080}/>;
