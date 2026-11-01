import catalog from '../mysql-covers/catalog.json';

const P = catalog.palette;
export const FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';
export const MONO = '"Noto Sans Mono", "Noto Sans Mono CJK SC", monospace';
export const C = {
  bg: P.background, surface: P.surface, edge: P.edge, text: P.text,
  muted: P.muted, teal: P.mint, blue: P.cyan, gold: P.amber,
  red: '#EE9D91', row: '#1C3832', header: '#203F37',
  active: '#3D3828', success: '#20443A', index: '#17372E',
};
export const PAGE = {bg:C.bg,ink:C.text,field:C.surface,row:C.row,border:C.edge};
export const pageBg=C.bg, pageInk=C.text;
