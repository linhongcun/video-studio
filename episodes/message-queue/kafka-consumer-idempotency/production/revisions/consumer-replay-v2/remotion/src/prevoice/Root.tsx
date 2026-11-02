import React from 'react';
import{Composition}from'remotion';
import storyboard from './board.json';
import{Main}from'../Main';
import{parseBoard}from'../data';
const {video}=parseBoard(storyboard);
const PrevoiceMain:React.FC<{showSubtitles?:boolean;hideSubtitles?:boolean}>=props=><Main storyboard={storyboard}prevoice withAudio={false}{...props}/>;
export const PrevoiceRoot=()=> <Composition id="Prevoice" component={PrevoiceMain}{...video}/>;
