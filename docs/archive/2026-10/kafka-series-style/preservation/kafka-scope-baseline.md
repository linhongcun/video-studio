# Kafka重制：独立保护范围基线

日期：2026-10-28。基线提交：`d7a5d7682080232617a03cc988b7c25cb50446f4`。这是用户扩大为Kafka重制之后的新范围，原cover-only的`preservation-baseline.json`原字节保留，SHA仍为`83bdeb1abbb9df8ba4675855179580b477f16d9155a3d6fd4aae4013e32839b7`。

本基线SHA：`f225347a53db12683b6ab7f3016e01241f992c48098a5f62d65560f499fae3fa`。实际发布目录尚未替换时捕获。

- 1833保护路径：1827实际存在，6个仅为原本缺失的显式可选候选。两套旧冻结清单277声明继续完整保护。
- 旧MQ根工程及旧mq-intro/历史工程555实际文件（含旧图、媒体和输入）全部保持；新kafka-intro前缀下的新文件不冒充旧源，另须按新片独立冻结。
- 其他48个episode目录的1122份现存文件全部保护，含5期puzzles新正文媒体、meta和sourcePath；排除node_modules/.git/__pycache__/.cache依赖缓存目录，不以本机缓存作源。
- 29份既有共享封面文件也保护；series.json、learning.ts和当前规范文档按root明确授权不纳入本批保护名单。
- 只允许明确列出的20个发布输出被替换或新增（17此前存在、3此前缺失）；原SHA仍记入authorizedReplacementFiles，后续差异单独列出，不混作未授权变化。
- 发布目录其他文件暂保护，包括captions.srt、render-result.json、pronunciation.md、README.md等；如需修改必须另建授权范围补充，不能重写此基线或为了检查通过删条目。

重验：`python3 /workspace/work/mq-cover-qa/kafka-scope-preservation.py --verify`。首次重验通过。此检查证明旧范围保真和新改动范围明确，不代表新Kafka内容或最终媒体已经验收。

## 另行补充的7份发布副本

root随后明确授权替换captions.srt、render-result.json、mix-report.json、pronunciation.md、research.md、references.md和README.md。已在替换前逐字节核对并另存kafka-scope-authorized-supplement.json，绑定本基线SHA；原基线未改写。有效授权输出合计27路径，有效不可变保护1826路径。source-sha256.json、qa-final.md、site-integration.json三份发布历史回执仍保护，新README须明确历史身份，当前冻结/QA按新sourcePath追溯。
