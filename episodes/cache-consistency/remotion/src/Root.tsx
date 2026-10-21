import React from 'react';
import { Composition } from 'remotion';
import { Main, MAIN_VIDEO } from './Main';
import { COVER_SIZES, Cover16x9, Cover4x3, Cover3x4 } from './Cover';
export const RemotionRoot: React.FC = () => <>
 <Composition id="Main" component={Main} {...MAIN_VIDEO} />
 <Composition id="Cover16x9" component={Cover16x9} width={COVER_SIZES['16x9'].width} height={COVER_SIZES['16x9'].height} fps={MAIN_VIDEO.fps} durationInFrames={1} />
 <Composition id="Cover4x3" component={Cover4x3} width={COVER_SIZES['4x3'].width} height={COVER_SIZES['4x3'].height} fps={MAIN_VIDEO.fps} durationInFrames={1} />
 <Composition id="Cover3x4" component={Cover3x4} width={COVER_SIZES['3x4'].width} height={COVER_SIZES['3x4'].height} fps={MAIN_VIDEO.fps} durationInFrames={1} />
</>;
