const path = require('node:path');
const fs = require('node:fs');
const {buildSync} = require('esbuild');
const output = path.resolve('out/ep03-verify.cjs');
try {
  buildSync({
    entryPoints: ['scripts/verify-storyboard.tsx'],
    bundle: true,
    platform: 'node',
    packages: 'external',
    external: ['react', 'react/*', 'react-dom', 'react-dom/*', 'remotion'],
    outfile: output,
    logLevel: 'error',
    sourcemap: 'inline',
  });
  require(output);
} finally {
  fs.rmSync(output, {force: true});
}
