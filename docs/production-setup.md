# 新环境制作与工具交接

供 Codex、Cursor 和其他 coding agent，也供换机器后接手的开发者使用。流程保存在仓库中；工具需要能读写文件、运行 shell、访问公开资料，并具备实际检查画面和音频的能力。某项能力不可用时，在本期记录里写清未完成范围，不能把命令通过写成已观看、听辨或用户认可。

## 从哪里开始

先读根 [AGENTS.md](../AGENTS.md)，再读 [RULES.md](RULES.md) 的现行规范与 STATUS、本页的环境准备、[制作流程](pipeline.md)和[质检清单](qa.md)。开工时同时查[教训](lessons-learned.md)、[成功经验](successful-practices.md)与[项目记忆](production-memory.md)；需要具体操作时再进入[配音](voice.md)、[渲染](render.md)、[图文](article-style.md)和[发布](publish.md)。[文档索引](README.md)区分现行手册与历史证据。

协作按内容统筹、调研编剧与分镜、制作、独立质检、发布与运营分工，不要求固定人名、bot 账号或专有 agent。按现有流程安排独立审读与复核，记录实际执行者，交接依据留在仓库；工具不自动读取 `AGENTS.md` 时，在任务指令里显式要求读取。不要另复制一套会逐渐分歧的制作规范。

所有下文命令除特别说明外都在仓库根执行。文中的 `EPDIR` 是本次实际制作或修订目录，使用前先替换；不能把示例期当作待重做任务。

## 先同步，再确定工程

先检查 `git status --short`，保护已有改动，再 `git fetch origin main`。新制作分支从最新 `origin/main` 建立；已有分支先检查差异再整合，不覆盖别人的工作。把实际基线完整 SHA、同步结果写进本期 README 或制作记录，同步后重读相关手册。

新期按[新期模板](../episodes/_template/README.md)建立 `episodes/<series>/<slug>/{production,publication}/`，系列键取自 [series.json](../site/src/content/series.json)。模板提供文稿与接入片段，**没有完整 Remotion 工程**；须选择当前同系列工程复用基础设施，并按本期主题重新设计。

修订已有期，先读 `publication/meta.json.sourcePath`，再读本期 README 和所指修订/系列入口。`sourcePath` 是源码位置，不一定是执行命令的目录；依赖通常装在对应 `package-lock.json` 所在的 Remotion 工程。不能仅因 `production/remotion/package.json` 存在，就认定其中旧 `render` 会生成当前发布版。

| 参考入口 | 用途与边界 |
| --- | --- |
| [LC.347 制作记录](../episodes/leetcode/top-k-frequent-elements/production/README.md) | 新期句级配音、代码卡、原题/署名片尾、实际字体与 limited BT.709、交付核验的完整案例；单期帧数、SHA 和检查能力不照搬 |
| [共享工具](../episodes/_shared/README.md) | 装配、铺轨、起音、冻结与媒体检查的真实接口 |
| [渲染手册](render.md) | 各系列当前视觉入口与封面模板；有的修订保留原 AAC，有的新期生成配音，按本期选择 |
| [固定回归样本](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md) | 仅供共享工具历史回归，不能当作现行新期模板 |

已有媒体的复核先找只读入口。目录迁移保留的旧清单只证明原输入；换路径、源码、字体或依赖后的渲染须在新修订中冻结实际输入，保留旧清单与回执，见[迁移记录](archive/2026-11/episode-layout/README.md)。

## 环境与依赖

现有制作入口主要针对 Linux，常固定 `/usr/bin/chromium` 和 `/usr/share/fonts/…`。Windows/macOS 使用者可采用 Linux 容器/虚拟机；原生适配时须核查真实路径、字体与编码能力，先做小样，再冻结新输入。相同依赖版本不保证跨机器编码的 MP4 字节相同；交付以本次冻结和本次产物的完整 SHA 为准。

| 项目 | 安装与检查依据 |
| --- | --- |
| Git、ripgrep、Node.js、npm | `rg` 用于下方环境检查。本站本地可用 Node.js 22/24 LTS；站点 CI 当前使用 Node 20，实际配置见 [deploy.yml](../.github/workflows/deploy.yml)。站点与动画工程分别 `npm ci`，不在仓根运行 `npm install` |
| Python | 建议 Python 3.12 + 独立 venv；优先安装本期 `requirements-runtime.txt`。音轨工具用 numpy、scipy、soundfile；资料卡用锁定的 [Pillow 依赖](../episodes/_shared/requirements-reference-appendix.txt) |
| FFmpeg / ffprobe | 需要 H.264/AAC 编解码、loudnorm、ebur128；limited BT.709 入口还使用 zscale。用本机实际功能和版本检查，不能只改颜色标签 |
| Chromium | 检查本期 package、QA 和系列脚本实际使用的路径；系统浏览器与 Remotion 默认下载的浏览器不能未经核对互换 |
| fontconfig、字体 | 用 `fc-match` 确认实际 family/style/path；常用 Noto Sans CJK SC、Noto Sans Mono、DejaVu Sans 的 regular/bold。资料卡默认读取 Noto CJK 的两份系统 TTC；实际字体路径和完整 SHA 进入本期绑定及冻结 |
| 网络与凭据 | 调研访问公开原文；首次 npm/pip 安装需网络；新配音需 MiMo API。GitHub PR/Release/部署另需已授权的 GitHub 连接或 CLI；本地制作无需发布凭据 |
| 可选语音能力 | 逐字 ASR 另需 faster-whisper 及实际模型缓存/下载，部分声学 QA 另需 praat-parselmouth。安装、模型、执行结果都具备才声明对应检查已完成，详见 [配音工具](../episodes/_shared/voice/README.md) |

例如 Debian/Ubuntu 可安装系统组件（Node.js 按所选版本另行安装）：

```sh
sudo apt-get update
sudo apt-get install -y git ripgrep python3 python3-venv python3-pip ffmpeg chromium \
  fontconfig fonts-noto-cjk fonts-noto-core fonts-noto-mono fonts-dejavu-core libsndfile1
```

下面用 LC.347 演示安装已提交的依赖；接手其他期时替换为该期实际锁文件。只安装依赖不会重新制作该期：

```sh
python3 -m venv "$HOME/.venvs/video-studio"
. "$HOME/.venvs/video-studio/bin/activate"
python3 -m pip install -r episodes/leetcode/top-k-frequent-elements/production/requirements-runtime.txt
npm --prefix site ci
npm --prefix episodes/leetcode/top-k-frequent-elements/production/remotion ci
```

不要依赖原机器的 `/workspace/.venv-*`、已删除工程的 `node_modules` 软链或全局 npm 包。共享依赖安装仅在当前保留工程的锁文件依赖完全相同时复用。没有本期 Python 清单时，先核对实际 imports 和共享工具要求，记录所用版本；不要把示例期的依赖声明为全系列统一锁。

安装后先检查环境，不请求 TTS、不渲染整片：

```sh
git --version
node --version
npm --version
python3 --version
ffmpeg -version
ffprobe -version
chromium --version
ffmpeg -hide_banner -filters | rg 'loudnorm|ebur128|zscale'
ffmpeg -hide_banner -encoders | rg 'libx264|aac'
fc-match -f '%{family} | %{style} | %{file}\n' 'Noto Sans CJK SC'
fc-match -f '%{family} | %{style} | %{file}\n' 'Noto Sans CJK SC:style=Bold'
fc-match -f '%{family} | %{style} | %{file}\n' 'Noto Sans Mono'
python3 -c 'import numpy, scipy, soundfile, PIL; print(numpy.__version__, scipy.__version__, soundfile.__version__, PIL.__version__)'
```

`fc-match` 找不到目标字体时可能返回替代字体，要核对输出的 family，随后按本期字体清单核对文件 SHA。有些工程还保留字体快照，但渲染器仍读取系统路径；快照存在不代表系统字体已匹配。环境检查通过后，先运行本期类型检查和关键连续小样，复核文字、动态及网页实际颜色，再展开全片。

## 配音凭据与复用

通过工具的凭据管理或当前进程环境注入 `MIMO_API_KEY`，只检查是否存在，不打印值，不写进命令日志、制作文档或 Git。共享 `voice/gen.py` 会启动 TTS 子进程，继承环境变量；它不转发 `--env`。直接调用 `tts/mimo_say.py` 才可用 `--env` 指向已忽略的本地文件。脚本默认的 `/workspace/video-studio/.mimo.env` 是旧机器路径，跨机器应优先使用环境变量。

```sh
python3 -c 'import os; print("MIMO_API_KEY 已配置" if os.environ.get("MIMO_API_KEY") else "MIMO_API_KEY 未配置")'
```

只有需要新配音时才调用 TTS。普通复核或画面小修优先保留已选 takes、`picks.json` 与整轨；TTS 非确定，不能为验证安装而重生成已验收音轨。已有音轨可在无密钥时复核或按本期约定复用。实际流程见[配音手册](voice.md)。

## 按阶段接续

以下是各阶段的交接依据，具体检查仍执行[制作流程](pipeline.md)，不以本表替代完整清单。

| 阶段 | 接手时需要的产物与判断 |
| --- | --- |
| 调研、脚本与图文定稿 | 实读来源/证据、`references.json`、脚本、图文、读音与草分镜；完成独立逻辑审读及图文结构审读，资料预检通过后再配音 |
| 配音、实测时序与分镜 | 已选 takes/picks、送模文本记录、真实 `voice.wav`、`words.json`、字幕与分镜；记录 ASR/声学/听辨的实际范围，哈希与时序一致 |
| 动画预检 | 当前源码、类型检查、关键连续小样和实际封面；复核动作因果、起音、文字边界、跨镜接续、字体和颜色 |
| 停写、冻结与正式编码 | 本期实际冻结器/只读核对命令、完整输入清单；默认渲染包含正文、适用代码卡和资料附录，正文临时 MP4 不作交付 |
| 成片与图文接入 | 最终视频、三比例封面、附录两份回执、渲染记录和完整 SHA；完成实际成片检查，核验截图、引用、字幕、章节、桌面/手机阅读和播放器 |
| 站点与收尾 | `publication/` 与检查通过的媒体一致，元数据指向当前源；按发布手册构建、发版和部署，线上完整 SHA/页面核验后更新记录及 issue |

常见命令的副作用要在接续前辨清：

| 命令或脚本 | 实际影响 |
| --- | --- |
| `prep.py`、`build.py`、本期 `assemble.py`、`place_v2.py --mode whole` | 写入句表、音轨、时序或公开音轨；用于正在制作的本期输入 |
| `gen.py` | 调用外部 TTS 并写 takes；`done` 不代表每句成功，须核对实际文件与选段 |
| 本期 `freeze.py` / 系列 `--freeze` | 写新冻结；先确认本期调用约定。有的脚本无 `--help` 处理，不能靠试运行探测接口 |
| 已核实的 `--verify`、`verify-freeze.py` | 不重写冻结输入；有的验证仍写 QA 报告，按当前入口说明选择报告位置 |
| `check_sentence_episode.py`、默认起音检查 | 会写本期检查报告；只读审计时使用工具提供的报告路径参数，或选择已说明的只读入口 |
| `npm run render` / 系列 `--render` | 可能覆盖输出，按当前工程 README 执行；不要对历史工程盲跑 |
| `npm --prefix site run build` | 运行内容检查、复制媒体、生成站点及搜索索引；不部署。`dev` 也会先检查图文并复制媒体 |

从仓根可先执行下列不改制作输入的检查；阶段未完成的缺项按实际处理，不能绕过检查或补造回执：

```sh
# 示例为已存在的 LC.347；接手其他期时先替换成该期实际目录。
EPDIR=episodes/leetcode/top-k-frequent-elements/production
python3 scripts/check-layout.py
node site/scripts/check-references.mjs --sources "$EPDIR"
npm --prefix site run check:dates
npm --prefix site run check:references
npm --prefix site run check:articles
python3 episodes/_shared/tests/secret_scan.py
```

`git status` 干净也可能留有 ignored 的旧根目录缓存。若布局检查报 `Unexpected series directory`，先核对该目录是否只有旧 `node_modules`，以及是否仍被有效工程引用；确认是可重建缓存后再移出内容目录保留。不能把制作稿、素材或冻结证据当缓存删除，也不能修改布局检查放行旧目录。

## 留给下一个工具的信息

在本期现有 README / 制作说明中维护下列信息，不要求另造日志体系；[制作说明模板](production-notes.template.md)可直接使用。先写当前阶段与下一步，再给足复现依据：

- 任务范围、slug/系列、基线完整 SHA、分支与上游同步结果。
- 当前制作/修订目录、发布目录、`meta.sourcePath`，以及实际源码入口、依赖安装位置。
- Node/Python/FFmpeg/Chromium 版本，锁文件、字体路径及 SHA，凭据仅写变量名。
- 已完成的审读、配音、小样、冻结、编码与成片检查；每条关键命令写明工作目录、参数、输出和副作用。
- 输入冻结清单、最终产物完整 SHA、附录/媒体回执及已核验的发布版本；区分正文帧数、代码卡和最终资料片尾。
- 未执行或受限的检查、待办与阻塞原因，区分本地通过、已上线和线上已核验。

可以给新工具这样的开工指令，并补上具体任务与 slug：

> 接手 video-studio 的本期制作。先读 AGENTS.md、docs/production-setup.md、docs/RULES.md 与 docs/pipeline.md，检查工作区并同步最新主干；按本期 publication/meta.json.sourcePath 和制作记录定位当前入口。先核对环境、当前阶段、冻结与已完成检查，再接续下一步。按本期真实命令交付视频、图文、封面与资料附录，更新制作记录；未做的检查如实列出。发布范围按现行 STATUS 与本次任务执行。

GitHub 站点持续发布与外部平台投稿的范围仍以 [STATUS](RULES.md#status) 和[发布手册](publish.md)为准。本页不扩大发布授权；纯文档整理不需要重新配音、编码或视频发版。
