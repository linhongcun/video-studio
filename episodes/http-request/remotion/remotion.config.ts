// 每期 remotion/remotion.config.ts：让 episodes/_shared 下的共享组件也从本期 node_modules 解析 remotion / react（单实例）。
import path from 'node:path';
import {existsSync} from 'node:fs';
import webpack from 'webpack';
import {Config} from '@remotion/cli/config';
Config.overrideWebpackConfig((c) => ({
  ...c,
  resolve: {...c.resolve, modules: [path.resolve(process.cwd(), 'node_modules'), 'node_modules']},
  plugins: [...(c.plugins ?? []), new webpack.DefinePlugin({
    __HAS_VOICE_AUDIO__: JSON.stringify(existsSync(path.resolve(process.cwd(), 'public/audio/voice.wav'))),
  })],
}));
