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
const bg=(w,h)=>`<rect width="${w}" height="${h}" fill="${c.background}"/><image href="${background}" width="${w}" height="${h}" opacity=".65" preserveAspectRatio="xMidYMid slice"/>`;
function mark(x,y){return `<g transform="translate(${x} ${y})" fill="${c.surface}" stroke="${c.mint}" stroke-width="3"><path d="M0 12V47C0 63 64 63 64 47V12"/><ellipse cx="32" cy="12" rx="32" ry="12"/><path d="M0 30C0 46 64 46 64 30M0 47C0 63 64 63 64 47" fill="none"/></g>`;}

function content(ep,portrait){
 const [w,h]=portrait?sizes['3x4']:sizes['16x9'],x=portrait?104:140;
 const panel=portrait?[104,710,872,500]:[1040,290,740,580];
 const image=portrait?[135,760,810,430]:[1060,378,700,420];
 return `${bg(w,h)}
 <g data-group="header">${mark(x,105)}${txt('series',x+94,155,catalog.seriesLabel,46,c.mint,'font-weight="800" letter-spacing="3"')}
 ${txt('watermark',w-x,154,catalog.brand,30,c.muted,'font-weight="600" text-anchor="end"')}
 <path d="M${x} 218H${w-x}" stroke="${c.edge}" stroke-width="2"/></g>
 <g data-group="identity"><rect x="${x}" y="${portrait?270:294}" width="198" height="60" rx="13" fill="${c.mint}"/>
 ${txt('number',x+99,portrait?313:337,ep.number,36,c.background,'font-family="DejaVu Sans,sans-serif" font-weight="800" text-anchor="middle"')}</g>
 <g data-group="title">${txt('title',portrait?100:132,portrait?468:510,ep.title,portrait?104:120,c.text,'font-weight="900" letter-spacing="-3"')}</g>
 ${txt('question',portrait?104:140,portrait?584:632,ep.question,portrait?35:38,c.mint,'font-weight="600"')}
 ${txt('boundary',portrait?104:140,portrait?644:774,ep.boundary,portrait?28:30,c.muted)}
 ${txt('scope',portrait?104:140,portrait?690:834,ep.scope,portrait?24:26,c.muted)}
 <g data-group="diagram"><rect x="${panel[0]}" y="${panel[1]}" width="${panel[2]}" height="${panel[3]}" rx="26" fill="${c.surface}" fill-opacity=".97" stroke="${c.edge}" stroke-width="2"/>
 ${txt('diagram-label',panel[0]+32,panel[1]+47,'教学示例',25,c.muted)}
 <svg x="${image[0]}" y="${image[1]}" width="${image[2]}" height="${image[3]}" viewBox="0 0 600 360">${diagram(ep.slug)}</svg></g>`;
}
export function cover(ep,size){
 if(!sizes[size])throw new Error('Unknown cover size '+size);
 const [w,h]=sizes[size];
 const body=size==='4x3'?`${bg(w,h)}<g transform="translate(315 0) scale(.75)">${content(ep,true)}</g>`:content(ep,size==='3x4');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(ep.number+' '+ep.title)}" font-family="Noto Sans CJK SC,sans-serif">${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes){const dir=path.join(out,ep.slug);fs.mkdirSync(dir,{recursive:true});for(const size of Object.keys(sizes))fs.writeFileSync(path.join(dir,`cover-${size}.svg`),cover(ep,size));}
 console.log(`Generated ${catalog.episodes.length*3} covers: ${out}`);
}
