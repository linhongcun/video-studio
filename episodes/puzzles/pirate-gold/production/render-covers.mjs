import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {catalog, cover, sizes} from '../../../_shared/puzzles-covers/template.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const ep=catalog.episodes.find(e=>e.slug==='pirate-gold');
if (!ep) throw new Error('P09 catalog entry missing');
for (const size of Object.keys(sizes)) fs.writeFileSync(path.join(here,`cover-${size}.svg`),cover(ep,size));
