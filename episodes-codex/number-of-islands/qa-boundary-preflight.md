# 首格边界解释：定向预检通过

仅审新增06，不覆盖原整片预检。当前151项源实文件全部匹配 `source-sha256.json`，清单SHA256 `43c4a31200364d1f9f3bbf1bd697abe2b84784cd150c8290feb59ece1516803e`。Main `eddbd4fcb1e592b25b821fc57756785c3699a84ae77df0dfd215e685e104975e`；IslandMap `c29095c860aa41385310c74f1bd7862c955a527f693e8917845209c6e57a31dd`；storyboard `2f91afa197238acf635e94d268825c9ecfc38e2b8913a0d1c64799ac5e833cd4`。真实总长5845帧，06从2046起长487帧，第二句局部cue243。

实际产物 `qa-boundary-motion.json`（SHA256 `4585ce5427eacd375bcfcfc747926feaa604d08089004e975a0b18453513c5bd`）及 `remotion/out/qa-boundary/boundary06.mp4`（SHA256 `244148c621a9d7390b5ff77774797d82e221a778b7791fc056bb113b80e51e70`）。ffprobe确认487帧/960×540/30fps。审查者 derive_container 实际打开26个连续片解码时点和字幕2436、2484；三张contact sheet、精确帧路径见 `qa-boundary-preflight.json`。

- 右检查→mark→push，下检查→mark→push，然后左12、上13，顺序与不变真实trace一致。已查看所有转折前后，不仅静态末点。
- 左2418..2465、上2466..2513各48帧，红箭头止于真实网格边框，拒绝短横清楚，行1/列1仍可辨；没有外部格或把越界画成海水。当前始终锚定第1行第1列。
- 越界前后seen保持三勾、stack两项（底1,2／顶2,1）、count1；不标记或入栈越界坐标。13仍有当前白框，2514到14才结束首格展开，尾19帧留出收尾。
- 新长字幕、左/上标题与越界注记清楚，未遮地图、行列号、状态或彼此。

独立范围核对：Main除06外逐字节同旧；移除Map新BoundaryArrow及默认false的opt-in新增字节，完整重建旧Map；其余13镜duration/subtitles/cueFrames/codeCardFrom逐项相同。06后全局+62，旧范围复用见 `reuse-proof.json`。未因此重审全片、重跑65852算法案例或封面。

无未解决视觉阻塞，可进入06局部正式渲染。音频另独立审查；本报告未声称人耳听完整片、ASR或487帧逐帧实时播放。最终新拼接MP4尚需定向成片复核，不能以本预览通过替代。
