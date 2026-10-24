# Deming 质检清单

给 Codex 或同类 coding agent 打勾。规范以 [RULES.md](RULES.md) 为准。命令和阈值的出处在 [validate.md](validate.md)。本文件只排顺序，不另写一套起音、响度或安全区。

制作与站点发布沿用 [RULES.md 的 STATUS](RULES.md#status) 中用户的持续授权。预检在 SHA-256 冻结之后、渲染之前；成片审在渲染之后。预检不过就改分镜或配音，回到 [pipeline.md](pipeline.md) 第 5 步重新冻结。检查通过后可以自主合并和部署 GitHub 站点，不再逐期等待用户批准；平台发布另行授权。

通用分镜检查是 `episodes/_shared/storyboard/validate.py`。命令、引擎覆盖的条目，以及 EP.14 写在 `checks(V)` 里的条目，见 [validate.md](validate.md)「分镜检查」。下面标明「手工」的步骤，引擎没有覆盖。不要跑 [validate.md](validate.md)「不要跑的脚本」里那些旧 `validate.py`，也不要在期目录再写一份同名脚本。

会写文件的命令，输出放到 `/tmp`。`label_onset_strict.py` 默认把报告写进期目录，已上线期必须加 `--out`。

参考期是 `episodes/degradation`（分镜 `meta.slug` 为 `degradation-v1`）。下面用 `EPDIR` 表示本期目录。

## 预检

### 1. 配音和分镜 SHA-256

手工。本仓没有统一的冻结脚本。算法与 `episodes/https/remotion/scripts/verify-storyboard.tsx`、`episodes/http-request/validate_v6.py` 相同：`hashlib.sha256` 全文，分镜里写前 8 位。

`words.json` 的字段：

- `audio`：wav 文件名。`audioSha256` 必须等于该 wav 的全文 SHA-256。文件在 `EPDIR/voice.wav`，没有则用 `EPDIR/remotion/public/audio/voice.wav`。
- `scriptSha256`：旁白逐字的哈希，不是整份 `script.md`。degradation 的 `meta.timingSource` 把这一前缀写在「旁白逐字」后面（`629b5042`）。不要拿整份脚本的哈希去对这个字段。
- `words.json` 文件自身的前 8 位写在 `meta.timingSource` 和每个镜头的 `timing.source` 里（degradation 为 `36bccee8`）。

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
D = Path("EPDIR")
w = json.loads((D / "words.json").read_text())
wav = D / "voice.wav"
if not wav.exists():
    wav = D / "remotion" / "public" / "audio" / "voice.wav"
audio = hashlib.sha256(wav.read_bytes()).hexdigest()
words = hashlib.sha256((D / "words.json").read_bytes()).hexdigest()
sb = json.loads((D / "storyboard.json").read_text())
src = sb["meta"]["timingSource"]
print("audioSha256", audio == w["audioSha256"], audio[:8])
print("words.json", words[:8], words[:8] in src)
print("voice prefix", audio[:8] in src)
print("scriptSha256 prefix", w["scriptSha256"][:8], w["scriptSha256"][:8] in src)
PY
```

通过：`audioSha256` 全文相等；`timingSource` 含这份 `voice.wav` 和这份 `words.json` 的 8 位前缀；`scriptSha256` 的 8 位前缀能在 `timingSource` 里找到。镜头 `timing.source` 用同一对前缀。对不上就停止，不要渲染。

### 2. 起音窗口

用分镜模式，不要加 `--words`。`--words` 只列出规则起音，退出码 0，不检查标签窗口。

```sh
python3 episodes/_shared/label_onset_strict.py --dir EPDIR --out /tmp/label-onset-strict.txt
```

已批准的例外才加 `--exc 06,18`（镜头 id 前两位）。例外只把窗口越界改记为 EXCEPTION，不抵消 NOT FOUND 和 MISMATCH。

通过：退出码 0，报告里没有 FAIL、NOT FOUND、MISMATCH。窗口和算法见 [RULES.md](RULES.md)、[validate.md](validate.md)。检查器是 `episodes/_shared/label_onset_strict.py`，只 import `episodes/_shared/onset_rule.py`。不要另存一份算法。

### 3. COPYFIT 为空

文字不自动缩小。溢出日志前缀是 `COPYFIT overflow`，由该期 `remotion/src/components/ui.tsx` 的 `Copy` 打出。`scripts/stills.mjs` 不打这行。`still.sh` 也不是这条的入口。

`episodes/degradation/remotion/scripts/` 和 `episodes/circuit-breaker/remotion/scripts/` 有 `prep-stills.mjs`、`diagfit.mjs`。换期先进那一期的 `remotion/`。这一期没有这两个文件，就不要从别的期复制。静帧和分镜检查是两件事，分镜检查用 [validate.md](validate.md) 里的 `validate.py`。

`frames.json` 由调用者临时写到 `/tmp`，不是仓库里的固定文件。至少包括第 0 帧，以及每个 `frame` 为 `browser` 的镜头的 `from`（成片绝对帧）。元素形状：`{"name": "hook", "frame": 0}`。

```sh
cd EPDIR/remotion
npm ci
node scripts/prep-stills.mjs /tmp/ep-stills /tmp/frames.json
node scripts/prep-stills.mjs /tmp/ep-stills /tmp/frames.json --covers /tmp/ep-covers
node scripts/diagfit.mjs /tmp/ep-stills /tmp/frames.json --covers
```

`prep-stills.mjs` 的 `--covers` 后面是目录。`diagfit.mjs` 的 `--covers` 只是开关，封面 PNG 写进第一个参数那个静帧目录。通过：这几条日志都没有 `COPYFIT`。封面合成 id 为 `Cover16x9`、`Cover4x3`、`Cover3x4`。

### 4. 封面 4:3 安全区

4:3 的 `centerRegion` 和 `bottom15Y` 由 `episodes/_shared/storyboard/validate.py` 的封面段检查，命令见 [validate.md](validate.md)「分镜检查」。`episodes/https/remotion/scripts/verify-storyboard.tsx` 只回归那一期。

读 `covers.json` 的 `sizes["4x3"]`。规范见 [RULES.md](RULES.md)：内容落在 `centerRegion` 内，底边小于 `bottom15Y`。degradation 是 `centerRegion` `[315, 1125]`、`bottom15Y` `918`。水印用该尺寸的 `watermarkZone`（degradation 4:3 为 `[1200, 30, 1400, 100]`），不要为了塞进 `centerRegion` 去挪水印。

```sh
python3 - <<'PY'
import json
from pathlib import Path
s = json.loads(Path("EPDIR/covers.json").read_text())["sizes"]["4x3"]
x0, x1 = s["centerRegion"]
y1 = s["bottom15Y"]
for e in s["elements"]:
    if e["x"] < x0 or e["x"] + e["w"] > x1 or e["y"] + e["h"] >= y1:
        print("OUT", e.get("id"), e["x"], e["y"], e["w"], e["h"])
PY
```

这段只打印，方便对照引擎报告。标题、窗口、价格行算内容，外接框要在区域内，且 `y + h < bottom15Y`。铺满画布的底色不是内容。水印不在 `elements` 里，不参与这条。坐标不合格就改封面 spec 再重跑，不要手改 `covers.json`。同时还要满足上一节的无 `COPYFIT`。

另外核对 [validate.md](validate.md)「封面」：`meta.covers` 与 `covers.json` 解析后相等；封面第一行离页头 ≥ 24 px；地址栏按 `BrowserChrome.tsx` 的公式放得下，并留 24 px。

### 5. 字宽和字框

手工估算，不能代替第 3 节的 COPYFIT，也不能代替分镜里的不缩字检查。不缩字在 `episodes/_shared/storyboard/validate.py` 的 `V.wid`（全角 1em、其余 0.62em，≤ `w − 16 − padLeft`），见 [validate.md](validate.md)。

CJK 一字大约等于 `fontSize` 像素。degradation 的实现是 `episodes/degradation/remotion/src/components/ui.tsx` 的 `textWidth`：码点大于 255 的字加 `fontSize`，ASCII 加 `fontSize * 0.58`，等宽加 `fontSize * 0.61`。换期先打开该期自己的 `textWidth`，系数以那份为准。

估算宽度大于元素的 `w`（组件有左右 padding 时先扣掉）就视为溢出风险，回到第 3 节看日志。

机器上若已有 `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`，可以用 PIL 量同一行。旧封面脚本 `episodes/db-index/cover/make_cover.py` 用的是 `ImageFont.truetype(..., index=2)`。字体文件不在就只用上面的估算，不要为质检去装字体，也不要新写脚本。

```sh
python3 - <<'PY'
from PIL import ImageFont
font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 48, index=2)
print(font.getlength("结算接口"))
PY
```

### 6. 图的位置和旁白一致

手工。读该镜的 `narration`、`direction` 和元素的 `x`、`y`。谁调用谁，调用方在箭头起点，被调用方在箭头终点。

曾经错过的一种画法：服务画在「浏览器」正下方，看起来像浏览器直接调用那些服务。EP.13 镜 2 的旁白是「浏览器只打一个结算接口，商品、地址、运费险，都是这个接口在后台依次去问」。现稿里「浏览器」在 `x=160`，「结算接口」在它右侧，三个服务从 `x=480` 接在结算接口下方，浏览器侧不直接连三个服务。对照该镜 `direction`。讲解图是 `frame: "canvas"`，不套浏览器壳。

### 7. 画面上的熔断、雪崩、半开

手工。在分镜元素的 `text`、封面元素的 `text`、`script.md` 的屏幕文字里搜这三个词。

本期脚本不是在讲这个词，画面上就不能出现。EP.13 讲熔断，片中可以有「熔断」，按该期 `script.md` 文首用词，仍然不能有「雪崩」和「半开」。只写进文章、片中不出现的分支留在 `article.mdx`。这条不改 [RULES.md](RULES.md)；词能不能上屏，以本期脚本和 RULES 的画面条为准。

### 8. 浏览器壳只给真网页

手工。对照 [RULES.md](RULES.md)。

- `shots[].frame` 为 `browser` 的镜头，内容是网页、地址栏或 DevTools，元素用 `BrowserChrome`（或该期等价的真网页壳），地址是 `.example`。
- 表、图、流程图是 `canvas`，不出现 `BrowserChrome`。
- 不出现假应用窗。旧期组件 `NotepadWindow` 不算通过。

`meta.style` 应与 `script.md` 文首的画面约定一致。`meta.devtoolsShots` 见第 12 节。

### 9. 页身色

手工。规则、分镜亮度、源码 grep 和成片采样都在 [validate.md](validate.md) 的「页身色」。通过以那一节为准：浅色 `background` / `fill` 不超过画布 5%，`#FFF` / `#FFFFFF` 不作超过 1% 的底，页身组件用 `PAGE.bg`，分镜里没有 `pageBg` / `pageInk` 字段；静帧页身没有大面积近白。

### 10. 第 0 帧就是钩子

手工。对照 [RULES.md](RULES.md) 的开头。

镜头 1 的成片绝对帧 0 同时有标题和冲突，是主体画面。不是黑屏，不是片头，不是自我介绍。前 2 秒（30 fps 时为 60 帧）只升级这个冲突，不把答案讲完。读该镜 `direction`，以及 `appearFrame` 为 0 的元素。静帧用第 3 节的 `frames.json` 里 `frame: 0` 那一张，文件在 `/tmp`。

### 11. 片尾顺序

手工。三段按这个顺序出现：

1. 讨论题，与 `meta.discussionQuestion` 逐字一致。
2. 下期预告，与 `meta.nextEpisode.teaser` 一致。
3. 关注句（旁白里的「关注我」或「关注、点赞、收藏」）跟到最后一镜镜尾。

degradation 是镜 `19-discussion`，然后镜 `20-next-episode` 里先预告、再关注句。讨论题和预告之间可以有本期脚本自己的收束句（EP.14 是「降级就讲到这里」），三段的先后不要对调。没有 `nextEpisode` 就不要编预告。不说「下期见」。见 [RULES.md](RULES.md) 仍然有效条。

### 12. boxShots 和 devtoolsShots

读 `meta.boxShots`、`meta.boxShotRule`、`meta.devtoolsShots`。`validate.py` 会核 `boxShots` 与 spec 的 `BOX_SHOTS`，以及 `devtoolsShots` 与 spec 的 `DEVTOOLS`。不超过 2 仍以 [RULES.md](RULES.md) 为准。

```sh
python3 - <<'PY'
import json
from pathlib import Path
sb = json.loads(Path("EPDIR/storyboard.json").read_text())
shots = [sh for sc in sb["scenes"] for sh in sc["shots"]]
print("boxShots", sb["meta"]["boxShots"])
print("flagged", [sh["id"] for sh in shots if sh.get("boxShot")])
print("rule", sb["meta"].get("boxShotRule"))
print("devtoolsShots", sb["meta"]["devtoolsShots"])
PY
```

通过：`boxShot: true` 的镜头 id 与 `meta.boxShots` 一致，并与 `boxShotRule` 的说法一致。`devtoolsShots` 不超过 2，且就是画面上真的打开 DevTools 的镜头。degradation 的 `devtoolsShots` 是空数组。上限见 [RULES.md](RULES.md)。

### 13. 帧数、涟漪、术语时长

各镜 `durationInFrames` 之和等于 spec 的 `WAVLEN`，点击到下一状态 ≥ 12，都在 `episodes/_shared/storyboard/validate.py`。细节见 [validate.md](validate.md)。`meta.durationInFrames`、各镜之和、`words.json` 的 `durationFrames` 三数相同，用下面这段。术语完整显示至少 63 帧仍没有通用脚本。

- `meta.durationInFrames` 等于各镜头 `durationInFrames` 之和，并等于 `words.json` 的 `durationFrames`。degradation 是 5152。
- 点击（带 `ripples` 的状态帧）到同一元素的下一状态 ≥ 12 帧（引擎的 `RIPPLE_MIN`，默认 12）。`growFrames` 仍与 `meta.timingSource` 一致（degradation 是 20）。见 [validate.md](validate.md)「点击和下一状态」。
- 术语标签完整显示至少 63 帧。

```sh
python3 - <<'PY'
import json
from pathlib import Path
D = Path("EPDIR")
sb = json.loads((D / "storyboard.json").read_text())
w = json.loads((D / "words.json").read_text())
shots = [sh for sc in sb["scenes"] for sh in sc["shots"]]
print(sum(sh["durationInFrames"] for sh in shots), sb["meta"]["durationInFrames"], w["durationFrames"])
PY
```

三数相同才通过。

### 14. 版式

先跑 [validate.md](validate.md)「分镜检查」。引擎已经覆盖：上一镜是 canvas 时，browser 镜第 1–8 帧不改 `view` / `pageBlank`；`CalloutTag` / `CornerBadge` 余量 ≥ 12；不缩字（`V.wid` ≤ `w − 16 − padLeft`）。冻结副本不在引擎里，仍用 [validate.md](validate.md)「冻结」那一节的只读比较。

下面这些不在引擎里。EP.14 写在 `episodes/_shared/storyboard/examples/degradation/validate_spec.py` 的 `checks`。换期要重写，不能当成引擎已经会查：

- [ ] browser 镜第 0 帧接上一个 browser 镜的标签和 `view`
- [ ] 子流程在父节点下方，且 `x` ≥ 父节点 `x`
- [ ] 同一个服务只有一个节点，箭头的 `pointsTo` 都指向它
- [ ] 有「核心链路」时，标签在核心元素正下方
- [ ] 页面注释离按钮 ≥ 16 px
- [ ] 冻结副本 `storyboard.<sha8>.json` 与 `storyboard.json` 逐字节相同

## 成片审

复核动态表达和实际编码结果，记录执行者、检查结果及能力限制。检查通过后按 STATUS 的持续授权发布 GitHub 站点，无需逐期用户批准；先核验冻结输入与待发布文件，再替换站点成片。缺失的 ASR 或人工听辨不得冒称完成，用户后续反馈按实际问题修正并重新检查、发布。

### 1. 帧数和时长

`ffprobe` 随本仓混音所用的 ffmpeg 一起用，不是仓库里的新脚本。

```sh
ffprobe -v error -select_streams v:0 \
  -show_entries stream=nb_frames,r_frame_rate,width,height -show_entries format=duration \
  -of json EPDIR/video.mp4
```

`nb_frames` 为空时改跑 `-count_frames`，读 `nb_read_frames`。

通过：帧数等于 `meta.durationInFrames`，也等于 `words.json` 的 `durationFrames`；宽高等于 `meta.width`、`meta.height`；时长约等于帧数除以 `meta.fps`。不要在分镜总帧数之外再加片尾，除非该期 `timingSource` 写明要加。见 [render.md](render.md)。

### 2. 响度

读该期 `remotion/out/mix-report.json`。degradation 的 `package.json` 把报告放在 `remotion/out/mix-report.json`，由 `episodes/_shared/music/mix_bgm.py` 在 `render:mix` 时写出。

字段：`final_LUFS`、`true_peak_dBTP`。规范见 [RULES.md](RULES.md)：成片 −16 LUFS，真峰值目标 −2.0 dBTP。脚本的 `loudnorm` 目标是 `I=-16`、`TP=-2.0`。

通过：报告存在；`final_LUFS` 在 −16 附近；`true_peak_dBTP` 不高于 −2.0。把这两个数抄进审片记录。没有报告就停。不要新写响度脚本，不要手改成片音量。

### 3. 三种封面，jpg 和 png 都打开

手工。16:9、4:3、3:4 各打开 jpg 和 png，六份都要看。degradation 期目录里的文件名是 `cover-16x9.jpg`、`cover-16x9.png`，4:3 和 3:4 同样。`poster.jpg` 与 `covers.json` 的 `poster` 一起对（degradation 注明海报与 3:4 同一构图）。

第 3 节 `--covers` 写出的是草稿名 `Cover16x9.png`、`Cover4x3.png`、`Cover3x4.png`，不能代替期目录里这六份。共享封面工程 `episodes/_shared/cover` 只出 jpg，而且不要对 degradation 跑。某一期缺 png 就记未齐。本仓没有把 png 转成这些 jpg 的系列脚本，见 [render.md](render.md)。不要为了补文件新写转码脚本。

看的时候核对 4:3 安全区和水印，字没有被切。

### 4. 重制时容易错的画面

手工。用成片或 `/tmp` 里的静帧看，不要只看分镜 json。至少包括：

- 第 0 帧钩子（第 10 节）
- 一个浏览器镜的页身色（[validate.md](validate.md)「页身色」）
- 有调用关系的讲解图：谁调用谁（第 6 节）
- 讨论题、预告、关注句的先后（第 11 节）
- 4:3 封面的 jpg 和 png（成片审第 3 节）

### 5. 发站点前对上冻结的 SHA

手工。制作源在 `episodes-codex/<slug>/`，站点读取 `episodes/<slug>/`。发布前核对两份 `video.mp4`、海报、`voice.wav`、`words.json` 与 `storyboard.json` 的完整 SHA-256，必须与检查通过的冻结文件一致；有用户批准文件时也使用同一份。对不上先修复，不以更新清单代替重新核验。做法与第 1 节相同，发布按 [publish.md](publish.md) 和 STATUS 的持续授权执行。

## 页身色

见 [validate.md](validate.md)「页身色」。分镜亮度、源码和成片采样在同一节，这里不另写一套数。
