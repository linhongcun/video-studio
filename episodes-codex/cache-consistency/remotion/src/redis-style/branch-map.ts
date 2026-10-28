import type {BranchMapSpec,BranchMapShot} from '../../../../_shared/branch-map';
import {actualNavState,navigationEvents} from '../../../../_shared/branch-map';
import type {Shot} from './data';
export const FLOW_DESIGN_ID='flow-map-20261024/#199';
import {C} from './theme';
const blue=C.blue,gold=C.gold,red=C.red;
export const branchMap:BranchMapSpec={
 title:'写路径与读路径，合看一份临时副本',
 overviewTitle:'写入与读取，是两次不同的操作',
 overviewHint:'写者先存原记录、再撤副本；另一个读取独立检查。该顺序仍可能读到旧值。',
 nodes:[
  {id:'write',label:'写：保存数据库\n新价格',x:350,y:350,w:320},
  {id:'invalidate',label:'写：撤下对应\n旧副本',x:960,y:350,w:320},
  {id:'pending',label:'旧副本可能仍在\n须额外处理',x:1550,y:350,w:300,kind:'unknown'},
  {id:'check',label:'读：检查缓存\n这一项在吗？',x:350,y:610,w:300,kind:'decision'},
  {id:'load',label:'读：从数据库\n取回价格',x:960,y:610,w:300},
  {id:'fill',label:'读：填回副本\n并返回结果',x:1550,y:610,w:300},
  {id:'hit',label:'读：采用这份副本\n不再查数据库',x:350,y:820,w:300},
 ],
 edges:[
  {id:'write-invalidate',from:'write',to:'invalidate',label:'写成功后',labelAt:[655,325]},
  {id:'invalidate-pending',from:'invalidate',to:'pending',label:'若删除失败',labelAt:[1255,325],color:red},
  {id:'invalidate-check',from:'invalidate',to:'check',label:'后续另一个请求',via:[[760,460],[350,460]],labelAt:[555,460],dashed:true},
  {id:'check-hit',from:'check',to:'hit',label:'命中',labelAt:[435,720]},
  {id:'check-load',from:'check',to:'load',label:'未命中',labelAt:[655,585]},
  {id:'load-fill',from:'load',to:'fill',label:'取回后回填',labelAt:[1255,585]},
 ],
 shots:{
  '01':{focus:'hit',activeNodes:['write','check','hit'],activeEdges:['check-hit'],crumb:'刷新冲突 → 库179，副本199，读者仍读旧值',exit:{zoom:30,hold:89},overviewHint:'先看关系：写库不会自动改另一份副本；刷新仍要经过读路径。'},
  '02':{focus:'check',activeNodes:['check','hit'],activeEdges:['check-hit'],crumb:'回到更新前 → 库与缓存都是199，本次读副本',enter:{hold:18,zoom:24},exit:{zoom:18,hold:12}},
  '03':{focus:'write',activeNodes:['write'],crumb:'写路径 → 本次保存数据库新价格',enter:{hold:12,zoom:24},exit:{zoom:18,hold:6},overviewTitle:'原记录改变，不代表副本随之改变'},
  '04':{focus:'check',activeNodes:['check','hit'],activeEdges:['check-hit'],crumb:'读路径 → 检查缓存，命中就采用这份副本',enter:{hold:12,zoom:18},exit:{zoom:18,hold:12},overviewTitle:'命中，只说明找到了副本'},
  '05':{focus:'invalidate',activeNodes:['write','invalidate'],activeEdges:['write-invalidate'],crumb:'重新演示 → 先确认写库，再撤旧副本',enter:{hold:12,zoom:24},overviewHint:'重置为库199、缓存199；先保存新价，再使对应副本失效。'},
  '06':{focus:'invalidate',activeNodes:['write','invalidate'],activeEdges:['write-invalidate'],crumb:'同一路径回看 → 重新从199／199演两步',exit:{zoom:18,hold:18},overviewTitle:'写路径先结束，读者之后另行检查',overviewHint:'写库与删副本有顺序；下一次读取是另一个操作，不会被自动触发。'},
  '07':{focus:'load',activeNodes:['check','load','fill'],activeEdges:['check-load','load-fill'],crumb:'读路径 → 未命中才回源，取回后填副本',enter:{hold:6,zoom:18},exit:{zoom:18,hold:12},overviewTitle:'读路径：没有副本，才取原记录',overviewHint:'另一个读取先检查缓存，未命中才读库、回填并返回。'},
  '08':{focus:'hit',activeNodes:['check','hit'],activeEdges:['check-hit'],crumb:'读路径 → 检查副本，命中就直接采用',enter:{hold:12,zoom:24},exit:{zoom:18,hold:18},overviewTitle:'下一次命中，走读路径的另一出口'},
  '09':{focus:'invalidate',activeNodes:['invalidate','check','load','fill','write'],activeEdges:['invalidate-check','check-load','load-fill','wrong-late-write'],crumb:'错误对照重置 → 库199／缓存199，先删后写',enter:{hold:12,zoom:24},overviewTitle:'错误次序对照：读者插入写入空档',overviewHint:'对照重置为199／199：先删副本，写库暂缓；读者可在空档插入。'},
  '10':{focus:'invalidate',activeNodes:['invalidate','check','load','fill','write'],activeEdges:['invalidate-check','check-load','load-fill','wrong-late-write'],crumb:'错误对照延续 → 读者已回填199，写者随后继续',exit:{zoom:18,hold:18},overviewTitle:'对照次序：旧值先回填，写库在后',overviewHint:'这是先删后写的错误对照，不是推荐路径；旧副本不会自动跟着写库变新。'},
  '11':{focus:'invalidate',activeNodes:['write','invalidate'],activeEdges:['write-invalidate'],crumb:'另一结果 → 本次写库179已确认，再尝试删除',enter:{hold:18,zoom:24},exit:{zoom:18,hold:18},overviewTitle:'另一种结果：写库成功，删除仍可能失败',overviewHint:'此分支从本次写库已确认、旧缓存199仍在开始；删除是后续另一个动作。'},
  '12':{focus:'check',activeNodes:['check','load','fill'],activeEdges:['check-load','load-fill'],crumb:'期限边界 → 下一次读取仍须检查，未命中才回源',enter:{hold:18,zoom:24},exit:{zoom:24,hold:80},overviewTitle:'期限能撤下副本，更新仍须按路径处理',overviewHint:'图示后续请求：未找到才回源；到期不能代替更新治理或保证实时一致。'},
 }
};
export function navigationContext(s:Shot,f:number){
 let cfg:BranchMapShot={...branchMap.shots[s.id]};let nodes=branchMap.nodes,edges=branchMap.edges;
 if(s.id==='03'&&f>=92)cfg={...cfg,crumb:'数据库已确认179 → 对应副本仍是199'};
 if(s.id==='04'&&f>=76)cfg={...cfg,crumb:'查到旧副本199 → 本次不读取原记录'};
 if(s.id==='04'&&f>=136)cfg={...cfg,crumb:'本次返回旧199完成 → 刷新没有绕过应用缓存'};
 if(s.id==='06'&&f>=170)cfg={...cfg,crumb:'本次写库179已确认、旧副本已撤下'};
 if(s.id==='07'&&f>=175)cfg={...cfg,crumb:'本次回填179完成 → 后续请求仍先检查缓存'};
 if(s.id==='08'&&f>=135)cfg={...cfg,crumb:'本次返回缓存179完成 → 未再读取数据库'};
 if(s.id==='09'||s.id==='10'){
  const labels:Record<string,string>={invalidate:'① 写：先撤下\n旧副本',check:'② 读：检查\n这项副本',load:'③ 读：取回\n旧价格199',fill:'④ 读：填回\n旧价格199',write:'⑤ 写：随后保存\n新价格179'};
  nodes=nodes.map(n=>labels[n.id]?{...n,label:labels[n.id],color:n.id==='write'||n.id==='invalidate'?red:blue}:n);
  edges=[...edges.filter(e=>e.id!=='write-invalidate').map(e=>e.id==='invalidate-check'?{...e,label:'删后，另一个读者插入'}:e),{id:'wrong-late-write',from:'fill',to:'write',label:'随后才写库',via:[[1800,610],[1800,255],[350,255]],labelAt:[1800,460],color:red,dashed:true}];
  if(s.id==='09'&&f>=74)cfg={...cfg,crumb:'错误对照 → 副本已撤下，写库暂缓，读者插入'};
  if(s.id==='09'&&f>=273)cfg={...cfg,crumb:'错误对照 → 读者已回填旧199，写者尚未改库'};
  if(s.id==='10'&&f>=63)cfg={...cfg,crumb:'错误对照 → 库179已保存，旧副本199仍在'};
 }
 if(s.id==='11'&&f>=182)cfg={...cfg,activeNodes:['invalidate','pending'],activeEdges:['invalidate-pending'],crumb:'删除未成 → 副本仍是199，须额外处理'};
 const spec:BranchMapSpec={...branchMap,nodes,edges,shots:{...branchMap.shots,[s.id]:cfg}};
 return {spec,shotId:s.id,frame:f,durationInFrames:s.durationInFrames};
}
export const navigationState=(s:Shot,f:number)=>{const n=navigationContext(s,f);return actualNavState(n.spec,n.shotId,n.frame,n.durationInFrames);};
export const navigationFrameSamples=(s:Shot)=>navigationEvents(branchMap,s.id,s.durationInFrames);
