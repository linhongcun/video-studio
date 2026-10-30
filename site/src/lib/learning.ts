import {BASE, getSeries, type Episode, type Series} from './episodes';

export type LearningSeries = Series & {
  eyebrow: string;
  outcome: string;
  audience: string;
  start: Episode;
  href: string;
  number: string;
};

type SeriesDefinition = Pick<LearningSeries, 'id' | 'eyebrow' | 'outcome' | 'audience' | 'number'>;

const definitions: SeriesDefinition[] = [
  {
    id: 'peak',
    number: '01',
    eyebrow: '限流 · 幂等 · 熔断 · 降级',
    outcome: '看懂入口怎样控制流量、重复请求怎样处理，以及故障时怎样保护核心功能与恢复服务。',
    audience: '会基本编程，希望理解高峰流量、重复请求与服务故障处理的开发者。',
  },
  {
    id: 'agent',
    number: '02',
    eyebrow: '理解机制与取舍',
    outcome: '分清相近概念的职责，理解机制与代价，为实际开发作出更有依据的选择。',
    audience: '会基本编程，希望理解 AI 与 Agent 设计机制的开发者。',
  },
  {
    id: 'leetcode',
    number: '03',
    eyebrow: '把每一步看明白',
    outcome: '把动画里的每一步与代码对应起来，理解解法为什么正确，而不只记住答案。',
    audience: '正在学习数据结构与算法，希望看懂解题过程的开发者。',
  },
  {
    id: 'design-patterns',
    number: '04',
    eyebrow: '从变化理解设计',
    outcome: '看清职责怎样拆分、变化怎样隔离，并比较引入设计模式与保留简单方案的取舍。',
    audience: '会基本编程，希望理解代码结构和设计取舍的开发者。',
  },
  {
    id: 'puzzles',
    number: '05',
    eyebrow: '每一步都有依据',
    outcome: '理解哪些信息已经足够作出判断，能解释每一次选择和排除的依据。',
    audience: '无需编程基础，喜欢逻辑推理、想把解题过程看明白的学习者。',
  },
  {
    id: 'engineering-algorithms',
    number: '06',
    eyebrow: '按兴趣探索独立专题',
    outcome: '从感兴趣的问题出发，理解具体机制、条件与适用边界。',
    audience: '对独立技术专题感兴趣的学习者，可按各篇内容选择观看。',
  },
  {
    id: 'message-queue',
    number: '07',
    eyebrow: '跟随一条记录理解 Kafka',
    outcome: '看清记录怎样追加、保留和读取，分清业务结果、消费进度与写入确认，理解 Kafka 的条件与代价。',
    audience: '会基本编程，希望系统理解 Kafka 工作原理与设计取舍的开发者。',
  },
  {
    id: 'database',
    number: '08',
    eyebrow: '从MySQL读写理解内部机制',
    outcome: '看清MySQL怎样查找数据、协调事务与冲突访问，以及异步复制怎样传播更改，理解具体实现的条件与边界。',
    audience: '会基本编程，希望理解MySQL工作原理并持续深入的开发者。',
  },
  {
    id: 'redis',
    number: '09',
    eyebrow: '从应用场景到内部机制',
    outcome: '看懂Redis怎样用作共享缓存、数据更新后怎样处理旧副本，再把查找和插入与底层结构对应起来。',
    audience: '会基本编程，希望理解Redis应用场景、缓存设计与内部机制的开发者。',
  },
  {
    id: 'distributed',
    number: '10',
    eyebrow: '从数据拆分理解跨节点协作',
    outcome: '看清数据怎样分布、标识怎样生成，以及多个服务怎样协调业务结果，理解各方案的条件、代价与失败处理。',
    audience: '会基本编程，希望理解分布式系统工作原理与设计取舍的开发者。',
  },
  {
    id: 'request',
    number: '11',
    eyebrow: '从一次网页请求理解网络',
    outcome: '看清名称解析、安全连接、登录状态、请求分发与缓存复用怎样共同完成一次网页访问。',
    audience: '想理解浏览器与服务器怎样通信，建立计算机网络基础的开发者。',
  },
];

/** 每个已发布系列直接对应一组视频，名称与介绍以系列元数据为准。 */
export function getLearningSeries(): LearningSeries[] {
  const published = getSeries()
    .map((series) => ({...series, episodes: series.episodes.filter((episode) => !episode.draft && !episode.archived)}))
    .filter((series) => series.episodes.length);
  return published.map((series) => {
    const definition = definitions.find((item) => item.id === series.id);
    return {
      eyebrow: definition?.eyebrow ?? '用短片理解每一步',
      audience: definition?.audience ?? '对这个主题感兴趣的学习者。',
      outcome: definition?.outcome ?? series.description,
      number: definition?.number ?? String(series.order).padStart(2, '0'),
      ...series,
      start: series.episodes[0],
      href: `${BASE}series/${series.id}/`,
    };
  }).sort((a, b) => Number(a.number) - Number(b.number));
}

export function getLearningSeriesById(seriesId?: string): LearningSeries | undefined {
  return seriesId ? getLearningSeries().find((series) => series.id === seriesId) : undefined;
}

// 旧调用名称保留为别名；不再构造额外的学习方向层。
export const getLearningTracks = getLearningSeries;
export const getTrackForSeries = getLearningSeriesById;
