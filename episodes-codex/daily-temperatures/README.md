# LC.739 每日温度

## 当前交付状态

用户观看v0.69.0后指出默认懂单调栈，现先补栈的同端操作、后放先取、底顶，再演不升与维护，之后才命名。新增4句、复用28句；正文5322帧，最终含参考资料5472帧/182.4秒，Python与参考资料卡各150帧/5秒。190项生产输入核对通过。实际最终视频SHA256：`f3aa4f315770896ef3b3d15d8ad3d38ed5602d07528d9fcc20300bad3d6b3a3b`。实际动态、声音、正式MP4独立视觉与媒体检查均通过，能力范围见当前QA；网站及发布状态见[修订记录](../../docs/daily-temperatures-stack-primer/README.md)。尚无修后用户认可，无逐字ASR或全片人工听辨。旧片/旧QA完整保留于`revisions/stack-primer-before/`。

现行正式渲染从`remotion/`运行`npm run render`，默认共享入口生成正文和参考资料附录。旧版算法/封面保持，源卡片操作来自真实Python append/pop概念演示，与解题trace分开。
以下保留阶段1制作交接记录，开发占位分镜和未生成配音的说明只适用于当时，不是当前状态。

开工基线8d037aa3e05ce1ed992df6b758b9b2227dd8b18b，issue #80，内部EP35，片内只标LC.739。root已从clean最新主干创建codex/leetcode-batch-next，当前独立锁图已npm ci；不依赖被删除工程。计划批次firstRelease v0.69.0，实际发布由root完成。

本期阶段1已完成14镜28句4章脚本、官方题面实际读取、唯一完整Python、独立oracle验证、同源真实执行trace及原创Remotion源码。当前storyboard明确provisionalTiming/pendingAudio，4303帧约143.43秒只是编辑排布，末150帧静态Python卡。尚未生成TTS、实际静帧或视频，不能预记媒体、起音、听辨及上线通过。

主线：每日气温要返回未来第一个严格更暖的等待天数 → 重复往后找 → 留下未解决日期 → 按温度不升、末尾先检查 → 命名单调栈 → 按日执行 → 相等与末尾0 → 复杂度和完整Python。主例[33,34,35,31,30,32,36,33]，输出[1,1,4,2,1,1,0,0]；相等补例[30,30,31]，输出[2,1,0]。示例无指定单位、非真实预报。

核心文件：script.md、plan.json、article.mdx、research.md、pronunciation.md、visual-direction.md、knoll-props.md、covers.json。research/source-access.json与official-web-response.json是官方网页访问证据，solution.py是唯一算法执行源，solution.json与文章代码同源，research/trace.json由sys.settrace观察真实函数生成。Main.tsx读取事件id，不另写解题器。

阶段1复现（从本目录运行，无媒体）：

```sh
/workspace/.venvs/video-studio/bin/python research/verify_solution.py
/workspace/.venvs/video-studio/bin/python build_draft.py
/workspace/.venvs/video-studio/bin/python research/verify_production_inputs.py
./remotion/node_modules/.bin/tsc --noEmit -p remotion/tsconfig.json
```

算法验证：8个官方/边界样例、21844组穷举、3000组确定随机、2组十万长度输入通过；main35事件、equality13事件。源码SHA256为5f628ef12f8f1fd15c85289eeaabec3b2aa01706df39fa1356afb09a8314b718。静态源检查验证双句、四章、题意与方法命名顺序、同源程序、末卡边界、封面声明安全区及固定字号实测宽度。它不能替代实际图像或动态检查。

root安排独立编辑与算法审稿，审稿闭合后才生成配音。后续只使用共享voice prep/gen/build、共享整轨与起音算法；真实build后执行prepare_code_endcard.py，再铺轨、检查真实时序和动态。build_draft.py不能作为生产时间来源。所有写入停止后freeze.py冻结；使用flock /tmp/video-studio-render.lock与TMPDIR=/workspace/daily-tmp串行渲染。检查合格后按持续授权接入GitHub站点，本期无外部平台发布授权。

本阶段没有ASR、全片人工听辨或用户观看结论。

## 制作海报补齐

真实封面复核发现`covers.json`声明的竖版`poster.jpg`缺失，六张比例封面本身已通过。保留原阻塞记录于`revisions/missing-poster-before/`，仅执行`cp cover-3x4.jpg poster.jpg`补齐声明产物，二者逐字节相同。网站另由`episodes/daily-temperatures/meta.json`明确选择`cover-16x9.jpg`。新增竖版已独立实际查看，详见`qa-covers.md/json`；未重渲不变封面，未改覆盖源码、分镜、声音或其他冻结输入。
