# EP39 布隆过滤器：单位置主线修订

公开课程保持`bloom-filter`、EP39、工程算法第二期。该目录是本次独立制作工程；旧`episodes-codex/bloom-filter`的v0.71.0冻结输入、配音和媒体保留原字节。站点发布副本仍为`episodes/bloom-filter`，元数据`sourcePath`指向本目录的`remotion`。

主线为8位、一个元素计算一个位置：A/B共享3，D在7读0可排除，C在3读1却从未加入。错误清位说明共享边界；片尾仅用另建、完整重插A/B的双位置对照解释如何排除C的这次误判，不据此估算误判率或声称增加次数必定更好。

资料、脚本与模型先独立审查。所有旁白重新生成，使用共享冰糖TTS/整轨/起音工具；句包络不是逐字ASR。实际时序、动态、冻结、编码与发布状态以本目录各阶段QA为准，文件存在不表示检查已完成。

仓库根路径记为`ROOT`，本目录记为`D`。依次执行共享`voice/prep.py`、`voice/gen.py`、`voice/build.py`、`assemble_sentence_episode.py`、`place_v2.py`和`label_onset_strict.py`；在实际时序上完成动态与版式预检后，运行本期`freeze.py`，然后在`remotion`运行默认`npm run render`。默认入口包含正文混音和原始题名参考资料附录，最终交付`D/video.mp4`。

`freeze.py --verify`只读核对本期冻结；旧版的验证入口和结果仍适用于旧版，不能用新清单追认旧编码。`sync_site.py`同步通过检查的最终媒体，保留创建、首发时间和首发版本，仅更新内容修改时间；`verify_published.py`在Release后的Pages成功后核验普通线上GET与完整SHA。外部平台未获本轮新发授权。

修订追踪：[issue #342](https://github.com/linhongcun/video-studio/issues/342)、[PR #343](https://github.com/linhongcun/video-studio/pull/343)。反馈以原因和改进的总结记录，不摘录对话；检查通过不代表已获新版观看认可。
