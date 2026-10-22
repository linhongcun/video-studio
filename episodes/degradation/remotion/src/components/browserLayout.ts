import {animatedValue, progress} from '../animation';
import {Shot, ShotElement} from '../storyboard';
import {stateAt} from './ui';

export type PageLayout = {
  padding: number; gap: number; titleSize: number; titleHeight: number;
  rowHeight: number; rowGap: number; fontSize: number; iconSize: number;
  rowPadding: number; buttonPadding: number; buttonSize: number; badgeHeight: number;
};
export type BrowserContentLayout = {height: number; shop: PageLayout; login: PageLayout; cardsRightInset: number};
export const compactBrowserHeaderHeight = (e: ShotElement) => Math.min(110, Math.max(104, e.h * .3));
// Absolute page boxes use the author's standard 80 px header at every width.
export const browserHeaderHeight = (e: ShotElement) => e.boxes && (e.page === 'itemShop' || e.page === 'ordersPage' || e.page === 'adminItem' || e.page === 'orderFlow' || e.page === 'ticketBuy' || e.page === 'payCheckout' || e.page === 'shopCheckout' || e.page === 'shopPrice' || e.page === 'payBills')
  ? 80 : e.w < 600 ? compactBrowserHeaderHeight(e) : 80;

/** Authored boxes are in canvas space; children live inside the browser border and header. */
export const browserPageBox = (e: ShotElement, [x, y, width, height]: number[]) => ({
  position: 'absolute' as const, left: x - e.x - 3, top: y - e.y - 3 - browserHeaderHeight(e), width, height,
});

export const fitLayout = (height: number, login: boolean, button: boolean, badge: boolean, docked = false): PageLayout => {
  const metrics = (t: number): PageLayout => {
    const mix = (small: number, large: number) => small + (large - small) * t;
    const titleSize = mix(26, !login && docked ? 36 : 42), fontSize = mix(26, !login && docked ? 32 : 36);
    const buttonPadding = mix(4, !login && docked ? 4 : 10), buttonSize = mix(26, 32);
    return {
      padding: mix(6, login ? 20 : docked ? 12 : 24), gap: mix(6, !login && docked ? 8 : 20), titleSize,
      titleHeight: Math.max(titleSize * 1.2, button && !login ? buttonSize * 1.2 + buttonPadding * 2 : 0),
      rowHeight: mix(login ? 36 : 40, login ? 64 : docked ? 70 : 146), rowGap: mix(6, 12),
      fontSize, iconSize: mix(28, docked ? 44 : 76), rowPadding: mix(6, docked ? 16 : 24), buttonPadding, buttonSize,
      badgeHeight: badge && !login ? fontSize * 1.2 + 8 : 0,
    };
  };
  const total = (m: PageLayout) => m.padding * 2 + m.titleHeight + m.gap
    + (login ? m.rowHeight * 2 + m.rowGap : m.rowHeight)
    + (m.badgeHeight ? m.badgeHeight + m.gap : 0);
  const small = total(metrics(0)), large = total(metrics(1));
  const fitted = metrics(Math.max(0, Math.min(1, (height - small) / (large - small))));
  // Even the compact form must fit inside the annotation reservation. Field
  // heights include their borders, and the bottom padding keeps all content clear.
  if (login && height < small) {
    const scale = Math.max(0, height) / small;
    return Object.fromEntries(Object.entries(fitted).map(([key, value]) => [key, value * scale])) as PageLayout;
  }
  return fitted;
};

/** Reserve annotations visible at any shot frame, before rendering any frames. */
export function browserContentLayout(shot: Shot, browser: ShotElement): BrowserContentLayout | undefined {
  const annotations = shot.elements.filter(e => e.id !== browser.id
    && (e.component === 'CalloutTag' || (!e.component && e.type === 'text'))
    && e.role !== 'subtitle' && e.binding !== 'subtitles');
  let height = Infinity;
  for (let frame = 0; frame < shot.durationInFrames; frame++) {
    const resolve = (original: ShotElement) => {
      const e = stateAt(original, frame);
      const rect = Object.fromEntries(['x', 'y', 'w', 'h'].map(p => [p, Number(animatedValue(shot, e.id, p, frame, e[p]))]));
      return {...e, ...rect} as ShotElement;
    };
    const b = resolve(browser), pageTop = b.y + 3 + browserHeaderHeight(b);
    const docked = shot.elements.some(e => {
      const panel = resolve(e);
      return panel.component === 'DevToolsNetwork' && panel.layout === 'docked'
        && frame >= (panel.appearFrame ?? 0) && frame < (panel.disappearFrame ?? Infinity) && panel.state !== 'hidden'
        && panel.x < b.x + b.w && panel.x + panel.w > b.x && panel.y >= b.y && panel.y < b.y + b.h;
    });
    const titleBottom = pageTop + (b.w < 600 ? 10 : b.page === 'loginForm' ? 20 : docked ? 12 : 24)
      + Math.max((b.w < 600 ? 30 : b.page === 'loginForm' || !docked ? 42 : 36) * 1.2, b.loginButton ? docked ? 56 : 68 : 0);
    for (const original of annotations) {
      const e = resolve(original);
      const fade = e.opacityTo === undefined ? 1 : 1 + (e.opacityTo - 1) * progress(frame, e.stateFrame, e.fadeFrames ?? e.durationFrames ?? 0);
      // transient overlays that fade out (e.g. the shot-1 cover title) do not reserve page space
      if ((original.stateKeyframes ?? []).some(k => k.opacityTo === 0)) continue;
      if (frame < (e.appearFrame ?? 0) || frame >= (e.disappearFrame ?? Infinity) || e.state === 'hidden'
        || Number(animatedValue(shot, e.id, 'opacity', frame, e.opacity ?? 1)) * fade <= 0) continue;
      if (e.x >= b.x && e.x + e.w <= b.x + b.w && e.y >= titleBottom && e.y + e.h <= b.y + b.h) {
        height = Math.min(height, e.y - pageTop - 12);
      }
    }
  }
  if (!Number.isFinite(height)) return undefined;
  const states = [browser, ...(browser.stateKeyframes ?? [])];
  const docked = shot.elements.some(e => e.component === 'DevToolsNetwork' && [e, ...(e.stateKeyframes ?? [])].some(state => state.layout === 'docked'));
  // page-level badges (e.g. user-badge) that sit on the compact cards row: keep cards left of them
  const pageTop = browser.y + 3 + browserHeaderHeight(browser);
  const badges = shot.elements.filter(e => e.component === 'CornerBadge' && e.y >= pageTop && e.y < browser.y + 3 + browserHeaderHeight(browser) + height && e.x > browser.x + browser.w / 2);
  const cardsRightInset = badges.length ? Math.max(...badges.map(e => browser.x + browser.w - e.x + 16)) : 0;
  return {cardsRightInset, height, shop: fitLayout(height, false, states.some(e => e.loginButton), states.some(e => e.userBadge), docked), login: fitLayout(height, true, false, false)};
}
