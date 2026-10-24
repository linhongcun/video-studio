const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const ROOT=path.resolve(__dirname,'../..');
const compiler=require(require.resolve('esbuild',{paths:[path.join(ROOT,'episodes-codex/dns/remotion')]}));
const slugs=process.argv.slice(2);if(!slugs.length)slugs.push(...JSON.parse(fs.readFileSync(path.join(__dirname,'index.json'))).selected);const records=[];
for(const slug of slugs){
 const D=path.join(ROOT,'episodes-codex',slug),sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'))),cache=new Map();
 function load(file){
  if(cache.has(file))return cache.get(file).exports;
  if(file.endsWith('.json'))return JSON.parse(fs.readFileSync(file));
  const module={exports:{}};cache.set(file,module);
  const code=compiler.transformSync(fs.readFileSync(file,'utf8'),{loader:file.endsWith('.tsx')?'tsx':'ts',format:'cjs',target:'es2022'}).code;
  const req=(name)=>{
   if(name==='@storyboard')return sb;
   if(!name.startsWith('.'))return require(name);
   const stem=path.resolve(path.dirname(file),name);
   const target=[stem,stem+'.ts',stem+'.tsx',stem+'.json',path.join(stem,'index.ts')].find(p=>fs.existsSync(p)&&fs.statSync(p).isFile());
   assert(target,`Cannot resolve ${name} in ${file}`);return load(target);
  };
  new Function('require','module','exports',code)(req,module,module.exports);return module.exports;
 }
 const nav=load(path.join(D,'remotion/src/branch-map.ts'));
 const common=load(path.join(ROOT,'episodes-codex/_shared/branch-map/index.ts'));
 let motion={};const motionFile=path.join(D,'remotion/src/motion.ts');if(fs.existsSync(motionFile))motion=load(motionFile);
 const shots=sb.scenes.flatMap(sc=>sc.shots).map(s=>({...s,id:String(s.id).padStart(2,'0')}));
 const functions=Object.entries(nav).filter(([name,value])=>typeof value==='function');
 const specs=Object.values(nav).filter(value=>value&&Array.isArray(value.nodes)&&value.shots);
 let total=0;const shotRows=[];let globalGeometry=null;
 for(const shot of shots){
  const getSpec=f=>{
   for(const [name,fn] of functions){if(!/(spec|map)/i.test(name))continue;const value=fn(shot,f);if(value&&Array.isArray(value.nodes)&&value.shots)return value;}
   for(const value of specs)if(value.shots[shot.id])return value;
   throw Error(`No map spec for ${slug}/${shot.id}; exports=${Object.keys(nav)}`);
  };
  let geometry=null,focus=null,previousState=null;const phases={},focusChanges=[];
  for(let f=0;f<shot.durationInFrames;f++){
   const spec=getSpec(f),ids=new Set(spec.nodes.map(n=>n.id));assert(ids.size===spec.nodes.length,'Repeated node');
   for(const e of spec.edges)assert(ids.has(e.from)&&ids.has(e.to),`Invalid edge ${e.id}`);
   const shape=JSON.stringify(spec.nodes.map(n=>[n.id,n.x,n.y,n.w]));if(globalGeometry===null)globalGeometry=shape;assert(shape===globalGeometry,`${slug}: world geometry changed across shots`);if(geometry===null)geometry=shape;assert(shape===geometry,`${slug}/${shot.id}: geometry drift`);
   const s=common.actualNavState(spec,shot.id,f,shot.durationInFrames),node=spec.nodes.find(n=>n.id===s.focusId);
   if(focus===null)focus=s.focusId;
   if(focus!==s.focusId){
    assert(previousState&&previousState.phase==='detail'&&s.phase==='detail'&&previousState.progress===1&&s.progress===1&&previousState.mapOpacity===0&&s.mapOpacity===0,`${slug}/${shot.id}: focus changed while map or camera visible`);
    const priorNode=spec.nodes.find(n=>n.id===focus);
    const box=(n,z)=>{const w=n.w??240,h=w*900/1920;return [(n.x-w/2)*z.camera.scale+z.camera.tx,(n.y-h/2)*z.camera.scale+z.camera.ty,w*z.camera.scale,h*z.camera.scale]};
    const a=box(priorNode,previousState),b=box(node,s);assert(a.every((v,i)=>Math.abs(v-b[i])<1e-6),`${slug}/${shot.id}: visible detail jumped`);
    focusChanges.push({local:f,from:focus,to:s.focusId,reason:'Explicit detail context change; map fully hidden and projected detail box identical'});focus=s.focusId;
   }
   previousState=s;
   const {scale,tx,ty}=s.camera,x=node.x*scale+tx,y=node.y*scale+ty;
   assert([scale,tx,ty,x,y].every(Number.isFinite));assert(scale>=1);assert(x>=0&&x<=1920&&y>=160&&y<=900,`${slug}/${shot.id}/${f}: subject off canvas`);
   phases[s.phase]=(phases[s.phase]??0)+1;total++;
  }
  const windows=typeof motion.mechanismWindows==='function'?motion.mechanismWindows(shot):[];
  for(const [name,a,b] of windows){
   assert(a>=0&&b>=a&&b<shot.durationInFrames,`${slug}/${shot.id}/${name}: window outside shot`);
   for(let f=a;f<=b;f++){
    const state=common.actualNavState(getSpec(f),shot.id,f,shot.durationInFrames);
    assert(state.phase==='detail',`${slug}/${shot.id}/${name}/${f}: mechanism during ${state.phase}`);
   }
  }
  shotRows.push({id:shot.id,frames:shot.durationInFrames,focus,phases,hiddenMapFocusChanges:focusChanges,mechanismWindows:windows});
 }
 records.push({slug,framesAudited:total,shots:shotRows,mechanismWindowAuditAvailable:typeof motion.mechanismWindows==='function',navSourceSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(D,'remotion/src/branch-map.ts'))).digest('hex')});
}
console.log(JSON.stringify({status:'passed',scope:'Actual per-frame camera geometry, visibility, stable visible camera focus, recorded hidden-map detail context changes and explicitly declared mechanism windows; does not score readability or infer undeclared actions.',episodes:records},null,2));
