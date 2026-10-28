# Redis系列封面扩展

沿用跳表封面的冷银灰、冰白、Redis红与石墨文字，以及原字体、背景、标记和三比例版式。v1已被原生产冻结绑定，保持原字节；本入口复制其确定模板并只增加当前EP.08服务端缓存、EP.09缓存一致性。catalog核对全部三个Redis条目的原EP、完整原题和实际sourcePath；`preservedEpisodes`明确保留EP.40全部现有图像与sidecar，不重新生成或安装跳表图。

本轮EP号保留真实08/09，不另起R编号。应用示例均为原商品7042：EP.08未命中由应用查数据库、取回199并回填，后来命中返回缓存199；不会画成Redis自动查询数据库。EP.09先更新数据库为179，再删除同一商品旧缓存199，下次读重新取回填充179；它是常见策略，不宣称强一致保证。原题和数字只表达教学示例，不是压测或性能结论。

`style-v1.json`、原背景和Redis标记按v1原字节复用，来源、MIT许可及商标边界继续随完整输入SHA绑定。文字与机制图用确定SVG生成，没有重新生成背景图或引入新事实。

尺寸仍为1920×1080、1080×1440、1440×1080；4:3居中放完整竖版，检查x315..1125、底边<918。真实六图及九份虚构长文字/三位EP压力样例检查实际字体、图形/边框与组间距。压力样例不表示新选题已制作。

仓根执行：

```bash
python3 episodes-codex/_shared/redis-covers-v2/render.py --out-dir work/redis-cache-style/covers
python3 episodes-codex/_shared/redis-covers-v2/render.py --out-dir work/redis-cache-style/covers --install
```

安装前核对候选报告与全部输入/产物SHA，解析所有已跟踪平面及嵌套source-sha256清单，拒绝任何冻结目标覆盖。两期新生产副本安装到各自`revisions/redis-style/`，原制作根封面不动；发布根只更新三比例JPG、3:4别名poster.jpg及配对cover-style.json。原meta.poster仍为cover-16x9.jpg，sourcePath继续定位实际Remotion目录。旧封面入口与旧冻结保留，后续不要用历史npm covers覆盖本系列模板。

本README是编码输入，完成渲染后不追加任务进度；实际制作、独立审查与发布记录存任务归档。
