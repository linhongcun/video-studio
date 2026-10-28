/**
 * MQ01 static responsibility diagram, not an animation or execution trace.
 * Website producer -> one Kafka partition log -> background consumer.
 * Positions 0/1/2 keep records 7042/7043/7044 in the log; reading does not delete.
 * No consumer commit, ACK, retry or extra future episode is introduced here.
 * Both orientations use viewBox 0 0 600 420.
 */
import fs from 'node:fs';
const style=JSON.parse(fs.readFileSync(new URL('./style-v1.json',import.meta.url),'utf8'));
const C=style.palette;
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const text=(id,x,y,value,size=28,fill=C.text,anchor='middle')=>`<text data-element="diagram-${id}" x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="600" text-anchor="${anchor}">${esc(value)}</text>`;
const box=(x,y,w,h,color=C.edge,fill=C.surface,rx=14)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${color}" stroke-width="2.5"/>`;
const down=(y1,y2,color)=>`<path d="M300 ${y1}V${y2}M293 ${y2-8}L300 ${y2}L307 ${y2-8}" fill="none" stroke="${color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>`;
function mq01(){
 let content=box(30,7,540,63,C.blue)
   +text('producer',300,51,'网站服务 · 生产者',32,C.blue)
   +down(78,103,C.orange)
   +text('write-boundary',325,99,'写入成功 ≠ 业务完成',24,C.muted,'start')
   +box(30,110,540,200,C.blue)
   +text('partition-log',300,152,'Kafka · 单分区日志',32,C.blue);
 for(const [i,message] of ['7042','7043','7044'].entries()){
   const x=54+i*172;
   content+=box(x,171,148,85,C.edge,C.background,9)
     +text(`position-${i}`,x+74,201,`位置 ${i}`,24,C.muted)
     +text(`record-${i}`,x+74,246,message,30,C.orange);
 }
 return content+text('retained',300,296,'读取后，原记录仍保留',26,C.text)
   +down(318,337,C.orange)
   +box(30,345,540,65,C.blue)
   +text('consumer',300,389,'后台处理 · 消费者',32,C.blue);
}
export function diagram(slug,portrait=false){
 if(slug!=='message-queue')throw new RangeError(`Unsupported Kafka cover diagram: ${slug}`);
 return `<g data-kafka-diagram="${slug}" data-orientation="${portrait?'portrait':'landscape'}" font-family="${esc(style.fontFamily)}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">${mq01()}</g>`;
}
export const SUPPORTED_SLUGS=Object.freeze(['message-queue']);
