import React from 'react';
import {Composition} from 'remotion';
import storyboard from '@storyboard';
import covers from '@covers';
import {Main} from './Main';
import {Cover} from './Cover';

const durationInFrames = (storyboard.scenes ?? []).flatMap((scene: any) => scene.shots ?? [])
  .reduce((total: number, shot: any) => total + Number(shot.durationInFrames), 0);
if (!Number.isInteger(durationInFrames) || durationInFrames <= 0) {
  throw new Error('A real storyboard with a positive integer frame count is required.');
}
const video = {
  width: storyboard.meta.width,
  height: storyboard.meta.height,
  fps: storyboard.meta.fps,
  durationInFrames,
};
export const RemotionRoot = () => <>
  <Composition id="Main" component={Main} {...video}
    defaultProps={{hideSubtitles: false, auditLayout: false}} />
  {(['16x9', '4x3', '3x4'] as const).map(size => <Composition key={size}
    id={'Cover' + size} component={Cover} width={covers.sizes[size].width}
    height={covers.sizes[size].height} fps={30} durationInFrames={1}
    defaultProps={{size, auditLayout: false}} />)}
</>;
