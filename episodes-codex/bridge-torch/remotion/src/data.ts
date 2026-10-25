import storyboard from '@storyboard';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;durationInFrames:number;from:number;visualType:string;subtitles?:Subtitle[];cueFrames?:Record<string,any>;[key:string]:any};
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((s:any)=>s.shots??[]).map((s:any)=>{const shot={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=shot.durationInFrames;return shot;});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
