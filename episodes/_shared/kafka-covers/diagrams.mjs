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
function mq02(){
 let content=box(30,7,540,100,C.blue)+text('topic',300,45,'Kafka · 同一主题',30,C.blue)
  +text('p0',158,85,'P0 · E01 / E03',24,C.orange)+text('p1',442,85,'P1 · E02 / E04',24,C.blue);
 content+=`<path d="M158 115V132H86V162M442 115V132H514V162" fill="none" stroke="${C.orange}" stroke-width="3"/>`;
 content+=box(20,170,560,119,C.orange)+text('notify-group',300,205,'通知组 · 组内分工',28,C.orange)
  +box(39,220,246,54,C.edge,C.background,8)+box(315,220,246,54,C.edge,C.background,8)
  +text('n1',162,257,'N1 ← P0',26,C.text)+text('n2',438,257,'N2 ← P1',26,C.text);
 content+=`<path d="M30 70H7V341H30M570 70H593V341H570" fill="none" stroke="${C.blue}" stroke-width="3"/>`;
 return content+box(30,310,540,100,C.blue)+text('points-group',300,348,'积分组 · 独立订阅',28,C.blue)
  +text('points-all',300,390,'S1 ← P0 + P1 · 完整四条',25,C.text);
}
/** MQ03: retained P0 log and an explicit inactive-group committed-offset reset. */
function mq03(){
 let content=box(30,7,540,192,C.blue)
  +text('replay-log',300,47,'Kafka · P0保留日志',31,C.blue);
 for(const [i,event] of ['E01','E03'].entries()){
  const x=54+i*270;
  content+=box(x,67,222,86,C.edge,C.background,9)
   +text(`replay-offset-${i}`,x+111,99,`位置 ${i}`,24,C.muted)
   +text(`replay-event-${i}`,x+111,139,event,31,C.text);
 }
 content+=text('replay-retained',300,183,'读取与提交，都不删除记录',26,C.text);
 content+=box(30,244,540,166,C.orange)
  +text('reset-inactive',300,281,'通知组停用后 · 仅重置P0',27,C.orange)
  +text('reset-label',300,312,'已提交恢复位点',22,C.muted)
  +text('reset-before',156,361,'2',39,C.muted)
  +text('reset-arrow',300,360,'→',37,C.orange)
  +text('reset-after',444,361,'0',39,C.orange)
  +text('restart',300,393,'重启后，从位置0重新读取',24,C.text);
 return content+`<path d="M30 328H7V111H30M20 104L30 111L20 118" fill="none" stroke="${C.orange}" stroke-width="3" stroke-linejoin="round"/>`;
}
/** MQ04: send return and confirmed RecordMetadata are separate producer evidence. */
function mq04(){
 let content=box(30,7,540,80,C.orange)
  +text('send-return',300,43,'生产者 · 调用send返回',30,C.orange)
  +text('future-pending',300,74,'返回Future ≠ 已确认成功',23,C.text)
  +box(30,128,540,125,C.blue)
  +text('send-log',300,170,'Kafka · 分区日志',31,C.blue)
  +text('send-record',300,226,'P0 · 位置0 · E01',29,C.text)
  +box(30,294,540,116,C.success)
  +text('confirmed-result',300,332,'发送确认成功',30,C.success)
  +text('metadata',300,367,'元数据定位：P0 / 位置0',25,C.text)
  +text('business-boundary',300,399,'不代表消费者业务已完成',24,C.muted);
 return content+`<path d="M300 94V120M293 112L300 120L307 112" fill="none" stroke="${C.orange}" stroke-width="3"/>`
  +`<path d="M300 260V286M293 278L300 286L307 278" fill="none" stroke="${C.success}" stroke-width="3"/>`;
}
export function diagram(slug,portrait=false){
 if(!SUPPORTED_SLUGS.includes(slug))throw new RangeError(`Unsupported Kafka cover diagram: ${slug}`);
 return `<g data-kafka-diagram="${slug}" data-orientation="${portrait?'portrait':'landscape'}" font-family="${esc(style.fontFamily)}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">${slug==='message-queue'?mq01():slug==='kafka-consumer-groups'?mq02():slug==='kafka-log-replay'?mq03():mq04()}</g>`;
}
export const SUPPORTED_SLUGS=Object.freeze(['message-queue','kafka-consumer-groups','kafka-log-replay','kafka-send-confirmation']);
