# LC.1 制作说明

- 制作目录：episodes-codex/two-sum；internal EP.25，LeetCode 1。
- 成片：1920×1080、30fps；12镜24句；四章problem/lookup/distinct/code。最终帧数以root真实声学装配为准，不预写时长。
- 旁白：script.md为唯一文本；冰糖音色由root统一制作。sentences cue只来自真实句级起音；本代理未执行TTS、ASR或听辨。
- 主输入：[3,8,11,6,15]、target9；依次访问0/1/2/3，返回[0,3]，4未访问。独立重置输入：[3,8,3]、target6，返回[0,2]。
- 一遍哈希表。先计算需要值，再按值直接查询；未命中反馈后insert；命中直接return。表内数值与下标位置稳定，负need合法，不画成逐行线性搜索。
- 风格：深蓝canvas；teal正确匹配、gold当前/查询、red错误假设；无比喻、假应用窗、装饰进度条。
- 正文唯一代码画面在11镜：if need in seen:与seen[x] = i。末尾从codeCardFrom读取solution.json，13行完整Python，35px字、43px行距，静态150帧并提示暂停，无字幕与人声。
- solution.py、solution.json逐行及文章唯一python块必须相同；末尾return []仅健壮性，题目保证一解。
- 封面：16:9、3:4独立布局，4:3竖版缩.75于x315；重要内容仅在x315..1125、y<918。
- 独立资料与执行核验由batch_research负责research.md和research/verify_algorithm.py；本代理不将未核读editorial称为已读。
- 本代理只做轻量TypeScript检查，不启动TTS、整片或连续片渲染。实际动态/媒体/响度/冻结/线上检查由root排队，具体证据以最终QA为准。
