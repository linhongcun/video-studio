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
const bg=(w,h)=>`<rect width="${w}" height="${h}" fill="${c.background}"/><image href="${background}" width="${w}" height="${h}" opacity=".75" preserveAspectRatio="xMidYMid slice"/>`;

function content(ep,portrait){
 const w=portrait?1080:1920,h=portrait?1440:1080,x=portrait?104:140;
 const center=w/2,brandX=w-x;
 const titleY=portrait?365:380,questionY=portrait?470:487;
 const panel=portrait?[104,560,872,650]:[365,530,1190,420];
 const image=portrait?[135,650,810,486]:[415,540,1090,385];
 return `${bg(w,h)}
 <g data-group="identity"><rect x="${x}" y="108" width="132" height="64" rx="18" fill="${c.coral}"/>
 ${txt('number',x+66,154,ep.number,39,c.background,'font-family="DejaVu Sans,sans-serif" font-weight="800" text-anchor="middle"')}
 ${txt('series',x+163,157,catalog.seriesLabel,portrait?43:48,c.violet,'font-weight="800" letter-spacing="3"')}
 ${txt('watermark',brandX,154,catalog.brand,30,c.muted,'font-weight="600" text-anchor="end"')}
 <path d="M${x} 218H${brandX}" stroke="${c.edge}" stroke-width="2"/></g>
 <g data-group="title">${txt('title',center,titleY,ep.title,portrait?112:126,c.text,'font-weight="900" text-anchor="middle" letter-spacing="-3"')}</g>
 ${txt('question',center,questionY,ep.question,portrait?35:42,c.violet,'font-weight="600" text-anchor="middle"')}
 <g data-group="diagram"><rect x="${panel[0]}" y="${panel[1]}" width="${panel[2]}" height="${panel[3]}" rx="32" fill="${c.surface}" fill-opacity=".92" stroke="${c.edge}" stroke-width="2"/>
 <svg x="${image[0]}" y="${image[1]}" width="${image[2]}" height="${image[3]}" viewBox="0 0 600 360">${diagram(ep.slug)}</svg></g>`;
}
export function cover(ep,size){
 if(!sizes[size])throw new Error('Unknown cover size '+size);
 const [w,h]=sizes[size];
 const body=size==='4x3'?`${bg(w,h)}<g transform="translate(315 0) scale(.75)">${content(ep,true)}</g>`:content(ep,size==='3x4');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(ep.episodePart+' '+ep.title)}" font-family="Noto Sans CJK SC,sans-serif">${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes){const dir=path.join(out,ep.slug);fs.mkdirSync(dir,{recursive:true});for(const size of Object.keys(sizes))fs.writeFileSync(path.join(dir,`cover-${size}.svg`),cover(ep,size));}
 console.log(`Generated ${catalog.episodes.length*3} covers: ${out}`);
}
