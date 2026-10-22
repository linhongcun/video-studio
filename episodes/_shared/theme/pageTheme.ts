/**
 * Demo page body palette (pageBg / pageInk).
 * Separate from remotion P chrome theme: browser chrome / DevTools stay on P.*;
 * in-page surfaces (*Page.tsx) use PAGE.* so they match the dark frame without
 * large pure-white fills.
 */
export const PAGE = {
  /** Page body background — slate-900, a touch above P.bg so the chrome edge reads. */
  bg: '#0F172A',
  /** Primary body text on pageBg. */
  ink: '#E5E7EB',
  /** Secondary / muted body text. */
  muted: '#94A3B8',
  /** Input / field fill. */
  field: '#1E293B',
  /** Soft card / row fill (e.g. bill rows). */
  row: '#1E293B',
  /** Row / field border. */
  border: '#334155',
  /** Highlight wash for lit rows (ShopPricePage); dark amber so yellow edge pops. */
  highlight: '#422006',
  /** Highlight edge. */
  highlightEdge: '#FBBF24',
  /** Success / coupon / saved on dark page (brighter than #15803D). */
  success: '#4ADE80',
} as const;

/** Nolan naming aliases. */
export const pageBg = PAGE.bg;
export const pageInk = PAGE.ink;
