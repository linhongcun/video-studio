# 仓库旧版内容清理

2026-10-25（北京时间）。按用户要求清理已被后续版本替代或不再使用的内容。对照基线 `686473df4fe89f6083a2386a8631d5dc32f4c04a` 的 Git 跟踪文件，共删除 **1925 个文件、652,497,310 字节（622.27 MiB）**；另清理旧工程目录内可重建的本地依赖与渲染产物。Git 历史未改写，删除清单可用 `git diff --diff-filter=D 686473df4fe89f6083a2386a8631d5dc32f4c04a..v0.56.3` 查看。

## 最新补充：撤下两期Agent试片

用户在评价原两期内容价值不足后明确要求删除。A01/EP.22（`agent-intro`）与A02/EP.28（`agent-tool-execution`）的发布内容和制作工程在本轮移除；`agent-intro-v2/`的拼接输入随第三版一起退出，不再受下方旧保留说明保护。具体删除范围、固定历史入口及待完成的部署核验见[撤下记录](agent-video-retirement.md)。下方文件数量、保留边界与检查均是v0.56.3清理批次的历史证据，不表示当前课程总数或仍需保留这两期。

## 删除依据

| 范围 | 依据 |
|---|---|
| `episodes/<slug>/remotion/`、`assets/`、`cover/` 及旧制作脚本 | 所有发布条目的 `sourcePath` 均已指向 Codex 制作工程；旧工程未被站点或当前冻结输入使用 |
| 站点侧 WAV、制作 PNG、未使用的 poster、哈希分镜快照、旧计划与词典 | 站点使用 MP4/JPG 和当前分镜；制作原稿及选定配音保留在当前制作目录 |
| Agent 第一版 `episodes-codex/agent-intro/` | 当前入口为第三版，第二、三版冻结清单不引用第一版 |
| `episodes/db-isolation/` | 已下架的旧草稿，未进入发布目录或学习路径 |
| 旧共享封面、Kokoro/tts_timing、旧品牌组件及其字体子集 | 当前各期封面和品牌画面自行实现，配音使用 MiMo；品牌 `spec.json` 的兼容参数保留 |
| Hero、SeriesFilter、ACCOUNT、旧站设计稿与 v0.3.0 截图 | 已被现行站点替代，代码和内容无引用 |

同时更新制作手册和源码入口。接入脚本不再向站点复制 WAV、制作 PNG 或未使用的 poster；临时目录实跑确认接入会移除旧副本。四份已过期的站点研究资料（HTTPS、缓存一致性、消息队列、熔断器）同步为当前制作资料，未改动站点正文与媒体。

## 保留边界

- 当前 31 支课程、1 支历史合集的 MP4、JPG、正文、元数据、分镜、字幕与源码入口保留；285 份发布核心文件与清理前逐字节一致。
- 当前制作的 33 份冻结清单及其 3170 个去重路径与基线比较，无新增缺失或哈希变化；制作原稿、选定素材与 QA 证据保留。
- 当时保留`agent-intro-v2/`：第三版仍将其`video.mp4`作为冻结输入。该项仅描述v0.56.3边界，已被后续明确删除两期Agent试片的决定取代。
- `distributed-tx/` 历史合集及原 URL 保留；旧网址兼容跳转不变。
- 共享配音、混音、主题、起音、品牌兼容参数，以及仍实际运行的历史固定回归样本保留。

## 验证

- `cd site && npm run build`：89 页构建成功，31 页进入搜索索引；历史合集维持排除。
- `node site/scripts/check-chapters.mjs`、`node site/scripts/check-learning-path.mjs --complete --built`：章节、字幕、媒体副本、课程路径和历史链接检查通过。
- `node site/scripts/check-frames.mjs`：32 个发布媒体帧数检查通过。
- `python3 -B episodes-codex/check-batch.py --integrated --built`：EP.01–14 当前制作输入、发布副本、构建媒体与逐句字幕检查通过。
- 使用 `/workspace/.venvs/video-studio/bin` 的 Python 环境运行 `sh episodes/_shared/tests/run_all.sh`：起音、铺轨、制作说明、配音合成样本、配音回归、分镜正反例及密钥扫描通过，没有跳过配音检查。
- 同一环境运行 `sh episodes/_shared/storyboard/examples/degradation/rerun.sh`：6623 项检查零错误、91 个起音事件通过，分镜与封面同固定 fixture 逐字节一致。
- 当前 32 份 `meta.json` 的成片、海报和源码目录均存在；当前代码相对引用复核及 `git diff --check` 通过。

### 清理前已有的复现限制

LC.11 与 LC.3 各有三项未纳入 Git 的局部拼接中间文件在本工作区原本就缺失。两期 `source-sha256.json` 对这些路径的记录未改：

- `remotion/out/problem-first-baseline/video.mp4`
- `remotion/out/problem-first-baseline/storyboard.json`
- `remotion/out/problem-first-intro.mp4`

这六项是清理前预检已发现的缺失，本次未删除或补写。现有完整成片、站点和其余输入核对通过，但不能据此宣称两期局部拼接流程已从零复现。本次没有重渲视频；按用户后续明确指令发布 v0.56.3，实际结果见下节。


## 上线结果

[PR #227](https://github.com/linhongcun/video-studio/pull/227) 已合并到 `main`，发布 [v0.56.3](https://github.com/linhongcun/video-studio/releases/tag/v0.56.3)。附注标签与正式部署指向 `42f0d35161b9557aa18a5a1c166d0200d6e6b8c3`；[Release 后 Pages 部署](https://github.com/linhongcun/video-studio/actions/runs/40139414111) 成功。

部署后对全部 32 条发布内容实际 GET，完整视频/海报 SHA-256、字节数、逐字节字幕、章节、标题和当前源码链接均通过；首页与更新日志可见 v0.56.3 和真实 Release 链接。原 URL 兼容、当前目录和历史合集入口另行核对通过。完整值与执行边界见 [线上核验记录](repository-cleanup-online.json)。未将文件核验声称为浏览器播放、全片听辨或用户观看认可。

LC.704 和 LC.3 的制作目录 `video.mp4` 输出在本工作区原本就未保留，站点及构建媒体与制作 `render-result.json` 的完整 SHA、字节数和帧数一致，报告已分别标注；未重建这些输出。其余 30 条媒体与制作实体文件三方一致。Git 历史保留，其他分支可同步 `origin/main` 获取清理结果。
