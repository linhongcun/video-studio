/** EP.40 static lookup snapshot. Real source example: lower10..80, upper40/70.
 * Red route enters40 on upper level, descends at40, then advances only to50.
 * The70 and60 candidates are not visited;55 is a target, not an inserted node.
 */
import fs from 'node:fs';
const style=JSON.parse(fs.readFileSync(new URL('./style-v1.json',import.meta.url),'utf8'));
const C=style.palette;
const text=(id,x,y,s,size=28,fill=C.text,extra='')=>`<text data-element="diagram-${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="650" ${extra}>${s}</text>`;
function arrow(id,x1,y1,x2,y2,color=C.link,width=3){
 const vertical=x1===x2;
 const head=vertical?`M${x2-6} ${y2-9}L${x2} ${y2}L${x2+6} ${y2-9}`:`M${x2-9} ${y2-6}L${x2} ${y2}L${x2-9} ${y2+6}`;
 return `<path data-ink="${id}" d="M${x1} ${y1}L${x2} ${y2}${head}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
}
function node(id,cx,y,value,active=false){
 return `<g data-node="${id}"><rect data-ink="node-${id}" x="${cx-30}" y="${y}" width="60" height="56" rx="10" fill="${active?C.redSoft:C.surface}" stroke="${active?C.red:C.edge}" stroke-width="${active?3:2}"/>${text(id,cx,y+39,value,31,active?C.redDark:C.text,'text-anchor="middle"')}</g>`;
}
export function diagram(slug){
 if(slug!=='redis-skiplist')throw new RangeError('Unsupported Redis cover diagram: '+slug);
 const xs=[90,182,274,366,458,550,642,734];
 let s=`<g data-redis-diagram="lookup55" font-family="${style.fontFamily}">`
  +text('target',70,38,'查找 55',28,C.redDark)
  +text('upper-label',2,108,'上层',23,C.muted)
  +text('lower-label',2,250,'底层',23,C.muted)
  +`<circle data-ink="entry" cx="70" cy="100" r="5" fill="${C.red}"/>`
  +arrow('route-upper',80,100,336,100,C.red,4)
  +arrow('upper-original-link',396,100,612,100)
  +`<path data-ink="same-node-70" d="M642 130V210" fill="none" stroke="${C.edge}" stroke-width="2" stroke-dasharray="5 6"/>`
  +arrow('route-descent',366,132,366,210,C.red,4)
  +text('blocked-upper',642,58,'70 &gt; 55',25,C.muted,'text-anchor="middle"')
  +text('descent-label',386,178,'在40下降',24,C.redDark);
 for(let i=0;i<xs.length-1;i++)s+=arrow('lower-link-'+i,xs[i]+30,242,xs[i+1]-30,242,i===3?C.red:C.link,i===3?4:3);
 s+=node('upper40',366,72,40,true)+node('upper70',642,72,70);
 for(let i=0;i<xs.length;i++)s+=node('lower'+(i+1)*10,xs[i],214,(i+1)*10,i===4);
 s+=text('blocked-lower',550,198,'60 &gt; 55',24,C.muted,'text-anchor="middle"')
  +`<path data-ink="insertion-gap" d="M488 280V288H520V280M504 288V299" fill="none" stroke="${C.red}" stroke-width="2.5"/>`
  +text('position',504,330,'55在50与60之间',27,C.redDark,'text-anchor="middle"')
  +'</g>';
 return s;
}
