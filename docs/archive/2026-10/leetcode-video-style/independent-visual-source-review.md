# LeetCode视觉副本独立源码审查

结论：源码层通过，可进入实际逐镜预检。审查基线`d04a30c12b1ce0fb5743f20ce61f9db8908311ad`，覆盖11期64个独立视觉文件及4个共享视觉输入。完整SHA和逐文件差异摘要见`work/leetcode-video-style/visual-source-review.json`；本次未改生产文件、未完整渲染/解码、未执行算法或核验新音频。

逐份阅读新旧Main、CodeCard、辅助图形、Root和theme的完整差异。动作、状态、索引、插值/phase、trace选择、数学分支及codeCardFrom判定保持；data.ts、SB/words/script、solution.py/json与原source-sha256清单等170份保护文件的SHA仍与基线一致。新Root继续使用原VIDEO，1920×1080/30fps与正文含代码卡总时长未改；旧cover compositions未复制到新视频入口，封面仍独立使用已验模板。

## 身份与视觉来源

identities-v1的11条题号、题名、方法与现行封面catalog逐条相同；style-v1的7个原封面色值完全相同，中文/等宽字体保持，DejaVu系列品牌字与封面一致。常规Header显示“算法可视化”，具体方法仍由原镜头引出；仅代码卡compact Header展示方法或原卡片caption，避免提前揭示哈希表、并查集、单调栈等术语。长列表输入为不可变快照，不绑定未来增长的catalog。

A组4期只替换原kicker、水印、背景层和身份栏，LC42 Terrain仅改data导入。B组4期保留排列/楼梯/地图/链表所有过程，Staircase只将固定表面与边线颜色接入主题。C组3期保留全部根/组色、实际trace与LC739的ProblemFitIntro/StackPrimer逻辑；后两辅助仅改相对导入路径。所有CodeCard仍读取同一solution.json.lines，显示内容与原程序逐行相同；代码行字号、行距、缩进和5秒区间不改。LC547、LC739只将代码页标题下移30像素，代码列本身未移动。

## 审查中收口的问题

- 源码字体bbox提示正常Header分割线与SVG标题区域相交，但bbox不等于实际墨迹覆盖；根实际首帧确认TwoSum墨迹在线下、间距偏紧后将共享线143改为136。LC42原baseline160改为204。
- 新绝对不透明Backdrop曾遮住未positioned的静态SVG。根实际PNG发现空画面后改为透明定位marker，每期原Main的C.bg继续承担实际背景；真实失败PNG和后续复查由根的逐镜记录保留，不能把仅DOM齐全当作画面已显示。
- LC704代码页旧kicker与新compact身份重复，删除该旧caption；完整代码、字号/行距、底注、门限不改。
- Header常规方法改为系列标签，保留原“先推导再命名”的首次呈现节奏。

## 后续实际检查门禁

源码审查不能证明foreignObject已实际绘出、字体墨迹间距、动态标签包络、全部字幕/代码边界和正式音轨保真。需逐镜实际DOM和截图、代码卡首中末与完整代码行核对，并独立查看LC739推导/入栈、LC46选择撤销、LC200长代码和LC547直接连接/归属等关键画面。编码及网站发布另记实际身份与能力边界，不预记用户观看认可。

## 后续有界页脚修订

首轮545帧报告之后，五期正文小字页脚距字幕不足，根仅将LC3/70/200/704的footer从1015、LC206从1020移到1045，LC200完整代码页底注从1053移到1040。独立逐字替换校验确认恰好6处坐标变化，字号、代码行/行距、字幕、数据/动作/时序均不动。其余62份已审视觉源SHA完全相同，170原文件保护SHA仍匹配。修前源均在before-footer-fix，与上一阶段68份SHA对应；原阶段机器报告不改写，最终68源SHA与6处前后身份见[independent-bounded-footer-review.json](independent-bounded-footer-review.json)。修后实际PNG通过情况由独立预检图审继续记录。
