"""Collage asset library: cut-out stickers (RGBA png) and short cut-out loops, stylised to the PV palette."""
import os, glob, functools, math
import numpy as np, cv2, skia
from core import *

CUT = os.path.join(ROOT, 'assets', 'cut')

@functools.lru_cache(None)
def _load(name):
    p = os.path.join(ROOT, 'assets', 'gen', name[4:] + '.png') if name.startswith('gen:') else os.path.join(CUT, name + '.png')
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None: raise FileNotFoundError(p)
    if im.shape[2] == 3: im = np.concatenate([im, np.full(im.shape[:2] + (1,), 255, np.uint8)], 2)
    return cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)

def _halftone(g, cell=7, ang=45):
    """g float 0..1 (1 = paper) -> ink coverage 0..1 via a rotated dot screen"""
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(ang); u = xx * math.cos(a) - yy * math.sin(a); v = xx * math.sin(a) + yy * math.cos(a)
    scr = (np.cos(u * 2 * math.pi / cell) * np.cos(v * 2 * math.pi / cell) + 1) / 2     # 0..1
    return np.clip(((1 - g) - scr) * 6 + 0.5, 0, 1)

def stylise(rgba, style, lo=INK, hi=PAPER, accent=RED):
    rgb = rgba[:, :, :3].astype(np.float32) / 255; a = rgba[:, :, 3:].astype(np.float32) / 255
    if style == 'raw': out = rgb
    else:
        g = rgb.mean(2)
        if style in ('bw', 'duo'):
            g = np.clip((g - 0.5) * 1.25 + 0.52, 0, 1)
            out = np.array(lo, np.float32)[None, None] / 255 * (1 - g[..., None]) + np.array(hi, np.float32)[None, None] / 255 * g[..., None]
        elif style == 'red':
            g = np.clip((g - 0.5) * 1.35 + 0.5, 0, 1)
            out = np.array(BLACK, np.float32)[None, None] / 255 * (1 - g[..., None]) + np.array(accent, np.float32)[None, None] / 255 * g[..., None]
        elif style.startswith('ht'):          # ht / ht_red / ht_white : halftone print
            cell = 6 if rgba.shape[1] < 900 else 8
            ink = _halftone(np.clip((g - 0.5) * 1.3 + 0.55, 0, 1), cell)
            inkc = {'ht': lo, 'ht_red': accent, 'ht_white': (240, 236, 228)}[style]
            paperc = {'ht': hi, 'ht_red': hi, 'ht_white': BLACK}[style]
            out = (np.array(paperc, np.float32)[None, None] * (1 - ink[..., None]) + np.array(inkc, np.float32)[None, None] * ink[..., None]) / 255
        elif style == 'tint':                 # hand-tinted postcard look: keep colour, lift towards paper
            g3 = rgb.mean(2, keepdims=True); out = np.clip(g3 + (rgb - g3) * 0.75, 0, 1) * 0.85 + np.array(PAPER, np.float32)[None, None] / 255 * 0.15
        else: raise ValueError(style)
    return np.concatenate([np.clip(out * 255, 0, 255).astype(np.uint8), (a * 255).astype(np.uint8)], 2)

def bordered(rgba, border, color=WHITE, shadow=0):
    """add a cut-paper margin around the alpha shape (+ optional soft drop shadow baked in)"""
    pad = border + shadow * 3 + 4
    im = cv2.copyMakeBorder(rgba, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    a = im[:, :, 3]
    out = np.zeros_like(im)
    if shadow > 0:
        sh = cv2.GaussianBlur(cv2.dilate(a, np.ones((3, 3), np.uint8), iterations=max(1, border // 2)), (0, 0), shadow)
        M = np.float32([[1, 0, shadow * 0.8], [0, 1, shadow * 1.2]])
        sh = cv2.warpAffine(sh, M, (sh.shape[1], sh.shape[0]))
        out[:, :, 3] = (sh * 0.45).astype(np.uint8)
    if border > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border + 1, 2 * border + 1))
        m = cv2.dilate((a > 40).astype(np.uint8) * 255, k)
        m = cv2.GaussianBlur(m, (0, 0), 0.8)
        mf = m.astype(np.float32) / 255
        for ch in range(3): out[:, :, ch] = (out[:, :, ch] * (1 - mf) + color[ch] * mf).astype(np.uint8)
        out[:, :, 3] = np.maximum(out[:, :, 3], m)
    af = im[:, :, 3:].astype(np.float32) / 255
    out[:, :, :3] = (out[:, :, :3] * (1 - af) + im[:, :, :3] * af).astype(np.uint8)
    out[:, :, 3] = np.maximum(out[:, :, 3], im[:, :, 3])
    return out

@functools.lru_cache(256)
def sticker_img(name, style='bw', border=0, shadow=0, maxw=1600, bcol=WHITE):
    im = _load(name)
    if im.shape[1] > maxw: im = cv2.resize(im, (maxw, int(im.shape[0] * maxw / im.shape[1])), interpolation=cv2.INTER_AREA)
    im = stylise(im, style)
    if border or shadow: im = bordered(im, border, bcol, shadow)
    # premultiply for skia
    a = im[:, :, 3:].astype(np.float32) / 255
    pm = np.concatenate([(im[:, :, :3] * a).astype(np.uint8), im[:, :, 3:]], 2)
    return skia.Image.fromarray(np.ascontiguousarray(pm), colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)

def sticker(c, name, x, y, h=None, w=None, rot=0.0, alpha=1.0, style='bw', border=0, shadow=0, ax=0.5, ay=0.5, flip=False, maxw=1600, sx=1.0, bcol=WHITE):
    """draw sticker with anchor (ax, ay) at (x, y); give target height h or width w"""
    if alpha <= 0: return
    try: img = sticker_img(name, style, border, shadow, maxw, bcol)
    except FileNotFoundError:          # placeholder while the cut-out is not ready
        hh = h or (w or 300); ww = w or hh
        c.save(); c.translate(x, y); c.rotate(rot)
        rect(c, -ww * ax, -hh * ay, ww, hh, (150, 150, 150), alpha * 0.6)
        draw_text(c, name, -ww * ax + 10, -hh * ay + 40, font('mono', 30), (255, 0, 255), 'l', alpha)
        c.restore(); return
    iw, ih = img.width(), img.height()
    s = (h / ih) if h is not None else ((w / iw) if w is not None else 1.0)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s * sx * (-1 if flip else 1), s)
    p = skia.Paint(AntiAlias=True); p.setAlphaf(min(1.0, alpha))
    c.drawImage(img, -iw * ax, -ih * ay, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    c.restore()

def size(name):
    im = _load(name); return im.shape[1], im.shape[0]

# ---------------------------------------------------------------- cut-out loops (stop motion)
@functools.lru_cache(None)
def seq_frames(name):
    return sorted(glob.glob(os.path.join(CUT, 'seq', name, '*.png')))

def seq_name(name, t, fps=12, loop=True, t0=0.0):
    fr = seq_frames(name)
    if not fr: return 'seq/' + name + '/missing'
    i = int(max(0, t - t0) * fps)
    i = i % len(fr) if loop else min(i, len(fr) - 1)
    return 'seq/' + name + '/' + os.path.splitext(os.path.basename(fr[i]))[0]

def seq(c, name, t, x, y, fps=12, loop=True, t0=0.0, **kw):
    sticker(c, seq_name(name, t, fps, loop, t0), x, y, **kw)
