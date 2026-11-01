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
function skiplistDiagram(slug){
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


const card=(id,x,y,w,h,label,value,active=false)=>`<g data-card="${id}"><rect data-ink="${id}-card" x="${x}" y="${y}" width="${w}" height="${h}" rx="12" fill="${active?C.redSoft:C.surface}" stroke="${active?C.red:C.edge}" stroke-width="2"/>${text(id+'-label',x+w/2,y+30,label,25,C.text,'text-anchor="middle"')}${value?text(id+'-value',x+w/2,y+h-16,value,27,active?C.redDark:C.muted,'text-anchor="middle"'):''}</g>`;
function leftArrow(id,x1,y,x2,color=C.red){return `<path data-ink="${id}" d="M${x1} ${y}H${x2}M${x2+9} ${y-6}L${x2} ${y}L${x2+9} ${y+6}" fill="none" stroke="${color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>`;}
function serverCache(){
 return `<g data-redis-diagram="cache-miss-fill-hit" font-family="${style.fontFamily}">`
 +text('sc-product',420,30,'同一商品7042 · 199元',28,C.redDark,'text-anchor="middle"')
 +text('sc-miss',10,95,'① 未命中',25,C.muted)
 +card('sc-app1',165,55,145,86,'应用','查询7042')
 +card('sc-cache1',440,55,165,86,'Redis缓存','未找到')
 +card('sc-db1',700,55,125,86,'数据库','199元')
 +arrow('sc-check-cache',310,95,440,95,C.red,3.5)
 +`<path data-ink="sc-app-reads-db" d="M238 141V169H763V141M757 150L763 141L769 150" fill="none" stroke="${C.link}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`
 +text('sc-read-db',496,164,'应用未命中后查库',20,C.muted,'text-anchor="middle"')
 +text('sc-fill',420,207,'取回199后，由应用填入缓存',24,C.redDark,'text-anchor="middle"')
 +text('sc-hit',10,280,'② 回填后',25,C.muted)
 +card('sc-app2',165,240,145,86,'应用','得到199')
 +card('sc-cache2',440,240,165,86,'Redis缓存','199元',true)
 +card('sc-db2',700,240,125,86,'数据库','199元')
 +leftArrow('sc-hit-return',440,284,310)
 +text('sc-hit-label',375,265,'命中',22,C.redDark,'text-anchor="middle"')
 +'</g>';
}
function consistency(){
 return `<g data-redis-diagram="db-write-invalidate-refill" font-family="${style.fontFamily}">`
 +text('cc-product',420,32,'商品7042 · 199 → 179',28,C.redDark,'text-anchor="middle"')
 +card('cc-write',20,80,240,150,'① 先写数据库','179元',true)
 +card('cc-delete',300,80,240,150,'② 删除旧缓存','199元')
 +`<path data-ink="cc-invalidated-price" d="M365 204H475" stroke="${C.red}" stroke-width="3"/>`
 +card('cc-refill',580,80,240,150,'③ 下次读回填','179元',true)
 +arrow('cc-order1',260,150,300,150,C.red,3.5)
 +arrow('cc-order2',540,150,580,150,C.red,3.5)
 +text('cc-order-caption',420,280,'先更新原记录，再撤掉临时旧副本',28,C.redDark,'text-anchor="middle"')
 +text('cc-boundary',420,326,'常见策略 · 不等于强一致保证',23,C.muted,'text-anchor="middle"')
 +'</g>';
}
export function diagram(slug){
 if(slug==='server-cache')return serverCache();
 if(slug==='cache-consistency')return consistency();
 return skiplistDiagram(slug);
}
