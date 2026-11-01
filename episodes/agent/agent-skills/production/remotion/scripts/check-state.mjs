// Cross-check the actual demo and spoken example before freezing/encoding.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
const root=path.resolve('..'),read=file=>JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
const plan=read('plan.json'),config=read('episode-config.json');
assert.equal(plan.length,config.shotCount);assert.equal(new Set(plan.map(x=>x.visualType)).size,plan.length);
const old=read('demo/fixtures/old-client-request.json'),required=read('demo/outputs/review.json'),optional=read('demo/outputs/review-optional.json');
assert.deepEqual(Object.keys(old).sort(),['quantity','sku']);assert.equal(old.sku,'SKU-7');assert.equal(old.quantity,1);
assert.deepEqual(required.newRequiredFields,['channel']);assert.deepEqual(required.oldClientValidation.missingRequiredFields,['channel']);
assert.deepEqual(optional.newRequiredFields,[]);assert.deepEqual(optional.oldClientValidation.missingRequiredFields,[]);
const sb=read('storyboard.json'),shots=sb.scenes.flatMap(x=>x.shots);assert.equal(shots.length,plan.length);
assert.deepEqual(shots.map(s=>s.visualType),plan.map(s=>s.visualType));assert.equal(sb.meta.provisionalTiming,false);
console.log(JSON.stringify({shots:shots.length,example:'SKU-7/quantity1; channel is newly required',requiredAndOptionalDemoEvidence:'passed',scope:'Simplified local contract validator; no HTTP/LLM performance claim'}));
