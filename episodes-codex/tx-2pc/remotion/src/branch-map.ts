import type {Shot} from './data';
import type {BranchMapSpec,BranchMapShot} from '../../../_shared/branch-map/index.ts';
import {navigationEvents as sharedNavigationEvents} from '../../../_shared/branch-map/index.ts';
const node=(id:string,label:string,x:number,y:number,kind:'step'|'decision'|'success'|'failure'|'unknown'='step',w=250)=>({id,label,x,y,kind,w});

// This is a map of the three examples in this film. A completed successful
// transaction is never routed into the rejection example or vice versa.
const nodes=[
 node('prepare','先把修改做好',240,430),
 node('result','看双方答复',650,430,'decision'),
 node('saved','可靠的\n保存决定',1080,350,'decision',270),
 node('apply','分别落实\n保存结果',1560,350,'success',270),
 node('abort','可靠放弃\n再撤销待改',1120,575,'failure',280),
 node('unknown','决定未知\n先等，不猜',650,735,'unknown',270),
 node('recover','找回原决定',1120,735,'unknown',270),
];
const edges=[
 {id:'prepared-result',from:'prepare',to:'result',label:'收集答复'},
 {id:'all-ready',from:'result',to:'saved',label:'全部就绪',color:'#7DB5FF'},
 {id:'save-apply',from:'saved',to:'apply',label:'按保存决定',color:'#56E4D3'},
 {id:'reject-abort',from:'result',to:'abort',label:'有人拒绝',color:'#FF929B'},
 {id:'result-unknown',from:'result',to:'unknown',label:'已就绪，但没得到决定',color:'#FFCC70'},
 {id:'wait-recover',from:'unknown',to:'recover',label:'等待恢复查证',color:'#FFCC70'},
 {id:'recover-saved',from:'recover',to:'saved',label:'本例原来是保存',labelAt:[1510,545] as [number,number],color:'#7DB5FF',via:[[1430,820],[1750,820],[1750,470],[1080,470]] as [number,number][]},
];
const shots:Record<string,BranchMapShot>={
 '01':{focus:'prepare',mode:'focus',activeNodes:[],activeEdges:[],crumb:'先看问题：两边各自处理，结果可能分开'},
 '02':{focus:'prepare',mode:'overview',activeNodes:['prepare'],activeEdges:[],crumb:'先看全局：下面是三种分别演示的情景'},
 '03':{focus:'prepare',mode:'focus',activeNodes:['prepare'],activeEdges:['prepared-result'],crumb:'成功示例 · 第一步：本次修改先就位',enter:{hold:0,zoom:36}},
 '04':{focus:'prepare',mode:'focus',activeNodes:['prepare','result'],activeEdges:['prepared-result'],crumb:'成功示例 · 本地可靠保存后，才能答复就绪'},
 '05':{focus:'saved',mode:'focus',activeNodes:['result','saved'],activeEdges:['all-ready'],crumb:'成功示例 · 第二步：把保存决定可靠记下'},
 '06':{focus:'saved',mode:'focus',activeNodes:['saved'],activeEdges:['save-apply'],crumb:'成功示例 · 决定已记录，再发最终指令'},
 '07':{focus:'apply',mode:'focus',activeNodes:['saved','apply'],activeEdges:['save-apply'],crumb:'成功示例 · 第三步：订单与库存先后落实'},
 '08':{focus:'apply',mode:'focus',activeNodes:['prepare','result','saved','apply'],activeEdges:['prepared-result','all-ready','save-apply'],crumb:'成功示例结束 · 接着回到全图，看另一种结果',exit:{zoom:22,hold:16}},
 '09':{focus:'abort',mode:'focus',activeNodes:['result','abort'],activeEdges:['reject-abort'],crumb:'另看拒绝情景 · 从无本单记录、库存4重新开始',enter:{hold:24,zoom:30}},
 '10':{focus:'abort',mode:'focus',activeNodes:['abort'],activeEdges:['reject-abort'],crumb:'拒绝情景 · 先记录放弃，再撤销待改',exit:{zoom:20,hold:14}},
 '11':{focus:'unknown',mode:'focus',activeNodes:['result','unknown'],activeEdges:['result-unknown'],crumb:'另看未知情景 · 已准备，但参与方还不知道决定',enter:{hold:24,zoom:30}},
 '12':{focus:'recover',mode:'focus',activeNodes:['unknown','recover','saved'],activeEdges:['wait-recover','recover-saved'],crumb:'延续未知情景 · 只读取原记录，不重新选择'},
 '13':{focus:'unknown',mode:'focus',activeNodes:['unknown'],activeEdges:['result-unknown'],crumb:'回看未知阶段的代价 · 等待仍占用资源',exit:{zoom:26,hold:16}},
 '14':{focus:'result',mode:'overview',activeNodes:['prepare','result','saved','apply','abort','unknown','recover'],activeEdges:edges.map(e=>e.id),crumb:'回到全局 · 保存、拒绝与未知，各按其路径收尾'},
};

export const navigationSpec=(s:Shot,frame:number):BranchMapSpec=>{
 const n=Number(s.id),prepareNamed=n>3||(n===3&&frame>=Number(s.cueFrames?.labels?.['准备']??1));
 const title=n===2&&frame>=Number(s.cueFrames?.labels?.['两阶段提交']??1)
  ?'两阶段提交：先看三种处理情景'
  :n===14?'两阶段提交：回到同一张全局图':'这笔跨库交易，会走哪条路？';
 return {title,overviewHint:'各分支分别演示，不是同一单先成功再失败',nodes:nodes.map(q=>q.id==='prepare'&&prepareNamed?{...q,label:'先准备'}:q.id==='result'&&prepareNamed?{...q,label:'看准备结果'}:q),edges,shots};
};

export const navigationEvents=(s:Shot):[string,number][]=>{
 const p=shots[s.id];if(!p)return[];
 const extra:[string,number][]=p.mode==='overview'?[['nav-overview-start',0],['nav-overview-hold',Math.floor(s.durationInFrames*.5)]]:[];
 return [...extra,...sharedNavigationEvents(navigationSpec(s,0),s.id,s.durationInFrames)];
};
