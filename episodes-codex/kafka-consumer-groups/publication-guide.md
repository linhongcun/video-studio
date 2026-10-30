# MQ02 站点接入与线上核验

实际状态以本期 QA、render-result 和发布回执为准。本文件是执行说明，不表示成片或发布已通过检查。

当前基线 `68d2d2dbea525f08fce8a10441b77bec243d9ca7` 的站点从 `episodes/*/meta.json` 自动收录。`message-queue` 已是独立系列；EP.10/MQ01 与本期 EP.42/MQ02 按现有期号排序，无需修改共享系列或导航代码。`/learn/` 当前跳转至 `/library/`，线上核验分别检查这个兼容入口与内容库中的真实课程链接。

确认最终成片、三比例封面、资料附录和图文截图检查完成后，从仓根执行本地安装以构建预览；实际播放器和文章交互检查在本地接入后完成，通过后才能远程发布。时间参数使用有依据的实际创建时间与本次计划首次公开时间，版本使用发布前最新主干确定的 tag，不从示例推定：

```sh
python3 episodes-codex/kafka-consumer-groups/publish.py \
  --created-at '<实际含时区ISO时间>' \
  --published-at '<本次首次公开含时区ISO时间>' \
  --release '<实际首次Release tag>'
```

安装器只复制本期真实生产文件、核对完整 SHA 并生成 `publication-files.json`；不会渲染、批准质量、修改站点版本或远程发布。它先检查冻结清单、成片与附录回执一致，媒体检查确实通过，要求实际文章图片存在。若已有发布元数据，不允许重置创建或首发身份。正式编码后的制作稿若要改动，按文章派生规则保留冻结稿，不通过重写清单追认旧媒体。

接入后运行 `npm --prefix site run check:references`、`npm --prefix site run check:articles` 与完整 build，并进行真实页面、引用、回看、原图、暂停/全屏检查。新一期按仓库规则升次版本，发布者在最新主干上确认版本和未占用 tag 后执行 PR、合并、附注 tag、Release，再触发 Release 后 Pages 部署。提交按实际贡献保留 Codex trailer；本次仅 GitHub 与本站，不向外部视频平台投稿。

Release 后 Pages 部署成功后，从仓根运行：

```sh
python3 episodes-codex/kafka-consumer-groups/online_verify.py --release '<实际Release tag>'
```

线上脚本执行普通 canonical HTTPS GET，保留继承的代理与 CA 验证，不使用 Range、改请求头、cache-busting 或静默重试。检查完整 MP4、16:9海报、构建 VTT 及文章图片的 SHA，页面章节/当前源码身份、系列/内容库/首页课程入口、旧 `/learn/` 兼容入口和真实 Release 更新日志链接。4:3与3:4封面不在现行 Pages 复制范围，不对不存在的线上文件发请求。HTTP 内容身份与浏览器交互分别记录；全部必要线上核验通过后，再以 completed 关闭 #310 并更新总览 #308。
