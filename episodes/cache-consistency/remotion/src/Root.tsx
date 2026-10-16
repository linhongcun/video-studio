// EP.22：不再追加全局 60 帧品牌片尾卡（新片尾在正片 ending-1/2 内，长度跟随结尾旁白）
import {Composition} from 'remotion';
import {Main, totalFrames} from './Main';
export const Root = () => (
  <Composition id="Main" component={Main} durationInFrames={totalFrames} fps={30} width={1920} height={1080} />
);
