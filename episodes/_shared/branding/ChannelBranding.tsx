// 「IT小村」频道品牌层（规范 v1.2.0，见 ./spec.md / spec.json，Miyazaki 出样、Nolan 定稿）。
// 每期 Main.tsx 默认使用，第五期起复制模板即自动带上：
//   <CenterMark episode="EP.0x" plan={plan} />   放在 <Grid/> 之后、镜头之前（镜头元素之下、背景之上）
//   <ChannelBranding mainFrames={totalFrames} />  放在最后（右上常驻水印 + 片尾卡）
//   Root.tsx 的 durationInFrames = totalFrames + END_CARD_FRAMES
// 中央淡水印位置来自 center_placement.json（center_place.py 生成；分镜改了要重跑），null = 本镜头不显示。
// 字体：Noto Sans SC Bold（SIL OFL 1.1，见 fonts/OFL.txt），仅子集化「IT小村·原创」几个字，打包进渲染，不依赖系统字体。
// 需要每期 remotion.config.ts 把 node_modules 解析指向本期工程（见模板）。
import React from 'react';
import {AbsoluteFill, Easing, continueRender, delayRender, interpolate, useCurrentFrame} from 'remotion';
import spec from './spec.json';
import placement from './center_placement.json';
import fontUrl from './fonts/NotoSansSC-Bold-subset.ttf';

const W = spec.watermark, C = spec.centerMark, E = spec.endCard;
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

/** 中央淡水印：逐镜头静态选位，随镜头淡入淡出各 15 帧。 */
export const CenterMark: React.FC<{episode: string; plan: {sh: {id: string}; from: number; dur: number}[]}> = ({episode, plan}) => {
  useBrandFont();
  const frame = useCurrentFrame();
  if (!C.enabled) return null;
  const table: Record<string, {x: number; y: number} | null> = (placement as any)[episode] ?? {};
  const p = plan.find((q) => frame >= q.from && frame < q.from + q.dur);
  if (!p) return null;
  const pos = table[p.sh.id];
  if (!pos) return null;
  const f = frame - p.from, fi = Math.min(C.fade.in, p.dur / 2), fo = Math.min(C.fade.out, p.dur / 2);
  const o = Math.min(interpolate(f, [0, fi], [0, 1], clamp), interpolate(f, [p.dur - fo, p.dur], [1, 0], clamp));
  return (
    <div style={{position: 'absolute', left: pos.x - C.box.w / 2, top: pos.y - C.box.h / 2, width: C.box.w, height: C.box.h,
      display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: BRAND_FONT, fontWeight: 700, fontSize: C.fontSize,
      color: C.color, opacity: C.opacity * o, whiteSpace: 'nowrap', lineHeight: 1, pointerEvents: 'none'}}>{C.text}</div>
  );
};

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
