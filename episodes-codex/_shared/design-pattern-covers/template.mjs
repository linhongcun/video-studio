import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {diagram} from './diagrams.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
export const catalog=JSON.parse(fs.readFileSync(path.join(here,'catalog.json'),'utf8'));
export const sizes={'16x9':[1920,1080],'3x4':[1080,1440],'4x3':[1440,1080]};
const c=catalog.palette;
const background='data:image/png;base64,'+fs.readFileSync(path.join(here,'background.png')).toString('base64');
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const txt=(id,x,y,s,size,fill=c.text,extra='')=>`<text data-element="${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const bg=(w,h)=>`<rect width="${w}" height="${h}" fill="${c.background}"/><image href="${background}" width="${w}" height="${h}" opacity=".72" preserveAspectRatio="none"/>`;
function mark(x,y){return `<g transform="translate(${x} ${y})" fill="none" stroke="${c.blue}" stroke-width="4"><rect x="0" y="0" width="22" height="22" rx="3"/><rect x="39" y="0" width="22" height="22" rx="3"/><rect x="39" y="39" width="22" height="22" rx="3" stroke="${c.orange}"/><path d="M22 11H39M50 22V39"/></g>`;}

function content(ep,portrait){
 const [w,h]=portrait?sizes['3x4']:sizes['16x9'],x=portrait?104:140;
 const panel=portrait?[104,650,872,550]:[140,610,1640,280];
 const image=portrait?[123,730,834,440]:[180,650,1560,230];
 return `${bg(w,h)}
 <g data-group="header">${mark(x,104)}${txt('series',x+88,151,catalog.seriesLabel,46,c.text,'font-weight="800" letter-spacing="3"')}
 ${txt('watermark',portrait?w-x:w-x-100,149,catalog.brand,30,c.muted,'font-weight="700" text-anchor="end"')}
 <path d="M${x} 209H${w-x}" stroke="${c.edge}" stroke-width="2"/></g>
 <g data-group="identity"><rect x="${x}" y="${portrait?256:238}" width="160" height="60" rx="6" fill="${c.blue}"/>
 ${txt('number',x+80,portrait?299:281,ep.number,36,c.surface,'font-family="DejaVu Sans,sans-serif" font-weight="800" text-anchor="middle"')}</g>
 <g data-group="title">${txt('title',portrait?100:132,portrait?458:455,ep.title,portrait?106:120,c.text,'font-weight="900" letter-spacing="-3"')}</g>
 ${txt('question',x,portrait?565:555,ep.question,portrait?34:42,c.text,'font-weight="500"')}
 <g data-group="diagram"><rect x="${panel[0]}" y="${panel[1]}" width="${panel[2]}" height="${panel[3]}" rx="16" fill="${c.surface}" stroke="${c.edge}" stroke-width="2"/>
 ${txt('diagram-label',panel[0]+30,panel[1]+43,'教学示例 · '+ep.boundary,portrait?24:25,c.muted)}
 <svg x="${image[0]}" y="${image[1]}" width="${image[2]}" height="${image[3]}" viewBox="${portrait?'0 0 600 400':'0 0 1200 250'}">${diagram(ep.slug,portrait)}</svg></g>`;
}
export function cover(ep,size){
 if(!sizes[size])throw new Error('Unknown cover size '+size);
 const [w,h]=sizes[size];
 const body=size==='4x3'?`<rect width="${w}" height="${h}" fill="${c.background}"/><g transform="translate(315 0) scale(.75)">${content(ep,true)}</g>`:content(ep,size==='3x4');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(ep.number+' '+ep.title)}" font-family="Noto Sans CJK SC,sans-serif">${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes){const dir=path.join(out,ep.slug);fs.mkdirSync(dir,{recursive:true});for(const size of Object.keys(sizes))fs.writeFileSync(path.join(dir,`cover-${size}.svg`),cover(ep,size));}
 console.log(`Generated ${catalog.episodes.length*3} covers: ${out}`);
}
