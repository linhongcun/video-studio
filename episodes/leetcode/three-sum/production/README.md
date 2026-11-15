# LC.15 三数之和
基线 origin/main 15fc310e958d5b1394151b6d9a041e9a7dcca4db；2026-11-15 13:46 +08:00 开工。用户授权自选下一题，使用既有 Issue #490。
工作区保留 LC.56 旧未跟踪产物；本期只写 three-sum 及版本、索引。冻结、渲染和发布身份以本期清单为准。
入口：solution.py / three_sum_trace.py → scripts/build_trace.py → tests/test_solution.py；九镜脚本与文章独立审读后批量真实 MiMo。
依赖：Python requirements-runtime.txt；Remotion package-lock.json，锁依赖与 LC.20 相同才复用其已保留 node_modules。Chromium 通过 CHROME_BIN 选择实际路径。
命令（仓根，激活 ~/.venv-lc56）：
```sh
python episodes/leetcode/three-sum/production/scripts/build_trace.py
python -m unittest discover -s episodes/leetcode/three-sum/production/tests
python episodes/_shared/voice/prep.py --dir episodes/leetcode/three-sum/production
python episodes/_shared/voice/gen.py --dir episodes/leetcode/three-sum/production
sh episodes/_shared/voice/run.sh episodes/leetcode/three-sum/production
python episodes/leetcode/three-sum/production/prepare_code_endcard.py
python episodes/leetcode/three-sum/production/freeze.py
python episodes/leetcode/three-sum/production/render.py
```
正式默认入口只执行一次：render.py 自带输入验证、正文渲染、混音、资料页与最终媒体核验；不要先另跑 render:body。
正式装配后运行 `node episodes/leetcode/three-sum/production/scripts/preflight.mjs`，以实际 Remotion DOM 检查逐镜、最长字幕、代码边界的文字边界及字幕遮挡；报告在 qa/preflight。它只证明抽样帧几何，不代替连续成片审片。第六镜内部移动起点必须从共享 voice/cues.json 读取，不估计词时间。
封面入口是仓库 episodes/_shared/leetcode-covers/render.py；cover-inputs 是源文件快照而非单独安装入口。只安装本期三比例产物，不覆盖旧片；qa/covers-report.json 记录本期完整 SHA 与 4:3 安全边界。
发布副本只来自完成检查的本期视频，站点数据复制到 ../publication。来源阅读、文稿复审、冻结、成片与浏览器验收绑定各自输入SHA；未做检查不可记通过。
阶段耗时与重跑见 qa/production-timing.json；本页在冻结前定稿，后续执行记录另放 QA，避免追改冻结输入。
