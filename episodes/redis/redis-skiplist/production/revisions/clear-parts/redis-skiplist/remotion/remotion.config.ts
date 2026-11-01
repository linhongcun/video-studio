import path from 'node:path';
import {existsSync} from 'node:fs';
import webpack from 'webpack';
import {Config} from '@remotion/cli/config';

Config.setCachingEnabled(false);
Config.setBrowserExecutable('/usr/bin/chromium');
Config.overrideWebpackConfig(config => ({
  ...config,
  resolve: {...config.resolve, alias: {
    ...((config.resolve?.alias as Record<string, string>) ?? {}),
    '@storyboard': path.resolve(existsSync('../storyboard.json')
      ? '../storyboard.json' : 'src/placeholders/storyboard.json'),
    '@covers': path.resolve('../covers.json'),
  }, modules: [path.resolve('node_modules'), 'node_modules']},
  plugins: [...(config.plugins ?? []), new webpack.DefinePlugin({
    __HAS_VOICE_AUDIO__: JSON.stringify(existsSync('public/audio/voice.wav')),
  })],
}));
