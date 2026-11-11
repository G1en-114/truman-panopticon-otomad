# 楚门的圆形监狱（Truman's Panopticon）

音MAD 制作流水线：把电影《楚门的世界》（The Truman Show, 1998）的对白逐音节拆开，
用 WORLD 声码器重采样到稻叶昙（稲葉曇）《圆形监狱（パノプティコン / Panopticon）》的旋律上，
再配一套自动生成的 kinetic-collage PV。

> **本仓库包含自制脚本、文档，以及复现 PV 渲染所必需的贴纸素材与时间轴数据；不含片源、原曲、伴奏等任何受版权保护的原始素材**（见[版权声明](#版权声明)）。

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
work/      中间产物：转写、对齐、切片、stems（不入库；
           例外：timeline.json / spoken.json 为渲染所需的时间轴数据，入库）
assets/    cut/ 抠像贴纸与序列帧、gen/ 生成素材、fonts/ 字体（入库，见版权声明）
out/       成品音频 / 视频 / 封面（不入库）
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
    下的抠像贴纸与序列帧均截取 / 衍生自该电影画面，入库仅为复现 PV 渲染之需，版权归原版权所有人；
  - 稻叶昙（稲葉曇）《圆形监狱（パノプティコン）》原曲、伴奏及第三方制作的音MAD用 MIDI（© 其版权所有方）；
  - 参考所用的 B 站音视频内容（© 各自创作者）。
- `assets/fonts/` 下的字体（Anton、Bodoni Moda、Playfair Display、Space Mono）来自
  [Google Fonts](https://fonts.google.com/)，按 SIL Open Font License 1.1 授权，附各自版权与许可声明。
- 仓库不收录片源、原曲、伴奏、MIDI 及音频中间产物；如需复现请自行取得素材。
- 本工程为个人兴趣的二次演绎创作，与上述版权方无任何关联。
