import type {Shot} from './data';
import type {BranchMapSpec, BranchMapShot} from '../../../_shared/branch-map/index.ts';

const nodes:BranchMapSpec['nodes']=[
 {id:'publish',label:'网站发送任务',x:220,y:370,w:280,kind:'step'},
 {id:'save',label:'队列接收\n可靠保存待办',x:700,y:370,w:310,kind:'step'},
 {id:'work',label:'后台处理业务\n队列仍留待确认',x:1400,y:370,w:330,kind:'step'},
 {id:'confirmed',label:'队列收到完成回执\n本次投递结束',x:700,y:730,w:330,kind:'success'},
 {id:'retry',label:'断连已被发现\n未确认任务再投递',x:1180,y:730,w:310,kind:'unknown'},
 {id:'check',label:'同任务重来\n先查已有业务结果',x:1640,y:730,w:310,kind:'decision'},
];
const edges:BranchMapSpec['edges']=[
 {id:'publish-save',from:'publish',to:'save',label:'写入待办',color:'#7DB5FF'},
 {id:'save-receipt',from:'save',to:'publish',label:'网站收到保存回执',via:[[700,515],[220,515]],labelAt:[460,515],color:'#FFCC70'},
 {id:'save-work',from:'save',to:'work',label:'投递后仍待确认',color:'#7DB5FF'},
 {id:'work-confirmed',from:'work',to:'confirmed',label:'业务成功后，回执送到队列',via:[[1400,560],[700,560]],labelAt:[1030,560],color:'#56E4D3'},
 {id:'work-retry',from:'work',to:'retry',label:'手动确认：断连被发现且仍未确认',via:[[1570,490],[1570,610],[1180,610]],labelAt:[1370,610],color:'#FFCC70'},
 {id:'retry-check',from:'retry',to:'check',label:'同一编号',labelAt:[1410,708],color:'#7DB5FF'},
 {id:'check-work',from:'check',to:'work',label:'未完成：继续处理',via:[[1850,730],[1850,250],[1400,250]],labelAt:[1710,268],color:'#7DB5FF'},
 // A requirement for the following acknowledgement, not an event shown in shot10.
 {id:'check-confirmed',from:'check',to:'confirmed',label:'已有结果：复用后仍需向队列确认',via:[[1640,855],[700,855]],labelAt:[1170,855],dashed:true,color:'#91A5BA'},
];
const shots:Record<string,BranchMapShot>={
 '01':{focus:'work',activeNodes:[],activeEdges:[],crumb:'问题：网站已回已提交，后台还没完成'},
 '02':{focus:'save',activeNodes:['publish','save','work'],activeEdges:['publish-save','save-work'],crumb:'先看集中到来，再定位整条处理路径',exit:{zoom:30,hold:54}},
 '03':{focus:'save',activeNodes:['publish','save'],activeEdges:['publish-save'],crumb:'第一段：网站把同一任务交给队列',enter:{hold:45,zoom:30}},
 '04':{focus:'save',activeNodes:['save','publish'],activeEdges:['save-receipt'],crumb:'保存回执送到网站；后台尚未做完'},
 '05':{focus:'work',activeNodes:['save','work'],activeEdges:['save-work'],crumb:'第二段：后台收到任务，队列仍留待确认'},
 '06':{focus:'work',activeNodes:['work'],activeEdges:[],crumb:'业务可以已成功；队列尚未收到完成回执'},
 '07':{focus:'confirmed',activeNodes:['work','confirmed'],activeEdges:['work-confirmed'],crumb:'业务完成回执送到队列，投递才结束',exit:{zoom:20,hold:0}},
 '08':{focus:'work',activeNodes:['work','retry'],activeEdges:['work-retry'],crumb:'另看7043：处理半途断连，尚未完成',enter:{hold:36,zoom:30},overviewTitle:'下一笔任务：处理到一半断开',overviewHint:'新的7043情景；本笔业务未做完，队列没有收到处理确认。'},
 '09':{focus:'retry',activeNodes:['work','retry','check'],activeEdges:['work-retry','retry-check'],crumb:'断连被发现后，同一7043重投；仍须确认',exit:{zoom:20,hold:0}},
 '10':{focus:'check',activeNodes:['work','retry','check'],activeEdges:['work-retry','retry-check'],crumb:'另看7043：已有业务结果，队列尚未收到确认',enter:{hold:36,zoom:30},exit:{zoom:24,hold:14},overviewTitle:'另一情景：业务已经成功，队列仍未收到确认',overviewHint:'本例同样在断连被发现后重投；虚线是后续仍须确认，并非本镜已经完成。'},
 '11':{focus:'save',activeNodes:['publish','save','work'],activeEdges:['publish-save','save-work'],crumb:'作用边界：回看集中到来，后台能力没有变',enter:{hold:12,zoom:30},exit:{zoom:24,hold:8},overviewHint:'回看任务集中到来的时段；等待和容量代价依然存在。'},
 '12':{focus:'save',mode:'overview',activeNodes:nodes.map(n=>n.id),activeEdges:edges.filter(e=>e.id!=='check-confirmed').map(e=>e.id),crumb:'同一生命周期：保存确认与处理确认属于不同边界',overviewTitle:'回到全局：网站已提交，后台处理仍有后续',overviewHint:'不同情景共用同一生命周期；虚线表示复用结果后仍需完成确认。'},
};

export const navigationSpec=(s:Shot,f:number):BranchMapSpec=>{
 const named=Number(s.id)>7||(s.id==='07'&&f>=Number(s.cueFrames?.ackLabel??1));
 return {title:'网站、队列、后台：先看两个不同的确认边界',overviewHint:'保存回执送到网站；处理完成后的确认送到队列。',
  nodes:nodes.map(n=>n.id==='confirmed'&&named?{...n,label:'队列收到处理确认\n本次投递结束'}:n),edges,shots};
};
