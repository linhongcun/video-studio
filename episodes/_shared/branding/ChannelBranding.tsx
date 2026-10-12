// 「IT小村」频道品牌层（规范 v1.2.0，见 ./spec.md / spec.json，Miyazaki 出样、Nolan 定稿）。
// 每期 Main.tsx 默认使用，第五期起复制模板即自动带上：
//   <ChannelBranding mainFrames={totalFrames} />  放在最后（右上常驻水印 + 片尾卡）
//   Root.tsx 的 durationInFrames = totalFrames + END_CARD_FRAMES
// v1.3.0（v0.9.1）：中央淡水印已整体取消，只保留右上常驻水印与片尾卡。
// 字体：Noto Sans SC Bold（SIL OFL 1.1，见 fonts/OFL.txt），仅子集化「IT小村·原创」几个字，打包进渲染，不依赖系统字体。
// 需要每期 remotion.config.ts 把 node_modules 解析指向本期工程（见模板）。
import React from 'react';
import {AbsoluteFill, Easing, continueRender, delayRender, interpolate, useCurrentFrame} from 'remotion';
import spec from './spec.json';
import fontUrl from './fonts/NotoSansSC-Bold-subset.ttf';

const W = spec.watermark, E = spec.endCard;
export const END_CARD_FRAMES: number = E.frames;
export const BRAND_FONT = '"ITXC Brand","Noto Sans SC","Noto Sans CJK SC",sans-serif';

let fontReady: Promise<void> | null = null;
const useBrandFont = () => {
  const [handle] = React.useState(() => delayRender('IT小村 品牌字体'));
  React.useEffect(() => {
    if (!fontReady) {
      const f = new FontFace('ITXC Brand', `url(${fontUrl})`, {weight: '700'});
      fontReady = f.load().then((ff) => { (document as any).fonts.add(ff); });
    }
    fontReady.then(() => continueRender(handle), (err) => { console.error(err); continueRender(handle); });
  }, [handle]);
};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Watermark: React.FC<{mainFrames: number}> = ({mainFrames}) => {
  const frame = useCurrentFrame();
  if (frame >= mainFrames) return null;
  const o = Math.min(interpolate(frame, W.fadeInFrames, [0, 1], clamp), interpolate(frame, [mainFrames - W.fadeOutFrames, mainFrames], [1, 0], clamp));
  return (
    <div style={{position: 'absolute', right: spec.width - W.anchorX, top: W.anchorY, fontFamily: BRAND_FONT, fontWeight: 700, fontSize: W.fontSize,
      color: W.color, opacity: W.opacity * o, whiteSpace: 'nowrap', lineHeight: 1.4, textAlign: 'right', pointerEvents: 'none'}}>{W.text}</div>
  );
};

const EndCard: React.FC<{mainFrames: number}> = ({mainFrames}) => {
  const frame = useCurrentFrame() - mainFrames;
  if (frame < 0) return null;
  const o = Math.min(interpolate(frame, [0, E.fadeIn], [0, 1], clamp), interpolate(frame, [E.frames - 1 - E.fadeOut, E.frames - 1], [1, 0], clamp));
  const u = E.underline;
  const draw = interpolate(frame, [u.start, u.start + u.frames], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: E.bg}}>
      <div style={{opacity: o}}>
        <div style={{position: 'absolute', left: 0, width: spec.width, top: E.y - E.fontSize * 0.7, height: E.fontSize * 1.4, display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontFamily: BRAND_FONT, fontWeight: 700, fontSize: E.fontSize, whiteSpace: 'pre', lineHeight: 1}}>
          {E.runs.map(([t, c]) => <span key={t} style={{color: c}}>{t}</span>)}
        </div>
        <div style={{position: 'absolute', left: (spec.width - u.w) / 2, top: u.y - u.h / 2, width: u.w * draw, height: u.h, borderRadius: u.h / 2, background: u.color}} />
      </div>
    </AbsoluteFill>
  );
};

/** 右上常驻水印（正片全程，无例外）+ 片尾卡（正片之后 60 帧）。放在 Main 的最上层。 */
export const ChannelBranding: React.FC<{mainFrames: number}> = ({mainFrames}) => {
  useBrandFont();
  return (<><Watermark mainFrames={mainFrames} /><EndCard mainFrames={mainFrames} /></>);
};
