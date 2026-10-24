# AGENTS.md

给 Codex 或同类 coding agent。做一期之前先读本文件，再按下面的手册往下走。规范以 [docs/RULES.md](docs/RULES.md) 为准，步骤以 [docs/pipeline.md](docs/pipeline.md) 为准。

本仓没有 `share/RULES.md`。2026-10-16 那份团队规范里的冲突条已经写进 `docs/RULES.md` 的废止节。不要从根 `README.md` 的旧段落、`design.md`、`site-plan.md`、站点关于页，或各期 `plan.md` 里恢复「比喻优先」和「发布含快手」。

## 系列状态

系列默认暂停。2026-10-24 用户单独批准 #66 的 EP.15 重制及 GitHub 站点部署（v0.45.1，只上站点）；其他新期与平台新发尚未恢复。详见 [docs/RULES.md](docs/RULES.md) 的 STATUS。

## 角色

| 角色 | 谁 | 做什么 |
|---|---|---|
| 导演 | Nolan | 定选题和主线；和质检一起审成片。维护 `AGENTS.md`、`docs/RULES.md`、`docs/pipeline.md`，审并合并 PR |
| 编剧、分镜 | 宫崎（Hayao Miyazaki） | 调研输入、`script.md`、`article.mdx`、`pronunciation.md`、`storyboard.json`、`covers.json` |
| 制作 | Knoll（John Knoll） | 配音、Remotion、渲染、封面、站点 PR、Release、deploy |
| 质检 | Deming | 冻结后的预检，以及成片审 |
| 运营 | Tim Cook | 抖音（头条同步）、B站、视频号发布；平台链接私信 Knoll（站点维护者）和 Nolan |
| 村长 | — | 只批最终上线 |

脚本和分镜在团队内定稿。配音听辨由 Knoll 和 Nolan 完成，不找村长听。请村长决定时用单选 widget，一次只问一件事，并附上成片和站点 PR。

## 闸门

按这个顺序，前一步没有产物就不要做下一步：

1. 配音与分镜冻结：把 SHA-256 写进 `words.json` 和 `storyboard.json` 的 `meta.timingSource`。
2. Deming 预检：起音窗口、COPYFIT、封面 4:3 安全区。见 [docs/validate.md](docs/validate.md)。
3. 渲染 `video.mp4` 和封面。见 [docs/render.md](docs/render.md)。
4. Nolan 与 Deming 审成片。
5. 村长用 widget 批准上线。
6. 站点发版，再发平台。见 [docs/publish.md](docs/publish.md)。站点发版由 Knoll 做。

## 目录地图

| 路径 | 本仓实际情况 |
|---|---|
| `episodes/` | 站点内容。已上线各期的 `meta.json`、`article.mdx`、`video.mp4` 和重制工程都在这里 |
| `episodes/degradation/` | 最新重制参考。分镜 `meta.slug` 是 `degradation-v1`，站点 slug 仍是 `degradation` |
| `episodes-codex/` | 现行制作目录。`db-index/` 为 EP.15 已批准的重制工程；其他期入口见 [`episodes-codex/_template/README.md`](episodes-codex/_template/README.md) |
| `*-backup/` | 各角色备份。本仓没有这些目录 |
| `share/` | 本仓没有。规范不要写回这里 |
| `episodes/_shared/` | 页身色、水印规范、混音、TTS、旧的共享封面工程，以及 `onset_rule.py`、`label_onset_strict.py`、`place_v2.py`、`make_knoll_props.py`、`voice/`（配音整轨） |
| `docs/` | 下面这些手册。制作说明模板是 `docs/knoll-props.template.md` |
| `site/` | Astro 站点。`site/package.json` 的 `version` 是三段式版本号 |
| `covers/cover-spec.json` | 只给共享封面工程用，不含 degradation |

## 手册

1. [docs/RULES.md](docs/RULES.md) — 现行规范，以及废止条
2. [docs/pipeline.md](docs/pipeline.md) — 调研 → 脚本 → 分镜 → 配音 → 渲染 → 校验 → 发版
3. [docs/research-template.md](docs/research-template.md)
4. [docs/storyboard-schema.md](docs/storyboard-schema.md)
5. [docs/voice.md](docs/voice.md)
6. [docs/render.md](docs/render.md)
7. [docs/validate.md](docs/validate.md)
8. [docs/publish.md](docs/publish.md)
9. [episodes-codex/_template/README.md](episodes-codex/_template/README.md)
10. [docs/knoll-props.template.md](docs/knoll-props.template.md) — 制作说明模板；EP.14 全文在 [docs/examples/knoll-props.degradation.md](docs/examples/knoll-props.degradation.md)

## 禁止

- 暂停期间开新期，或改已上线成片。
- 比喻、实物设备、假应用窗（文件管理器、记事本一类）。
- 把讲解表、图、流程图塞进浏览器壳。浏览器壳只给真网页、地址栏和 DevTools。
- 大面积纯白页身。页身色用 `episodes/_shared/theme/pageTheme.ts` 的 `pageBg` / `pageInk`。
- 新发快手或 X，或把平台链接发到群里。
- 编造本仓没有的脚本，或在期目录另写一份配音整轨脚本。配音整轨用 `episodes/_shared/voice/`（产出 `voice.wav`、`words.json`、`voice/cues.json`、`voice/shot_frames.json`）；参数改 `voice/params.json`，不要改脚本里的数。
- 另存一份起音算法。唯一实现是 `episodes/_shared/onset_rule.py`。`episodes/_shared/label_onset_strict.py` 只 import 它。冻结分镜里的 `episodes-codex/_shared/onset_rule.py` 是旧路径。期目录不要复制；需要从本期目录 import 时，symlink 到 `_shared`，或只写转发 import 的薄包装。
- 把 `episodes/*/validate.py` 里的「画面不出数字 / 不出英文」当成现行检查。那些脚本还依赖本仓没有的 `episodes/_audit/`。
- 把密钥、token、cookie 写进仓库或日志。TTS 密钥只来自环境变量 `MIMO_API_KEY`（或 `mimo_say.py --env` 指向的已忽略文件）；提交前跑 `python3 episodes/_shared/tests/secret_scan.py`。
