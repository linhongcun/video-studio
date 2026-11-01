import catalog from '../puzzles-covers/catalog.json';

// The cover catalog owns the series colors. Actions, results and alternatives
// keep separate semantic colors throughout each explanation.
const P = catalog.palette;
export const FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';
export const MONO = '"Noto Sans Mono", "Noto Sans Mono CJK SC", monospace';
export const C = {
  bg: P.background, surface: P.surface, edge: P.edge, text: P.text,
  muted: P.muted, blue: P.violet, gold: P.coral, teal: P.teal,
  red: '#F29DAF', violet: P.violet, coral: P.coral,
};
