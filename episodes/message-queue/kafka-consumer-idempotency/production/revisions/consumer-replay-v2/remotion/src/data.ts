export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;voice?:{localStart:number;localEnd:number}[];subtitles?:Subtitle[];[key:string]:any};
export function parseBoard(board:any){let offset=0;const shots:Shot[]=(board.scenes??[]).flatMap((s:any)=>s.shots??[]).map((s:any)=>{const v={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=s.durationInFrames;return v;});return {shots,video:{width:1920,height:1080,fps:30,durationInFrames:offset}};}
