# LC.42 制作说明

范围：issue86、内部EP37，仅片内LC.42；14镜28句四章，文稿866字符，开发估计178.2秒含5秒代码卡。正式时间只认root实际TTS/句级装配，不将估计当起音/成片证据。唯一方法为左右最高值预处理；scope调整理由见research.md/README，不把旧草案双指针塞进短片。

素材均程序化SVG，无外部图像、假应用壳、无关比喻或装饰进度条。题目柱形地形固定；单位格按同一比例，蓝水不进入柱体。Terrain负责真实柱子、水与记录，Main负责按真实分镜和观察事件展示，CodeCard从唯一solution.json读19行、固定35px/38px行距。封面同一Terrain复用原柱子/8格水，四比三重要内容位于中心810px且高于918。

| 镜 | 实际机制与入口 |
| --- | --- |
| 01–02 | 原题对象/宽1/非负/单位水量；题意预览明确7+1=8 |
| 03–05 | 较矮两侧定水位；矮柱被淹与右盆水位1；重复找高点推得双向扫描 |
| 06–07 | 清空预览；真实事件1–14逐个留下L/R记录，包含本柱 |
| 08–09 | 真实句首命名前缀/后缀；水位3与水深1分开 |
| 10 | 真实首列事件15，加0；末列仅作边界规则预览 |
| 11–12 | 真实事件16–21，空心金框预告后整列水/累计同帧确认，返回8 |
| 13–14 | 同源代码节选/0下标映射/三遍O(n)/两数组O(n)；8格回收及150帧完整程序 |

research/generate_demo_trace.py对solution.py的AST赋值做只读观察；research/demo-trace.json与remotion/src/lesson.json字节一致，动画不另写solver。research/verify_algorithm.py使用水平逐层独立oracle，22257组与2组满约束通过，21事件核对蓝格与累计一致。这些不是动态画面审、成片或用户理解检查。

共享工具：voice/build.py和句级assemble_sentence_episode.py、place_v2.py、label_onset_strict.py，不复制TTS、铺轨或声学起音实现；prepare_code_endcard.py在真实装配后声明附录。root决定TTS/预检与render，渲染按flock /tmp/video-studio-render.lock和TMPDIR=/workspace/rain-tmp。起音、术语至少63帧、COPYFIT、封面安全区、真实连续动作与MP4由后续独立闸门记录。

当前未TTS、未媒体渲染、未逐字ASR或人工全听；正式分镜尚未生成，占位分镜pendingAudio与provisionalTiming均true，不预记冻结/预检/发布通过。GitHub最终发布由root在检查后按持续授权处理，平台未获授权。
