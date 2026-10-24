import type {Shot} from './data';
type Window=[number,number];
const rows:Record<string,Record<string,Window>>={
 '01':{check:[18,63],back:[75,120]},
 '02':{cache:[48,88],back:[205,250]},
 '03':{write:[42,92]},
 '04':{check:[36,76],back:[91,136]},
 '05':{write:[134,174],remove:[189,229]},
 '06':{confirm:[15,55],remove:[120,170]},
 '07':{miss:[30,55],query:[60,90],back:[99,134],fill:[140,175]},
 '08':{read:[42,82],back:[90,135]},
 '09':{remove:[42,74],read:[160,195],back:[198,233],fill:[238,273]},
 '10':{write:[18,63],read:[165,210]},
 '11':{fail:[147,182]},
 '12':{gone:[48,108],back:[116,151],fill:[157,192]},
};
export const windowAt=(s:Shot,name:string):Window=>{
 const result=rows[s.id]?.[name];if(!result)throw new Error(`Missing visual window ${s.id}/${name}`);return result;
};
export const actionWindows=(s:Shot)=>rows[s.id]??{};
export const events=(s:Shot):[string,number][]=>Object.entries(actionWindows(s)).flatMap(([name,[a,b]])=>[[`${name}-start`,a],[`${name}-mid`,Math.round((a+b)/2)],[`${name}-end`,b]] as [string,number][]);
