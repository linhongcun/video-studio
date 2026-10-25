# 二分查找：为什么能放心排除一半？ · 先推导，再命名

本轮用户反馈与六片范围扫描见[统一修订记录](../../docs/leetcode-derivation-20261025/README.md)。当前思考链：有序使一次比较可排整段→比较边端与中间的剩余规模→选择中间→命名二分查找并重置正式执行。

15镜30句、四章、5209帧/30fps。题意前两镜保持，完整Python及三尺寸封面不变；片尾150帧为静态完整程序，提示暂停，原生控件可操作。代码卡无人声但正式混音仍有背景音乐。实际媒体身份、容器时长与响度看`render-result.json`，不要从文字稿推断已编码通过。

编辑审读、预检与成片复核分别见`qa-editorial-approach.md`、`qa-preflight-approach.md/json`、`qa-final-approach.md/json`。本轮只合成新增或改词句，未改句按文本/送模文本及原选中take完整SHA映射，见`revisions/approach-first/voice-reuse.json`。程序、文章代码同源保持见`algorithm-preservation.json`；原有算法执行结果按相同程序继续有效，不冒充新执行测试。

## 本次实际制作入口

Python环境需要numpy、scipy、soundfile与Pillow；Node依赖按当前锁文件安装。旧三片不再链接已删除的旧站degradation目录。本机共享当前有效two-sum依赖；六片锁文件的非根packages一致。

新增/改词配音使用共享`episodes/_shared/voice/prep.py/gen.py/build.py`，本轮选中take名为approach，映射由批次`prepare_voice_revision.py`记录；不要凭同名WAV存在跳过已改词句。完整脚本/句时装配与末卡用本期`prepare_code_endcard.py`，铺轨/起音和句级检查继续走共享工具，不复制其算法。

预检用`freeze.py --preflight`，其原始清单保存在`revisions/approach-first/preflight-source-sha256.json`。预检后Core逐值保持，最终清单额外加入实际局部MP4、拼接计划及独立视觉复用审批；不把新增媒体依赖误写为修改Core后追认旧片。当前只读入口：

```sh
python3 episodes-codex/binary-search/freeze.py --verify
```

实际重渲镜号为 03,04,09,12,14，范围见`render-scope.json`。其中未改旁白但局部cue舍入变化的镜头也重渲，没有放宽内部时序断言。新工具`episodes-codex/_shared/remix_approach.py`以唯一slug映射：只复用字幕局部时间、语义cue、选中take SHA一致且经独立同帧视觉审批的旧画面；±1尾hold需明确逐镜审批，150帧程序卡另核。旧混音和所有片段音轨被丢弃，唯一音轨来自共享整轨，再用共享mix_bgm混音。

执行`remix_approach.py ... --render-shots 03,04,09,12,14 --allow-tail-frame-adjustment --plan-only`先生成区间命令，按计划用2CPU/共享`/tmp/video-studio-render.lock`渲染；审批后重跑plan-only写实际clip SHA，执行本期`freeze.py`纳入全部依赖，再`remix_approach.py ... --run`生成`remotion/out/voice-approach.mp4`并共享混音。计划与实际PTS/输入SHA结果见`approach-remix-plan.json`/`approach-remix-result.json`。完整新源码也可按原`npm run render`从头渲染，不能把不同编码方法的输出假称逐字节等于本次已验收文件。

## 历史来源与重建边界

旧报告快照和来源身份在`revisions/approach-first/before/`、`baseline.json`、`baseline-identity.json`；原版实际Git基线e38fa923保留。局部拼接实际读取ignored `remotion/out/approach-baseline/`，缓存存在不是权威：video/voice/storyboard按baseline.json的完整Git路径取出并核对完整SHA，src快照也逐文件对Git字节验证后才能使用。只恢复明确媒体/数据以作复用，不恢复已删除的旧工程或旧依赖。新清单记录这些实际输入；缺缓存时先按已记录Git来源重建它们，或选择当前完整渲染流程，不能改清单认可别的缓存。

旧静帧与失败布局证据保留原目录/原SHA，布局修后再采的证据独立标识。本轮没有逐字ASR、全片人工听辨或新手学习效果实验；技术/视觉验收和用户观看反馈分开记录。站点、实际版本与线上完整SHA统一见批次发布记录。
