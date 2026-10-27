import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {diagram} from './diagrams.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
export const catalog=JSON.parse(fs.readFileSync(path.join(here,'catalog.json'),'utf8'));
export const sizes={'16x9':[1920,1080],'3x4':[1080,1440],'4x3':[1440,1080]};
const c=catalog.palette;
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const txt=(id,x,y,s,size,fill=c.text,extra='')=>`<text data-element="${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const line=(x,y,w)=>`<path d="M${x} ${y}h${w}" stroke="${c.edge}" stroke-width="2"/>`;

function header(portrait){
 const x=portrait?104:140,brandX=portrait?976:1780,y=portrait?132:142;
 return `<g data-group="header">${txt('series',x,y,'LeetCode',portrait?42:44,c.text,'font-family="DejaVu Sans, sans-serif" font-weight="750" letter-spacing="-1"')}
 ${txt('series-label',x,y+50,catalog.seriesLabel,portrait?26:28,c.muted,'letter-spacing="5"')}
 ${txt('watermark',brandX,y,catalog.brand,portrait?30:32,c.muted,'text-anchor="end" font-weight="600"')}
 ${line(x,y+84,portrait?872:1640)}</g>`;
}
function badge(ep,x,y){
 const n=`LC.${ep.number}`,w=ep.number>99?192:ep.number>9?172:150;
 return `<g data-group="identity"><rect x="${x}" y="${y}" width="${w}" height="58" rx="15" fill="${c.gold}"/>
 ${txt('number',x+w/2,y+40,n,32,c.background,'text-anchor="middle" font-family="DejaVu Sans,sans-serif" font-weight="750"')}
 ${txt('method',x+w+24,y+40,ep.method,32,c.teal,'font-weight="600"')}</g>`;
}
function portrait(ep){
 const titleY=460;
 return `${header(true)}${badge(ep,104,265)}
 <g data-group="title">${ep.title.map((s,i)=>txt('title-'+i,100,titleY+i*119,s,104,i?c.gold:c.text,'font-weight="900" letter-spacing="-3"')).join('')}</g>
 ${txt('question',104,ep.title.length===2?664:578,ep.question,35,c.muted,'font-weight="500"')}
 <g data-group="diagram"><rect x="104" y="720" width="872" height="490" rx="28" fill="${c.surface}"/>
 ${txt('example',136,764,'题目示例',25,c.muted)}
 <svg x="126" y="772" width="828" height="416" viewBox="0 0 600 400">${diagram(ep.number)}</svg></g>`;
}
function landscape(ep){
 const titleY=510;
 return `${header(false)}${badge(ep,140,295)}
 <g data-group="title">${ep.title.map((s,i)=>txt('title-'+i,134,titleY+i*143,s,124,i?c.gold:c.text,'font-weight="900" letter-spacing="-4"')).join('')}</g>
 ${txt('question',140,ep.title.length===2?750:626,ep.question,40,c.muted,'font-weight="500"')}
 <g data-group="diagram"><rect x="1080" y="295" width="700" height="585" rx="30" fill="${c.surface}"/>
 ${txt('example',1122,350,'题目示例',28,c.muted)}
 <svg x="1094" y="365" width="672" height="488" viewBox="0 0 600 400">${diagram(ep.number)}</svg></g>
 <g data-group="accent"><path d="M140 822h60" stroke="${c.gold}" stroke-width="7" stroke-linecap="round"/>
 ${txt('tagline',226,834,'从题意，到思路',30,c.muted,'letter-spacing="3"')}</g>`;
}
export function cover(ep,size){
 if(!sizes[size])throw new Error('Unknown cover size '+size);
 const [w,h]=sizes[size];
 const body=size==='16x9'?landscape(ep):size==='3x4'?portrait(ep):`<g transform="translate(315 0) scale(.75)">${portrait(ep)}</g>`;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="LeetCode ${ep.number} ${esc(ep.title.join(''))}" font-family="Noto Sans CJK SC, sans-serif"><rect width="${w}" height="${h}" fill="${c.background}"/>${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');
 if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes){
  const dir=path.join(out,ep.slug);fs.mkdirSync(dir,{recursive:true});
  for(const size of Object.keys(sizes))fs.writeFileSync(path.join(dir,`cover-${size}.svg`),cover(ep,size));
 }
 console.log(`Generated ${catalog.episodes.length*3} covers: ${out}`);
}
