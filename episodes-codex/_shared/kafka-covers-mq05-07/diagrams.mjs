import fs from 'node:fs';
const style=JSON.parse(fs.readFileSync(new URL('../kafka-covers/style-v1.json',import.meta.url),'utf8'));
const C=style.palette;
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const text=(id,x,y,value,size=28,fill=C.text,anchor='middle')=>`<text data-element="diagram-${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="600" text-anchor="${anchor}">${esc(value)}</text>`;
const box=(x,y,w,h,color=C.edge,fill=C.surface,rx=14)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${color}" stroke-width="2.5"/>`;
const down=(x,y1,y2,color=C.orange)=>`<path d="M${x} ${y1}V${y2}M${x-7} ${y2-8}L${x} ${y2}L${x+7} ${y2-8}" fill="none" stroke="${color}" stroke-width="3.5"/>`;

function idempotency(){
 return box(30,7,540,64,C.blue)+text('event',300,50,'同一事件 E01 · 积分 +10',30,C.blue)
 +down(300,79,102)+box(30,110,540,190,C.orange)
 +text('tx',300,151,'同一本地数据库事务',31,C.orange)
 +text('key',300,200,'唯一登记：积分业务 / E01',27)
 +text('points',300,251,'取得资格，积分 0 → 10',29)
 +text('atomic',300,285,'登记与积分共同提交或回滚',23,C.muted)
 +down(300,308,331,C.success)+box(30,340,540,70,C.success)
 +text('reread',300,384,'再次读到 E01，不再重复加分',28,C.success);
}

function ordering(){
 return box(30,7,540,66,C.blue)+text('key',300,51,'订单 7042 · 相同 Key',31,C.blue)
 +down(300,81,102)+box(30,110,540,155,C.orange)
 +text('log',300,149,'P0 · 按确定的发送顺序追加',28,C.orange)
 +box(53,169,224,75,C.edge,C.background,9)+box(323,169,224,75,C.edge,C.background,9)
 +text('pay',165,201,'位置 0 · 支付',26)+text('pay-event',165,230,'E01',25,C.blue)
 +text('refund',435,201,'位置 1 · 退款',26)+text('refund-event',435,230,'E02',25,C.blue)
 +down(300,273,298,C.success)+box(30,307,540,103,C.success)
 +text('serial',300,346,'应用也要按序完成',30,C.success)
 +text('business',300,390,'已支付 → 已退款',29);
}

function backlog(){
 let s=box(30,7,540,65,C.blue)+text('partitions',300,50,'2 个分区 · 本例按分区串行',28,C.blue);
 for(const [i,p] of ['P0','P1'].entries()){
  const x=45+i*275;
  s+=box(x,100,235,70,C.orange)+text('p'+i,x+117,145,p,32,C.orange)
  +down(x+117,177,202,C.blue)+box(x,211,235,66,C.blue)+text('owner'+i,x+117,254,'分区持有者',27,C.blue);
 }
 return s+text('members',300,314,'同组12个实例，稳定态最多2个有分区',24)
 +text('idle',300,350,'其余 10 个：无分区归属',27,C.muted)
 +text('capacity',300,397,'本例处理未提速，积压仍可增长',27,C.orange);
}

export const SUPPORTED_SLUGS=Object.freeze(['kafka-consumer-idempotency','kafka-message-ordering','kafka-message-backlog']);
export function diagram(slug,portrait=false){
 if(!SUPPORTED_SLUGS.includes(slug))throw new RangeError('Unsupported new Kafka episode: '+slug);
 const content=slug==='kafka-consumer-idempotency'?idempotency():slug==='kafka-message-ordering'?ordering():backlog();
 return `<g data-kafka-diagram="${slug}" data-orientation="${portrait?'portrait':'landscape'}" font-family="${esc(style.fontFamily)}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">${content}</g>`;
}
