import {Composition} from 'remotion';
import {Main, totalFrames} from './Main';
import {END_CARD_FRAMES} from '../../../_shared/branding/ChannelBranding';
export const Root = () => (
  <Composition id="Main" component={Main} durationInFrames={totalFrames + END_CARD_FRAMES} fps={30} width={1920} height={1080} />
);
