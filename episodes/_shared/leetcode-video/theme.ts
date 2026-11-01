import style from './style-v1.json';
export const FONT=style.fonts.sans;
export const MONO=style.fonts.mono;
export const pageBg=style.palette.background;
export const pageInk=style.palette.text;
export const PAGE={pageBg,pageInk};
export const C={...style.palette,bg:style.palette.background};
export const GROUP_COLORS=[C.teal,C.blue,C.gold,C.purple,C.pink,'#95D69B'];
