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

版本在 `site/package.json` 的 `version`，三段式。只改成片或文章升修订号；新一期或站点功能升次版本号。第21期常见实现独立短片与旧合集归档本次版本为 v0.47.0；EP.01–14 Codex重制与章节首帧定位版本为 v0.48.0；EP.21四片的全局流程与缩放导航修订为v0.50.2，保留协作主干v0.49.0算法系列；实际版本以该文件及 Release 为准。

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

1. 把制作目录 `episodes-codex/<slug>/` 中检查通过并冻结的 `video.mp4`、`cover-16x9.jpg`、`cover-4x3.jpg`、`cover-3x4.jpg` 及站点所需数据复制到 `episodes/<slug>/`。若用户已观看批准，使用同一份批准文件，不重新生成未经观看的替代品；按持续授权自主发布时使用完成检查的冻结文件。站点只读 `episodes/<slug>/`。保存各文件完整 SHA-256，并在部署后核对完整值；以下 sha8 只便于展示：

```sh
sha256sum <file> | cut -c1-8
```

2. 改 `site/package.json` 的 `version`：只改成片或文章升修订号；新一期或站点功能升次版本号。改该期 `meta.json`：`draft` 设为 `false`，写上 `publishedAt`；重发或只改站点时更新 `updatedAt`。制作入口迁到 `episodes-codex/` 时，将 `sourcePath` 设为对应仓库相对目录（如 `episodes-codex/db-replication/remotion`），让页面“源码”指向当前工程；未设置时兼容原来的 `episodes/<slug>/remotion`。本地先构建通过：

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

现行渠道：抖音（打开同步到今日头条，同一条成片）、B站、微信视频号。不发快手，不发 X。小红书由村长自己发，运营和 Codex 不发。

`meta.json` 的 `platforms` 只填真实 URL。站点实际渲染的键只有 `bilibili` 和 `douyin`（`site/src/lib/episodes.ts` 的 `PLATFORMS`）。不要新写 `kuaishou`。已上线各期里残留的 `kuaishou` URL 是历史链接，规范不再扩展。

头条没有单独的键，在抖音侧同步，不另传一条。视频号没有网页链接，不写进 `meta.json`，也不写进 Release。不要为了显示视频号去改 `episodes.ts`。

`site/src/components/PlatformLinks.astro` 在没有真实平台链接时不显示，不以泛化搜索提示暗示本期已在平台发布。`site/src/pages/about.astro` 仍写着「B站、抖音、快手」，那是历史文案，发布时不要照着它去发快手。

## 三平台实操

GitHub 站点已有持续发布授权，见 [RULES.md](RULES.md) 的 STATUS；该授权不扩展为三平台发布。在用户另行明确授权平台新发之前，不向三个平台上传成片，也不因站点返工把旧成片再传一遍。只改站点走「只上站点」。

下列是 2026-10-22 核对过的规则。界面文案以后若改名，仍按这些限制做，不要另编一套点击路径。

三个平台和站点一起发，只在村长本人说出「可以，上线三个平台和站点」这类原话之后。发完，运营把 B站和抖音链接私信给 Knoll（站点维护者）和 Nolan。群里只 @ Nolan，说明发布已完成，不贴链接。

标识：抖音用「内容由AI生成」。B站和视频号用「含AI生成内容」。抖音打开同步到今日头条。

封面文件：B站用 `cover-16x9.jpg`。抖音和视频号用 `cover-4x3.jpg` 与 `cover-3x4.jpg`。文件怎么产出见 [render.md](render.md)。抖音主页格子按中心裁切 4:3。给抖音的这张 4:3 要把竖版 `cover-3x4.jpg` 整张居中放到 4:3 画布上，裁完仍能看见完整标题。

B站在 `member.bilibili.com` 投稿。分区只选最上级「科技数码」，不选它下面的子分区。话题填「程序员」；这是话题，不要再当成自定义标签填一次。去掉自动加上的无关标签，例如「生活记录」。章节名不超过 10 个汉字。章节在编辑页的章节管理里填，2026-10-22 的入口是「更多设置 → 章节管理」。保存后若要求重新提交，在原来那条投稿上提交，不要新开一条。讨论区置顶评论只在 B站做，并且在村长批准之后。抖音和视频号不置顶。

B站改封面只有封面制作里的一个上传位，4:3 由这一张图裁出。上传 `cover-16x9.jpg`。标题要落在 [RULES.md](RULES.md) 的 4:3 安全区里，裁切后仍然完整。

视频号在视频号助手上传。位置保持默认，发布后显示为华盛顿 / 美国，不要改。同一条只传一次，避免重复稿。已发布作品改封面走「修改描述和封面」，每条只能改一次；之后约 30 分钟审核，成片上会显示「作者修改过视频信息」。不要为了改封面再传一遍。

抖音已发布的封面可以改，每条最多 5 次。

## 只上站点

页面或演示页改了、平台成片不重发时：升版本、PR、Release，正文写明「只上站点，不重发平台」。v0.45.0 即此例（第 9 至 14 期深色页身）。`platforms` 保持原链接，不把新站内地址当作平台链接。

用户交办或已确定选题的内容做好并检查后，按持续授权走本节自主发布；收到反馈后修正、重新检查并发新版。PR 与 Release 写清本次实际涉及的期数和变更，平台历史链接保持原样。
