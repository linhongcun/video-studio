# P06逻辑补充修订

基线27329c38a，共用分支codex/puzzles-followup-logic-20261111。只补12两句与对应构造动画，28个原选定take完整SHA复用；新时序由当前共享工具实际装配。旧冻结清单原字节保留baseline，并通过input-provenance.json绑定；封面原字节复用，保留历史生成身份。文章取当前publication稿，仅更新必要图位，不重构正文。

当前处于独立稿审通过后的制作阶段，尚未冻结/编码。默认完整入口`bash render-final.sh`持有全局/tmp/video-studio-render.lock，由父任务协调。未对发布目录或共享文件写入。

实际装配：正文6951帧，12为4789..5522（734帧），片尾预计6951..7100共150帧，总7101帧。2新句窗局部0.11..320.64及331.14..713.39；全局镜界以storyboard为准。

命令（使用已获本任务授权复用的`/workspace/work/pirate-motivation-20261107/.venv/bin/python`，无重新实现装配）：

```sh
python prepare.py
python gen.py
python build.py
python assemble.py
python /workspace/video-studio/episodes/_shared/place_v2.py --dir . --mode whole
python make-props.py
python verify.py
```

`gen.py`仅允许12两个jobs，28旧take和文本由voice_reuse逐SHA核对。正式冻结之前须完成独立动态预检；随后`python freeze.py`绑定真实输入，再由父任务批准占用全局锁运行`bash render-final.sh`；完整默认流程包括实际正文、色彩转换、共享混音及5秒原题署名资料页，禁止把已有MP4路径当成本轮完成。

文章从当前publication稿复制，同字节保留SourceQuote、结构与正文；两图绑定仍为3000/3480帧，因为01–11镜界/句窗完全相同，检查见qa/article-binding-and-chapters.json。成片后`python export-article.py`只向本revision的publication-stage/article导图，不写发布目录；父任务统一接入。字幕、章节和片尾范围均以本轮实际产物派生。
