import {BASE, getSeries, type Episode, type Series} from './episodes';

export type LearningTrack = {
  id: 'systems' | 'agent' | 'algorithms' | 'patterns' | 'puzzles';
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
    description: '从浏览器与网络，到缓存、数据库和分布式。沿着真实的数据流，理解一个系统怎样运转。',
    outcome: '看懂请求怎样到达服务、数据怎样保存，以及系统遇到高峰和故障时怎样继续工作。',
    audience: '想建立计算机与后端基础，或补齐系统知识的开发者。',
    seriesIds: ['request', 'cache', 'peak', 'database', 'distributed'],
  },
  {
    id: 'agent',
    number: '02',
    title: 'Agent 开发',
    eyebrow: '从回答到执行',
    description: '模型怎样选择下一步，程序怎样调用工具，又怎样根据结果继续完成任务。先建立概念，再走向可靠执行。',
    outcome: '分清模型的回答、工具调用请求与程序的真实执行，理解一次 Agent 运行的来龙去脉。',
    audience: '会基本编程，想理解和开发 Agent 的学习者。',
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
    const episodes = series.flatMap((s) => s.episodes);
    const start = episodes[0];
    return start ? [{...definition, series, episodes, start, href: `${BASE}learn/#${definition.id}`}] : [];
  });
}

export function getTrackForSeries(seriesId?: string): LearningTrack | undefined {
  if (!seriesId) return undefined;
  return getLearningTracks().find((track) => track.series.some((series) => series.id === seriesId));
}
