export type MainProps={hideSubtitles?:boolean;auditLayout?:boolean};
export type CoverSize='16x9'|'4x3'|'3x4';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;visualType:string;voice?:any[];subtitles?:Subtitle[];cueFrames?:any;[key:string]:any};
export type Stage={key:string;position:number;slot:number;kind:'write'|'read'|'clear';raw:number;p:number;arrived:boolean;active:boolean;started:boolean};
