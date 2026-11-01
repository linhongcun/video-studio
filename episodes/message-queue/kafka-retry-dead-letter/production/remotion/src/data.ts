import storyboard from '@storyboard';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;voice?:{localStart:number;localEnd:number}[];subtitles?:Subtitle[];[key:string]:any};
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((s:any)=>s.shots??[]).map((s:any)=>{const out={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=s.durationInFrames;return out;});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:Math.max(1,offset)};
export const hasMeasuredBody=offset>0;
