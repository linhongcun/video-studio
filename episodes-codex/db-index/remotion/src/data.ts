import storyboard from '@storyboard';
export type Subtitle = {text:string; from:number; to?:number; duration?:number};
export type Shot = {id:string; durationInFrames:number; narration?:string; subtitles?:Subtitle[]; cueFrames?:Record<string,number>; from:number; [key:string]:any};
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((s:any)=>s.shots??[]).map((s:any)=>{
 const shot={...s,id:String(s.id).padStart(2,'0'),from:offset}; offset+=s.durationInFrames; return shot;
});
export const VIDEO={width:storyboard.meta?.width??1920,height:storyboard.meta?.height??1080,fps:storyboard.meta?.fps??30,durationInFrames:offset};
export const ORDERS=[
 {id:'7061',item:'书桌灯',amount:'129',status:'已发货'},
 {id:'7024',item:'笔记本',amount:'28',status:'已完成'},
 {id:'7098',item:'水杯',amount:'59',status:'已发货'},
 {id:'7013',item:'收纳盒',amount:'36',status:'已完成'},
 {id:'7086',item:'帆布袋',amount:'49',status:'待发货'},
 {id:'7042',item:'耳机',amount:'199',status:'待发货'},
 {id:'7075',item:'鼠标垫',amount:'39',status:'已完成'},
 {id:'7009',item:'手机支架',amount:'45',status:'已发货'},
];
export const INDEX=ORDERS.map((o,i)=>({id:o.id,row:i+1})).sort((a,b)=>a.id.localeCompare(b.id));
