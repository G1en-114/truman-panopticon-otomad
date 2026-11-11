# 楚门的圆形监狱（Truman's Panopticon）

音MAD 制作流水线：把电影《楚门的世界》（The Truman Show, 1998）的对白逐音节拆开，
用 WORLD 声码器重采样到稻叶昙（稲葉曇）《圆形监狱（パノプティコン / Panopticon）》的旋律上，
再配一套自动生成的 kinetic-collage PV。

> **本仓库包含自制脚本、文档、复现 PV 渲染所必需的贴纸素材与时间轴数据，以及音频制品
> （干声声部与最终混音）；不含片源、原曲、伴奏等任何受版权保护的原始素材**（见[版权声明](#版权声明)）。

## 流水线

| 阶段 | 脚本 / 工具 | 说明 |
| --- | --- | --- |
| 素材检索 / 下载 | `scripts/bili_search.py`、`scripts/dl.sh` | B 站 WBI 搜索（免登录）+ yt-dlp 下载参考音频 / PV |
| 转码 | ffmpeg | 片源转 `src/movie.mkv` / `movie.wav`，原曲与伴奏 |
| 语音转写 | `scripts/transcribe.py` | OpenAI Whisper（turbo, CUDA），词级时间戳 |
| 人声分离 | Demucs（`htdemucs_ft`） | 从电影音轨分离人声 |
| 强制对齐 | `scripts/align*.py`、`scripts/falign.py` | librosa onset + wav2vec2 CTC，逐音节对齐 |
| 歌词 / 采样规格 | `scripts/lyrics.py` | `SUNG` / `SPOKEN`：音节 ↔ 音符 ↔ 片段映射表 |
| 切片 | `scripts/prep_clips.py`、`clipwav.py`、`slice.py` | 按音节切出素材片段 |
| 唱段合成 | `scripts/synth.py` | pyworld（WORLD）重采样，输出干声 stems 与 `work/timeline.json` |
| 混音 | `scripts/mix.py` | 伴奏 + 唱段 + 念白 + FX → `out/audio_vN.wav` |
| QC | `scripts/qc_f0.py`、`qc_whisper.py`、`msheet.py`、`sheet.sh` | F0 复核、contact sheet 抽查 |
| 抠像 | `scripts/cutout.py`、`matte_isnet.py` | rembg（BiRefNet）/ IS-Net，产出 RGBA 贴纸 |
| 3D 素材 | `scripts/bl_assets.py` | Blender headless 渲染监控摄像头 / 穹顶序列帧 |
| PV 渲染 | `scripts/pv/` | skia-python 渲染引擎（见下） |
| 封面 | `scripts/pv/cover.py` | 生成封面 / 缩略图 |

## 音频是怎么做的

整首歌的人声全部来自电影对白，没有使用任何原唱人声。
流程是「分离 → 转写 → 对齐 → 重采样 → 混音」：

1. **人声分离**：ffmpeg 抽出电影音轨，Demucs（`htdemucs_ft`）分离出干净人声
   （`work/clips/dm/htdemucs_ft/all_raw/vocals.wav`，不入库），之后所有唱段素材都取自这条人声轨。
2. **转写与选段**：Whisper turbo 词级时间戳转写（`transcribe.py` → `work/whisper.json`）；
   人工挑选咬字清楚、语气合适的对白句写进 `scripts/lyrics.py` 的 `SUNG`（唱段）/ `SPOKEN`（念白）表，
   `prep_clips.py` 按表切出片段并登记到 `work/clips/index.json`。
3. **音节对齐**：`align*.py` 用 librosa onset 做粗对齐，`falign.py` 再用 wav2vec2 CTC 做逐音节强制对齐
   （`work/clips/align.json`），得到每个音节的元音起点 / 音节核 / 收尾——这是后面时间拉伸的锚点。
4. **歌词记谱**：`lyrics.py` 用一套记法把音节钉到 MIDI 音符上：空格 = 下一个词的下一个音符、
   `-` = 同词的下一个音符、`&` = 同音符拆成两个词、`+` = 同音符拆成两半、`~` = 延音、`_` = 该音符不唱；
   `PHRASES` 决定每段歌曲复用哪些片段、整体移多少半音。`synth.py` 会 assert 音节数与音符数严格对账。
5. **WORLD 重采样（`synth.py`）**：对每个片段做 WORLD 分析（`harvest` 提 F0 → `stonemask` 精修 →
   `cheaptrick` 谱包络 → `d4c` 非周期性），再逐音节把源时间轴映射到目标音符：
   元音起点对准音符起点，按拉伸比分三档处理（近似原速时保留协同发音的自然拉伸、
   音符更长时保持元音中心、素材过长时只保留起始段），谱包络随映射后的时间轴插值重采样；
   音高替换为 MIDI 音符，并叠加修饰——portamento 平滑、长音 5.4 Hz 颤音、按比例保留原对白的
   音高起伏（角色可调）、慢随机漂移（约 ±10 音分）。每个角色有声部配置：Christof 唱
   lead + harm + 低八度 sub，Sylvia 唱 lead + harm + 高八度 up，其余角色 lead。
   产出 `work/stems/{lead,harm,sub,up}.wav` 干声与 `work/timeline.json`（PV 用的逐音节时间轴）。
6. **混音（`mix.py`）**：伴奏取 off-vocal 版并做编排处理——开头模拟小电视喇叭（带通 + tanh 失真），
   清唱段静音伴奏，正拍全奏进入；人声链为高通 + presence EQ + 压缩，harm/up 声部用 Haas 微延迟
   加宽，句尾叠八分音符回声与合成 IR 混响；念白按剧情点穿插，做角色化处理
   （Christof 是「天空之声」的 PA 音色、Truman 开场念白过电视喇叭、片尾欢呼直接用原始电影声轨限带）；
   最后人声对伴奏做侧链闪避与中频让位，过限幅器输出 `out/audio_v1.wav`，
   同时把念白时间表写进 `work/spoken.json`（PV 字幕同步用）。

复现完整音频需要自备电影音频与伴奏（不入库）；若只想重混音 / 研究效果器链，
入库的四个干声声部已可直接喂给 `mix.py` 的对应部分。

### PV 渲染引擎（`scripts/pv/`）

- `core.py` — 时间轴（拍 ↔ 秒）、缓动、字幕、素材与后期工具
- `kit.py` — 共享绘制件：歌词弹字、字幕、HUD、圆形监狱蓝图
- `lib.py` — 拼贴素材库：抠像贴纸与短片循环，统一调色
- `motion.py` — 动效引擎 v2：关键帧世界摄像机（子帧运动模糊）、3D 平面、转场
- `scenes_a/b/c.py`、`v2_a/b/c.py` — 分段场景（v2 为 kinetic collage 版）
- `render.py` / `render2.py` — 静帧预览与整片渲染，输出 `out/`
- `cover.py` — 封面

## 目录约定

```
scripts/   流水线脚本（入库）
src/       片源、原曲、伴奏（需自备，不入库）
ref/       参考音频 / PV（需自备，不入库）
work/      中间产物：整片音频分离、切片等（不入库；
           例外入库：timeline.json / spoken.json（时间轴）、whisper.json（转写）、
           clips/index.json + align.json（片段索引与音节对齐）、stems/ 四个干声声部）
assets/    cut/ 抠像贴纸与序列帧、gen/ 生成素材、fonts/ 字体（入库，见版权声明）
out/       成品（例外入库：audio_v1.wav 最终混音；视频 / 封面不入库）
tools/     Blender 等第三方工具（不入库）
```

脚本中的路径均按上述布局编写；换目录时需相应调整。

## 依赖

- Python 3.12+（见 `requirements.txt`）
- ffmpeg、yt-dlp
- Blender 5.x（headless，仅 3D 素材环节需要）
- NVIDIA GPU + CUDA（Whisper / wav2vec2 / Demucs / rembg / onnxruntime-gpu）

## 使用

1. 自备素材放到对应目录：电影片源与原曲 / 伴奏（`src/`）、B 站「音MAD用」MIDI（仓库根目录，脚本内引用其文件名）。
2. 安装依赖后，按「流水线」表的顺序执行脚本；各脚本头部注释有用法。
3. 最终混音在 `out/audio_vN.wav`，PV 在 `out/`（`scripts/pv/render2.py video`）。

## 版权声明

- 本仓库的自制脚本与文档以 [Apache License 2.0](LICENSE) 授权；`assets/gen/` 为自制生成素材，同样按 Apache-2.0 授权。
- 本工程使用的**原素材均属于原版权所有人**，包括但不限于：
  - 电影《楚门的世界》（The Truman Show）的画面与对白（© 其版权所有方）。`assets/cut/`
    下的抠像贴纸与序列帧均截取 / 衍生自该电影画面，`work/stems/` 的干声声部与
    `out/audio_v1.wav` 中的人声部分均重采样自该电影对白，入库仅为复现与展示之需，
    相应版权归原版权所有人；
  - 稻叶昙（稲葉曇）《圆形监狱（パノプティコン）》原曲、伴奏及第三方制作的音MAD用 MIDI（© 其版权所有方），
    `out/audio_v1.wav` 中的伴奏部分亦来自该伴奏音源；
  - 参考所用的 B 站音视频内容（© 各自创作者）。
- `assets/fonts/` 下的字体（Anton、Bodoni Moda、Playfair Display、Space Mono）来自
  [Google Fonts](https://fonts.google.com/)，按 SIL Open Font License 1.1 授权，附各自版权与许可声明。
- 仓库不收录片源、原曲、伴奏、MIDI、整片音频及其人声分离结果；如需完整复现请自行取得素材。
- 本工程为个人兴趣的二次演绎创作，与上述版权方无任何关联。
