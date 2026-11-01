# MQ04 站点接入与线上核验

本文件是执行说明，当前不表示本期成片、QA或发布已经通过。根代理负责最终安装、版本、GitHub和issue操作；本目录辅助入口只处理本期。

站点从episodes/*/meta.json自动收录，message-queue已是独立系列；本期身份为EP44 / Kafka MQ04 / kafka-send-confirmation，sourcePath为episodes-codex/kafka-send-confirmation/remotion。现有三课和本期按实际发布meta排序；无需改共享系列或导航代码。旧/learn/为/library/兼容入口。

先完成最终媒体、三比例封面、资料附录与图文截图检查，再本地安装用于构建预览。实际播放器/文章交互在本地接入后检查，通过后才远程发布。真实创建时间、计划首次公开时间与Release由根代理根据记录和最新上游填写：

```sh
python3 episodes-codex/kafka-send-confirmation/publish.py \
  --created-at '<实际含时区ISO时间>' \
  --published-at '<本次首次公开含时区ISO时间>' \
  --release '<实际首次Release tag>'
```

安装器检查冻结清单、成片完整SHA和附录媒体回执，要求真实文章图片存在；只复制当前产物并写publication-files.json，不渲染、不批准质量、不改站点版本或远程发布。只将完全匹配本期slug/EP/标题/series/episodePart/sourcePath/draft的7键封面临时记录识别为暂存身份；已有真实创建/首发字段不允许被重置。最终meta结构见publication-meta.schema.json，不把schema当作实际发布数据。

本地检查：

```sh
npm --prefix site run check:references
npm --prefix site run check:articles
npm --prefix site run build
python3 episodes-codex/kafka-send-confirmation/qa/site-independent.py
```

浏览器入口从实际元数据、分镜、参考资料和Figure生成检查范围，核对系列完整课程集合、实际播放/暂停、全部章节/图位回看、原文交互、准确PTS、附录首中末与Fullscreen API，并保留截图。实际查看原图、等待/控件状态、亮暗主题与手机模拟可读性后再记视觉复核；程序通过不自动生成视觉阅读结论。原生字幕默认值须与成片实际烧录字幕事实一致，保留观众选择原生轨的能力。

完成Release后的Pages部署并核对目标SHA后：

```sh
python3 episodes-codex/kafka-send-confirmation/online_verify.py --release '<实际Release tag>'
python3 episodes-codex/kafka-send-confirmation/qa/site-independent.py \
  --base https://linhongcun.github.io/video-studio \
  --out episodes-codex/kafka-send-confirmation/qa/site-online-native
```

online_verify执行普通canonical HTTPS GET，保留继承代理与CA验证，不使用Range、改请求头、cache-busting或静默重试。比较完整MP4、16:9海报、VTT与文章图片的SHA，核对页面章节、当前源码身份、系列实际篇数/完整课程集合、内容库/首页、旧learn入口及真实Release更新日志。4:3/3:4封面不在当前Pages复制范围，不请求不存在的线上文件。

浏览器先用原生HTTPS路径，不忽略TLS错误；若另行决定使用显式verified-http-route，报告须如实区分经环境CA验证的HTTP回填与原生Chromium传输，不能将回填写成原生直连。HTTP身份、程序交互、截图实读和真机能力分别记录。全部必要线上核验完成后，根代理以completed关闭#312、更新#308。本轮仅GitHub与本站，无外部平台新发。
