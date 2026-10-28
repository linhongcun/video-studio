import React from 'react';
import {LeetcodeHeader} from '../../../../_shared/leetcode-video/Frame';
/** Shared HTML identity in the original SVG coordinate system. */
export const EpisodeHeader=({detail,compact=false}:{detail?:React.ReactNode;compact?:boolean})=><foreignObject x={0} y={0} width={1920} height={compact?84:150}><LeetcodeHeader slug="longest-substring" detail={detail} compact={compact}/></foreignObject>;
