// 每期 remotion/remotion.config.ts：让 episodes/_shared 下的共享组件也从本期 node_modules 解析 remotion / react（单实例）。
import path from 'node:path';
import { existsSync, lstatSync } from 'node:fs';
import webpack from 'webpack';
import { Config } from '@remotion/cli/config';
import { BundlerInternals } from '@remotion/bundler';
// node_modules is a shared, read-only symlink; do not write a bundler cache there.
if (lstatSync(path.resolve(process.cwd(), 'node_modules')).isSymbolicLink()) {
  Config.setCachingEnabled(false);
  // Remotion 4 clears existing caches even with caching disabled. Do not probe
  // the shared cache: this project will bundle without reading or writing it.
  BundlerInternals.cacheExists = () => 'does-not-exist';
}
const pick = (frozen: string, placeholder: string) => existsSync(path.resolve(process.cwd(), frozen)) ? path.resolve(process.cwd(), frozen) : path.resolve(process.cwd(), placeholder);
Config.overrideWebpackConfig(c => ({
  ...c,
  resolve: {
    ...c.resolve,
    alias: {
      ...((c.resolve?.alias as Record<string, string>) ?? {}),
      // cdn-v1: frozen storyboard/covers win; placeholders keep the project bundling before freeze.
      '@storyboard': pick('../storyboard.json', 'src/placeholders/storyboard.json'),
      '@covers': pick('../covers.json', 'src/placeholders/covers.json'),
    },
    modules: [path.resolve(process.cwd(), 'node_modules'), 'node_modules']
  },
  plugins: [...(c.plugins ?? []), new webpack.DefinePlugin({
    __HAS_VOICE_AUDIO__: JSON.stringify(existsSync(path.resolve(process.cwd(), 'public/audio/voice.wav')))
  })]
}));
