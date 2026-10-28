# LeetCode独立工具审查

结论：通过。审查者`lc_qa`未参与三个制作工具实现，也未更改生产源、原冻结或元数据。基线为`d04a30c12b1ce0fb5743f20ce61f9db8908311ad`；本层是制作工具与实际依赖审核，正式逐镜预检、编码成片、网站与发布验证分别记录。

## 实际检查与修改后的闭包

逐段审查`_shared/leetcode-video/render.py`、`references.py`、`qa.mjs`及其真实调用的旧puzzles媒体/书目引擎；只读执行11题当前入口的时序/依赖枚举、原Python边界与源SHA检查。原正文最后150帧完整Python页属于body，再在其后追加原题与机构书目页；原`solution.py`及`solution.json`的完整SHA必须匹配原分镜。正文新画面只静音重渲，完整基线AAC包/PTS/DTS/duration及解码PCM不变，附录引擎仍校验全部正文帧与PTS。

| 题目 | 当前实际输入项 | 正文帧（含Python页） |
| --- | ---: | ---: |
| two-sum | 52 | 5096 |
| longest-substring | 54 | 5980 |
| container-most-water | 49 | 6817 |
| trapping-rain-water | 54 | 5926 |
| permutations | 54 | 5613 |
| climbing-stairs | 51 | 4779 |
| number-of-islands | 54 | 5845 |
| reverse-linked-list | 50 | 5400 |
| number-of-provinces | 47 | 5159 |
| binary-search | 48 | 5209 |
| daily-temperatures | 53 | 5158 |

合计566项逐期依赖，计数是逐期相加而非去重总文件数。已独立枚举每项现存完整SHA并检查引用闭包；两份文章（旧制作稿与当前发布稿）、实际文章来源与递归证据、全部代码源与不可变style-v1/identities-v1均在清单内。所有被冻结JSON中现存saved/archive/evidence命名字段指向的仓内文件均已覆盖；成功保留GET的2条path/sha绑定另外独立重算通过。历史裸path/commit仍表示当时身份，不假装为本轮新GET或当前响应。

审查中发现并在正式冻结前修正两项真实闭包问题：原继承入口只有参考页两份CJK字体，现补齐正文、代码与品牌实际消费的6个字体文件/8个字体族与权重绑定；原多种出处schema漏掉LC42版权原文、LC46版权原文与source-access.json，现按具体字段的SHA语义加入，未将函数正文SHA误绑定给版权原文。原始证据与原研究日期没有改写。

## 字体、私有复用与真DOM

独立重算6份实际字体完整SHA并核对`fc-match`绑定。新manifest在第一次写盘前补齐字体；已有缺项清单的只读拒绝另经实际调用确认，清单SHA/mtime保持。字体fixture后只有`production_inputs`的函数AST改变，字体/媒体/verify路径AST不变，故有界复用已通过的字体闸门及1秒H.264/AAC加5秒书目小样，不重复完整解码；书目adapter字节亦未改。

只读确认新工具使用私有函数namespace，旧puzzles EPISODES、路径全局与紫色palette不受影响；旧puzzles-video/mysql-video文件树相对基线无diff。真实DOM取样使用renderer页面close前的evaluate，无生产审计Hook，按每镜0/.5/.98及Python前一帧/首/中/末检查；缺码卡、字幕仍在代码页、代码行差异、重复代码页、边界/字体或采样错误均失败退出。

已读取并验证实际DOM小样：全排列f5538完整22行；LC547 f5084完整24行；LC739 f5083完整12行。三份均逐行保留原缩进和空行、字体检查全true且0违规/警告/错误。后两期保留原`full-python-static-150-frames`标记，QA兼容它与`complete-python-solution`两种原结构，仅从可见代码根内的data-code-line或xml:space=preserve文本提取代码，未为审计改生产代码卡。

## 证据与范围

独立机器记录位于`work/leetcode-video-style/siteqa/independent-tool-check.json`，含全部路径/SHA和三个DOM报告身份。制作者小样原报告位于`work/leetcode-video-style/tool-selftest/`；第一次scratch输出相对路径设置错误、共享Frame同时变化被保护闸门拒绝、初版QA对LC547/739原标记的误识别均保留，均不能记作原生产片错误。更改QA兼容后整批正式预检由主任务重新执行，不复用初轮失败结论。

本层没有新来源实读、正式MP4渲染/全流重解码、算法重新执行、听辨/ASR、真机或线上站点检查。网站QA脚本已准备但尚未完整build；最终等待全部11片安装后的候选提交。
