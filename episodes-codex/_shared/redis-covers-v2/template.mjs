import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {diagram} from './diagrams.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const catalog=JSON.parse(fs.readFileSync(path.join(here,'catalog.json'),'utf8'));
const style=JSON.parse(fs.readFileSync(path.join(here,'style-v1.json'),'utf8'));
const C=style.palette;
export const sizes={'16x9':[1920,1080],'3x4':[1080,1440],'4x3':[1440,1080]};
const bg='data:image/png;base64,'+fs.readFileSync(path.join(here,'background.png')).toString('base64');
const logo='data:image/svg+xml;base64,'+fs.readFileSync(path.join(here,'../middleware-identity/redis-original.svg')).toString('base64');
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const txt=(id,x,y,s,size,fill=C.text,extra='')=>`<text data-element="${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
function content(ep,portrait,proof){
 if(!/^EP\.\d{2,3}$/.test(ep.number))throw new Error('Use actual two/three digit EP number');
 if(!Array.isArray(ep.titleLines)||ep.titleLines.length<1||ep.titleLines.length>2||ep.questionLines.length<1||ep.questionLines.length>2)throw new Error('One/two title/question lines required');
 const [w,h]=portrait?sizes['3x4']:sizes['16x9'];
 const x=portrait?96:132,two=ep.titleLines.length===2;
 const titleSize=portrait?(two?100:140):(two?100:160);
 const titleY=portrait?(two?455:510):(two?495:580);
 const titleStep=portrait?125:128;
 const questionY=portrait?(two?680:635):(two?770:735);
 const panel=portrait?[96,820,888,380]:[950,290,830,565];
 const graph=portrait?[120,848,840,350]:[974,390,782,326];
 return `<rect width="${w}" height="${h}" fill="${C.background}"/><image href="${bg}" width="${w}" height="${h}" preserveAspectRatio="none"/>
 <g data-group="header"><image data-ink="redis-mark" href="${logo}" x="${x}" y="94" width="74" height="74"/>
 ${txt('series',x+98,147,catalog.seriesLabel,portrait?42:46,C.redDark,'font-weight="800"')}
 ${txt('watermark',w-x,145,catalog.brand,29,C.muted,'font-weight="700" text-anchor="end"')}
 <path data-ink="header-rule" d="M${x} 209H${w-x}" stroke="${C.edge}" stroke-width="2"/></g>
 <g data-group="identity"><rect data-ink="number-badge" x="${x}" y="${portrait?260:290}" width="235" height="62" rx="11" fill="${C.red}"/>
 ${txt('number',x+117.5,portrait?304:334,ep.number,38,'#FFFFFF','font-family="DejaVu Sans,sans-serif" font-weight="800" text-anchor="middle"')}</g>
 <g data-group="title">${ep.titleLines.map((s,i)=>txt('title-'+i,x-6,titleY+i*titleStep,s,titleSize,i?C.redDark:C.text,'font-weight="900" letter-spacing="-2"')).join('')}</g>
 <g data-group="question">${ep.questionLines.map((s,i)=>txt('question-'+i,x,questionY+i*(portrait?50:55),s,portrait?36:42,C.muted,'font-weight="600"')).join('')}</g>
 <g data-group="diagram"><rect data-ink="diagram-panel" x="${panel[0]}" y="${panel[1]}" width="${panel[2]}" height="${panel[3]}" rx="25" fill="${C.surface}" fill-opacity=".96" stroke="${C.edge}" stroke-width="2"/>
 ${portrait?'':txt('diagram-caption',panel[0]+28,panel[1]+48,proof?'文字压力检查 · 非单集封面':ep.diagramCaption??'前向链接示例',26,C.muted,'font-weight="600"')}
 ${proof?txt('proof-caption',panel[0]+panel[2]/2,panel[1]+200,'仅检查文字排版',30,C.muted,'text-anchor="middle"'): `<svg x="${graph[0]}" y="${graph[1]}" width="${graph[2]}" height="${graph[3]}" viewBox="0 0 840 350" overflow="visible">${diagram(ep.slug)}</svg>`}
 </g>
 ${portrait?txt('portrait-boundary',x,794,proof?'文字压力检查 · 非单集封面':ep.boundary,25,C.muted,'font-weight="600"'):''}`;
}
export function cover(ep,size,proof=false){
 const [w,h]=sizes[size]||[];if(!w)throw new Error('Unknown cover size '+size);
 const body=size==='4x3'?`<rect width="${w}" height="${h}" fill="${C.background}"/><g transform="translate(315 0) scale(.75)">${content(ep,true,proof)}</g>`:content(ep,size==='3x4',proof);
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(ep.number+' Redis '+ep.titleLines.join(' '))}" font-family="${esc(style.fontFamily)}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes.filter(ep=>!(catalog.preservedEpisodes??[]).includes(ep.slug))){const dir=path.join(out,ep.slug);fs.mkdirSync(dir,{recursive:true});for(const size of Object.keys(sizes))fs.writeFileSync(path.join(dir,`cover-${size}.svg`),cover(ep,size));}
 const proofs=JSON.parse(fs.readFileSync(path.join(here,'plan-layout.json'),'utf8')).entries;
 const pdir=path.join(out,'typography-only');fs.mkdirSync(pdir,{recursive:true});for(const ep of proofs)for(const size of Object.keys(sizes))fs.writeFileSync(path.join(pdir,`${ep.slug}-${size}.svg`),cover(ep,size,true));
}
