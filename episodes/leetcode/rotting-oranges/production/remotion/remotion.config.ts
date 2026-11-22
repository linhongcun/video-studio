import path from 'node:path';
import {existsSync} from 'node:fs';
import webpack from 'webpack';
import {Config} from '@remotion/cli/config';

const defaultChrome = existsSync('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  : 'google-chrome';

Config.setCachingEnabled(false);
Config.setBrowserExecutable(process.env.CHROME_BIN ?? defaultChrome);
Config.overrideWebpackConfig((config) => ({
  ...config,
  resolve: {
    ...config.resolve,
    alias: {
      ...((config.resolve?.alias as Record<string, string>) ?? {}),
      '@storyboard': path.resolve(
        existsSync('../storyboard.json') ? '../storyboard.json' : 'src/placeholders/storyboard.json',
      ),
    },
  },
  plugins: [
    ...(config.plugins ?? []),
    new webpack.DefinePlugin({
      __HAS_VOICE_AUDIO__: JSON.stringify(existsSync('public/audio/voice.wav')),
    }),
  ],
}));
