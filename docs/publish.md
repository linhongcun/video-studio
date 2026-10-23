# 发布

村长批准最终上线之后才做这一节。平台和暂停状态以 [RULES.md](RULES.md) 为准。链接写在 `meta.json` 或 Release 说明里，不发到群。

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
2. 开 PR 合并进 `main`。Pages 随推送部署。
3. 打与 `version` 同名的 tag，并发布 GitHub Release。更新日志页 `site/src/lib/releases.ts` 读 `https://api.github.com/repos/linhongcun/video-studio/releases`。
4. Release 发出后在 `main` 上再跑一次部署，让 `/changelog/` 带上新版本。工作流注释里的命令是：

```sh
gh workflow run deploy.yml --ref main
```

本仓没有包一层的 `release.sh`。tag 和 Release 用仓库已有的 GitHub 发布方式，说明文字写清改了哪一期。

## 三个平台

现行渠道：抖音（头条同步同一条成片）、B站、微信视频号。不发快手，不发 X。

`meta.json` 的 `platforms` 只填真实 URL。站点实际渲染的键只有 `bilibili` 和 `douyin`（`site/src/lib/episodes.ts` 的 `PLATFORMS`）。不要新写 `kuaishou`。已上线各期里残留的 `kuaishou` URL 是历史链接，规范不再扩展。

头条没有单独的键，和抖音同步。微信视频号也不在 `PLATFORMS` 里。这两处链接写在 Release 说明，不进群。站点要显示微信视频号需要改 `episodes.ts`，那不是本手册要做的代码改动。

`site/src/pages/about.astro` 和 `site/src/components/PlatformLinks.astro` 的空状态仍写着「B站、抖音、快手」。那是旧文案。发布时不要照着它去发快手。

## 只上站点

页面或演示页改了、平台成片不重发时：升版本、PR、Release，正文写明「只上站点，不重发平台」。v0.45.0 即此例（第 9 至 14 期深色页身）。`platforms` 保持原链接，不把新站内地址当作平台链接。

暂停期间不做新期发布。已上线内容的站点返工仍走本节，并在 PR 里写明没有新开一期。
