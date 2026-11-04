# P10 · 100囚徒与一盏灯

本期为EP57／`prisoners-light`，对应[#214](https://github.com/linhongcun/video-studio/issues/214)。从初始已知灭的一盏灯推导一次性发送与唯一计数员接收，用4人12访完整过程解释灯亮保留资格、重复来访不重发及收到最后一份后宣布，再推广100人／99份。公平保证最终完成，不承诺固定天数。

当前共享源码与静态参数只作为新工程规格；声音、时序、模型、图文及QA为本期新制作。研究中的2022计账平移和2010末次宣布动作差异明确记录；Python有限穷尽、独立Node执行及公平调度证明分别留证。

## 制作入口

```bash
node site/scripts/check-references.mjs --sources episodes/puzzles/prisoners-light/production
python3 episodes/puzzles/prisoners-light/production/verify_protocol.py
python3 episodes/puzzles/prisoners-light/production/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes/puzzles/prisoners-light/production
python3 episodes/_shared/voice/build.py --dir episodes/puzzles/prisoners-light/production
python3 episodes/puzzles/prisoners-light/production/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes/puzzles/prisoners-light/production --mode whole
python3 episodes/puzzles/prisoners-light/production/verify.py
```

声音已选定的take保留，普通复核不重新请求非确定性TTS。句级声学边界、PCM归属、独立整轨复建和能力限制以本期实际审计为准，不冒称逐字ASR或全片语义听辨。

封面共享追加在P06全部校验收尾后执行，避免改变正在编码与验收的P06冻结输入。本期动画与图位按最终真实语音及封面源码身份独立复验；源负责人全部停写、新文件纳入实际diff样式检查后才冻结：

```bash
python3 episodes/puzzles/prisoners-light/production/make-props.py
python3 episodes/puzzles/prisoners-light/production/freeze.py
python3 episodes/puzzles/prisoners-light/production/freeze.py --verify
npm --prefix episodes/puzzles/prisoners-light/production/remotion run check:types
bash episodes/puzzles/prisoners-light/production/render-final.sh
python3 episodes/puzzles/prisoners-light/production/verify.py --final
python3 episodes/puzzles/prisoners-light/production/export-article.py
```

Composition为PrisonersLight，1920×1080、30fps。完整默认入口经全局渲染锁完成正文、真实颜色转换、共享混音及5秒原题／作者附录；最终交付为video.mp4。Figure在冻结前绑定真实整数帧，成片导出与实际看图另验。媒体、本地和canonical线上结果只按实际执行记录；本批仅GitHub站点持续发布，不含外部平台新发。
