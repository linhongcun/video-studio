// Scoped article SVG correction: build once, inspect actual native SVG attributes
// at desktop/mobile sizes. Reuse the already passed media/chapter/caption suite.
const fs=require('node:fs'), path=require('node:path'), cp=require('node:child_process'), crypto=require('node:crypto'), assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../..'), site=path.join(root,'site'), dist=path.join(site,'dist'), out=path.join(__dirname,'site-qa');
const json=(p)=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=(b)=>crypto.createHash('sha256').update(b).digest('hex');
const fileSha=(p)=>sha(fs.readFileSync(p));
const files=(dir)=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
const fingerprint=(paths)=>sha([...paths].sort().map(p=>`${path.relative(root,p)}\0${fileSha(p)}`).join('\n'));
const derivation=json(path.join(__dirname,'site-article-derivation.json'));
const production=fs.readFileSync(path.join(__dirname,'article.mdx'),'utf8');
let derived=production; for(const t of derivation.transformations)derived=derived.replaceAll(t.from,t.to);
assert.equal(derived,fs.readFileSync(path.join(__dirname,'article-site.mdx'),'utf8'));
assert.equal(fileSha(path.join(__dirname,'article.mdx')),derivation.baselineSha256);
assert.equal(fileSha(path.join(__dirname,'article-site.mdx')),derivation.derivedSha256);
assert.equal(fileSha(path.join(root,'episodes/observer-pattern/article.mdx')),derivation.derivedSha256);
const manifest=json(path.join(__dirname,'site-copy-manifest.json'));
for(const f of manifest.files){assert.equal(fileSha(path.join(root,'episodes/observer-pattern',f.file)),f.sha256);assert.equal(fileSha(path.join(__dirname,f.sourceFile||f.file)),f.sha256);}
const oldReport=json(path.join(__dirname,'site-browser-check.json'));
assert.equal(oldReport.status,'passed');assert.equal(oldReport.browserChecks.length,2);
assert.ok(oldReport.browserChecks.every(v=>v.seeks.length===5&&v.captions.cueCount===24));
const version=json(path.join(site,'package.json')).version;
assert.equal(oldReport.siteVersion,version);
const inputFiles=fs.readdirSync(path.join(root,'episodes')).filter(s=>fs.existsSync(path.join(root,'episodes',s,'meta.json'))).flatMap(s=>['meta.json','article.mdx','storyboard.json'].map(n=>path.join(root,'episodes',s,n)).filter(fs.existsSync));
const inputFingerprint=fingerprint([...files(path.join(site,'src')),...files(path.join(site,'scripts')),path.join(site,'package.json'),path.join(site,'package-lock.json'),path.join(site,'astro.config.mjs'),...inputFiles,path.join(root,'episodes/observer-pattern/video.mp4'),path.join(root,'episodes/observer-pattern/cover-16x9.jpg')]);
const reuseBuild=process.argv.includes('--reuse-build');
if(reuseBuild){const receipt=json(path.join(out,'build-receipt.json'));assert.equal(receipt.inputFingerprint,inputFingerprint);assert.equal(receipt.distFingerprint,fingerprint(files(dist)));assert.equal(receipt.buildPassed,true);}
const build=reuseBuild?{status:0,stdout:'',stderr:''}:cp.spawnSync('npm',['run','build'],{cwd:site,encoding:'utf8',maxBuffer:32*1024*1024});
if(!reuseBuild)fs.writeFileSync(path.join(out,'build-svg-correction.log'),`${build.stdout||''}${build.stderr||''}`);
if(build.error)throw build.error;assert.equal(build.status,0,'Build failed; see site-qa/build-svg-correction.log');
const buildReceipt={inputFingerprint,distFingerprint:fingerprint(files(dist)),checkedAtUTC:new Date().toISOString(),buildPassed:true,reusedForScopedBrowserResume:reuseBuild,scope:'Only article SVG native attribute derivative; previous full media/chapter/caption checks retained.',previousReceipt:'site-qa/before-svg-native-attributes/build-receipt.json',historicalRegressionReused:true};
fs.writeFileSync(path.join(out,'build-receipt.json'),JSON.stringify(buildReceipt,null,2)+'\n');
const preview=cp.spawn(process.execPath,[path.join(site,'node_modules/astro/astro.js'),'preview','--host','127.0.0.1','--port','4199'],{cwd:site,stdio:'ignore'});
(async()=>{let browser;const checks=[];try{
for(let i=0;i<100;i++){try{if((await fetch('http://127.0.0.1:4199/video-studio/')).ok)break;}catch{}assert.ok(i<99,'Preview did not start');await new Promise(r=>setTimeout(r,100));}
browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
for(const [width,theme]of [[1440,'light'],[390,'dark']]){
const context=await browser.newContext({viewport:{width,height:900},colorScheme:theme}),page=await context.newPage();
const response=await page.goto('http://127.0.0.1:4199/video-studio/episodes/observer-pattern/',{waitUntil:'networkidle'});assert.equal(response.status(),200);await page.evaluate(()=>document.fonts.ready);
const figures=page.locator('article figure');assert.equal(await figures.count(),2);
for(let i=0;i<2;i++){
const result=await figures.nth(i).evaluate(figure=>{const svg=figure.querySelector('svg'),box=svg.viewBox.baseVal;return{viewBox:{width:box.width,height:box.height},texts:[...svg.querySelectorAll('text')].map(el=>{const b=el.getBBox();return{text:el.textContent,nativeFontSize:el.getAttribute('font-size'),computedFontSize:getComputedStyle(el).fontSize,nativeTextAnchor:el.getAttribute('text-anchor'),computedTextAnchor:getComputedStyle(el).textAnchor,nativeX:el.getAttribute('x'),computedTextLength:el.getComputedTextLength(),bbox:{x:b.x,y:b.y,width:b.width,height:b.height}}}),paths:[...svg.querySelectorAll('path')].map(el=>({nativeStrokeWidth:el.getAttribute('stroke-width'),computedStrokeWidth:getComputedStyle(el).strokeWidth})),rect:figure.getBoundingClientRect().toJSON()};});
for(const t of result.texts){assert.ok(t.nativeFontSize);assert.equal(parseFloat(t.computedFontSize),Number(t.nativeFontSize));assert.ok(t.bbox.x>=0&&t.bbox.x+t.bbox.width<=result.viewBox.width+0.1);assert.ok(t.bbox.y>=0&&t.bbox.y+t.bbox.height<=result.viewBox.height+0.1);}
for(const p of result.paths){assert.ok(p.nativeStrokeWidth);assert.equal(parseFloat(p.computedStrokeWidth),Number(p.nativeStrokeWidth));}
if(i===0){const contract=result.texts.find(t=>t.text.startsWith('共同约定'));assert.equal(contract.computedTextAnchor,'middle');assert.equal(Number(contract.nativeX),215);assert.equal(result.texts.find(t=>t.text==='订单来源').computedFontSize,'23px');}
const screenshot=path.join(out,`observer-figure-corrected-${i+1}-${width}-${theme}.png`);await figures.nth(i).screenshot({path:screenshot});
checks.push({width,theme,figure:i+1,...result,screenshot:path.relative(root,screenshot),screenshotSha256:fileSha(screenshot)});
}
assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
// Default track remains disabled; enabling it in the original cue QA was intentional.
const trackMode=await page.locator('video').evaluate(v=>v.textTracks[0].mode);assert.equal(trackMode,'disabled');
await page.locator('video').evaluate(v=>{v.muted=true;v.currentTime=3;});
await page.locator('video').evaluate(v=>v.play());
await page.waitForFunction(()=>{const v=document.querySelector('video');return v.currentTime>3.6&&!v.paused&&v.readyState>=3&&v.getVideoPlaybackQuality().totalVideoFrames>0;});
await page.locator('video').evaluate(v=>v.pause());
await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
await page.mouse.move(10,10);await page.evaluate(()=>scrollTo({top:0,left:0,behavior:'instant'}));
await page.screenshot({path:path.join(out,`observer-player-default-captions-${width}-${theme}.png`)});
await context.close();
}
const report={status:'passed',checkedAtUTC:new Date().toISOString(),executedBy:'Codex observer_site agent',release:'v'+version,articleDerivation:derivation,build:buildReceipt,checks,
previousFullSuite:'site-qa/before-svg-native-attributes/site-browser-check.json',mediaChapterCaptionSuiteRepeated:false,mediaAndFrozenArticleUnchanged:true,scope:'Actual built native SVG attributes, computed sizes/anchors/strokes, all text bounding boxes and no page overflow; two figures at 1440/390. Default captions disabled. New screenshots captured for visual review.'};
fs.writeFileSync(path.join(__dirname,'site-svg-correction.json'),JSON.stringify(report,null,2)+'\n');
oldReport.articleSvgCorrection={status:'passed',checkedAtUTC:report.checkedAtUTC,articleSource:'article-site.mdx',articleSha256:derivation.derivedSha256,report:'site-svg-correction.json',previousFullSuite:report.previousFullSuite,originalFullSuiteRepeated:false,reason:'Only SVG presentation attributes changed; media, chapters, narration and subtitle timing unchanged.'};
fs.writeFileSync(path.join(__dirname,'site-browser-check.json'),JSON.stringify(oldReport,null,2)+'\n');
const staticReport=json(path.join(__dirname,'site-static-check.json'));staticReport.articleSvgCorrection=oldReport.articleSvgCorrection;staticReport.finalBuildCheckedAtUTC=report.checkedAtUTC;staticReport.articleSha256=derivation.derivedSha256;staticReport.articleSource='article-site.mdx';fs.writeFileSync(path.join(__dirname,'site-static-check.json'),JSON.stringify(staticReport,null,2)+'\n');
console.log(JSON.stringify({status:'passed',figures:checks.length,articleSha256:derivation.derivedSha256,report:'site-svg-correction.json'}));
}finally{if(browser)await browser.close();preview.kill('SIGTERM');}})().catch(e=>{console.error(e);process.exitCode=1;});
