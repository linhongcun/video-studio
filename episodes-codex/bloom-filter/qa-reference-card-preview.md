# 布隆过滤器参考资料卡：独立排版预检

结果：通过，仅为独立PNG排版预检。未生成正文媒体或正式附录回执，不代替实际编码卡片和播放器检查。

调用现有共享API `load_references`、`render_cards`，使用本期原题模式references和默认字体，实际生成并查看一张1920×1080 PNG。共享生成器、来源清单和文章未改。

- Redis原题 `Bloom filter`、Cassandra原题 `Bloom Filters`完整可读；两条连续原文摘录分别排为1行和2行，无省略、截断或文字改写。
- 核验日期2026-10-26与顶部暂停阅读提示可见。
- 共享生成器COPYFIT检查通过；实际Pillow文本包围盒均位于各自卡片与画布内。R1最右1655、最下389；R2最右999、最下760。
- 第二行卡片底边886；预检保守预留的底部160px（y920–1080）为纯背景。此处仅检查预留区，未声称已观察真实原生控件。
- 正式默认入口仍须重新生成附录，并审读实际MP4卡片、字幕边界及暂停/全屏显示。

## 产物与身份

- references: `episodes-codex/bloom-filter/references.json`，SHA-256 `87e9d938c67df1f86dae04feb6f2c1b2f31c85a3dc44dd0432f262e364459404`。
- generator: `episodes-codex/_shared/append_references_original.py`，SHA-256 `cacd1e138e3ccb030dc6d5aee9ca8c5ea3104edb802000780a015dee4acc3579`。
- frozenMediaEngine: `episodes-codex/_shared/append_references.py`，SHA-256 `6688770d1221a115c9c1f591e3bffd14a6603d8c809c5b66f5e03e2fa4639f02`。
- regularFont: `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`，SHA-256 `b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a`。
- boldFont: `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`，SHA-256 `faa5f3656a78b2e2d450d27fe8382c778bc2b6bb5ea29c986664a6a435056ceb`。
- 预览PNG：`episodes-codex/bloom-filter/qa-reference-card-preview/references-01.png`，SHA-256 `76ec1a7952a261d2bb0ec82e39934414c8608a4cd0fbd7f8d08292f908a43a71`。

字体faceIndex=2，Pillow 12.3.0。完整实际draw.text包围盒、行数和范围限制见qa-reference-card-preview.json。
