import React from 'react';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {rollingNumber} from './pageState';
import {Spinner} from './Spinner';
import {colorToken, Copy, stateAt, textWidth, UIProps} from './ui';

/** Page content only: BrowserChrome owns the frame, controls and reload animation. */
export const SaleDemoPage: React.FC<UIProps & {rotor?: number}> = ({e: original, source, frame, rotor = frame}) => {
  const e = stateAt(original, frame), base = source ?? original, boxes = e.boxes ?? {};
  const visitors = rollingNumber(base.visitors, base.stateKeyframes ?? [], 'visitors', frame, e.countFrames ?? 0);
  const navSize = e.navSize ?? 28;
  const content = boxes.content, cards = e.cards ?? [], stacked = e.cardLayout === 'stacked';
  const gap = stacked ? 12 : 24, pad = stacked ? 8 : 20;
  const cardWidth = content ? (content[2] - gap * Math.max(0, cards.length - 1)) / Math.max(1, cards.length) : 0;
  const swatch = e.cardSwatch ?? Math.min(96, (content?.[3] ?? 0) * .6);
  const titleSize = e.cardTitleSize ?? 34, buttonSize = e.cardButtonSize;
  const cardTextWidth = Math.max(1, cardWidth - pad * 2 - swatch - gap);
  return <>
    {boxes.nav && <div data-sale-nav style={{...browserPageBox(e, boxes.nav), display: 'flex', alignItems: 'center', gap: navSize * .8, padding: `0 ${navSize}px`, boxSizing: 'border-box', borderBottom: `2px solid ${P.panel2}`, color: P.text2, whiteSpace: 'nowrap'}}>
      <Copy size={navSize} width={(boxes.nav[2] - navSize * 2) * .4} height={boxes.nav[3]} style={{fontWeight: 700, whiteSpace: 'nowrap', color: P.primary}}>{e.brand}</Copy>
      <div style={{marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: navSize * .8}}>
        {e.clock != null && <Copy mono size={navSize} width={textWidth(e.clock, navSize, true) * 1.1 + 4} height={boxes.nav[3]} style={{whiteSpace: 'nowrap', color: P.text}}>{e.clock}</Copy>}
        {visitors != null && <Copy size={navSize} width={textWidth(e.visitorsLabel ?? '', navSize) * 1.05 + 4} height={boxes.nav[3]} style={{whiteSpace: 'nowrap'}}>{e.visitorsLabel}</Copy>}
        {visitors != null && <Copy mono size={navSize} width={textWidth(String(Math.max(Number(base.visitors ?? 0), ...(base.stateKeyframes ?? []).map((k: any) => Number(k.visitors ?? 0)))), navSize, true) * 1.1 + 4} height={boxes.nav[3]} style={{whiteSpace: 'nowrap', textAlign: 'right', fontWeight: 700, color: P.accent}}>{String(visitors)}</Copy>}
      </div>
    </div>}
    {boxes.title && e.pageTitle != null && <div data-sale-title style={{...browserPageBox(e, boxes.title), display: 'flex', alignItems: 'center'}}><Copy size={e.pageTitleSize} width={boxes.title[2]} height={boxes.title[3]} style={{fontWeight: 800, color: P.text, whiteSpace: 'nowrap'}}>{e.pageTitle}</Copy></div>}
    {boxes.countdown && (e.countdownText != null || e.countdownProgress != null) && <div data-sale-countdown style={{...browserPageBox(e, boxes.countdown), display: 'flex', alignItems: 'center', gap: boxes.countdown[3]}}>
      {e.countdownText != null && <Copy size={boxes.countdown[3] * .75} width={textWidth(e.countdownText, boxes.countdown[3] * .75) * 1.05 + 4} height={boxes.countdown[3]} style={{flexShrink: 0, whiteSpace: 'nowrap', color: P.text2}}>{e.countdownText}</Copy>}
      {e.countdownProgress != null && <div style={{flex: 1, height: Math.max(4, boxes.countdown[3] * .25), borderRadius: 4, overflow: 'hidden', background: P.panel2}}><div data-countdown-progress style={{width: `${Math.max(0, Math.min(1, e.countdownProgress)) * 100}%`, height: '100%', background: P.accent}} /></div>}
    </div>}
    {content && <div data-sale-content={e.content} style={{...browserPageBox(e, content), display: 'flex', alignItems: 'stretch', gap, borderRadius: 12, overflow: 'hidden', background: e.content === 'cards' ? undefined : P.panel2}}>
      {e.content === 'cards' ? cards.map((card, i) => {
        const buttonWidth = Math.min(cardTextWidth, textWidth(card.button ?? '', buttonSize) * 1.03 + 24);
        const titleWidth = stacked ? cardTextWidth : Math.max(1, cardTextWidth - buttonWidth - gap);
        const button = card.button && <div role="button" data-sale-card-button style={{boxSizing: 'border-box', width: buttonWidth, maxWidth: '100%', flexShrink: 0, padding: '3px 12px', borderRadius: 8, background: P.secondary, color: P.text, fontWeight: 700}}><Copy size={buttonSize} width={buttonWidth - 24} height={buttonSize * 1.25} style={{whiteSpace: 'nowrap', textAlign: 'center'}}>{card.button}</Copy></div>;
        return <div key={i} data-sale-card style={{width: cardWidth, minWidth: 0, padding: pad, boxSizing: 'border-box', display: 'flex', alignItems: 'center', gap, borderRadius: 12, background: P.panel2}}>
          <div data-card-swatch style={{width: swatch, height: swatch, flexShrink: 0, borderRadius: 8, background: colorToken(card.color)}} />
          <div style={{display: 'flex', flex: 1, minWidth: 0, flexDirection: stacked ? 'column' : 'row', alignItems: stacked ? 'flex-start' : 'center', gap: stacked ? 4 : gap}}>
            <Copy size={titleSize} width={titleWidth} height={stacked ? Math.max(1, content[3] - pad * 2 - buttonSize * 1.25 - 10) : content[3] - pad * 2} style={{fontWeight: 700, whiteSpace: 'nowrap', color: P.text}}>{card.title}</Copy>
            {button}
          </div>
        </div>;
      }) : <div style={{width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: 12}}>
        {e.content === 'loading' && <div data-sale-spinner style={{width: e.spinnerSize, height: e.spinnerSize, flexShrink: 0}}><Spinner frame={rotor} /></div>}
        {e.content === 'timeout' && <Copy size={e.hintSize} width={content[2] - 32} height={e.hintSize * 1.3} style={{color: colorToken(e.timeoutColor), textAlign: 'center', fontWeight: 700}}>{e.timeoutText}</Copy>}
        {e.content === 'loading' && <Copy size={e.hintSize} width={content[2] - 32} height={e.hintSize * 1.2} style={{color: P.text2, textAlign: 'center'}}>{e.loadingHint}</Copy>}
      </div>}
    </div>}
    {e.statusNote?.box && <div data-sale-status-note style={{...browserPageBox(e, e.statusNote.box), display: 'flex', alignItems: 'center', color: colorToken(e.statusNote.color)}}><Copy size={e.statusNote.fontSize} width={e.statusNote.box[2]} height={e.statusNote.box[3]} style={{fontWeight: 700, textAlign: 'center', whiteSpace: 'nowrap'}}>{e.statusNote.text}</Copy></div>}
  </>;
};
