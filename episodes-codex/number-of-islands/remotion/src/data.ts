import storyboard from '@storyboard';
import lesson from './lesson.json';
export type Cell=[number,number];
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;durationInFrames:number;from:number;visualType:string;subtitles?:Subtitle[];cueFrames?:Record<string,any>;[key:string]:any};
export type TraceEvent={index:number;action:string;row:number|null;col:number|null;cell:Cell|null;from:Cell|null;reason:string|null;islandId:number|null;count:number;active:Cell|null;stack:Cell[];seen:Cell[];expanded:Cell[]};
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((scene:any)=>scene.shots??[]).map((shot:any)=>{const item={...shot,id:String(shot.id).padStart(2,'0'),from:offset};offset+=shot.durationInFrames;return item;});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
export const DEMO:any=lesson;
export const GRID:string[][]=DEMO.grid;
export const EVENTS:TraceEvent[]=DEMO.events??[];
export const INITIAL:TraceEvent={index:0,action:'initial',row:null,col:null,cell:null,from:null,reason:null,islandId:null,count:0,active:null,stack:[],seen:[],expanded:[]};
export const cellKey=(cell:Cell)=>cell.join(',');
export const equalCell=(a:Cell|null,b:Cell|null)=>!!a&&!!b&&a[0]===b[0]&&a[1]===b[1];
export const contains=(cells:Cell[],cell:Cell)=>cells.some(item=>equalCell(item,cell));
export const displayCell=(cell:Cell)=>`(${cell[0]+1},${cell[1]+1})`;
export const LAND:Cell[]=GRID.flatMap((row,r)=>row.flatMap((value,c)=>value==='1'?[[r,c] as Cell]:[]));
/** Select recorded AST-observed snapshots. This module performs no island search. */
export const event=(index:number):TraceEvent=>{
 if(index===0)return INITIAL;
 const selected=EVENTS[index-1];
 if(selected?.index===index)return selected;
 if(DEMO.provisional)return INITIAL;
 throw new Error(`Missing actual DFS event ${index}; never synthesize a trace snapshot.`);
};
export const eventSequence=(indices:number[],progress:number)=>event(indices[Math.min(indices.length-1,Math.floor(Math.max(0,Math.min(1,progress))*indices.length))]);
export const eventRange=(start:number,end:number)=>Array.from({length:end-start+1},(_,i)=>start+i);
export const scanAt=(snapshot:TraceEvent):Cell|null=>{
 for(let i=Math.min(snapshot.index,EVENTS.length)-1;i>=0;i--)if(EVENTS[i].action==='scan')return EVENTS[i].cell;
 return null;
};
export const componentAt=(cell:Cell):number=>DEMO.componentMap?.[cell[0]]?.[cell[1]]??0;
export const componentCells=(id:number)=>LAND.filter(cell=>componentAt(cell)===id);
