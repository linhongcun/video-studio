# 发布

2026-10-24 用户已批准 EP.17 合并及 GitHub 上线，并持续授权以后视频做好、完成检查后自主合并主干、发布 Release、部署 Pages；有反馈再修改重发，不再逐期等待 widget 批准。授权范围以 [RULES.md](RULES.md) 的 STATUS 为准，质量与部署后完整 SHA 检查继续执行，实际能力限制如实记录。

此授权仅覆盖 GitHub 与本站。抖音、B站、视频号等平台新发仍须用户另行明确授权；代理、质检或导演的同意不代替用户的平台授权。只上站点走下方「站点发版清单」和「只上站点」。

链接不发到群。`meta.json` 的 `platforms` 只填真实的 `bilibili` 和 `douyin`。视频号没有网页链接，不写。

## 站点内容

一期在站点上可见，需要 `episodes/<slug>/meta.json` 的 `draft` 为 `false`，以及同目录的 `article.mdx`、`video.mp4`、海报。列表和页面由 `site/src/lib/episodes.ts` 读取 `episodes/*/meta.json`。`series` 必须是 `site/src/content/series.json` 里的键，具体系列以该文件为准；新增系列时同步添加标题、简介与顺序。LeetCode题号写`problemNumber`用于展示LC.N，内部整数`ep`继续用于排序和Release关联；独立算法系列不接入原技术系列的前后课学习链。

`draft: true` 的期默认不进构建。本地要看草稿：

```sh
cd site
SHOW_DRAFTS=1 npm run build
```

现行重制的制作目录按 [../AGENTS.md](../AGENTS.md) 是 `episodes-codex/<slug>/`，已包含 `db-index/`、`db-transaction/`、`db-lock/` 工程。站点仍只读取 `episodes/<slug>/`；将检查通过的冻结产物接入该目录，slug 与 `meta.json` 的 `slug` 一致。分镜内部 slug（如 `degradation-v1`）不要当成站点路径。

## 本地站点

`site/package.json`：

```sh
cd site
npm ci
npm run dev
npm run build
npm run preview
```

`dev` 和 `build` 都会先跑 `npm run copy-assets`。构建再跑 Pagefind。部署工作流是 `.github/workflows/deploy.yml`：推到 `main` 时构建 `site/` 并发布 GitHub Pages。

## PR 与版本

版本在 `site/package.json` 的 `version`，三段式。只改成片或文章升修订号；新一期或站点功能升次版本号。第21期常见实现独立短片与旧合集归档本次版本为 v0.47.0；EP.01–14 Codex重制与章节首帧定位版本为 v0.48.0；EP.21四片的全局流程与缩放导航修订为v0.51.0，保留至v0.50.5的协作主干；实际版本以该文件及 Release 为准。

1. 改 `meta.json`：`draft: false`，写上 `publishedAt`。重发或只改站点时更新 `updatedAt`。
2. 开 PR，合并进 `main`。推到 `main` 会跑 `.github/workflows/deploy.yml`，部署 GitHub Pages。这次构建发生在 Release 之前，`/changelog/` 还不会带上新版本。新版本要等第 4 步，在 Release 发出后再手动部署一次。命令顺序见「站点发版清单」。
3. 打与 `version` 同名的 tag，并发布 GitHub Release。更新日志页 `site/src/lib/releases.ts` 在构建时读 `https://api.github.com/repos/linhongcun/video-studio/releases`。
4. Release 发出后在 `main` 上再跑一次部署。这一次构建才能读到刚发出的 Release，`/changelog/` 才会带上新版本。工作流注释里的命令是：

```sh
gh workflow run deploy.yml --ref main
```

本仓没有包一层的 `release.sh`。tag 和 Release 用「站点发版清单」里的命令。说明文字写清改了哪一期。

## 站点发版清单

下面每条命令都在仓库或本机工具里，发布前已核对：`sha256sum`、`cut`、`site/package.json` 的 `npm ci` 与 `npm run build`、`git tag`、`git push`，以及 `gh release create`、`gh workflow run`、`gh run list`、`gh run cancel`、`gh run watch`。工作流文件是 `.github/workflows/deploy.yml`，含 `workflow_dispatch`。

1. 把制作目录 `episodes-codex/<slug>/` 中检查通过并冻结的 `video.mp4`、`cover-16x9.jpg`、`cover-4x3.jpg`、`cover-3x4.jpg` 及站点所需数据复制到 `episodes/<slug>/`。配音 WAV、制作 PNG 和完整制作工程保留在制作目录；站点所需的 meta、article、script、storyboard 等数据仍随发布同步，幕后说明链接需要的脚本和研究资料继续保留。若用户已观看批准，使用同一份批准文件，不重新生成未经观看的替代品；按持续授权自主发布时使用完成检查的冻结文件。站点只读 `episodes/<slug>/`。保存各文件完整 SHA-256，并在部署后核对完整值；以下 sha8 只便于展示：

```sh
sha256sum <file> | cut -c1-8
```

2. 改 `site/package.json` 的 `version`：只改成片或文章升修订号；新一期或站点功能升次版本号。改该期 `meta.json`：`draft` 设为 `false`，写上 `publishedAt`；重发或只改站点时更新 `updatedAt`。将 `sourcePath` 明确设为对应当前制作目录（如 `episodes-codex/db-replication/remotion`），让页面“源码”指向当前工程。旧制作目录已清理，不依赖缺省旧路径。本地先构建通过：

```sh
cd site
npm ci
npm run build
```

3. 保留各机器已有的主作者身份，不从 `git log` 抄邮箱。按 [AGENTS.md 的提交署名约定](../AGENTS.md#提交署名)，本机 Codex 制作的变更加 `Co-authored-by: Codex <codex@openai.com>`；Cursor 制作的变更加 `Co-authored-by: Cursor Agent <cursoragent@cursor.com>`。只添加实际参与工具的署名，不强制另一工具的独立提交添加自己的署名。Squash 合并保留本次变更实际贡献者已有的全部联合署名，不相互覆盖，不修改机器的全局 Git 配置。

开 PR，合并进 `main`。合并带来的那次 Pages 部署读不到这次 Release。随后打附注 tag 并发布。v0.44.0 和 v0.45.0 都是附注 tag，不要用轻量 tag：

```sh
git tag -a vX.Y.Z -m "vX.Y.Z: 第 N 至 M 期……"
git push origin vX.Y.Z
gh release create vX.Y.Z --verify-tag --title "vX.Y.Z: 第 N 至 M 期……" --notes "……"
```

先推送 tag，再 `gh release create`。tag 不在远端时，这条命令会从默认分支另打一个 tag。`--verify-tag` 会在 tag 缺失时停住。标题和正文写明「第 N 至 M 期」。只改站点、不重发平台时，同时写上「只上站点，不重发平台」。

4. Release 发出后再部署一次，`/changelog/` 才会收入新版本：

```sh
gh workflow run deploy.yml --ref main
```

`deploy.yml` 的并发组不会取消仍在排队的那次运行。若 Pages 停在排队（v0.45.0 曾等了 37 分钟），查出运行、取消、再触发，并等到结束：

```sh
gh run list --workflow deploy.yml
gh run cancel <id>
gh workflow run deploy.yml --ref main
gh run watch <id>
```

5. 打开 https://linhongcun.github.io/video-studio/ 。成片在 `/video-studio/episodes/<slug>/video.mp4`（`meta.json` 的 `video`）。核验实际线上文件的完整 SHA-256 与发布清单相同；有用户批准版时也必须与批准文件一致，不能只比较 sha8。`site/scripts/copy-assets.mjs` 只把 `video` 和 `poster` 拷进站点；线上海报用 `meta.poster` 的文件名（degradation 是 `cover-16x9.jpg`）。打开该期页面确认海报能显示。`cover-4x3.jpg` 和 `cover-3x4.jpg` 留在仓库里，用同一条 sha8 核对，它们不进 Pages。打开 `/changelog/`，确认新版本已经列出。

6. 视频制作、合并上线和线上核验完成后，将对应制作或重制 issue 关闭，状态理由为 `completed`；用户已持续授权这一步，无需另问。关闭时保留事项的真实执行情况，不把尚未执行的平台发布勾成完成，也不因旧选题模板含平台事项而遗漏制作 issue 的收尾。

7. 仅在另获平台发布授权并完成对应发布后，运营把 B站和抖音的链接私信给 Knoll（站点维护者）和 Nolan。`platforms` 只写这两个真实 URL。视频号没有网页链接，不写。不要新写 `kuaishou`。链接不发到群。

## 三个平台

现行渠道：抖音（按 [RULES.md](RULES.md) 的 STATUS 同步同一条成片到今日头条、懂车帝、番茄小说、红果短剧的可用项）、B站、微信视频号。默认不发快手，仅执行 STATUS 中逐次明确授权：此前 LC.11、LC.3、LC.704 的快手三条，以及趣味推理 P01（`horse-racing`）、P02（`bridge-torch`）各向快手、小红书、抖音投稿一次。本轮新增 LC.1（`two-sum`）、LC.70（`climbing-stairs`）、LC.206（`reverse-linked-list`）各向 B站、抖音、小红书、快手投稿一次，不含用户此前已放弃、仍受工具站点安全策略限制的微信视频号事项，不尝试访问或绕过限制，也不将其计为已发布平台。不扩展为未来全系列持续授权，逐平台查重，不重复已发布旧题；扫码登录、账号绑定或协议授权由用户操作，投稿后按实际页面核验发布或审核状态，不预记完成。不发 X。小红书由村长自己发，运营和 Codex 默认不发，STATUS 中逐次明确授权除外。

`meta.json` 的 `platforms` 只填真实 URL。站点实际渲染的键只有 `bilibili` 和 `douyin`（`site/src/lib/episodes.ts` 的 `PLATFORMS`）。不要新写 `kuaishou`。已上线各期里残留的 `kuaishou` URL 是历史链接，规范不再扩展。

抖音同步平台没有单独的键，在抖音侧同步，不另传一条。视频号没有网页链接，不写进 `meta.json`，也不写进 Release。不要为了显示视频号去改 `episodes.ts`。

`site/src/components/PlatformLinks.astro` 在没有真实平台链接时不显示，不以泛化搜索提示暗示本期已在平台发布。关于页不以泛化搜索提示暗示各期已在平台发布；平台入口以各期真实链接为准。

## 三平台实操

GitHub 站点已有持续发布授权，见 [RULES.md](RULES.md) 的 STATUS；该授权不扩展为三平台发布。在用户另行明确授权平台新发之前，不向三个平台上传成片，也不因站点返工把旧成片再传一遍。只改站点走「只上站点」。

LC.1、LC.70、LC.206重发及本次D01策略模式投稿的授权范围见STATUS；先执行下方版本闸门，再按各平台当前旧稿状态处理，不把旧稿消失直接判为平台发布失败。

### 平台发布前版本闸门

1. 开始投稿前检查工作区并保护已有改动，`git fetch origin --prune`，整合最新`origin/main`，重新读更新后的规范。记录检查时间、远端提交完整SHA和实际本地基线；“此前已拉过”不能代替本轮检查。
2. 从最新`episodes/<slug>/`发布目录核对成片、封面、脚本与章节，并与当前提交及制作验收记录逐项对应。不能仅凭文件名、修改时间、旧材料JSON或ignored制作缓存认定是最新版；制作目录与发布目录不一致时先查清，不上传。
3. 为本批建立独立上传目录，复制核验过的媒体并生成清单：题号/slug、基线提交、来源路径、完整SHA-256、时长和封面版本。副本文件名包含slug和版本标识，冻结后不覆盖；在文件选择器中只选清单中的确定路径，上传前再次核对完整SHA-256。标题、简介与章节也从同版脚本生成。
4. 每个平台批次开始前，以及中断恢复后，再次fetch并比较上游变化与本批媒体、脚本、章节和封面输入。有关变化时先整合、重做核对及上传副本，再继续；无关变化则记录差异与无交集依据。批次耗时较长时在下一条投稿前复核，不能只做最开始一次同步。
5. 逐平台查重，区分旧版、同版、审核中和已删除的稿件；用户已明确本轮有手动删改，记录消失不能直接归因为审核失败或平台故障。存在同版投稿时不另建重复稿，版本与旧稿状态不清时先查清。
6. 提交后分别保存成功回执和刷新后的管理列表状态，能取得时保留真实播放链接。页面曾提示成功但刷新后不可见，记录两次实际观察及已知人工操作，不宣称已发布，也不未经核实反复补传；抖音同步开关与各应用实际结果继续分别记录。

### 准确发布与减少重复操作

- 上传前一次备齐同版标题、简介、话题、章节和各比例封面；材料核验与文档整理可并行，浏览器及原生文件选择器由一个操作者串行控制。复用已观察到的语义控件和步骤，每个关键状态仍须确认，不依赖旧元素编号或固定坐标。
- 原生文件选择器只选清单中的带版本名文件。macOS「前往文件夹」用`setValue`填写精确路径，观察路径及候选更新后再回车；在打开面板核对目标文件URL和文件名，再点「打开」。`/tmp`可能显示为`/private/tmp`；不因AX属性顺序、标点或路径别名误判文件不存在，也不能接受仍选中的旧文件。
- 富文本首填整段正文，追加前定位到全文末尾；macOS用`Meta+ArrowDown`，单独`End`可能只到当前行尾。需要纠正时先确认已清空，再填一次，避免已有内容被追加。话题整段粘贴，等候选显示完整词后逐个选中，并核对实际标签；不边逐字输入边抢点候选。
- 上传完成、封面对话框关闭、声明菜单展开等状态变化确认后再执行下一步。只合并确定且互不抢焦点的操作，使用控件或对话框状态等待，不以固定长延时或反复点击代替确认。AI声明放在上传和封面已稳定后复核；提交回执与刷新后的发布状态分开记录。实操失误见L043，已验证复用范围见S020。

下列是 2026-10-22 核对过的规则。界面文案以后若改名，仍按这些限制做，不要另编一套点击路径。

三个平台和站点一起发，只在村长本人说出「可以，上线三个平台和站点」这类原话之后。发完，运营把 B站和抖音链接私信给 Knoll（站点维护者）和 Nolan。群里只 @ Nolan，说明发布已完成，不贴链接。

标识：抖音用「内容由AI生成」。B站和视频号用「含AI生成内容」。

抖音同步：2026-10-25 用户持续授权，在已获授权的抖音投稿中尽量开启今日头条、懂车帝、番茄小说、红果短剧的可用同步项，并开启「记住我的选择」。每次投稿先核验这些目标的实际可用性与开关状态；遇到新增登录、账号绑定或协议授权，交给用户操作。发布后逐一核验各平台结果，区分已开启同步、审核中、发布成功和失败，未验证的结果不得写成已发布。本授权仅覆盖抖音侧同步，不包含向这些平台独立投稿或其他平台新发；不为补开同步而重复上传、重发旧作品。

封面文件：B站当前双比例界面分别用 `cover-4x3.jpg` 和 `cover-16x9.jpg`；旧单上传位界面按下文处理。抖音和视频号用 `cover-4x3.jpg` 与 `cover-3x4.jpg`。文件怎么产出见 [render.md](render.md)。抖音主页格子按中心裁切 4:3。给抖音的这张 4:3 要把竖版 `cover-3x4.jpg` 整张居中放到 4:3 画布上，裁完仍能看见完整标题。

B站在 `member.bilibili.com` 投稿。分区只选最上级「科技数码」，不选它下面的子分区。话题填「程序员」；这是话题，不要再当成自定义标签填一次。去掉自动加上的无关标签，例如「生活记录」。章节名不超过 10 个汉字。章节在编辑页的章节管理里填，2026-10-22 的入口是「更多设置 → 章节管理」。保存后若要求重新提交，在原来那条投稿上提交，不要新开一条。讨论区置顶评论只在 B站做，并且在村长批准之后。抖音和视频号不置顶。

B站2026-10-25实际界面有「首页推荐封面（4:3）」和「个人空间封面（16:9）」两个比例槽：关闭「双比例同步改动」，分别上传同版`cover-4x3.jpg`和`cover-16x9.jpg`，逐一目视核对标题完整后完成。若当前界面确实只有单上传位，再上传`cover-16x9.jpg`并核对4:3裁切安全区；不把旧单槽说明套用到双槽界面。比例安全区继续遵守[RULES.md](RULES.md)。

视频号在视频号助手上传。位置保持默认，发布后显示为华盛顿 / 美国，不要改。同一条只传一次，避免重复稿。已发布作品改封面走「修改描述和封面」，每条只能改一次；之后约 30 分钟审核，成片上会显示「作者修改过视频信息」。不要为了改封面再传一遍。

抖音已发布的封面可以改，每条最多 5 次。

## 只上站点

页面或演示页改了、平台成片不重发时：升版本、PR、Release，正文写明「只上站点，不重发平台」。v0.45.0 即此例（第 9 至 14 期深色页身）。`platforms` 保持原链接，不把新站内地址当作平台链接。

用户交办或已确定选题的内容做好并检查后，按持续授权走本节自主发布；收到反馈后修正、重新检查并发新版。PR 与 Release 写清本次实际涉及的期数和变更，平台历史链接保持原样。
