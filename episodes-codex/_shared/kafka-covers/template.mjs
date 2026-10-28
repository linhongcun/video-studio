import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {diagram} from './diagrams.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
export const catalog=JSON.parse(fs.readFileSync(path.join(here,'catalog.json'),'utf8'));
export const style=JSON.parse(fs.readFileSync(path.join(here,'style-v1.json'),'utf8'));
export const sizes={'16x9':[1920,1080],'3x4':[1080,1440],'4x3':[1440,1080]};
const c=style.palette;
const background='data:image/png;base64,'+fs.readFileSync(path.join(here,'background.png')).toString('base64');
const logo='data:image/svg+xml;base64,'+fs.readFileSync(path.join(here,'../middleware-identity/apachekafka-original.svg')).toString('base64');
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const txt=(id,x,y,s,size,fill=c.text,extra='')=>`<text data-element="${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const bg=(w,h)=>`<rect width="${w}" height="${h}" fill="${c.background}"/><image href="${background}" width="${w}" height="${h}" opacity=".6" preserveAspectRatio="none"/>`;
function content(ep,portrait,proof){
 if(!/^MQ\d{2,3}$/.test(ep.number))throw new Error('Use stable two/three digit MQ index');
 if(!Array.isArray(ep.titleLines)||ep.titleLines.length<1||ep.titleLines.length>2||ep.questionLines.length<1||ep.questionLines.length>2)throw new Error('One or two title/question lines required');
 const [w,h]=portrait?sizes['3x4']:sizes['16x9'],x=portrait?104:140;
 const panel=portrait?[104,755,872,445]:[1040,285,740,600];
 const image=portrait?[133,813,814,365]:[1060,374,700,465];
 const titleY=portrait?445:(ep.titleLines.length===1?510:475),step=portrait?140:150;
 const questionY=portrait?670:(ep.titleLines.length===1?650:750);
 return `${bg(w,h)}
 <g data-group="header"><rect x="${x}" y="100" width="66" height="66" rx="9" fill="${c.text}"/><image href="${logo}" x="${x+9}" y="109" width="48" height="48"/>
 ${txt('series',x+94,151,catalog.seriesLabel,portrait?40:46,c.orange,'font-weight="800"')}
 ${txt('watermark',portrait?w-x:w-x-100,149,catalog.brand,30,c.muted,'font-weight="700" text-anchor="end"')}
 <path d="M${x} 209H${w-x}" stroke="${c.edge}" stroke-width="2"/></g>
 <g data-group="identity"><rect x="${x}" y="${portrait?255:270}" width="230" height="60" rx="10" fill="${c.orange}"/>
 ${txt('number',x+115,portrait?298:313,ep.number,40,c.background,'font-family="DejaVu Sans,sans-serif" font-weight="800" text-anchor="middle"')}</g>
 <g data-group="title">${ep.titleLines.map((s,i)=>txt('title-'+i,x-8,titleY+i*step,s,portrait?100:112,i?c.orange:c.text,'font-weight="900" letter-spacing="-2"')).join('')}</g>
 ${ep.questionLines.map((s,i)=>txt(i?'question-'+i:'question',x,questionY+i*(portrait?48:54),s,portrait?32:38,c.blue,'font-weight="600"')).join('')}
 <g data-group="diagram"><rect x="${panel[0]}" y="${panel[1]}" width="${panel[2]}" height="${panel[3]}" rx="24" fill="${c.surface}" fill-opacity=".97" stroke="${c.edge}" stroke-width="2"/>
 ${txt('diagram-label',panel[0]+28,panel[1]+43,proof?'规划排版检查 · 非成片':'教学示例',portrait?24:25,c.muted)}
 ${proof?'':`<svg x="${image[0]}" y="${image[1]}" width="${image[2]}" height="${image[3]}" viewBox="0 0 600 420">${diagram(ep.slug,portrait)}</svg>`}</g>`;
}
export function cover(ep,size,proof=false){
 if(!sizes[size])throw new Error('Unknown cover size '+size);
 const [w,h]=sizes[size];
 const body=size==='4x3'?`<rect width="${w}" height="${h}" fill="${c.background}"/><g transform="translate(315 0) scale(.75)">${content(ep,true,proof)}</g>`:content(ep,size==='3x4',proof);
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(ep.number+' '+ep.titleLines.join(' '))}" font-family="${esc(style.fontFamily)}">${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes){const dir=path.join(out,ep.slug);fs.mkdirSync(dir,{recursive:true});for(const size of Object.keys(sizes))fs.writeFileSync(path.join(dir,`cover-${size}.svg`),cover(ep,size));}
 const proofs=JSON.parse(fs.readFileSync(path.join(here,'plan-layout.json'),'utf8')).entries;
 const pdir=path.join(out,'typography-only');fs.mkdirSync(pdir,{recursive:true});
 for(const ep of [...proofs,{...proofs[0],number:'MQ100'}])for(const size of Object.keys(sizes))fs.writeFileSync(path.join(pdir,`${ep.number}-${size}.svg`),cover(ep,size,true));
 console.log(`Generated ${catalog.episodes.length*3} covers and ${proofs.length*3+3} typography-only checks: ${out}`);
}
