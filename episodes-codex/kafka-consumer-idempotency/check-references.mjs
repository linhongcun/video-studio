#!/usr/bin/env node
// Preserve the shared source checks, supplying this episode's configured slug.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const D=path.dirname(fileURLToPath(import.meta.url));
let root=D;while(!fs.existsSync(path.join(root,'AGENTS.md'))){const parent=path.dirname(root);if(parent===root)throw Error('Missing repository root');root=parent;}
const {checkSources}=await import(pathToFileURL(path.join(root,'site/scripts/check-references.mjs')).href);
if(process.argv.length!==4||process.argv[2]!=='--sources'||path.resolve(process.argv[3])!==D)throw Error('Use --sources with this episode directory');
const config=JSON.parse(fs.readFileSync(path.join(D,'episode-config.json'),'utf8'));
const {refs}=checkSources(D,{repoRoot:root,slug:config.slug});
console.log(`Reference source preflight passed: ${refs.episode}, ${refs.sources.length} sources; actual shared checks with explicit configured slug.`);
