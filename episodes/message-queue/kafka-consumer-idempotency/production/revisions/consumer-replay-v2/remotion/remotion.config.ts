import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
import {Config} from '@remotion/cli/config';
import {BundlerInternals} from '@remotion/bundler';
const D=path.resolve('..');let ROOT=D;
while(!fs.existsSync(path.join(ROOT,'AGENTS.md'))){const parent=path.dirname(ROOT);if(parent===ROOT)throw Error('Missing repository AGENTS.md');ROOT=parent;}
Config.setCachingEnabled(false);BundlerInternals.cacheExists=()=> 'does-not-exist';
Config.setBrowserExecutable('/usr/bin/chromium');
Config.overrideWebpackConfig(c=>({...c,resolve:{...c.resolve,alias:{...((c.resolve?.alias as Record<string,string>)??{}),'@storyboard':path.join(D,'storyboard.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:JSON.stringify(fs.existsSync('public/audio/voice.wav'))})]}));
