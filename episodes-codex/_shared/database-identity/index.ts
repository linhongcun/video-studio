import {MYSQL_ICON_DATA} from './icon-data';

type MarkProps = {size?: number; opacity?: number; style?: Record<string, any>};

/** A stable database identity; state colors stay on the data and request paths. */
export function createDatabaseIdentity(React: {createElement: (...args: any[]) => any}) {
  const h = React.createElement;
  return function DatabaseMark({size = 48, opacity = 1, style = {}}: MarkProps) {
    return h('span', {'data-database-identity': 'mysql', role: 'img', 'aria-label': 'MySQL 数据库',
      style: {display: 'inline-flex', width: size, height: size, flexShrink: 0,
        verticalAlign: 'middle', opacity, ...style}},
      h('svg', {viewBox: '0 0 80 84', width: size, height: size, 'aria-hidden': true},
        h('path', {d: 'M8 17V66C8 80 72 80 72 66V17', fill: '#DDECF2', stroke: '#82B5CB', strokeWidth: 3}),
        h('ellipse', {cx: 40, cy: 17, rx: 32, ry: 10, fill: '#EDF6FA', stroke: '#82B5CB', strokeWidth: 3}),
        h('path', {d: 'M8 62C8 76 72 76 72 62', fill: 'none', stroke: '#82B5CB', strokeWidth: 2}),
        h('image', {href: MYSQL_ICON_DATA, x: 17, y: 23, width: 46, height: 40, preserveAspectRatio: 'xMidYMid meet'})));
  };
}
