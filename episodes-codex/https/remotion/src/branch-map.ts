import type {Shot} from './data';
import type {BranchMapSpec,BranchMapShot} from '../../../_shared/branch-map';
import {navigationEvents as sharedEvents} from '../../../_shared/branch-map';

// Two different judgments: peer identity during the handshake, and the
// authenticated decryption of each received record. Neither failure continues.
const nodes:BranchMapSpec['nodes']=[
 {id:'handshake',label:'安全握手\n核验身份·协商密钥',x:330,y:410,w:350,kind:'decision'},
 {id:'blocked',label:'证书警告\n停止正常发送',x:330,y:735,w:340,kind:'failure'},
 {id:'transfer',label:'受保护的传输\n请求与响应',x:900,y:410,w:350},
 {id:'receive',label:'接收端\n解密并验证',x:1320,y:410,w:260,kind:'decision'},
 {id:'accepted',label:'验证通过\n才处理内容',x:1700,y:410,w:280,kind:'success'},
 {id:'rejected',label:'拒绝数据\n终止本次连接',x:1700,y:700,w:290,kind:'failure'},
];
const edges:BranchMapSpec['edges']=[
 {id:'identity-failed',from:'handshake',to:'blocked',label:'身份核验未通过',labelAt:[330,572],color:'#FF929B'},
 {id:'handshake-ready',from:'handshake',to:'transfer',label:'核验通过·握手完成',labelAt:[615,377],color:'#56E4D3'},
 {id:'record-arrives',from:'transfer',to:'receive'},
 {id:'record-valid',from:'receive',to:'accepted',label:'通过',labelAt:[1505,377],color:'#56E4D3'},
 {id:'record-invalid',from:'receive',to:'rejected',label:'验证失败',labelAt:[1500,565],color:'#FF929B'},
];
const shots:Record<string,BranchMapShot>={
 '01':{focus:'handshake',crumb:'先看问题：密码经过网络会怎样'},
 '02':{focus:'handshake',crumb:'无保护对照 · 不属于正常安全连接'},
 '03':{focus:'handshake',crumb:'无保护对照 · 内容可能被替换'},
 '04':{focus:'handshake',enter:{hold:70,zoom:30},activeNodes:['handshake'],crumb:'安全握手内 · 先看网站身份如何核验'},
 '05':{focus:'handshake',exit:{zoom:28,hold:40},activeNodes:['handshake'],crumb:'核验通过的示例 · 域名、有效期与信任关系'},
 '06':{focus:'blocked',enter:{hold:50,zoom:30},exit:{zoom:20,hold:20},activeNodes:['handshake','blocked'],activeEdges:['identity-failed'],crumb:'另看核验失败 · 证书警告后停止正常发送',overviewHint:'另看核验失败的情景：从安全握手的身份判断处分开'},
 '07':{focus:'handshake',enter:{hold:75,zoom:30},activeNodes:['handshake'],activeEdges:['handshake-ready'],crumb:'回到核验通过的正常情景 · 握手内协商并导出密钥',overviewHint:'换回正常情景：身份核验通过，继续看安全握手'},
 '08':{focus:'transfer',activeNodes:['transfer','receive','accepted'],activeEdges:['record-arrives','record-valid'],crumb:'正常情景 · 请求加密传输，接收端解密并验证'},
 '09':{focus:'transfer',exit:{zoom:20,hold:16},activeNodes:['transfer','receive','accepted'],activeEdges:['record-arrives','record-valid'],crumb:'正常情景 · 响应反向传输，接收验证同样存在'},
 '10':{focus:'rejected',enter:{hold:55,zoom:30},exit:{zoom:22,hold:20},activeNodes:['receive','rejected'],activeEdges:['record-invalid'],crumb:'另看数据被改 · 接收验证失败，拒绝并终止连接',overviewHint:'另看被篡改的一条数据：从接收端的验证判断处分开'},
 '11':{focus:'transfer',mode:'overview',activeNodes:['handshake','transfer','receive'],activeEdges:['handshake-ready','record-arrives'],crumb:'机制回顾 · 说明传输保护的边界',overviewHint:'机制回顾：这张图保护的是两端之间的传输'},
 '12':{focus:'handshake',mode:'overview',activeNodes:nodes.map(n=>n.id),activeEdges:edges.map(e=>e.id),crumb:'回到全局 · 两处判断，各自决定能否继续',overviewHint:'回看两处判断：身份不过不正常发送，数据验证不过不处理'},
};
export const navigationSpec=(s:Shot,frame=0):BranchMapSpec=>({
 title:'安全传输：两处判断，各有停止出口',
 overviewHint:'安全握手包含身份核验与密钥协商；接收数据还要解密并验证',
 nodes:nodes.map(n=>n.id==='blocked'&&(Number(s.id)<5||(s.id==='05'&&frame<Number(s.cueFrames?.certLabel??1)))?{...n,label:'身份不符\n停止正常发送'}:n),edges,
 // Identity has passed, but the handshake is not complete until derivation ends.
 shots:s.id==='07'&&frame<273?{...shots,'07':{...shots['07'],activeEdges:[]}}:shots,
});
export const navigationEvents=(s:Shot):[string,number][]=>sharedEvents(navigationSpec(s),s.id,s.durationInFrames);
