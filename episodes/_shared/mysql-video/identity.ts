import {MYSQL_ICON_DATA} from '../database-identity/icon-data';
import {C} from './theme';

type MarkProps={size?:number;opacity?:number;style?:Record<string,any>};

/** Original licensed MySQL mark inside the series' own cylinder treatment. */
export function createDatabaseIdentity(React:{createElement:(...args:any[])=>any}) {
 const h=React.createElement;
 return function MysqlMark({size=48,opacity=1,style={}}:MarkProps) {
  return h('span',{'data-database-identity':'mysql',role:'img','aria-label':'MySQL 数据库',
   style:{display:'inline-flex',width:size,height:size,flexShrink:0,verticalAlign:'middle',opacity,...style}},
   h('svg',{viewBox:'0 0 80 84',width:size,height:size,'aria-hidden':true},
    h('path',{d:'M8 17V66C8 80 72 80 72 66V17',fill:C.surface,stroke:C.teal,strokeWidth:3}),
    h('ellipse',{cx:40,cy:17,rx:32,ry:10,fill:C.row,stroke:C.teal,strokeWidth:3}),
    h('path',{d:'M8 62C8 76 72 76 72 62',fill:'none',stroke:C.teal,strokeWidth:2}),
    h('image',{href:MYSQL_ICON_DATA,x:17,y:23,width:46,height:40,preserveAspectRatio:'xMidYMid meet'})));
 };
}
