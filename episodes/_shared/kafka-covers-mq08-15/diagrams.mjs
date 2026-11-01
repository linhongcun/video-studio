import fs from 'node:fs';
const style=JSON.parse(fs.readFileSync(new URL('../kafka-covers/style-v1.json',import.meta.url),'utf8'));
const C=style.palette;
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const text=(id,x,y,value,size=28,fill=C.text,anchor='middle')=>`<text data-element="diagram-${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="600" text-anchor="${anchor}">${esc(value)}</text>`;
const box=(x,y,w,h,color=C.edge,fill=C.surface,rx=14)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${color}" stroke-width="2.5"/>`;
const down=(x,y1,y2,color=C.orange)=>`<path d="M${x} ${y1}V${y2}M${x-7} ${y2-8}L${x} ${y2}L${x+7} ${y2-8}" fill="none" stroke="${color}" stroke-width="3.5"/>`;

function retry(){
 return box(30,7,540,65,C.blue)+text('event',300,50,'同一通知 E01 · 应用重试',30,C.blue)
 +down(300,79,102)+box(30,110,540,165,C.orange)
 +text('budget',300,151,'调用名额：最多 3 次',31,C.orange)
 +text('journal',300,195,'调用前，先保存已用名额',28)
 +text('deadline',300,237,'到期且有名额，才再调用',28)
 +text('poll',300,267,'等待期间继续 poll',23,C.muted)
 +down(300,282,309,C.success)+box(30,318,540,88,C.success)
 +text('dlq',300,354,'名额用完 → 等待处置',28,C.success)
 +text('commit',300,391,'死信写入确认后，另提交原进度',25);
}

function replicas(){
 let s=box(30,7,540,65,C.blue)+text('record',300,49,'P0 · 同一记录 E01',30,C.blue);
 for(const [i,label]of ['A · Leader','B · Follower','C · Follower'].entries()){
  const x=30+i*185;
  s+=box(x,105,170,133,C.orange)
   +text('replica-'+i,x+85,145,label,24,C.orange)
   +box(x+25,166,120,51,C.blue,C.background,8)
   +text('copy-'+i,x+85,202,'E01',28,C.blue);
 }
 return s+box(30,257,540,71,C.blue)
 +text('isr',300,302,'本例稳定 ISR = { A, B, C }',28,C.blue)
 +text('minimum',300,365,'acks=all · minISR = 2',29,C.orange)
 +text('boundary',300,405,'先核准入数量，再等复制进度',26);
}

export const SUPPORTED_SLUGS=Object.freeze(['kafka-retry-dead-letter','kafka-replica-acks']);
export function diagram(slug,portrait=false){
 if(!SUPPORTED_SLUGS.includes(slug))throw new RangeError('Unsupported batch episode: '+slug);
 const content=slug==='kafka-retry-dead-letter'?retry():replicas();
 return `<g data-kafka-diagram="${slug}" data-orientation="${portrait?'portrait':'landscape'}" font-family="${esc(style.fontFamily)}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">${content}</g>`;
}
