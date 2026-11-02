# Redis Sentinel / EP50 制作输入

《Redis Sentinel：主节点失联后，谁有资格决定换主？》，对应issue#296。开工基线01cd181caf24d4a8ce846c0eb8faeeab8f0054e2；本目录为本期独立production，publication同级。本文是编码前制作说明，正式冻结后不追加进度，交付、上线与能力范围另记批次归档。

从已知五哨兵、quorum2的同一部署出发，先确认故障，再给一个Sentinel执行授权，最后由它筛选与提升数据副本。少数可达分支保留2/2故障判断却只有2/3授权；独立对照重新回到投票前，三张同轮票才授权执行者。优先级零即使进度更高仍不晋升；收到R2角色改变的INFO报告后再重配。客户端问哨兵地址后直连Redis，哨兵不转发业务数据。异步复制窗口不承诺零丢失。

sources/保存本轮实际固定官方文档与Redis8.4.0/60ba86f3源码GET、SHA、许可和失败响应；research说明实读范围，references.json两项title-author。model.py/model.json提供41个有限教学阶段与388项检查，不冒充Redis进程执行或共识证明。examples/run_sentinel.py另有真实一主两副本五哨兵实验，端口16500–16507，覆盖已知五台时少数ODOWN无授权、三台存活后R2晋升和priority0的R1改跟新主、前后键读取/复制；原报告、配置和日志保留。即时配置传播尚未完全收敛，见examples/runtime-scope.md；没有复现断电或异步写入丢失。

共享prep真实解析13镜、611字、26句；选中a候选生成4439正文帧/147.9666667秒，48k单声道音轨SHA-256 `e1807fc3d702f828ee90baee1cf77eddae9ddc21ee3fc240597d35f8c9683ca3`，-16LUFS、内部true peak-2.2dBTP。无大于0.5秒句内静音，所有裁尾独立尾段0.33–0.53秒。voice/input-provenance.json、原始候选、请求文本、picks及共享检查保留，未声称逐字ASR或全片人工听辨。

同一Main读取真实分镜和有限模型，事件窗口绑定实计时镜头；不把按句包络分段称为内部逐字对齐。文章两幅图预定整数帧2349与3717，秒数78.3及123.9，来源和图片位置在正式编码前冻结；JPEG只在最终媒体生成后按该帧抽取并实际验图。文章引用R1五台/两份判断/三票授权与R2已知成员计数，不用模型代替来源。

正文沿冷银灰/Redis红，与封面共享家族。封面使用redis-covers-v3，安装在covers/和publication，旧Redis封面及冻结保持。Main顶部传真实EP50，不使用EA02作为新系列期号。实际字体清单随本期输入记录并在冻结核验时复验；依赖按本期remotion/package-lock.json fresh npm ci安装，React类型声明为本期开发依赖，未借用已删除工程目录。

制作命令从仓根执行；Python使用已装numpy/scipy/soundfile/Pillow的环境：

```bash
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/redis/redis-sentinel/production/prepare.py
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/_shared/voice/gen.py --dir episodes/redis/redis-sentinel/production --jobs jobs-a.json
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/_shared/voice/build.py --dir episodes/redis/redis-sentinel/production
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/redis/redis-sentinel/production/assemble.py
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/_shared/place_v2.py --dir episodes/redis/redis-sentinel/production --mode whole
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/_shared/check_sentence_episode.py episodes/redis/redis-sentinel/production
python3 episodes/redis/redis-sentinel/production/model.py
python3 episodes/redis/redis-sentinel/production/sync_timing.py
npm --prefix episodes/redis/redis-sentinel/production/remotion ci --no-audit --no-fund
npm --prefix episodes/redis/redis-sentinel/production/remotion run check:types
```

上述准备命令仅用于本期尚未冻结的制作阶段；已选take复核不重请求TTS。covers.json及meta.covers后绑定同字节安装资产，cover-board-adaptation.json证明只调整封面元数据，不改配音/时序。

独立动态审查通过、所有写入停止并由根明确允许后，才运行：

```bash
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/redis/redis-sentinel/production/freeze.py
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/redis/redis-sentinel/production/freeze.py --verify
PATH=/workspace/.venvs/video-studio/bin:$PATH bash episodes/redis/redis-sentinel/production/render-final.sh
PATH=/workspace/.venvs/video-studio/bin:$PATH python3 episodes/redis/redis-sentinel/production/verify.py --final
```

默认render：来源/冻结检查→本期正文H264/AAC→真实pc601转tv709像素转换→共享混音→两项原题/Redis机构5秒简表。不能用render:body冒充最终交付。verify只读输入和回执，媒体报告另写；最终视频、资料首中末、字幕边界、Figure、播放器与线上完整SHA仍需实际验证，不预记完成。GitHub站点按持续授权发布，外平台未获本轮新发授权。
