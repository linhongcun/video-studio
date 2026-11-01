import style from './style-v1.json';
export const FONT=style.fonts.sans;
export const MONO=style.fonts.mono;
export const pageBg=style.palette.background;
export const pageInk=style.palette.text;
export const PAGE={pageBg,pageInk};
/** Redis-red focus, graphite content and cool-silver structure share the cover palette. */
export const C={...style.palette,bg:pageBg,gold:style.palette.red,teal:style.palette.redDark,blue:style.palette.muted,reject:style.palette.redDark};
