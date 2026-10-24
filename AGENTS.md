# AGENTS.md

给 Codex 或同类 coding agent。做一期之前先读本文件，再按下面的手册往下走。规范以 [docs/RULES.md](docs/RULES.md) 为准，步骤以 [docs/pipeline.md](docs/pipeline.md) 为准。

制作或重制视频前，先读 [教训](docs/lessons-learned.md) 和 [成功经验](docs/successful-practices.md)，再用 [项目制作记忆](docs/production-memory.md) 确认用户偏好和案例状态。新发现的错误与已经验证有效的做法分别追加到这两份文件，写清案例、改法与验证方式；单期参数不自动变成新规范。

本仓没有 `share/RULES.md`。2026-10-16 那份团队规范里的冲突条已经写进 `docs/RULES.md` 的废止节。不要从根 `README.md` 的旧段落、`design.md`、`site-plan.md`、站点关于页，或各期 `plan.md` 里恢复「比喻优先」和「发布含快手」。

## 提交署名

2026-10-24 用户要求：仓库由多台机器、不同工具共同维护，署名按实际参与本次变更的工具区分。后续由本机 Codex 制作的变更，保留原有主作者身份，在提交信息末尾空一行加入以下 trailer，以识别 Codex 参与：

```text
Co-authored-by: Codex <codex@openai.com>
```

Cursor 制作的变更使用以下署名，沿用仓库已有的显示名与用户确认的邮箱：

```text
Co-authored-by: Cursor Agent <cursoragent@cursor.com>
```

Cursor 或其他工具独立制作的提交不要求添加 Codex 署名，Codex 独立制作的提交也不添加 Cursor 署名。不得删除、替换或重复追加已有的 `Co-authored-by`；多工具实际共同贡献时可以并存多条不同署名。

Squash 合并生成的新提交应保留本次变更实际贡献者已有的全部联合署名；使用 GitHub merge API 时显式写入 `commit_message`，不能用固定的 Codex 署名覆盖其他贡献者。是否添加 Codex 署名依据实际贡献，不仅依据谁执行合并。

此约定只规定提交信息，不修改各机器的全局 Git 身份、提交模板或 hooks，从后续提交开始，不重写历史提交。

## 系列状态

2026-10-24 用户认可 EP.17 后批准本期合并及 GitHub 站点上线，并授权今后视频做好、完成检查后自主合并主干、发布 Release 和部署 Pages，无需逐期等待用户观看或 widget 批准；有反馈再修改、重新上线。资料、动画动态表达、配音时序、成片和线上完整 SHA 检查继续，能力限制须如实记录。授权范围和选题推进以 [docs/RULES.md](docs/RULES.md) 的 STATUS 为准；平台新发仍须另行明确授权。

## 角色

| 角色 | 谁 | 做什么 |
|---|---|---|
| 导演 | Nolan | 定选题和主线；和质检一起审成片。维护 `AGENTS.md`、`docs/RULES.md`、`docs/pipeline.md`，审并合并 PR |
| 编剧、分镜 | 宫崎（Hayao Miyazaki） | 调研输入、`script.md`、`article.mdx`、`pronunciation.md`、`storyboard.json`、`covers.json` |
| 制作 | Knoll（John Knoll） | 配音、Remotion、渲染、封面、站点 PR、Release、deploy |
| 质检 | Deming | 冻结后的预检，以及成片审 |
| 运营 | Tim Cook | 抖音（头条同步）、B站、视频号发布；平台链接私信 Knoll（站点维护者）和 Nolan |
| 村长 | — | 提出反馈；另行决定平台发布等持续授权范围外事项 |

脚本和分镜在团队内定稿。配音听辨由制作和复核人员处理，实际未完成的检查如实记录，不找村长代做质量检查。GitHub 站点按持续授权发布；确需用户决定范围外事项时，一次只问一件事，并附上成片和站点 PR。

## 闸门

按这个顺序，前一步没有产物就不要做下一步：

1. 配音与分镜冻结：把 SHA-256 写进 `words.json` 和 `storyboard.json` 的 `meta.timingSource`。
2. Deming 预检：起音窗口、COPYFIT、封面 4:3 安全区。见 [docs/validate.md](docs/validate.md)。
3. 渲染 `video.mp4` 和封面。见 [docs/render.md](docs/render.md)。
4. 完成成片复核，记录执行者、检查结果与能力限制。
5. 按 STATUS 的持续授权确认 GitHub 站点发布范围，无需逐期索取 widget 批准。
6. 合并主干、发布 Release、部署站点，并核对线上完整 SHA、字幕、章节、海报及更新日志。见 [docs/publish.md](docs/publish.md)。平台仅在另行明确授权后发布。
7. 视频制作完成、合并上线且核验通过后，将对应制作或重制 issue 以 `completed` 关闭；这是发布收尾的一部分，无需另行确认。

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

- 将 GitHub 站点持续发布授权用于尚未获授权的平台新发。
- 比喻、实物设备、假应用窗（文件管理器、记事本一类）。
- 把讲解表、图、流程图塞进浏览器壳。浏览器壳只给真网页、地址栏和 DevTools。
- 大面积纯白页身。页身色用 `episodes/_shared/theme/pageTheme.ts` 的 `pageBg` / `pageInk`。
- 新发快手或 X，或把平台链接发到群里。
- 编造本仓没有的脚本，或在期目录另写一份配音整轨脚本。配音整轨用 `episodes/_shared/voice/`（产出 `voice.wav`、`words.json`、`voice/cues.json`、`voice/shot_frames.json`）；参数改 `voice/params.json`，不要改脚本里的数。
- 另存一份起音算法。唯一实现是 `episodes/_shared/onset_rule.py`。`episodes/_shared/label_onset_strict.py` 只 import 它。冻结分镜里的 `episodes-codex/_shared/onset_rule.py` 是旧路径。期目录不要复制；需要从本期目录 import 时，symlink 到 `_shared`，或只写转发 import 的薄包装。
- 把 `episodes/*/validate.py` 里的「画面不出数字 / 不出英文」当成现行检查。那些脚本还依赖本仓没有的 `episodes/_audit/`。
- 把密钥、token、cookie 写进仓库或日志。TTS 密钥只来自环境变量 `MIMO_API_KEY`（或 `mimo_say.py --env` 指向的已忽略文件）；提交前跑 `python3 episodes/_shared/tests/secret_scan.py`。
