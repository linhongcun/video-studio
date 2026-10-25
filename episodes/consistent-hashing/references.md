# EA01片尾参考资料追加输入

资料核验：2026-10-25（北京时间）。本文件与`references.json`为本次新增的参考资料输入；既有正文、文章、分镜、配音和冻结文件均未修改。

正文为5881帧、30fps，约3分16.033秒。本次按新增片尾参考资料规则，计划在正文之后追加一页静态参考卡，默认停留5秒（150帧），用于暂停阅读；两条来源在每页最多三条的布局内。预期总长6031帧，约3分21.033秒。此处记录追加计划与输入，不预写实际拼接、AAC保持或最终编码核验已经完成；实际结果由根任务调用共享追加工具后记录。

## 原文与视频论点映射

| 来源 | 实际支持的正文论点 | 片中位置与读取证据 |
|---|---|---|
| R1 · [NGINX：Module ngx_http_upstream_module，hash指令](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#hash) | 普通哈希在成员变化后可能重映射大量键；consistent使用Ketama减少重映射，帮助保留缓存命中。 | 01、04–06、11、14镜；`research.md`的R1已记录本轮实际读取与三条短引。页面未标该节更新日期，参考卡写“持续维护文档”和核验日，不编造年份。 |
| R2 · [Apache Cassandra：Dynamo，Token Ring与vnodes](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html) | 固定环与顺时针定位；多个token对应同一物理节点；多个分散小区间及维护代价。 | 02–04、06–14镜；`research.md`的R2已记录本轮实际读取正文与页面5.0标识。参考卡标“5.0文档”，不把访问日期当发布时间。 |

片尾卡只列支撑视频主线的这两条。R3 Redis Cluster固定槽与迁移只用于配套文章的产品边界，未列入视频参考卡；文章与研究笔记原有链接保持。

0..99、A20/B50/C85、D70、十键8/10与2/10，以及另一套虚拟节点位置均为自设教学示例。两份官方文档支持机制，不提供本片这些数字，也不证明本例的请求负载或迁移性能。模型独立计算、视觉审读和来源核验各有各的证据，不相互替代。

## 追加范围

`references.json`按共享`append_references.py`的schemaVersion 1保存：两条来源均含完整标题、机构、适用版本、HTTPS URL、具体支持论点、原文章节及已核验记录，另给适合片尾显示的短标题与短论点。正文约3分16秒加参考5秒，不新增口播；原5881帧正文和原AAC的保持由追加工具实际验证，本任务不修改既有冻结清单去追认新媒体。

## 2026-10-25：原题名与逐字引用（当前显示）

此前记录作为历史保留。旧版为画面改拟短标题或短论点的做法已撤下；当前`presentation`为`original-title-quote`，显示原题名、完整逐字原句与独立定位。

### R1 · Module ngx_http_upstream_module

- 机构：NGINX
- 版本：持续维护文档 · 核验2026-10-25
- 正式链接：<https://nginx.org/en/docs/http/ngx_http_upstream_module.html#hash>
- 实读固定正文：<https://github.com/nginx/nginx.org/blob/34f63eb329ff52623cec453cd8f7539f9a5f8606/xml/en/docs/http/ngx_http_upstream_module.xml>
- 完整正文SHA-256：`0955576db8c2cafa8385214f0862e3751d6518efca3ccdcfc5e59557f2f0eaca`
- 定位：hash directive, consistent parameter paragraph
- 核验记录：[sources-extra.json](../../docs/reference-endcards/original-titles/sources-extra.json)

> The method ensures that only a few keys will be remapped to different servers when a server is added to or removed from the group.

### R2 · Dynamo

- 机构：Apache Cassandra
- 版本：5.0文档 · 核验2026-10-25
- 正式链接：<https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html>
- 实读固定正文：<https://github.com/apache/cassandra/blob/76550e931481e965ae3283d8cf4a59c320d74c55/doc/modules/cassandra/pages/architecture/dynamo.adoc>
- 完整正文SHA-256：`cf06d9156e211e81bf2530c33806d1ffc6a8ac1440c28669750f65d4e1760bb4`
- 定位：Multiple Tokens per Physical Node (vnodes), paragraph 2
- 核验记录：[sources-extra.json](../../docs/reference-endcards/original-titles/sources-extra.json)

> Virtual nodes solve the problem by assigning multiple tokens in the token ring to each physical node.

R2原题是Cassandra官方文档《Dynamo》，并非Amazon原论文；此身份与组织、URL及实际正文保持一致。
