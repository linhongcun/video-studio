// cdn-v1 stills overview: one bundle, renderStill for each requested global frame (Main) and the covers.
// Usage: node scripts/stills.mjs <outDir> <framesJson> [--covers]
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import webpack from 'webpack';
const cwd = process.cwd(), out = path.resolve(process.argv[2]), frames = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const covers = process.argv.includes('--covers');
fs.mkdirSync(out, {recursive: true});
const pick = (f, p) => fs.existsSync(path.resolve(cwd, f)) ? path.resolve(cwd, f) : path.resolve(cwd, p);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), enableCaching: false, webpackOverride: c => ({...c,
  resolve: {...c.resolve, alias: {...(c.resolve?.alias ?? {}), '@storyboard': process.env.STORYBOARD_JSON ? path.resolve(process.env.STORYBOARD_JSON) : pick('../storyboard.json', 'src/placeholders/storyboard.json'), '@covers': process.env.COVERS_JSON ? path.resolve(process.env.COVERS_JSON) : pick('../covers.json', 'src/placeholders/covers.json')}, modules: [path.resolve(cwd, 'node_modules'), 'node_modules']},
  plugins: [...(c.plugins ?? []), new webpack.DefinePlugin({__HAS_VOICE_AUDIO__: 'false'})]})});
const main = await selectComposition({serveUrl, id: 'Main'});
for (const {name, frame} of frames) {
  await renderStill({serveUrl, composition: main, frame, output: path.join(out, `${name}.jpeg`), imageFormat: "jpeg", scale: 0.25, overwrite: true, onBrowserLog: l => { if (String(l.text).startsWith("COPYFIT")) console.log("F", frame, l.text); }});
  console.log('ok', name, frame);
}
if (covers) for (const id of ['Cover16x9', 'Cover4x3', 'Cover3x4']) {
  const comp = await selectComposition({serveUrl, id});
  await renderStill({serveUrl, composition: comp, frame: 0, output: path.join(out, `${id}.png`), imageFormat: "png", overwrite: true, onBrowserLog: l => { if (String(l.text).startsWith("COPYFIT")) console.log("F", id, l.text); }});
  console.log('ok', id);
}
