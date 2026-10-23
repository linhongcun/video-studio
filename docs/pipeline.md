# 做片流程

从调研做到站点发版。命令只列仓库里真实存在的脚本。某一步没有脚本时写成待补，参考实现是 `episodes/degradation`（分镜 `meta.slug` 为 `degradation-v1`）。开新期的目录说明在 [../episodes-codex/_template/README.md](../episodes-codex/_template/README.md)。规范在 [RULES.md](RULES.md)。

EP.14 之后暂停。STATUS 改掉之前，做到「对照参考实现」为止，不要开新目录、不要重渲。

## 检查清单

- [ ] 调研笔记里的每条事实都有公开链接和访问日期
- [ ] `script.md`、`article.mdx`、`pronunciation.md` 三条主线一致
- [ ] `storyboard.json`、`covers.json` 冻结，并写上配音 SHA-256
- [ ] `words.json` 的 `scriptSha256`、`audioSha256` 与文件一致
- [ ] Deming 预检：起音窗口、无 `COPYFIT`、封面 4:3 安全区
- [ ] `video.mp4` 与封面由当期 `package.json` 的脚本产出
- [ ] Nolan 与 Deming 审过成片
- [ ] 村长 widget 批准上线
- [ ] 站点 PR 合并、`site/package.json` 升版本、tag 与 Release
- [ ] 抖音（头条同步）、B站、微信视频号；没有快手，没有 X；链接没有发到群里

## 1. 调研

交付物：公开出处清单。本仓没有统一的 `research.md` 文件名。`episodes/degradation/script.md` 把片外事实放在文首「文章提醒」，`episodes/degradation/article.mdx` 用脚注写链接和访问日期。新期沿用这个写法。格式见 [research-template.md](research-template.md)。

内部 handoff、旧分镜、对话不能当引用。

## 2. 脚本

交付物：

| 文件 | 作用 |
|---|---|
| `script.md` | 旁白、画面、屏幕文字、出处。旁白以「旁白：」为准 |
| `article.mdx` | 站点文章。前置信息见 degradation：`title`、`summary`、`chapters`、`related` |
| `pronunciation.md` | 多音字和整词读法，三列表：文本、读法、出现镜号 |

degradation 的脚本写明旧比喻作废、一条主线、术语在口播到时才上屏。画面约定（browser / canvas、示例域名、DevTools 次数）写在 `script.md` 文首，并原样进分镜 `meta.style`。

`plan.md` 只在部分旧期出现。degradation 脚本写的是「无单独 plan」。不要为了凑文件新建 `plan.md`。

## 3. 分镜与封面

交付物：

| 文件 | 作用 |
|---|---|
| `storyboard.json` | 镜头、字幕、配音区间、元素。字段见 [storyboard-schema.md](storyboard-schema.md) |
| `covers.json` | 16:9 / 4:3 / 3:4。重制期由本期 `remotion/src/Cover.tsx` 经别名 `@covers` 读取 |
| `knoll-props.md` | 待补。`episodes/degradation/storyboard.json` 的 `assets.procedural.description` 指向它，本仓没有这份文件。新页型以 `episodes/degradation/remotion/src/components/` 里实际使用的组件为准 |

参考镜头：`episodes/degradation` 共 6 个 `scenes`、20 个 `shots`，`meta.durationInFrames` 为 5152，`fps` 30，`frame` 只有 `browser` 和 `canvas`。

## 4. 配音

交付物：`remotion/public/audio/voice.wav`、`words.json`，以及分镜里每个镜头的 `voice` / `timing`。细节见 [voice.md](voice.md)。

本仓能直接调用的合成命令只有逐句 TTS：

```sh
python3 episodes/_shared/tts/mimo_say.py --text "一句带句号的旁白。" --out /tmp/line.wav --voice 冰糖 --gap 0.28 --segments /tmp/line.json
```

密钥读环境变量 `MIMO_API_KEY`，或 `--env` 指向的文件（默认 `/workspace/video-studio/.mimo.env`，不在仓库里）。不要把密钥写进仓库。

把逐句 wav 铺成整轨、写 `words.json`、写 `voice/shot_frames.json` 的脚本不在本仓。分镜 `timingSource` 和 `Main.tsx` 提到 `voice/place_v2.py`、`voice/shot_frames.json`、`voice/lastword_fix.py`。待补：见最新一期 knoll-props。铺轨完成前不要渲染成片。

## 5. 冻结 SHA-256

`episodes/degradation/words.json` 用全文：

- `scriptSha256`：脚本旁白所依据的文本
- `audioSha256`：`voice.wav`

`storyboard.json` 的 `meta.timingSource` 和每个镜头的 `timing.source` 写前缀，例如 `voice.wav 9e70470c`、`words.json 36bccee8`。

EP.02 把整份分镜的全文 SHA-256 写死在 `episodes/https/remotion/scripts/verify-storyboard.tsx`。那是该期回归，不是全系列脚本。

本仓没有统一的冻结脚本。核对时用与上述文件相同的 SHA-256（`hashlib.sha256`，见 `verify-storyboard.tsx` 和 `episodes/http-request/validate_v6.py`）。前缀对不上就停止，不要渲染。

## 6. Deming 预检

见 [validate.md](validate.md)。预检不过就改分镜或配音，然后回到第 5 步重新冻结。

## 7. 渲染

见 [render.md](render.md)。参考实现：

```sh
cd episodes/degradation/remotion
npm ci
npm run render
```

`npm run render` 先出 `out/voice.mp4`，再调用 `episodes/_shared/music/mix_bgm.py`，得到 `episodes/degradation/video.mp4`。

封面走本期的 `Cover16x9` / `Cover4x3` / `Cover3x4`，不要对 degradation 运行 `episodes/_shared/cover` 的 `npm run covers`：它的分镜没有顶层 `cover`，`covers/cover-spec.json` 里也没有 `degradation`。

## 8. 成片审与上线

Nolan 和 Deming 看成片。通过之后，村长用单选 widget 批准上线。然后按 [publish.md](publish.md) 改 `episodes/<slug>/meta.json`、开站点 PR、打 tag、发 Release、发三个平台。

站点只改页面、不重发平台时，沿用 v0.45.0 的做法：PR 说明写「只上站点」，Release 同样写明，平台链接保持不动。
