import style from './style-v1.json';
export const FONT=style.fonts.sans;
export const MONO=style.fonts.mono;
export const pageBg=style.palette.background;
export const pageInk=style.palette.text;
export const PAGE={pageBg,pageInk};
/** Cover cyan carries active paths; yellow carries focus; coral remains failure. */
export const C={...style.palette,bg:pageBg,gold:style.palette.yellow,teal:style.palette.cyan,blue:style.palette.cyan,red:style.palette.coral,reject:style.palette.coral};
