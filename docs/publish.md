# 发布

村长本人说出「可以，上线三个平台和站点」之后，才发三个平台。代理、质检或导演在对话里的同意不算。名单和暂停以 [RULES.md](RULES.md) 的 STATUS 与「发布」为准。EP.14 之后暂停：不开新期，不新发平台。只改站点走「只上站点」和「站点发版清单」。

链接不发到群。`meta.json` 的 `platforms` 只填真实的 `bilibili` 和 `douyin`。视频号没有网页链接，不写。

## 站点内容

一期在站点上可见，需要 `episodes/<slug>/meta.json` 的 `draft` 为 `false`，以及同目录的 `article.mdx`、`video.mp4`、海报。列表和页面由 `site/src/lib/episodes.ts` 读取 `episodes/*/meta.json`。`series` 必须是 `site/src/content/series.json` 里的键：`request`、`cache`、`peak`、`database`、`distributed`。

`draft: true` 的期默认不进构建。本地要看草稿：

```sh
cd site
SHOW_DRAFTS=1 npm run build
```

现行重制的制作目录按 [../AGENTS.md](../AGENTS.md) 是 `episodes-codex/`。本仓还没有该目录下的工程。已经上线的文件在 `episodes/<slug>/`。新期恢复制作后，进站点的仍然是 `episodes/<slug>/` 这份，slug 与 `meta.json` 的 `slug` 一致。degradation 的分镜内部 slug `degradation-v1` 不要当成站点路径。

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

版本在 `site/package.json` 的 `version`，三段式。只改成片或文章升修订号；新一期或站点功能升次版本号。当前已发布到 v0.45.0。

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

1. 把已批准的 `video.mp4`、`cover-16x9.jpg`、`cover-4x3.jpg`、`cover-3x4.jpg` 从备份拷进 `episodes/<slug>/`。该期若有制作目录 `episodes-codex/<slug>/`，同样拷入。本仓的 `episodes-codex/` 目前只有 `_template/`，没有期工程；站点只读 `episodes/<slug>/`。每个文件的前 8 位要和批准时的 sha8 一致：

```sh
sha256sum <file> | cut -c1-8
```

2. 改 `site/package.json` 的 `version`：只改成片或文章升修订号；新一期或站点功能升次版本号。改该期 `meta.json`：`draft` 设为 `false`，写上 `publishedAt`；重发或只改站点时更新 `updatedAt`。本地先构建通过：

```sh
cd site
npm ci
npm run build
```

3. 提交的作者名沿用 `git log` 里已有提交的作者。不要从 `git log` 抄邮箱。按 [AGENTS.md 的提交署名约定](../AGENTS.md#提交署名)，本机 Codex 提交在信息末尾加 `Co-authored-by: Codex <codex@openai.com>`；Squash 合并的新提交也保留该行。不要把作者或 `Co-authored-by` 写成 Cursor Agent。

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

5. 打开 https://linhongcun.github.io/video-studio/ 。成片在 `/video-studio/episodes/<slug>/video.mp4`（`meta.json` 的 `video`）。下载后用上面的 `sha256sum | cut -c1-8` 对上批准的 sha8。`site/scripts/copy-assets.mjs` 只把 `video` 和 `poster` 拷进站点；线上海报用 `meta.poster` 的文件名（degradation 是 `cover-16x9.jpg`）。打开该期页面确认海报能显示。`cover-4x3.jpg` 和 `cover-3x4.jpg` 留在仓库里，用同一条 sha8 核对，它们不进 Pages。打开 `/changelog/`，确认新版本已经列出。

6. 运营把 B站和抖音的链接私信给 Knoll（站点维护者）和 Nolan。`platforms` 只写这两个真实 URL。视频号没有网页链接，不写。不要新写 `kuaishou`。链接不发到群。

## 三个平台

现行渠道：抖音（打开同步到今日头条，同一条成片）、B站、微信视频号。不发快手，不发 X。小红书由村长自己发，运营和 Codex 不发。

`meta.json` 的 `platforms` 只填真实 URL。站点实际渲染的键只有 `bilibili` 和 `douyin`（`site/src/lib/episodes.ts` 的 `PLATFORMS`）。不要新写 `kuaishou`。已上线各期里残留的 `kuaishou` URL 是历史链接，规范不再扩展。

头条没有单独的键，在抖音侧同步，不另传一条。视频号没有网页链接，不写进 `meta.json`，也不写进 Release。不要为了显示视频号去改 `episodes.ts`。

`site/src/pages/about.astro` 和 `site/src/components/PlatformLinks.astro` 的空状态仍写着「B站、抖音、快手」。那是旧文案。发布时不要照着它去发快手。

## 三平台实操

EP.14 之后系列暂停，见 [RULES.md](RULES.md) 的 STATUS。恢复制作、并且村长本人说出上线原话之前，不要向三个平台新发成片，也不要因为站点返工把旧成片再传一遍。v0.45.0 那种只改页身，走「只上站点」。

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

暂停期间不做新期发布。已上线内容的站点返工仍走本节，并在 PR 里写明没有新开一期。
