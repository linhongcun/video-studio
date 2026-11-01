import {REDIS_ICON_DATA, KAFKA_ICON_DATA, RABBITMQ_ICON_DATA} from './icon-data';

export type MiddlewareKind = 'redis' | 'kafka' | 'rabbitmq';
type MarkProps = {kind: MiddlewareKind; size?: number; opacity?: number; style?: Record<string, any>};

/** Identity only. Keep status colors on records/paths; label the actual role beside the mark. */
export function createMiddlewareIdentity(React: {createElement: (...args: any[]) => any}) {
  const h = React.createElement;
  return function MiddlewareMark({kind, size = 44, opacity = 1, style = {}}: MarkProps) {
    const kafka = kind === 'kafka';
    const inset = kafka ? size * .12 : 0;
    const source = kind === 'redis' ? REDIS_ICON_DATA : kafka ? KAFKA_ICON_DATA : RABBITMQ_ICON_DATA;
    const label = kind === 'redis' ? 'Redis 缓存（实现示例）' : kafka ? 'Apache Kafka 消息中间件（实现示例）' : 'RabbitMQ 消息队列（实现示例）';
    return h('span', {'data-middleware-identity': kind, role: 'img',
      'aria-label': label,
      style: {display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        width: size, height: size, flexShrink: 0, verticalAlign: 'middle', opacity,
        boxSizing: 'border-box', background: kafka ? '#EDF3F7' : 'transparent',
        border: kafka ? '1px solid #BDD1DE' : undefined,
        borderRadius: kafka ? Math.round(size * .16) : undefined, ...style}},
      h('img', {src: source, alt: '', 'aria-hidden': true,
        width: size - inset * 2, height: size - inset * 2,
        style: {display: 'block', objectFit: 'contain'}}));
  };
}
