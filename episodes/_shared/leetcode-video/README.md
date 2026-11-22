# LeetCode正文视觉入口

## v2 顶部栏（新期与后续重制默认）

2026-11-22 起（见 [#527](https://github.com/linhongcun/video-studio/issues/527)），LeetCode 新期与后续重制默认使用 `FrameV2.tsx`（导出 `LeetcodeHeaderV2` / `LeetcodeHeader` 与 `LeetcodeBackdrop`）、`header-v2.ts` 和不可变配置 `style-v2.json`：

- **正片顶部栏显示具体算法题名称**：在 `LeetCode` 与金色 `LC.<number>` 胶囊右侧直接显示当前题目规范中文名（`identity.title`，如 `腐烂的橘子`、`实现 Trie（前缀树）`），不再常驻显示「算法可视化」。该槽位仅显示题名而不提前显示算法方法，继续保留「先推导再引出术语」的讲解顺序；若误传 `"算法可视化"` 或空标题将直接报错。
- **紧凑代码页（`compact`）自动去重拼接**：结尾 5 秒完整 Python 代码页使用 `compact` 模式时，自动格式化为 `题名 · 方法`；当 `method` 省略、与 `title` 相同（如 `二分查找`）或已以 `title` 开头时不再重复拼接。
- **排版自适应与副行去重**：四位题号（`LC.1000+`）自动放宽金色胶囊宽度并顺移题名起点；`detail` 仅用于当前章节或步骤摘要，若与题名或 `LeetCode N · 题名` 重复会自动抑制渲染。
- **保护历史冻结输入**：原有 7 个 v1 共享文件（`Frame.tsx`、`style-v1.json`、`identities-v1.json`、`theme.ts`、`references.py`、`render.py`、`qa.mjs`）保持原字节不变，不破坏存量成片的 `source-sha256.json`。新期按实际 import 闭包冻结 `FrameV2.tsx`、`header-v2.ts`、`style-v2.json`（及依赖的 `theme.ts`、`references.py`、`identities-v1.json`）。

示例用法：

```tsx
import {LeetcodeBackdrop, LeetcodeHeaderV2} from '../../../../../_shared/leetcode-video/FrameV2';

<LeetcodeHeaderV2
  slug="implement-trie"
  identity={{number: 208, title: '实现 Trie（前缀树）', method: '字典树'}}
  detail={shot.chapterTitle}
/>;
```

单元测试与真实 Chrome 1920×1080 DOM 预检：

```bash
node --test episodes/_shared/tests/test_leetcode_header_v2.mjs
node episodes/_shared/leetcode-video/verify-header-v2.mjs --out-dir /tmp/leetcode-header-v2-qa
```

## v1 视觉修订入口（历史冻结基线）

用于本轮已发布11题的独立视觉修订，正文、完整Python代码页与参考资料页沿现有封面的深蓝、暖金和青色风格。`style-v1.json`与`identities-v1.json`保存不可变样式和本轮身份快照；不读取会随新增题目增长的封面catalog作为运行输入。新增题目的Header可传独立身份，不能修改已经编码的v1快照。

各期新入口为`remotion/src/leetcode-style/index.ts`，新清单及产物位于`revisions/leetcode-style/`。原源码、模型、程序、分镜、字幕、声音和旧冻结保留历史字节。原分镜总帧包括最后150帧无旁白的完整Python代码；资料页在它之后另加150帧。本工具核对原`solution.py`、`solution.json`完整SHA与代码区间，不运行任何会改写分镜或配音的prepare/assemble脚本。

仓根执行：

```bash
node episodes/_shared/leetcode-video/qa.mjs two-sum --out-dir work/leetcode-video-style/preflight/two-sum
python3 episodes/_shared/leetcode-video/render.py two-sum --font-inputs
python3 episodes/_shared/leetcode-video/render.py two-sum --freeze
python3 episodes/_shared/leetcode-video/render.py two-sum --render
python3 episodes/_shared/leetcode-video/render.py two-sum --verify
```

默认只输出plan。正式编码前独立复核新入口及逐镜预检；QA默认采每镜0/.5/.98和代码边界、代码首/中/末帧，检查真实DOM、逐行完整Python文本、字幕退场、文字/字幕安全区及实际字体。`--frames 0,100`可作定向复查。静帧与DOM取样不能替代动态或听辨。

旧音轨按`baseline-publication.json`的Git提交/路径/完整SHA恢复至`work/leetcode-video-style/baseline/<slug>.mp4`，不能以新版片替代。新画面先静音渲染，再完整流拷贝旧AAC；逐包载荷/PTS/DTS/duration和解码PCM必须相同。参考资料复用既有原题及作者排版，每页最多4项、5秒；原正文含代码页全部解码帧/PTS由附录引擎保留。

新冻结同时包括原制作稿、当前发布稿、文章来源及完整保存证据、原代码源、实际import闭包、私有adapter/旧媒体核心和解析后的CJK/等宽/品牌字体文件（regular/bold）。字体在新manifest首次写入前加入；已存在清单缺字体或绑定不同会只读失败，不能修改旧manifest追认新输入。依赖按本期当前package-lock安装或复用非根依赖完全相同的保留安装目录。

实际制作、独立检查及发布状态见`docs/archive/2026-10/leetcode-video-style/`。不把旧来源阅读日期写成新官网GET，不预记ASR、全片人工听辨、真机或用户新版观看认可。
