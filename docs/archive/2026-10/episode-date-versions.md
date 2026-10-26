# 视频创建、修改时间与日期版本

2026-10-25 用户明确希望每期持续打磨，以创建时间保留起点、修改时间区分当前版本，避免不断累加“重制版”名称。现行维护规则见 [publish.md](../../publish.md#视频时间与版本)。

## 基线与历史回填

开工时工作区干净，已 fetch 并快进整合最新 `origin/main`，基线为 `17effcf6c18e4277d13178960f065ea82c904f6d`。发布前再次同步并整合 `1aad9cc24a794e2050165322a1e87eca679ad430`，保留新增的 LC.200 成片修订与 EP.20 命名更新；本次日期功能仅修改站点、元数据和维护规则，无视频制作输入或媒体变更；站点依赖按当前 `site/package-lock.json` 执行 `npm ci` 安装。

42 期历史元数据均无 `createdAt`，其中 36 期有 `updatedAt`。回填保留所有原有字段值、首发时间和已知修改日期，不使用本机文件 mtime、构建时间或今天作为历史时间。

- 40 期创建日期采用现有 `publishedAt`，与最早元数据 Git 记录的北京时间日期一致。
- `circuit-breaker` 的创建日期为 `2026-10-13`：[4180090c](https://github.com/linhongcun/video-studio/commit/4180090c) 中已有元数据；首发日期后来修正为 `2026-10-14`，仍保留。
- `distributed-tx` 的创建日期为 `2026-10-15`：[0757369c](https://github.com/linhongcun/video-studio/commit/0757369c) 中已存在草稿；首发日期仍为 `2026-10-16`。
- 无修改日期的 `agent-skills`、`bridge-torch`、`egg-drop`、`monty-hall`、`number-of-islands`、`water-jug`，初始化 `updatedAt = createdAt`；发布前主干已为 `number-of-islands` 增加同日修改时间，整合时优先保留该上游记录。上述历史数据均仅有日精度，不补造时分秒。

当前制作目录可能在重做时才建立，不能拿 `sourcePath` 的首个提交作为该期创建时间。例如 `cache-consistency` 于 [ac7bf34f](https://github.com/linhongcun/video-studio/commit/ac7bf34f) 已在 10 月 16 日存在，当前制作工程到 10 月 24 日才建立。

## 页面与检查

卡片和详情页均展示“创建于”“修改于”和当前日期版本。含时区的 ISO 时间统一按北京时间显示，精确到秒的记录能区分同日不同版本。新稿建立时写入相同的两个内容时间；首次公开前可不写 `publishedAt`，预览不会伪造首发。RSS、NEW 和首发排序继续基于首次公开时间。

已完成验证：

- 42 期迁移前后比较：所有原有字段值和已有修改日期不变。
- `npm run build`，包含元数据日期校验；本地构建通过代理正常读取真实 GitHub Releases。
- `node scripts/check-episode-dates.mjs --built`：历史精度、时区跨日、同日不同秒、非法时间、未发布草稿、42 个详情页、结构化数据和 RSS 首发时间通过。
- `node scripts/check-learning-path.mjs --complete`：学习方向、系列路径、历史 Release 和独立课程关联通过。
- Chromium 在 1440 与 390 像素检查列表及三个代表详情页，共 8 项；41 张公开卡片均有两个时间，筛选、同日显示与历史创建日期通过，无横向溢出或页面脚本错误。
- `python3 episodes/_shared/tests/secret_scan.py` 与 `git diff --check` 通过。

本次仅改日期信息与展示，不代表重新审阅视频的教学效果；视频和封面未重新生成。
