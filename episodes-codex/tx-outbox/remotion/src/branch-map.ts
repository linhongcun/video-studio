import type {BranchMapSpec, BranchMapShot} from '../../../_shared/branch-map';
import {actualNavState, navigationEvents} from '../../../_shared/branch-map';
import type {Shot} from './data';
import {eventAt} from './motion';

const blue='#7DB5FF',gold='#FFCC70',red='#FF929B';
export const branchMap:BranchMapSpec={
 title:'保存、发送、消费：先看清整条路线',
 overviewTitle:'订单记了，通知接下来怎么走？',
 overviewHint:'示例：订单已记录，库存4尚未扣；分开看保存、发送与消费。',
 nodes:[
  {id:'save',label:'一起保存\n订单＋待办',x:300,y:370,w:300},
  {id:'send',label:'后台发送\n队列确认后记已发',x:850,y:370,w:300},
  {id:'consume',label:'消费判断\n重复与库存',x:1400,y:370,w:300,kind:'decision'},
  {id:'rollback',label:'本地写入失败\n两条一起撤销',x:300,y:660,w:300,kind:'failure'},
  {id:'apply',label:'一起保存\n库存＋唯一标记',x:1330,y:610,w:300},
  {id:'skip',label:'已处理的重复通知\n不再扣减',x:1710,y:610,w:280,kind:'success'},
  {id:'refuse',label:'若缺货则拒绝\n按业务规则收尾',x:1330,y:810,w:270,kind:'failure'},
 ],
 edges:[
  {id:'save-send',from:'save',to:'send',label:'提交后',labelAt:[575,345]},
  {id:'save-rollback',from:'save',to:'rollback',label:'写入失败',labelAt:[390,515],color:red},
  {id:'send-consume',from:'send',to:'consume',label:'通知投递',labelAt:[1125,345]},
  {id:'send-retry',from:'send',to:'send',label:'未标记：恢复重发',via:[[1015,370],[1015,275],[685,275],[685,370]],labelAt:[850,265],color:gold,dashed:true},
  {id:'consume-apply',from:'consume',to:'apply',label:'未处理且有货',labelAt:[1390,500]},
  {id:'consume-skip',from:'consume',to:'skip',label:'已经处理',labelAt:[1580,500]},
  {id:'apply-retry',from:'apply',to:'consume',label:'本次未完成：重试检查',via:[[1120,610],[1120,500],[1240,500],[1240,440]],labelAt:[1030,550],color:blue,dashed:true},
  {id:'consume-refuse',from:'consume',to:'refuse',label:'未处理且缺货',via:[[1510,490],[1510,810]],labelAt:[1510,718],color:red},
 ],
 shots:{
  '01':{focus:'send',activeNodes:['save','send','consume'],activeEdges:['save-send','send-consume'],crumb:'问题：订单记了，通知还没发',exit:{zoom:30,hold:110},overviewHint:'订单已记录，库存4未扣；先认清保存、发送、消费三段。'},
  '02':{focus:'save',activeNodes:['save'],activeEdges:[],crumb:'保存 → 订单与待办共同写入',enter:{hold:12,zoom:24}},
  '03':{focus:'save',activeNodes:['save'],crumb:'保存 → 两条候选修改都未提交'},
  '04':{focus:'save',activeNodes:['save'],crumb:'保存 → 一起提交，记录可恢复',exit:{zoom:18,hold:0},overviewTitle:'保存之后，失败要从哪条支路退出？',overviewHint:'两条已保存后仍可恢复；接着另看写入失败分支。'},
  '05':{focus:'rollback',activeNodes:['save','rollback'],activeEdges:['save-rollback'],crumb:'保存失败 → 两条修改一起撤销',enter:{hold:24,zoom:24},exit:{zoom:18,hold:12},overviewTitle:'保存阶段失败：一起撤销',overviewHint:'另一条分支从未保存开始，不是在已提交后反悔。'},
  '06':{focus:'send',activeNodes:['save','send'],activeEdges:['save-send'],crumb:'发送 → 从持久待办读取通知',enter:{hold:18,zoom:24}},
  '07':{focus:'send',activeNodes:['send'],activeEdges:['send-consume'],crumb:'发送 → 队列接收后，再标记本地结果',exit:{zoom:18,hold:3},overviewTitle:'发送之后，还有一个标记结果的空档',overviewHint:'队列确认接收，不代表库存已经消费。'},
  '08':{focus:'send',activeNodes:['send'],activeEdges:['send-retry'],crumb:'发送故障 → 已发未标记，等待恢复',enter:{hold:24,zoom:24},overviewTitle:'发送回边：没有标记，就可能恢复重发',overviewHint:'回看同一阶段的故障空档，不另造一次业务。'},
  '09':{focus:'send',activeNodes:['send','consume'],activeEdges:['send-retry','send-consume'],crumb:'发送恢复 → 同一E8124可能重复投递',exit:{zoom:18,hold:3},overviewTitle:'重发后，通知进入消费阶段',overviewHint:'通知身份相同；消费端必须识别重复。'},
  '10':{focus:'apply',activeNodes:['consume','apply'],activeEdges:['consume-apply'],crumb:'尚未处理 → 本地处理库存与唯一标记',enter:{hold:24,zoom:26},exit:{zoom:18,hold:40},overviewTitle:'消费先判断：处理、跳过或缺货收尾',overviewHint:'库存与处理标记必须共同保存；随后对比消费失败怎样重试。'},
  '11':{focus:'apply',activeNodes:['consume','apply'],activeEdges:['consume-apply','apply-retry'],crumb:'消费技术失败 → 共同回滚，再尝试',enter:{hold:18,zoom:14},exit:{zoom:18,hold:2},overviewTitle:'技术故障回当前阶段，不当成新业务',overviewHint:'重置为库存4、无处理标记，再演示失败与重试。'},
  '12':{focus:'skip',activeNodes:['consume','skip'],activeEdges:['consume-skip'],crumb:'已经处理 → 跳过重复，不再扣库存',enter:{hold:24,zoom:24},exit:{zoom:18,hold:0},overviewTitle:'同一条通知：处理过就走跳过分支',overviewHint:'相同E8124已处理，库存保持3。'},
  '13-map':{focus:'consume',mode:'overview',activeNodes:['save','apply'],activeEdges:['save-send','send-consume','consume-apply'],overviewTitle:'两笔本地事务，靠消息流程衔接',overviewHint:'订单与待办一起保存；库存与唯一标记在另一笔事务保存。'},
  '13-refuse':{focus:'refuse',activeNodes:['consume','refuse'],activeEdges:['consume-refuse'],crumb:'库存检查拒绝 → 按业务规则收尾',enter:{hold:0,zoom:24},exit:{zoom:18,hold:8},overviewTitle:'业务拒绝：这里不是技术重试回边',overviewHint:'切换缺货分支：库存0，需要按业务规则结束。'},
  '14':{focus:'save',mode:'overview',activeNodes:['save'],activeEdges:[],overviewTitle:'回到总图：一起保存，再发送，最后防重复',overviewHint:'回顾正常路径与重复投递；缺货分支不会靠等待自动恢复。'},
 }
};

/** Keep the sound/subtitle shot intact while changing navigation within shot13. */
export function outboxNavigation(s:Shot,f:number){
 const second=Number(s.cueFrames?.sentences?.[1]??141);
 const id=s.id==='13'?(f<second?'13-map':'13-refuse'):s.id;
 const offset=s.id==='13'&&f>=second?second:0;
 const duration=s.id==='13'?(offset?s.durationInFrames-offset:second):s.durationInFrames;
 let cfg:BranchMapShot={...branchMap.shots[id]};
 let nodes=branchMap.nodes;
 if(s.id==='04'&&f>=eventAt(s,'producer-joint-commit')){nodes=nodes.map(n=>n.id==='save'?{...n,kind:'success' as const}:n);cfg={...cfg,crumb:'本例共同保存完成 → 订单与待办可恢复'};}
 if(s.id==='10'&&f>=eventAt(s,'consumer-joint-commit')){nodes=nodes.map(n=>n.id==='apply'?{...n,kind:'success' as const}:n);cfg={...cfg,crumb:'本例共同保存完成 → 库存与唯一标记'};}
 if(s.id==='14'){
  const relay=f>=eventAt(s,'focus-relay'),done=f>=eventAt(s,'focus-consumer');
  cfg={...cfg,focus:done?'skip':relay?'send':'save',activeNodes:done?['consume','apply','skip']:relay?['send']:['save'],activeEdges:done?['send-consume','consume-skip']:relay?['save-send']:[],overviewHint:done?'已经处理的同一E8124走跳过分支，库存仍为3。':relay?'共同保存之后，独立程序负责发送和恢复。':'先把订单和待办一起记好，发送意图才不会只留在内存。'};
 }
 const spec:BranchMapSpec={...branchMap,nodes,shots:{...branchMap.shots,[id]:cfg}};
 return {spec,shotId:id,frame:f-offset,durationInFrames:duration};
}
export function navigationFrameSamples(s:Shot):[string,number][] {
 const rows:[string,number][]=[];
 const second=Number(s.cueFrames?.sentences?.[1]??141);
 const segments=s.id==='13'?[{id:'13-map',offset:0,duration:second},{id:'13-refuse',offset:second,duration:s.durationInFrames-second}]:[{id:s.id,offset:0,duration:s.durationInFrames}];
 for(const p of segments)for(const [name,f]of navigationEvents(branchMap,p.id,p.duration))rows.push([name,f+p.offset]);
 if(s.id==='13')rows.push(['nav-business-branch-overview',second]);
 return rows;
}
export function navigationState(s:Shot,f:number){const n=outboxNavigation(s,f);return actualNavState(n.spec,n.shotId,n.frame,n.durationInFrames);}
/** Shared QA consumes the exact production context, including shot13's split. */
export const navigationContext=outboxNavigation;
