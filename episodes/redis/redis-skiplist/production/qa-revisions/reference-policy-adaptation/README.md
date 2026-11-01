# EP40 · 工程算法03：Redis 跳表

用一条查找55并接入55的因果链讲清跳表。底层10..80，上层仅40/70；只有一个活动游标，不能前进时在当前节点下降。本例采用固定合法两层，展示前向链接，不是Redis随机回放或默认8成员ZSET内存实测。

正式输入为script/plan/model、真实voice与storyboard、源码/封面及original-title-quote资料；模型由build_model.py确定性生成，每份状态深拷贝，不能用插入后指针污染before。新55各层先设后继再改上一节点，两层顺序与模型一致。

使用现行共享voice/prep、gen、build、assemble_sentence_episode、place_v2及唯一onset_rule。真实声学/来源检查不是逐字ASR或全片人工听辨。各阶段结果以对应QA记录为准，文件存在不表示检查已完成。

全部来源、时序、动态和封面预检通过并停写后，在仓根运行本期freeze.py；在remotion执行默认npm run render，自动生成正文混音与原始题名参考资料附录，最终交付本期video.mp4。freeze.py --verify只读核对，编码后不能改清单追认未采用的输入。

sync_site.py准备站点白名单；核实际成片后以完整SHA和显式release发布复制，verify_published.py在Release后的Pages成功后做普通canonical GET全文件身份检查。网页与实际浏览器播放/暂停/章节另验。GitHub主干、Release、Pages按持续授权交付；没有外部平台新发。

追踪：[issue #301](https://github.com/linhongcun/video-studio/issues/301)、[PR #344](https://github.com/linhongcun/video-studio/pull/344)。本期创建时间为首次建立meta记录的北京时间，首次公开另写publishedAt；EA07不是发布第七期。
