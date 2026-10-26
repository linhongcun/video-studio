# AGENTS.md

给 Codex 或同类 coding agent。做一期之前先读本文件，再按下面的手册往下走。规范以 [docs/RULES.md](docs/RULES.md) 为准，步骤以 [docs/pipeline.md](docs/pipeline.md) 为准。

制作或重制视频前，先读 [教训](docs/lessons-learned.md) 和 [成功经验](docs/successful-practices.md)，再用 [项目制作记忆](docs/production-memory.md) 确认用户偏好和案例状态。每期制作、返工和收到用户反馈时都检查是否需要更新记录：新发现的错误与已经验证有效的做法分别追加到这两份文件，写清案例、改法与验证方式；尚未验证的指导先记到项目记忆，验证后再补证据。没有新发现时不凑条目；单期参数不自动变成新规范。

经验与反馈记录使用总结性语言：结合反馈和实际制作过程，提炼有效做法、问题原因、改进措施及验证范围，保持简洁清晰。不摘录用户原话或复制对话；提交、issue和PR中的反馈说明也遵守此约定。

本仓没有 `share/RULES.md`。2026-10-16 那份团队规范里的冲突条已经写进 `docs/RULES.md` 的废止节。旧工程和旧站规划已清理，不要从 Git 历史恢复「比喻优先」和「发布含快手」。

2026-10-25用户进一步强调：参考资料附录必须从新片制作流程中默认生成，避免上线后返工补齐。开新期按[新期模板](episodes-codex/_template/README.md)准备 `references.json`，调研、脚本、分镜、冻结和渲染同步接入；正式编码前检查来源清单，发布前检查实际附录。存量暂缓仅限已登记、视频SHA仍为基线字节且尚未接入附录的旧片；旧slug后续重制或换片也必须带齐，不得扩大豁免名单。

当前参考资料片尾采用 `presentation: title-author` 的简洁列表，只显示实际文档原题与作者或机构，每页最多4项、默认5秒。`title` 与 `titleEvidence` 继续核对原题；有明确公开个人署名时填写非空字符串 `author`，未明确署名时省略该字段并显示 `organization`，不把维护账号或Git提交者推定为作者。摘录、定位、年份/版本、核验日期、链接和说明不出现在视频资料列表中，完整出处与必要原文保留在文章或研究记录。这项指导取代此前双行原题/摘录卡的默认样式，原题与真实性要求不变；旧QA、发布记录和冻结输入保留历史身份。具体审查按[调研模板](docs/research-template.md)执行。

## 开工前同步

2026-10-25用户明确要求：开始单期或批量制作之前，先拉取最新代码，避免重构、删除和流程更新造成冲突。先检查工作区状态并保护未提交工作，fetch最新主干，再从最新`origin/main`建立制作分支或整合到现有分支；不要覆盖其他人的改动。同步后重新读取已更新手册，核对本次涉及的删除/移动、共享脚本、源码入口和锁文件，再复制工程或改代码。记录基线SHA、同步结果和依赖位置。

本机仍存在的ignored文件不能当作现行依赖依据：新工程依赖按当前锁文件安装，共享软链只指向保留的当前制作目录，不继续指向已删除的旧工程。编码和发布前再次检查上游变化及冻结输入交集，版本标签按L029复核。具体案例见[批量开工记录](docs/leetcode-batch-20261025/README.md)与L032。

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
| 编剧、分镜 | 宫崎（Hayao Miyazaki） | 调研输入、`references.json`、`script.md`、`article.mdx`、`pronunciation.md`、`storyboard.json`、`covers.json` |
| 制作 | Knoll（John Knoll） | 配音、Remotion、渲染、封面、站点 PR、Release、deploy |
| 质检 | Deming | 冻结后的预检，以及成片审 |
| 运营 | Tim Cook | 抖音（头条同步）、B站、视频号发布；平台链接私信 Knoll（站点维护者）和 Nolan |
| 村长 | — | 提出反馈；另行决定平台发布等持续授权范围外事项 |

脚本和分镜在团队内定稿。配音听辨由制作和复核人员处理，实际未完成的检查如实记录，不找村长代做质量检查。GitHub 站点按持续授权发布；确需用户决定范围外事项时，一次只问一件事，并附上成片和站点 PR。

## 闸门

按这个顺序，前一步没有产物就不要做下一步：

1. 资料、配音与分镜冻结：核验核心来源，冻结 `references.json` 及附录生成输入；把配音 SHA-256 写进 `words.json` 和 `storyboard.json` 的 `meta.timingSource`。
2. Deming 预检：来源清单、起音窗口、COPYFIT、封面 4:3 安全区。正式编码前通过 `node site/scripts/check-references.mjs --sources EPDIR`。见 [docs/validate.md](docs/validate.md)。
3. 通过本期默认入口渲染正文、参考资料附录和封面，不能只交付未加附录的正文。见 [docs/render.md](docs/render.md)。
4. 完成成片复核，检查实际资料卡、字幕边界及播放器暂停/全屏，记录执行者、检查结果与能力限制。
5. 按 STATUS 的持续授权确认 GitHub 站点发布范围，无需逐期索取 widget 批准。
6. 站点构建先通过参考资料检查；新片缺少资料、实际附录或一致的媒体记录时停止发布。再合并主干、发布 Release、部署站点，并核对线上完整 SHA、字幕、章节、海报及更新日志。见 [docs/publish.md](docs/publish.md)。平台仅在另行明确授权后发布。
7. 视频制作完成、合并上线且核验通过后，将对应制作或重制 issue 以 `completed` 关闭；这是发布收尾的一部分，无需另行确认。

## 目录地图

| 路径 | 本仓实际情况 |
|---|---|
| `episodes/` | 站点发布内容：元数据、文章、字幕、分镜、MP4 和 JPG；制作源码及 WAV、PNG 原稿留在 `episodes-codex/` |
| `episodes/degradation/` | EP.14 站点数据副本；当前制作工程在 `episodes-codex/degradation/` |
| `episodes-codex/` | EP.01–21 的当前 Codex 制作目录，另有 EP.21 前置入门 `distributed-tx-intro/` 与独立短片 `tx-2pc/`、`tx-tcc/`、`tx-saga/`、`tx-outbox/`。EP.01–14 本轮状态见 [批次记录](docs/codex-remake-ep01-14.md)；开新期入口见 [`episodes-codex/_template/README.md`](episodes-codex/_template/README.md) |
| `*-backup/` | 各角色备份。本仓没有这些目录 |
| `share/` | 本仓没有。规范不要写回这里 |
| `episodes/_shared/` | 页身色、水印规范、混音、MiMo TTS，以及起音、铺轨、制作说明与配音整轨工具；固定回归样本仍保留 |
| `docs/` | 下面这些手册。制作说明模板是 `docs/knoll-props.template.md` |
| `site/` | Astro 站点。`site/package.json` 的 `version` 是三段式版本号 |

2026-10-25 清理已被替代的旧工程，记录见 [docs/repository-cleanup.md](docs/repository-cleanup.md)。当前制作入口以各期 `meta.json.sourcePath` 为准。用户随后明确要求删除两期Agent试片：A01/EP.22与A02/EP.28的发布目录及相关制作工程一并移除，原先保护`agent-intro-v2/video.mp4`拼接依赖的说明随第三版删除而失效。后续仍推进Skills、MCP、Subagent、Goal等11项概念研究候选；删除前工程与检查通过固定Git提交追溯。当前删除范围与发布验证见[撤下记录](docs/agent-video-retirement.md)，不从历史恢复这两期为现行课程。

## 手册

1. [docs/RULES.md](docs/RULES.md) — 现行规范，以及废止条
2. [docs/pipeline.md](docs/pipeline.md) — 调研 → 脚本 → 分镜 → 配音 → 渲染 → 校验 → 发版
3. [docs/research-template.md](docs/research-template.md)
4. [docs/storyboard-schema.md](docs/storyboard-schema.md)
5. [docs/voice.md](docs/voice.md)
6. [docs/render.md](docs/render.md)
7. [docs/validate.md](docs/validate.md)
8. [docs/publish.md](docs/publish.md)
9. 新拆分短片的句级装配/时序/冻结/编码检查共用 [episodes-codex/_shared/README.md](episodes-codex/_shared/README.md)，不复制配音整轨或起音算法。
10. [episodes-codex/_template/README.md](episodes-codex/_template/README.md)
11. [docs/knoll-props.template.md](docs/knoll-props.template.md) — 制作说明模板；EP.14 全文在 [docs/examples/knoll-props.degradation.md](docs/examples/knoll-props.degradation.md)

## 禁止

- 将 GitHub 站点持续发布授权用于尚未获授权的平台新发。
- 比喻、无关实物设备，以及给机制图套无关应用外壳。题目本身的楼梯等场景应直接参与动作和推导；可以按用户指导用对应功能的交互界面建立使用场景，具体边界见 `docs/RULES.md` 画面节。
- 把讲解表、图、流程图塞进浏览器壳。浏览器壳只给真网页、地址栏和 DevTools。
- 大面积纯白页身。页身色用 `episodes/_shared/theme/pageTheme.ts` 的 `pageBg` / `pageInk`。
- 新发快手（[STATUS](docs/RULES.md) 中逐次明确授权除外）或 X，或把平台链接发到群里。
- 编造本仓没有的脚本，或在期目录另写一份配音整轨脚本。配音整轨用 `episodes/_shared/voice/`（产出 `voice.wav`、`words.json`、`voice/cues.json`、`voice/shot_frames.json`）；参数改 `voice/params.json`，不要改脚本里的数。
- 另存一份起音算法。唯一实现是 `episodes/_shared/onset_rule.py`。`episodes/_shared/label_onset_strict.py` 只 import 它。冻结分镜里的 `episodes-codex/_shared/onset_rule.py` 是旧路径。期目录不要复制；需要从本期目录 import 时，symlink 到 `_shared`，或只写转发 import 的薄包装。
- 从历史旧校验器恢复「画面不出数字 / 不出英文」规则。现行检查入口见 `docs/validate.md`。
- 把密钥、token、cookie 写进仓库或日志。TTS 密钥只来自环境变量 `MIMO_API_KEY`（或 `mimo_say.py --env` 指向的已忽略文件）；提交前跑 `python3 episodes/_shared/tests/secret_scan.py`。
