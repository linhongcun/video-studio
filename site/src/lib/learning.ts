import {BASE, getSeries, type Episode, type Series} from './episodes';

export type LearningTrack = {
  id: 'systems' | 'agent' | 'algorithms' | 'patterns' | 'puzzles' | 'engineering' | 'message-queue' | 'database' | 'redis' | 'distributed';
  title: string;
  eyebrow: string;
  description: string;
  outcome: string;
  audience: string;
  series: Series[];
  episodes: Episode[];
  start: Episode;
  href: string;
  number: string;
};

type TrackDefinition = Pick<LearningTrack, 'id' | 'title' | 'eyebrow' | 'description' | 'outcome' | 'audience' | 'number'> & {
  seriesIds: string[];
};

const definitions: TrackDefinition[] = [
  {
    id: 'systems',
    number: '01',
    title: '系统原理',
    eyebrow: '从一次请求开始',
    description: '从浏览器与网络，到缓存和流量治理。沿着真实的数据流，理解请求怎样处理、系统怎样应对高峰与故障。',
    outcome: '看懂请求怎样到达服务、缓存怎样协作，以及系统遇到高峰和故障时怎样继续工作。',
    audience: '想建立计算机与后端基础，或补齐系统知识的开发者。',
    seriesIds: ['request', 'cache', 'peak'],
  },
  {
    id: 'agent',
    number: '02',
    title: 'Agent 开发',
    eyebrow: '理解机制与取舍',
    description: '从 Skills、MCP、Subagent、Goal 等 AI 概念出发，理解它们为何出现、怎样工作，以及各自的能力边界。',
    outcome: '分清相近概念的职责，理解机制与代价，为实际开发作出更有依据的选择。',
    audience: '会基本编程，希望理解 AI 与 Agent 设计机制的开发者。',
    seriesIds: ['agent'],
  },
  {
    id: 'algorithms',
    number: '03',
    title: '算法可视化',
    eyebrow: '把每一步看明白',
    description: '从具体题目和数据出发，用连续动画解释操作过程，再用推理说明为什么这样做。',
    outcome: '把动画里的每一步与代码对应起来，理解解法为什么正确，而不只记住答案。',
    audience: '正在学习数据结构与算法，希望看懂解题过程的开发者。',
    seriesIds: ['leetcode'],
  },
  {
    id: 'patterns',
    number: '04',
    title: '设计模式',
    eyebrow: '从变化理解设计',
    description: '跟随具体需求和代码的变化，理解设计模式解决了什么，以及什么时候值得使用。',
    outcome: '看清职责怎样拆分、变化怎样隔离，并比较引入设计模式与保留简单方案的取舍。',
    audience: '会基本编程，希望理解代码结构和设计取舍的开发者。',
    seriesIds: ['design-patterns'],
  },
  {
    id: 'puzzles',
    number: '05',
    title: '趣味推理',
    eyebrow: '每一步都有依据',
    description: '从赛马等经典问题出发，先看清题目规则，再用比较和排除一步步找到答案。',
    outcome: '理解哪些信息已经足够作出判断，能解释每一次选择和排除的依据。',
    audience: '无需编程基础，喜欢逻辑推理、想把解题过程看明白的学习者。',
    seriesIds: ['puzzles'],
  },
  {
    id: 'engineering',
    number: '06',
    title: '工程算法',
    eyebrow: '从系统问题理解算法',
    description: '从扩容、查询、故障和容量约束出发，用连续过程理解数据分配、集合摘要与节点协调。',
    outcome: '看清算法如何解决具体问题，理解它依赖的条件、维护成本与适用边界。',
    audience: '会基本编程，希望理解后端与分布式系统实现原理的开发者。',
    seriesIds: ['engineering-algorithms'],
  },
  {
    id: 'message-queue',
    number: '07',
    title: 'Kafka · 消息队列',
    eyebrow: '跟随一条记录理解 Kafka',
    description: '统一围绕 Apache Kafka，理解日志、消费组、写入确认、重放、顺序与积压。每期回答一个完整问题，可以独立观看。',
    outcome: '看清记录怎样追加、保留和读取，分清业务结果、消费进度与写入确认，理解 Kafka 的条件与代价。',
    audience: '会基本编程，希望系统理解 Kafka 工作原理与设计取舍的开发者。',
    seriesIds: ['message-queue'],
  },
  {
    id: 'database',
    number: '08',
    title: 'MySQL',
    eyebrow: '从MySQL读写理解内部机制',
    description: '以MySQL 8.4为背景，理解InnoDB索引、事务与锁，再看单主异步复制怎样传播更改。',
    outcome: '看清MySQL怎样查找数据、协调事务与冲突访问，以及异步复制怎样传播更改，理解具体实现的条件与边界。',
    audience: '会基本编程，希望理解MySQL工作原理并持续深入的开发者。',
    seriesIds: ['database'],
  },
  {
    id: 'redis',
    number: '09',
    title: 'Redis 系列',
    eyebrow: '从数据结构理解 Redis',
    description: '从跳表等数据结构出发，沿具体操作理解Redis内部机制、维护成本与适用边界。',
    outcome: '看清Redis怎样组织数据，把查找和插入的每一步与底层结构对应起来。',
    audience: '会基本编程，希望理解Redis数据结构与实现原理的开发者。',
    seriesIds: ['redis'],
  },
  {
    id: 'distributed',
    number: '10',
    title: '分布式',
    eyebrow: '从数据拆分理解跨节点协作',
    description: '从一个数据库装不下开始，理解分库分表、分布式 ID 与跨服务事务，再逐一看清不同事务方案的过程与边界。',
    outcome: '看清数据怎样分布、标识怎样生成，以及多个服务怎样协调业务结果，理解各方案的条件、代价与失败处理。',
    audience: '会基本编程，希望理解分布式系统工作原理与设计取舍的开发者。',
    seriesIds: ['distributed'],
  },
];

/** 方向只收录已发布课程；章节顺序沿用现有系列，历史 URL 与期号保持可追溯。 */
export function getLearningTracks(): LearningTrack[] {
  const allSeries = getSeries()
    .map((series) => ({...series, episodes: series.episodes.filter((episode) => !episode.draft && !episode.archived)}))
    .filter((series) => series.episodes.length);
  return definitions.flatMap(({seriesIds, ...definition}) => {
    const series = seriesIds.flatMap((id) => {
      const item = allSeries.find((s) => s.id === id);
      return item ? [item] : [];
    });
    const episodes = [...new Map(series.flatMap((s) => s.episodes).map((episode) => [episode.slug, episode])).values()];
    const start = episodes[0];
    return start ? [{...definition, series, episodes, start, href: `${BASE}learn/#${definition.id}`}] : [];
  });
}

export function getTrackForSeries(seriesId?: string): LearningTrack | undefined {
  if (!seriesId) return undefined;
  return getLearningTracks().find((track) => track.series.some((series) => series.id === seriesId));
}
