# LC347 封面检查

基线 `6868fd40b509a0811e5a89575639b16948144ca1`，EP58。按已认可 LeetCode 深蓝/暖金/青色共享模板扩展 catalog 与题图，没有修改视频不可变样式或身份快照。

生成：`python3 episodes/_shared/leetcode-covers/render.py --repo work/lc347-covers/meta-repo --out-dir work/lc347-covers/render-final-title`。临时 metadata 镜像包含现有11期的真实元数据与本期身份，以便本片仍为草稿时使用共享校验入口；36张全系列候选的文字边界/像素尺寸校验通过，但只安装本期3比例6张图及竖版 poster。没有执行全量 `--install`，没有覆盖旧期资产或冻结记录。

实际查看本期三比例 PNG：标题与题号清楚，例图根为数字1/3次，左子节点5/5次、右子节点4/4次，对应本片最终保留集；根的含义按出现次数而非数字大小解释，兄弟不表示全局排序。最终问句为“为什么把最少的放在堆顶？”。初稿的左右节点虽构成合法堆，冻结前已按Python真实最终数组交换为5/4，并重新生成、查看三比例。4:3所有文字/组落在315..1125，内容底边小于918，未出现COPYFIT。完整边界及SHA见 `qa-covers.json`，实际模板输入副本与SVG在 `cover-inputs/`，图片SHA在 `cover-style.json`。

执行者：Codex封面子任务。检查仅覆盖静态封面与本机模板裁切，不代表正文动态、听辨、外平台实际裁切、用户认可或学习效果。
