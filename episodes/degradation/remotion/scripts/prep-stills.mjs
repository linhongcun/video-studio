// EP.14 prep: one bundle, low-cost Main stills (jpeg, scale 0.5) for each requested frame, plus full-size cover drafts.
// Usage: node scripts/prep-stills.mjs <stillsDir> <framesJson> [--covers <coversDir>]
// Browser console lines starting with COPYFIT (text overflow reports from ui.tsx Copy) are echoed with the frame/cover id.
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import webpack from 'webpack';
const cwd = process.cwd(), out = path.resolve(process.argv[2]), frames = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const ci = process.argv.indexOf('--covers'), coversOut = ci > 0 ? path.resolve(process.argv[ci + 1]) : null;
fs.mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), enableCaching: false, webpackOverride: c => ({...c,
  resolve: {...c.resolve, alias: {...(c.resolve?.alias ?? {}), '@storyboard': path.resolve(cwd, '../storyboard.json'), '@covers': process.env.COVERS_JSON ? path.resolve(process.env.COVERS_JSON) : path.resolve(cwd, '../covers.json')}, modules: [path.resolve(cwd, 'node_modules'), 'node_modules']},
  plugins: [...(c.plugins ?? []), new webpack.DefinePlugin({__HAS_VOICE_AUDIO__: 'false'})]})});
console.log('bundled');
const log = id => l => { if (String(l.text).startsWith('COPYFIT')) console.log('COPYFIT', id, l.text); };
const main = await selectComposition({serveUrl, id: 'Main'});
for (const {name, frame} of frames) {
  await renderStill({serveUrl, composition: main, frame, output: path.join(out, `${name}.jpeg`), imageFormat: 'jpeg', jpegQuality: 85, scale: 0.5, overwrite: true, onBrowserLog: log(name)});
  console.log('ok', name, frame);
}
if (coversOut) {
  fs.mkdirSync(coversOut, {recursive: true});
  for (const id of ['Cover16x9', 'Cover4x3', 'Cover3x4']) {
    const comp = await selectComposition({serveUrl, id});
    await renderStill({serveUrl, composition: comp, frame: 0, output: path.join(coversOut, `${id}.png`), imageFormat: 'png', overwrite: true, onBrowserLog: log(id)});
    console.log('ok', id);
  }
}
console.log('done');
