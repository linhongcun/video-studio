import React from 'react';
import {progress} from '../animation';
import {ShotElement} from '../storyboard';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {ShopImageDrawing} from './ShopImage';
import {Copy, stateAt, UIProps} from './ui';

/** Only an actual transition of this image to shown starts its reveal. */
export function imageRevealOpacity(source: ShotElement, index: number, frame: number, duration: number) {
  let state = source.images?.[index], shownFrame: number | undefined;
  for (const key of [...(source.stateKeyframes ?? [])].sort((a, b) => a.frame - b.frame)) {
    if (key.frame > frame) break;
    if (!key.images) continue;
    const next = key.images[index];
    if (next === 'shown' && state !== 'shown') shownFrame = key.frame;
    state = next;
  }
  return duration <= 0 || shownFrame === undefined ? 1 : progress(frame, shownFrame, duration);
}

/** All page geometry is authored in scene/cover coordinates. */
export const CacheShopPage: React.FC<UIProps & {rotor?: number}> = ({e: original, source, frame, rotor = frame}) => {
  const e = stateAt(original, frame), boxes = e.boxes ?? {}, base = source ?? original;
  return <>
    {(boxes.cards ?? []).map((box: number[], i: number) => <div key={i} data-cache-card={i} style={{...browserPageBox(e, box), boxSizing: 'border-box', borderRadius: 14, border: `1px solid ${P.muted}44`, background: P.panel2}} />)}
    {boxes.logo && <div data-anchor="shopLogo" style={browserPageBox(e, boxes.logo)}><ShopImageDrawing id={`${e.id}-logo`} variant={e.logo === 'placeholder' ? 'arc' : e.logo} state={e.logo === 'placeholder' ? 'placeholder' : 'shown'} w={boxes.logo[2]} h={boxes.logo[3]} frame={rotor} /></div>}
    {boxes.title && <div data-cache-title style={{...browserPageBox(e, boxes.title), display: 'flex', alignItems: 'center'}}><Copy size={e.pageTitleSize} width={boxes.title[2]} height={boxes.title[3]} style={{fontWeight: 800, textAlign: 'left', color: P.text, whiteSpace: 'nowrap'}}>{e.pageTitle}</Copy></div>}
    {(e.cards ?? []).map((card, i) => {
      const image = boxes.images?.[i], title = boxes.cardTitles?.[i], button = boxes.buttons?.[i];
      const ready = e.buttons === 'ready', plain = e.buttons === 'plain';
      return <React.Fragment key={i}>
        {image && <div style={browserPageBox(e, image)}><ShopImageDrawing id={`${e.id}-image-${i}`} variant={card.pattern} state={e.images?.[i]} w={image[2]} h={image[3]} spinnerSize={e.spinnerSize} frame={rotor} reveal={imageRevealOpacity(base, i, frame, e.imageRevealFrames ?? 0)} /></div>}
        {title && <div style={{...browserPageBox(e, title), display: 'flex', alignItems: 'center'}}><Copy size={e.cardTitleSize} width={title[2]} height={title[3]} style={{fontWeight: 700, color: P.text, whiteSpace: 'nowrap'}}>{card.title}</Copy></div>}
        {button && <div data-anchor="cardButton" data-button-state={e.buttons} style={{...browserPageBox(e, button), display: 'flex', alignItems: 'center', justifyContent: plain ? 'flex-start' : 'center', borderRadius: 10, background: plain ? undefined : ready ? P.primary : `${P.primary}73`, color: plain ? P.text2 : ready ? P.bg : P.text}}><Copy size={e.buttonSize} width={button[2]} height={button[3]} style={{fontWeight: ready ? 700 : 400, textAlign: plain ? 'left' : 'center', whiteSpace: 'nowrap'}}>{card.button}</Copy></div>}
      </React.Fragment>;
    })}
    {e.dimPage > 0 && <div data-cache-dim style={{position: 'absolute', inset: 0, background: P.bg, opacity: e.dimPage}} />}
  </>;
};
