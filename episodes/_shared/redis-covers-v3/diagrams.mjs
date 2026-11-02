/** New Redis cover snapshots; all quantities explicitly belong to teaching examples. */
import fs from 'node:fs';
const style=JSON.parse(fs.readFileSync(new URL('./style-v1.json',import.meta.url),'utf8'));
const C=style.palette;
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const text=(id,x,y,s,size=26,fill=C.text,extra='')=>`<text data-element="diagram-${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="650" ${extra}>${esc(s)}</text>`;
const center=(id,x,y,s,size=26,fill=C.text)=>text(id,x,y,s,size,fill,'text-anchor="middle"');
const path=(id,d,color=C.link,width=3,extra='')=>`<path data-ink="${id}" d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round" ${extra}/>`;
function down(id,x,y1,y2,color=C.red,width=3.5){return path(id,`M${x} ${y1}V${y2}M${x-7} ${y2-10}L${x} ${y2}L${x+7} ${y2-10}`,color,width);}
function card(id,cx,y,w,h,label,value,active=false){return `<g data-card="${id}"><rect data-ink="${id}-card" x="${cx-w/2}" y="${y}" width="${w}" height="${h}" rx="12" fill="${active?C.redSoft:C.surface}" stroke="${active?C.red:C.edge}" stroke-width="${active?3:2}"/>${center(id+'-label',cx,y+32,label,26,active?C.redDark:C.text)}${center(id+'-value',cx,y+h-10,value,23,active?C.redDark:C.muted)}</g>`;}
function sentinel(){
 let s=`<g data-redis-diagram="sentinel-leader-then-replica" font-family="${style.fontFamily}">`;
 s+=center('s-example',420,28,'5个 Sentinel · 先选本次负责人',26,C.muted);
 const xs=[84,252,420,588,756];
 for(let i=0;i<5;i++)s+=card('s'+(i+1),xs[i],52,134,78,i===0?'S1 当选':'S'+(i+1),i===0?'自投1票':i<3?'投给S1':'未投此票',i===0);
 s+=path('s2-vote-to-s1','M252 130V144H110V134M103 144L110 134L117 144',C.red,3.2);
 s+=path('s3-vote-to-s1','M420 130V157H96V134M89 144L96 134L103 144',C.red,3.2);
 s+=center('s-majority',420,181,'3 / 5 多数授权',26,C.redDark);
 s+=path('s-leader-selects-replica','M70 134V208H685V236M678 226L685 236L692 226',C.red,3.5);
 s+=center('s-select-label',420,235,'S1 再筛选并提升副本',23,C.redDark);
 s+=card('s-old-master',155,246,218,90,'旧主 M','失联');
 s+=card('s-replica-r1',420,246,218,90,'R1 · 排除','priority 0 · 900');
 s+=card('s-replica-r2',685,246,218,90,'R2 · 提升','priority 100 · 800',true);
 return s+'</g>';
}
function cluster(){
 let s=`<g data-redis-diagram="cluster-master-votes-replica-slot-takeover" font-family="${style.fontFamily}">`;
 s+=center('c-example',420,28,'3个持槽主节点 · 副本申请接管',26,C.muted);
 s+=card('c-m1',140,57,212,84,'M1 · 旧主失联','0–5460 槽');
 s+=card('c-m2',420,57,212,84,'主节点 M2','5461–10922 槽',true);
 s+=card('c-m3',700,57,212,84,'主节点 M3','10923–16383 槽',true);
 s+=path('c-replication-relation','M140 141V279H282',C.link,2.5,'stroke-dasharray="6 7"');
 s+=text('c-original-replication',32,211,'原复制关系',22,C.muted);
 s+=down('c-m2-authorization',420,141,230);
 s+=path('c-m3-authorization','M700 141V184H456V230M449 220L456 230L463 220',C.red,3.5);
 s+=text('c-majority',482,218,'2 / 3 主节点授权',25,C.redDark);
 s+=card('c-candidate-r1',420,240,270,88,'副本 R1 获授权','接管 0–5460 槽',true);
 return s+'</g>';
}
function lru(){
 let s=`<g data-redis-diagram="approx-lru-sampling-candidate-pool" font-family="${style.fontFamily}">`;
 s+=center('l-example',420,26,'A 最久未访问，本轮却未抽中',26,C.muted);
 const keys=['A','B','C','D','E','F','G','H'],idle=[90,80,70,60,50,40,30,20],xs=[63,165,267,369,471,573,675,777];
 for(let i=0;i<keys.length;i++)s+=card('l-key-'+keys[i],xs[i],48,92,85,keys[i],`${idle[i]}秒`,['C','D','E'].includes(keys[i]));
 s+=center('l-sample',420,172,'首轮采样 C、D、E',27,C.redDark);
 s+=`<rect data-ink="l-pool" x="90" y="205" width="610" height="140" rx="15" fill="${C.surface}" stroke="${C.edge}" stroke-width="2"/>`;
 s+=text('l-pool-label',110,232,'候选池 · 16槽中的已占项',22,C.muted);
 const pool=[['E',50],['D',60],['C',70]];
 for(let i=0;i<pool.length;i++){
  const x=200+i*195,id='l-pool-'+pool[i][0],active=i===2;
  s+=card(id,x,246,140,78,pool[i][0]+' · '+pool[i][1],active?'选中淘汰':'取C后保留',active);
 }
 s+=path('l-pool-order-1','M270 285H320M311 279L320 285L311 291',C.link,3);
 s+=path('l-pool-order-2','M465 285H515M506 279L515 285L506 291',C.link,3);
 s+=path('l-choose-c','M660 285H753M744 278L753 285L744 292',C.red,3.5);
 s+=text('l-extraction-end',750,257,'取出端',22,C.muted,'text-anchor="middle"');
 s+=text('l-eviction',770,294,'取 C',25,C.redDark);
 return s+'</g>';
}
export function diagram(slug){
 if(slug==='redis-sentinel')return sentinel();
 if(slug==='redis-cluster-failover')return cluster();
 if(slug==='redis-lru')return lru();
 throw new RangeError('Unsupported Redis cover diagram: '+slug);
}
