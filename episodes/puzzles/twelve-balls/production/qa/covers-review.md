# P06 / EP.56 封面复核

资料与复核日：北京时间2026-11-04。本记录是新P06的实际检查，不继承P08或其他旧期QA的通过身份，不表示用户观看认可或成片审查。

使用当前紫黑系列模板；原字体、标题/水印位置不变。主标题「12球称重」，副题「轻重未知，3次找到异常球」。题图恰有12个同样外观的编号球，1–4对5–8为合法首称，9–12在盘外；「结果？」和左重/平衡/右重三态保持未知。没有特殊颜色、大小或倾斜提前指定异常球，没有展示主例6轻，也没有拟真天平或模拟App外壳。完整题设仍为恰1球异常、轻重未知、无砝码/外部正常球、最多3次等臂称重须确定球号与轻重。

制作角色 `/root/p06_covers` 逐张实际查看1920×1080、1080×1440、1440×1080三张PNG。独立角色 `/root/p06_independent_model` 于2026-11-04 01:01:19 UTC逐张实际查看同三图，并只读核对covers.json、render report和twelveBalls源码；确认数量/分组、同样外观、三态未知、模板层级、无裁切/交叠。独立范围仅当前三PNG与指定输入，未审JPG或旧片。

Chromium 154.0.8037.57 / Playwright 1.62.0实际测量每图23个非空文字边界、12个球、仅一种球外观，文字交叠0。4:3文字x411.42..1047、底836.72；全部内容组x393..1047、底907.5，均在x315..1125、y<918安全区内。横版文字底908.47<918。详见本期 `cover-render-report.json` 的完整文字/图组边界与输入输出SHA。

旧八题全目录（排除node_modules/.git）及共享不可变模板/背景/renderer/历史SHA清单共5,866文件、2,446,259,440字节，制作前SHA见 `covers-prior-baseline.json`。制作后逐文件复验5,866项全部相同、差异0；没有重渲旧片或改写旧冻结/QA。原始比较与本期源/三比例输出/六份publication副本核验见 `covers-preservation.json`；可用 `python3 episodes/puzzles/twelve-balls/production/qa/covers-check.py`只读复验并更新本期比较回执。

本期 `render-covers.py` 只生成P06；加 `--install` 只复制本期三JPG、竖版poster及两份清单。`cover-style.json` 与 `cover-render-report.json` 保留实际封面源码SHA，`covers-review.json`绑定所见PNG和复核时的报告SHA。生产目录保留SVG/PNG/JPG三比例，publication保留JPG三比例及poster；poster逐字节等于3:4 JPG。
