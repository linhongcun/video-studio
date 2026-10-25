import storyboard from '@storyboard';
import traceData from '../../research/trace.json';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;visualType:string;chapterId:string;cueFrames?:{sentences?:number[];labels?:Record<string,number>};subtitles?:Subtitle[];codeCardFrom?:number;[key:string]:any};
export type TraceEvent={id:number;type:string;today:number;temperature:number;pending:number[];answer:number[];previous?:number;reason?:string;distance?:number;sourceLine:number;result?:number[]};
export type TraceCase={input:number[];actual:number[];expected:number[];events:TraceEvent[]};
export const TRACE=traceData;
export const MAIN=traceData.cases.main as TraceCase;
export const EQUALITY=traceData.cases.equality as TraceCase;
export const STORYBOARD=storyboard;
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((scene:any)=>scene.shots??[]).map((shot:any)=>{
 const item={...shot,id:String(shot.id).padStart(2,'0'),from:offset};offset+=shot.durationInFrames;return item;
});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
export type Beat=[number,number,number]; // sentence index, fraction within envelope, actual event id
// All snapshots and answers are imported, never re-computed by the renderer.
export const PLAYBACK:Record<string,{caseName:'main'|'equality';initial:number;beats:Beat[]} >={
 'first-days':{caseName:'main',initial:0,beats:[[0,.10,0],[0,.65,1],[1,.05,2],[1,.26,3],[1,.44,4],[1,.68,5],[1,.84,6]]},
 cooler:{caseName:'main',initial:6,beats:[[0,.06,7],[0,.22,8],[0,.38,9],[0,.55,10],[0,.70,11],[1,.04,12],[1,.25,13],[1,.49,14],[1,.72,15]]},
 multiple:{caseName:'main',initial:15,beats:[[0,.04,16],[0,.22,17],[0,.40,18],[0,.60,19],[0,.78,20],[1,.04,21],[1,.39,22],[1,.77,23]]},
 warmer:{caseName:'main',initial:23,beats:[[0,.03,24],[0,.20,25],[0,.37,26],[0,.56,27],[0,.74,28],[1,.05,29],[1,.54,30],[1,.78,31]]},
 finish:{caseName:'main',initial:31,beats:[[0,.06,32],[0,.58,33],[1,.16,34]]},
 equality:{caseName:'equality',initial:1,beats:[[0,.10,2],[0,.66,3],[1,.04,4],[1,.19,5],[1,.33,6],[1,.48,7],[1,.61,8],[1,.73,9],[1,.84,10],[1,.90,11],[1,.97,12]]},
};
