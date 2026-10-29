import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {diagram} from './diagrams.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const catalog=JSON.parse(fs.readFileSync(path.join(here,'catalog.json'),'utf8'));
const style=JSON.parse(fs.readFileSync(path.join(here,'style-v1.json'),'utf8'));
const C=style.palette;
const background='data:image/png;base64,'+fs.readFileSync(path.join(here,'background.png')).toString('base64');
export const sizes={'16x9':[1920,1080],'3x4':[1080,1440],'4x3':[1440,1080]};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const txt=(id,x,y,s,size,color=C.text,extra='')=>`<text data-element="${id}" x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${esc(s)}</text>`;
function content(ep,portrait,proof){
 if(!/^EP\.\d{2,3}$/.test(ep.number))throw new Error('Use actual two/three-digit EP number');
 if(ep.titleLines.length<1||ep.titleLines.length>2||ep.questionLines.length<1||ep.questionLines.length>3)throw new Error('Explicit one/two title and one/two/three question lines required');
 const [w,h]=portrait?sizes['3x4']:sizes['16x9'],x=portrait?96:132;
 const two=ep.titleLines.length===2,titleFont=two?100:(portrait?140:160);
 const titleY=two?(portrait?459:483):(portrait?500:580),titleStep=portrait?116:127;
 const questionY=two?(portrait?660:760):(portrait?620:735);
 const questionFont=portrait?34:39,questionStep=portrait?46:52;
 const panel=portrait?[96,790,888,410]:[955,285,825,600];
 const graph=portrait?[118,851,844,330]:[980,390,775,400];
 return `<rect width="${w}" height="${h}" fill="${C.background}"/><image href="${background}" width="${w}" height="${h}" preserveAspectRatio="none" opacity=".75"/>
 <g data-group="header"><g data-ink="series-mark" stroke="${C.cyan}" stroke-width="5" fill="none" stroke-linecap="round"><path d="M${x+6} 110H${x+62}M${x+6} 132H${x+47}M${x+6} 154H${x+62}"/><path d="M${x+53} 124L${x+64} 132L${x+53} 140"/></g>
 ${txt('series',x+88,147,catalog.seriesLabel,portrait?31:38,C.cyan,'font-weight="800"')}
 ${txt('watermark',w-x,147,catalog.brand,29,C.muted,'font-weight="700" text-anchor="end"')}
 <path data-ink="header-rule" d="M${x} 209H${w-x}" stroke="${C.edge}" stroke-width="2"/></g>
 <g data-group="identity"><rect data-ink="number-badge" x="${x}" y="260" width="235" height="62" rx="11" fill="${C.cyan}"/>
 ${txt('number',x+117.5,304,ep.number,38,C.background,'font-weight="800" text-anchor="middle"')}</g>
 <g data-group="title">${ep.titleLines.map((s,i)=>txt('title-'+i,x-6,titleY+i*titleStep,s,titleFont,i?C.yellow:C.text,'font-weight="900" letter-spacing="-2"')).join('')}</g>
 <g data-group="question">${ep.questionLines.map((s,i)=>txt('question-'+i,x,questionY+i*questionStep,s,questionFont,C.muted,'font-weight="600"')).join('')}</g>
 <g data-group="diagram"><rect data-ink="diagram-panel" x="${panel[0]}" y="${panel[1]}" width="${panel[2]}" height="${panel[3]}" rx="25" fill="${C.surface}" fill-opacity=".98" stroke="${C.edge}" stroke-width="2"/>
 ${txt('diagram-caption',panel[0]+28,panel[1]+43,proof?'合成文字压力样例':ep.boundary,24,C.muted,'font-weight="600"')}
 ${proof?txt('proof-caption',panel[0]+panel[2]/2,panel[1]+215,'仅检查文字排版',29,C.muted,'text-anchor="middle"'):`<svg x="${graph[0]}" y="${graph[1]}" width="${graph[2]}" height="${graph[3]}" viewBox="0 0 760 360" overflow="visible">${diagram(ep.slug)}</svg>`}</g>`;
}
export function cover(ep,size,proof=false){
 const [w,h]=sizes[size]||[];if(!w)throw new Error('Unknown size '+size);
 const body=size==='4x3'?`<rect width="${w}" height="${h}" fill="${C.background}"/><g transform="translate(315 0) scale(.75)">${content(ep,true,proof)}</g>`:content(ep,size==='3x4',proof);
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(ep.number+' '+ep.titleLines.join(' ')+' '+ep.questionLines.join(''))}" font-family="${esc(style.fontFamily)}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">${body}</svg>`;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const at=process.argv.indexOf('--out-dir');if(at<0||!process.argv[at+1])throw new Error('Usage: node template.mjs --out-dir DIR');
 const out=path.resolve(process.argv[at+1]);fs.mkdirSync(out,{recursive:true});
 for(const ep of catalog.episodes){const d=path.join(out,ep.slug);fs.mkdirSync(d,{recursive:true});for(const s of Object.keys(sizes))fs.writeFileSync(path.join(d,`cover-${s}.svg`),cover(ep,s));}
 const proofs=JSON.parse(fs.readFileSync(path.join(here,'plan-layout.json'),'utf8')).entries,pdir=path.join(out,'typography-only');fs.mkdirSync(pdir,{recursive:true});
 for(const ep of proofs)for(const s of Object.keys(sizes))fs.writeFileSync(path.join(pdir,`${ep.slug}-${s}.svg`),cover(ep,s,true));
}
