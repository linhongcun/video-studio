# LC.46 全排列 · 独立封面检查

结论：**PASS**。检查人：Codex `/root/produce_daily`，未参与本片创意编写。实际检查日期：2026-10-25T12:29:22.019242+00:00。

六张本地PNG/JPG均分别用view_image实际打开。16:9、4:3、3:4的标题、问题、水印、箭头与数字完整可读，没有互遮。每行分别是123和132，均恰好使用1、2、3各一次；这是六种不同排列中的两种示例，“全部六种／找齐六种”与三张不同数字的语义一致，没有把两行当作全集。

4:3声明的六个文字框均落在x315..1125且底边<918。实际前景框（右/底不含）：PNG `[403,65,967,896]`，JPG `[400,65,968,897]`，均通过。量化以RGB相对背景[15,23,42]最大通道差>12取前景，排除JPEG背景微噪；同时核对源变换与真实图像，不能把该阈值测量单独当作排版审查。

`covers.json`声明poster直接使用`cover-16x9.jpg`、sameAs 16x9。此文件实际1920×1080、已打开，SHA见下表；没有另声明独立poster.jpg。

141项冻结输入逐份全文SHA-256核对，141项相符，0项不符。这里只复核冻结身份，没有重复算法或声音检查。manifest全文SHA：`e79c7123e94dcee4df162ba11ff20e65121891b9ad6481a2f5b63f64af95c4c6`。

| 实际文件 | 尺寸 | SHA-256 |
|---|---|---|
| cover-16x9.png | 1920×1080 | `969ee9be2dbf921fc32cefc95011fbc8e9c575a136b43fd560b0de3a0dd2c065` |
| cover-16x9.jpg | 1920×1080 | `e523962168ebddf0d013a0f4b0d06a32e08398ec50e3b3228ce715ee0fd5799c` |
| cover-4x3.png | 1440×1080 | `03f04561034736c4a6494a3f680a70f26d527ecf95b7529a8e3b0cb9eabc5836` |
| cover-4x3.jpg | 1440×1080 | `aa90948e2997fdf0ff706370331ed9e40803fcb23adf66dbd5efe968854591cb` |
| cover-3x4.png | 1080×1440 | `c358495e3682546a8ad8a0280a41b2b63e3b37fecb854978f425b4259cabb1c4` |
| cover-3x4.jpg | 1080×1440 | `d7e3e036a430dd1255317f751b6344adaef4f864a31867aa6b7daeab5384dcc5` |

| 封面相关输入 | SHA-256 |
|---|---|
| source-sha256.json | `e79c7123e94dcee4df162ba11ff20e65121891b9ad6481a2f5b63f64af95c4c6` |
| covers.json | `c447381e0be7569c8add72521d1d1adc7b4e3a04fc3d36cd79bfbe87d2b1dd0b` |
| remotion/src/Cover.tsx | `6b3a10e335a9f8e3313327b8a7e8499a5f57b13f063f9df00c1fb6db4f1600c5` |
| remotion/scripts/covers.mjs | `67b38f7afeb93e960b1ec46271f99278cc8072475bbb60da8658b6ad23b2eafa` |
| storyboard.json | `3221d17e6693e28b8bdaed3f90db9f2581b1b5e844f8b24a072fe223ee541903` |

完整结构化证据见[qa-covers.json](qa-covers.json)。检查前后上述输入摘要不变。本次只写这两份报告，没有修改源、图或metadata，没有重渲染、配音。

范围仅封面与声明poster；不代替成片、时序、音频、ASR、人耳、站点接线或发布检查，也不表示用户观看认可。
