import {Composition} from 'remotion';
import {Main, totalFrames} from './Main';
export const Root = () => (
  <Composition id="Main" component={Main} durationInFrames={totalFrames} fps={30} width={1920} height={1080} />
);
