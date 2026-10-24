import type {BranchMapSpec,BranchMapShot} from '../../../_shared/branch-map';
import type {Shot} from './data';
const bindings:Record<string,BranchMapShot>={
 '01':{focus:'local',crumb:'问题起点：名字已输入，地址还未知'},
 '02':{focus:'local',mode:'overview'},
 '03':{focus:'local',mode:'overview',activeNodes:['local','resolver','answer']},
 '04':{focus:'local',enter:{hold:0,zoom:30},exit:{zoom:30,hold:45},crumb:'本地缓存：已有可用记录，就可以直接复用'},
 '05':{focus:'resolver',enter:{hold:35,zoom:30},activeNodes:['local','resolver'],activeEdges:['ask-resolver'],crumb:'本地未命中 → 解析器先查自己的缓存'},
 '06':{focus:'resolver',activeNodes:['resolver','root'],activeEdges:['ask-root','root-referral'],crumb:'两个缓存都无答案 → 解析器问根，接回指引'},
 '07':{focus:'resolver',activeNodes:['resolver','tld'],activeEdges:['ask-tld','tld-referral'],crumb:'收到指引 → 解析器自己继续问顶级域'},
 '08':{focus:'resolver',activeNodes:['resolver','authority'],activeEdges:['ask-authority','authority-answer'],crumb:'解析器再问权威 → 这次才拿到地址'},
 '09':{focus:'resolver',exit:{zoom:30,hold:40},activeNodes:['resolver','answer'],activeEdges:['answer-client'],crumb:'权威回答 → 解析器留缓存，并返回客户端'},
 '10':{focus:'resolver',enter:{hold:30,zoom:30},exit:{zoom:30,hold:35},activeNodes:['resolver'],crumb:'同一缓存记录：有效期到期，按规则再查'},
 '11':{focus:'resolver',enter:{hold:40,zoom:30},exit:{zoom:25,hold:25},activeNodes:['local','resolver','answer'],activeEdges:['ask-resolver','answer-client'],crumb:'另一个时点：缓存仍有效 → 直接返回地址'},
 '12':{focus:'answer',mode:'overview',activeNodes:['local','resolver','root','tld','authority','answer'],activeEdges:['ask-resolver','ask-root','root-referral','ask-tld','tld-referral','ask-authority','authority-answer','answer-client']}
};
export function navigationSpec(s:Shot,f=0):BranchMapSpec{
 const b={...bindings[s.id]};
 if(s.id==='04'){b.activeNodes=['local','answer'];b.activeEdges=['local-hit'];b.overviewHint='本地已有可用记录，可以直接复用';}
 if(s.id==='05')b.overviewHint='切回本次主线：本地没有可用答案，交给递归解析器';
 if(s.id==='10'&&f>=176){b.activeEdges=[];b.overviewHint='本条记录到期：按规则重新查询，不一定从根开始';}
 if(s.id==='11')b.overviewHint='重置示例：另一个时点，缓存尚未到期';
 if(s.id==='12'&&f>=125){b.activeNodes=[...(b.activeNodes??[]),'later'];b.activeEdges=[...(b.activeEdges??[]),'continue'];b.overviewHint='查询只负责拿到地址；连接、请求和绘制还在后面';}
 return {title:'同一个名字，答案从哪里回来',overviewHint:'先查本地，再交解析器；两个缓存都无答案，才逐级询问',nodes:[
  {id:'local',label:'客户端\n先查本地缓存',x:290,y:380,w:330},
  {id:'resolver',label:'递归解析器\n先查自己的缓存',x:850,y:500,w:360,kind:'decision'},
  {id:'root',label:'① 根服务器\n返回下层指引',x:1560,y:340,w:300},
  {id:'tld',label:'② 顶级域服务器\n返回权威指引',x:1560,y:520,w:300},
  {id:'authority',label:'③ 权威服务器\n本例返回地址',x:1560,y:700,w:300},
  {id:'answer',label:'客户端拿到地址',x:290,y:720,w:330,kind:'success'},
  {id:'later',label:'随后连接、获取页面',x:850,y:790,w:340}
 ],edges:[
  {id:'ask-resolver',from:'local',to:'resolver',label:'本地无可用答案',via:[[550,380],[550,500]],labelAt:[565,425]},
  {id:'local-hit',from:'local',to:'answer',label:'本地可用：直接复用',color:'#56E4D3',labelAt:[285,550]},
  {id:'answer-client',from:'resolver',to:'answer',label:'缓存可用 / 查询完成后返回',via:[[660,660],[510,660]],labelAt:[600,690],color:'#56E4D3'},
  {id:'ask-root',from:'resolver',to:'root',label:'① 问',via:[[1170,300]],labelAt:[1190,285]},
  {id:'root-referral',from:'root',to:'resolver',label:'指引',via:[[1210,405]],labelAt:[1265,395],color:'#FFCC70'},
  {id:'ask-tld',from:'resolver',to:'tld',label:'② 问',via:[[1165,480]],labelAt:[1225,470]},
  {id:'tld-referral',from:'tld',to:'resolver',label:'指引',via:[[1190,565]],labelAt:[1260,565],color:'#FFCC70'},
  {id:'ask-authority',from:'resolver',to:'authority',label:'③ 问',via:[[1180,640]],labelAt:[1200,625]},
  {id:'authority-answer',from:'authority',to:'resolver',label:'地址',via:[[1205,740],[1090,690]],labelAt:[1215,750],color:'#56E4D3'},
  {id:'continue',from:'answer',to:'later',dashed:true,label:'查询之后',labelAt:[565,785]}
 ],shots:{[s.id]:b}};
}
