# EP.63 · LC.994 腐烂的橘子

- **基线与分支**：`origin/main` 完整基线 `8601807405d1c0c492d9f7002b2a58c38c932b50`；制作分支 `feat/lc994-rotting-oranges`；2026-11-22 10:52 +08:00 开工。
- **选题与授权**：依据用户 2026-11-22 指示挑选 LeetCode 开放选题 Issue [#515](https://github.com/linhongcun/video-studio/issues/515)（LC.994 腐烂的橘子，`rotting-oranges`，EP.63）。质量验收通过后按 `docs/RULES.md` STATUS 持续授权自主合并主干、发布 Release 与部署 GitHub 站点；外平台新发不在范围内。
- **当前目录**：制作目录 `episodes/leetcode/rotting-oranges/production/`；发布目录 `episodes/leetcode/rotting-oranges/publication/`；`meta.json.sourcePath` 为 `episodes/leetcode/rotting-oranges/production/remotion`。
- **核心入口**：`solution.py` / `rotting_oranges_trace.py` → `scripts/build_trace.py` → `tests/test_solution.py`；12 镜脚本与文章经独立审读两轮通过后批量真实 MiMo 配音（音色「冰糖」）。
- **依赖与运行环境**：
  - Python venv：`~/.venvs/lc994`（Python 3.12.13，见 `requirements-runtime.txt`；另安装 `playwright` 与 `certifi` 供封面/页面检查及严格 TLS 证书验证）
  - Remotion：`remotion/package-lock.json`（Remotion 4.0.534，`npm ci` 独立安装）
  - 浏览器：macOS Google Chrome（`CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`，Linux 默认回退 `/usr/bin/chromium` / `google-chrome`）
  - 字体：Noto Sans CJK SC（Regular / Bold）与 Noto Sans Mono（实际路径与 SHA 记录于 `qa/preflight/report.json` 与 `reference-appendix.json`）
  - 配音凭据：仅通过进程环境变量 `MIMO_API_KEY` 注入，不写入仓库或日志。

## 制作命令（仓根，使用 `~/.venvs/lc994`）

```sh
python episodes/leetcode/rotting-oranges/production/scripts/build_trace.py
python -m unittest discover -s episodes/leetcode/rotting-oranges/production/tests
python episodes/_shared/voice/prep.py --dir episodes/leetcode/rotting-oranges/production
python episodes/_shared/voice/gen.py --dir episodes/leetcode/rotting-oranges/production
python episodes/_shared/voice/build.py --dir episodes/leetcode/rotting-oranges/production
python episodes/leetcode/rotting-oranges/production/prepare_code_endcard.py
python episodes/_shared/place_v2.py --dir episodes/leetcode/rotting-oranges/production --mode whole
python episodes/_shared/label_onset_strict.py --dir episodes/leetcode/rotting-oranges/production
node episodes/leetcode/rotting-oranges/production/scripts/preflight.mjs
python episodes/leetcode/rotting-oranges/production/freeze.py
python episodes/leetcode/rotting-oranges/production/render.py
```

- 正式渲染只执行一次默认入口 `render.py`（内部依次完成来源检查、冻结核对、`render:body` 渲染与混音、limited BT.709 `title-author` 参考资料页追加及完整流媒体校验），不预先单独跑 `render:body`。
- 封面通过共享 `episodes/_shared/leetcode-covers/template.mjs` + `diagrams.mjs` 渲染三比例并执行完整 DOM COPYFIT 与 4:3 安全区核验，仅安装本期文件，不改写旧期 `cover-style.json`；输入快照保留在 `cover-inputs/`，完整报告在 `qa/covers-report.json`。
- 阶段耗时、重跑、审读与验收边界见 `qa/`（本页在冻结前定稿，冻结后不追改）。
