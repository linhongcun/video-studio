# 仓库旧版内容清理

2026-10-25（北京时间）。按用户要求清理已被后续版本替代或不再使用的内容。对照基线 `686473df4fe89f6083a2386a8631d5dc32f4c04a` 的 Git 跟踪文件，共删除 **1925 个文件、652,497,310 字节（622.27 MiB）**；另清理旧工程目录内可重建的本地依赖与渲染产物。Git 历史未改写，删除清单可用 `git diff --diff-filter=D 686473df4fe89f6083a2386a8631d5dc32f4c04a..v0.56.3` 查看。

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
- `agent-intro-v2/` 保留：第三版仍将其 `video.mp4` 作为显式冻结输入拼接尾段，不能按目录版本号删除。
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

这六项是清理前预检已发现的缺失，本次未删除或补写。现有完整成片、站点和其余输入核对通过，但不能据此宣称两期局部拼接流程已从零复现。本次没有重渲视频；在用户明确要求提交上线后，按 v0.56.3 发布，合并、部署及线上实测结果在发布完成后追加。
