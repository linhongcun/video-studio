# EP40 · 工程算法03：Redis 跳表

用一条查找55并接入55的因果链讲清跳表。底层10..80，上层仅40/70；只有一个活动游标，不能前进时在当前节点下降。本例采用固定合法两层，展示前向链接，不是Redis随机回放或默认8成员ZSET内存实测。

正式输入为script/plan/model、真实voice与storyboard、源码/封面及title-author资料（仅原题与作者或机构，每页最多4项、默认5秒）；模型由build_model.py确定性生成，每份状态深拷贝，不能用插入后指针污染before。新55各层先设后继再改上一节点，两层顺序与模型一致。

使用现行共享voice/prep、gen、build、assemble_sentence_episode、place_v2及唯一onset_rule。真实声学/来源检查不是逐字ASR或全片人工听辨。各阶段结果以对应QA记录为准，文件存在不表示检查已完成。

全部来源、时序、动态和封面预检通过并停写后，在仓根运行本期freeze.py；在remotion执行默认npm run render，自动生成正文混音与原题、机构参考资料列表，最终交付本期video.mp4。freeze.py --verify只读核对，编码后不能改清单追认未采用的输入。

sync_site.py准备站点白名单；核实际成片后以完整SHA和显式release发布复制，verify_published.py在Release后的Pages成功后做普通canonical GET全文件身份检查。网页与实际浏览器播放/暂停/章节另验。GitHub主干、Release、Pages按持续授权交付；没有外部平台新发。

追踪：[issue #301](https://github.com/linhongcun/video-studio/issues/301)、[PR #344](https://github.com/linhongcun/video-studio/pull/344)。本期创建时间为首次建立meta记录的北京时间，首次公开另写publishedAt；EA07不是发布第七期。

## 交付结果

已由PR #344合并656b525f，首发[v0.72.0](https://github.com/linhongcun/video-studio/releases/tag/v0.72.0)，Release后Pages40299437706成功。[观看成片与图文](https://linhongcun.github.io/video-studio/episodes/redis-skiplist/)。

最终4632帧/154.4秒/7,062,438字节，正文4482帧、资料150帧；139项冻结。49实际编码图、声轨与90项本地浏览器检查通过，最终整合构建保持8个已审页面/运行产物字节；10项canonical完整GET与线上两视口实际播放、四章、20条字幕、4482帧精确暂停均通过。完整身份、时间、报告与能力范围见[最终QA](qa-final.md)和[发布记录](publication.json)。

本期没有用户新观看结论，不将技术通过写成学习效果或用户已认可。

制作issue #301已在上线核验后以completed关闭；总览#294已更新为3项完成、6项待安排。
