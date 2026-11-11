"""Rendering toolkit for the PV: timing, easing, type, footage, textures, post."""
import os, json, math, functools
import numpy as np, cv2, skia

W, H, FPS = 1920, 1080, 30
SPB = 0.344828; PRE = 16
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def b2t(b): return (b + PRE) * SPB
def t2b(t): return t / SPB - PRE

PAPER = (236, 232, 223); INK = (20, 18, 16); RED = (214, 38, 30); WHITE = (250, 248, 242); BLACK = (8, 8, 9)
GREY = (120, 116, 110)
def col(rgb, a=1.0): return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(max(0, min(1, a)) * 255))
def mixc(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))

# ---------------------------------------------------------------- easing
def c01(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)
def lin(t, a, b): return c01((t - a) / (b - a)) if b != a else float(t >= b)
def out_cubic(x): x = c01(x); return 1 - (1 - x) ** 3
def out_quint(x): x = c01(x); return 1 - (1 - x) ** 5
def out_expo(x): x = c01(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def in_cubic(x): x = c01(x); return x ** 3
def in_out(x): x = c01(x); return 3 * x * x - 2 * x ** 3
def out_back(x, s=1.70158): x = c01(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def pulse(t, t0, decay=0.18): return math.exp(-(t - t0) / decay) if t >= t0 else 0.0
def rnd(seed):  # deterministic hash -> [0,1)
    x = math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - math.floor(x)

# ---------------------------------------------------------------- fonts
F = os.path.join(ROOT, 'assets', 'fonts')
_FILES = dict(serif=F + '/Playfair.ttf', serifi=F + '/PlayfairItalic.ttf', bodoni=F + '/BodoniModa.ttf',
              anton=F + '/Anton-Regular.ttf', mono=F + '/SpaceMono-Regular.ttf', monob=F + '/SpaceMono-Bold.ttf',
              cn='/usr/share/fonts/adobe-source-han-serif/SourceHanSerifCN-Medium.otf',
              cnb='/usr/share/fonts/adobe-source-han-serif/SourceHanSerifCN-Heavy.otf',
              cnl='/usr/share/fonts/adobe-source-han-serif/SourceHanSerifCN-Light.otf',
              jpb=('/usr/share/fonts/noto-cjk/NotoSansCJK-Black.ttc', 0))
_TAG = 0x77676874
@functools.lru_cache(None)
def typeface(name, wght=None):
    fp = _FILES[name]
    tf = skia.Typeface.MakeFromFile(*fp) if isinstance(fp, tuple) else skia.Typeface.MakeFromFile(fp)
    if wght is not None:
        C = skia.FontArguments.VariationPosition.Coordinate
        fa = skia.FontArguments()
        fa.setVariationDesignPosition(skia.FontArguments.VariationPosition(
            skia.FontArguments.VariationPosition.Coordinates([C(axis=_TAG, value=float(wght))])))
        tf = tf.makeClone(fa)
    return tf
@functools.lru_cache(4096)
def font(name, size, wght=None):
    f = skia.Font(typeface(name, wght), size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
    return f
def text_w(s, f, tracking=0.0):
    return f.measureText(s) + tracking * max(0, len(s) - 1)

def draw_text(c, s, x, y, f, color=INK, anchor='l', alpha=1.0, tracking=0.0, stroke=0.0, blur=0.0):
    """baseline at y. anchor l|c|r"""
    if alpha <= 0 or not s: return 0
    w = text_w(s, f, tracking)
    if anchor == 'c': x -= w / 2
    elif anchor == 'r': x -= w
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha))
    if stroke > 0: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    if blur > 0: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if tracking == 0: c.drawString(s, x, y, f, p)
    else:
        cx = x
        for ch in s:
            c.drawString(ch, cx, y, f, p); cx += f.measureText(ch) + tracking
    return w

def draw_text_arc(c, s, cx, cy, r, a0, f, color=INK, alpha=1.0, tracking=0.0, inward=False, center=True):
    """text along a circle; a0 (deg, 0 = top, clockwise) is the centre (or start) angle."""
    if alpha <= 0: return
    ws = [f.measureText(ch) + tracking for ch in s]; tot = sum(ws)
    ang = math.radians(a0) - (tot / r / 2 if center else 0)
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha))
    for ch, w in zip(s, ws):
        am = ang + (w / 2) / r
        c.save(); c.translate(cx + r * math.sin(am), cy - r * math.cos(am)); c.rotate(math.degrees(am) + (180 if inward else 0))
        c.drawString(ch, -(w - tracking) / 2, 0, f, p); c.restore()
        ang += w / r

def rect(c, x, y, w, h, color, alpha=1.0, stroke=0.0, r=0.0):
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha))
    if stroke > 0: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    if r > 0: c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, p)
    else: c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)
def circle(c, x, y, r, color, alpha=1.0, stroke=0.0):
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha))
    if stroke > 0: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    c.drawCircle(x, y, r, p)
def line(c, x0, y0, x1, y1, color, w=2.0, alpha=1.0, dash=None):
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha), StrokeWidth=w, Style=skia.Paint.kStroke_Style)
    if dash: p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    c.drawLine(x0, y0, x1, y1, p)
def arc(c, cx, cy, r, a0, sweep, color, w=2.0, alpha=1.0, dash=None):
    """a0 deg from top clockwise"""
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha), StrokeWidth=w, Style=skia.Paint.kStroke_Style)
    if dash: p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    c.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), a0 - 90, sweep, False, p)

# ---------------------------------------------------------------- footage
class Movie:
    """frame-accurate-ish access to the movie (top 1280x600, subtitles cropped away)."""
    def __init__(self, path=os.path.join(ROOT, 'src', 'movie.mkv')):
        self.path = path; self.caps = {}; self.fps = None; self.still = {}
    def _cap(self, key):
        if key not in self.caps:
            cap = cv2.VideoCapture(self.path); self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.caps[key] = [cap, -1, None]
        return self.caps[key]
    def raw(self, t, key='a'):
        st = self._cap(key); cap, pos, last = st
        n = int(round(t * self.fps))
        if n == pos and last is not None: return last
        if not (pos < n <= pos + 40):
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, n - 1)); pos = max(0, n - 1) - 1
            ok, fr = cap.read(); pos += 1
        while pos < n:
            ok, fr = cap.read(); pos += 1
            if not ok: break
        if fr is None: fr = np.zeros((720, 1280, 3), np.uint8)
        fr = fr[:600]
        st[1] = n; st[2] = fr
        return fr
    def get_still(self, t):
        k = round(t, 2)
        if k not in self.still: self.still[k] = self.raw(t, key='still').copy()
        return self.still[k]
MOVIE = Movie()

def grade(fr, mode='bw', lo=INK, hi=PAPER, gamma=1.0, contrast=1.25, sat=1.0):
    """BGR uint8 -> RGBA uint8.  mode bw: duotone lo->hi.  mode color: mild grade."""
    if mode == 'color':
        x = fr[:, :, ::-1].astype(np.float32) / 255
        g = x.mean(2, keepdims=True); x = g + (x - g) * sat
        x = np.clip((x - 0.5) * contrast + 0.5, 0, 1) ** gamma
        out = (x * 255).astype(np.uint8)
    else:
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        g = np.clip((g - 0.45) * contrast + 0.5, 0, 1) ** gamma
        lo = np.array(lo, np.float32); hi = np.array(hi, np.float32)
        out = (lo + (hi - lo) * g[:, :, None]).astype(np.uint8)
    a = np.full(out.shape[:2] + (1,), 255, np.uint8)
    return np.ascontiguousarray(np.concatenate([out, a], 2))
def to_img(rgba): return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)

def draw_img(c, img, x, y, w, h, alpha=1.0, shape='rect', r=0.0, zoom=1.0, fx=0.5, fy=0.5):
    """cover-fit img into rect (x,y,w,h); shape rect|round|circle|ellipse"""
    if alpha <= 0 or w <= 1 or h <= 1: return
    iw, ih = img.width(), img.height()
    s = max(w / iw, h / ih) * zoom
    sw, sh = w / s, h / s
    sx = (iw - sw) * fx; sy = (ih - sh) * fy
    c.save()
    dst = skia.Rect.MakeXYWH(x, y, w, h)
    if shape == 'circle' or shape == 'ellipse':
        pth = skia.Path(); pth.addOval(dst); c.clipPath(pth, True)
    elif shape == 'round': c.clipRRect(skia.RRect.MakeRectXY(dst, r, r), True)
    else: c.clipRect(dst, True)
    p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
    c.drawImageRect(img, skia.Rect.MakeXYWH(sx, sy, sw, sh), dst, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()

def footage(c, t_movie, x, y, w, h, key='a', mode='bw', alpha=1.0, shape='rect', r=0.0, zoom=1.0, fx=0.5, fy=0.5, still=False, **gk):
    fr = MOVIE.get_still(t_movie) if still else MOVIE.raw(t_movie, key)
    draw_img(c, to_img(grade(fr, mode, **gk)), x, y, w, h, alpha, shape, r, zoom, fx, fy)

# ---------------------------------------------------------------- textures
def _fbm(h, w, seed, octaves=6):
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = 2 ** (o + 2)
        g = r.random((n * h // w + 2, n + 2), dtype=np.float32)
        out += cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC) * amp; tot += amp; amp *= 0.55
    return out / tot
@functools.lru_cache(None)
def paper_tex(seed=1, dark=False):
    h, w = H + 160, W + 160
    n = _fbm(h, w, seed); n = (n - n.mean()) / (n.std() + 1e-6)
    r = np.random.default_rng(seed + 9)
    fine = cv2.GaussianBlur(r.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.1)
    fib = cv2.GaussianBlur(r.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=9, sigmaY=0.7)
    v = n * 5.5 + fine * 5.0 + fib * 5.0
    # a few stains / scratches
    for _ in range(26):
        x0, y0 = r.integers(0, w), r.integers(0, h); L = r.integers(40, 420); a = r.uniform(0, math.pi)
        cv2.line(v, (int(x0), int(y0)), (int(x0 + L * math.cos(a)), int(y0 + L * math.sin(a))), float(v.mean() - r.uniform(5, 14)), 1, cv2.LINE_AA)
    base = np.array(BLACK if dark else PAPER, np.float32)
    k = 0.55 if dark else 1.0
    img = np.clip(base[None, None, :] + v[:, :, None] * k, 0, 255).astype(np.uint8)
    rgba = np.ascontiguousarray(np.concatenate([img, np.full((h, w, 1), 255, np.uint8)], 2))
    return to_img(rgba)
def paper(c, t, seed=1, dark=False, drift=1.0):
    img = paper_tex(seed, dark)
    ox = -80 + 30 * math.sin(t * 0.21 * drift + seed); oy = -80 + 30 * math.cos(t * 0.17 * drift + seed * 2)
    c.drawImage(img, ox, oy)

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_rr = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
VIG = np.clip(1 - 0.34 * np.clip(_rr - 0.55, 0, 1) ** 1.6, 0, 1)[:, :, None].astype(np.float32)
_GR = [np.random.default_rng(100 + i).normal(0, 1, (H // 2, W // 2)).astype(np.float32) for i in range(8)]
_SCAN = (0.94 + 0.06 * np.cos(np.arange(H) * math.pi))[:, None, None].astype(np.float32)

def post(rgba, frame, grain=7.0, vig=1.0, chroma=0.0, scan=0.0, shake=(0, 0), invert=0.0, flash=0.0, glitch=0.0, seed=0,
         zblur=0.0, zc=(W / 2, H / 2), slice_=0.0, tvoff=0.0, tvon=None, **_):
    """numpy RGBA uint8 -> RGB uint8 with grain / vignette / chromatic aberration / scanlines / glitch / zoom blur / slice / CRT off"""
    x = rgba[:, :, :3].astype(np.float32)
    if zblur > 0.004:
        acc = x.copy(); K = 7
        for k in range(1, K):
            s = 1 + zblur * k / (K - 1)
            M = np.float32([[s, 0, zc[0] * (1 - s)], [0, s, zc[1] * (1 - s)]])
            acc += cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        x = acc / K
    if slice_ > 0:
        r = np.random.default_rng(seed * 31 + frame // 2)
        y = 0
        while y < H:
            hh = int(r.integers(30, 200)); dx = int((r.random() * 2 - 1) * slice_ * 420)
            x[y:y + hh] = np.roll(x[y:y + hh], dx, 1); y += hh
    if invert > 0: x = x + (255 - 2 * x) * invert
    if shake != (0, 0):
        M = np.float32([[1, 0, shake[0]], [0, 1, shake[1]]]); x = cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if chroma > 0.3:
        d = int(round(chroma))
        x[:, :, 0] = np.roll(x[:, :, 0], d, 1); x[:, :, 2] = np.roll(x[:, :, 2], -d, 1)
    if glitch > 0:
        r = np.random.default_rng(seed * 977 + frame)
        for _ in range(int(3 + glitch * 9)):
            y0 = int(r.integers(0, H - 8)); hh = int(r.integers(4, 10 + int(60 * glitch))); dx = int(r.integers(-1, 2) * r.integers(10, 30 + int(160 * glitch)))
            x[y0:y0 + hh] = np.roll(x[y0:y0 + hh], dx, 1)
            if r.random() < 0.35: x[y0:y0 + hh, :, 1:] *= 0.55
    if vig > 0: x *= (1 - vig) + vig * VIG
    if scan > 0: x *= (1 - scan) + scan * _SCAN
    if grain > 0:
        g = cv2.resize(_GR[frame % 8], (W, H), interpolation=cv2.INTER_LINEAR)
        if (frame // 8) % 2: g = g[::-1, ::-1]
        x += g[:, :, None] * grain
    if flash > 0: x = x + (255 - x) * flash
    for k in ([tvoff] if tvoff > 0 else []) + ([1 - tvon] if tvon is not None and tvon < 1 else []):
        # CRT collapse: squash to a bright line, then to a dot
        ky = c01(k / 0.6); kx = c01((k - 0.6) / 0.4)
        hh = max(2, int(H * (1 - ky) ** 2)); ww = max(2, int(W * (1 - kx) ** 1.5))
        small = cv2.resize(x, (ww, hh), interpolation=cv2.INTER_AREA) * (1 + 1.5 * ky) + 120 * ky
        out = np.zeros_like(x); y0 = (H - hh) // 2; x0 = (W - ww) // 2
        out[y0:y0 + hh, x0:x0 + ww] = small
        if k >= 1: out[:] = 0
        x = out
    return np.clip(x, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- lyric timeline
def load_timeline():
    tl = json.load(open(os.path.join(ROOT, 'work', 'timeline.json')))
    sp = json.load(open(os.path.join(ROOT, 'work', 'spoken.json')))
    words = []; cur = None
    for tk in tl['tokens']:
        if tk.get('nw', True) or cur is None or cur['cid'] != tk['cid']:
            cur = dict(cid=tk['cid'], text=tk['syl'], t=tk['t'], end=tk['end'], spk=tk['spk'], phrase=tk['phrase'], syl=[tk]); words.append(cur)
        else:
            cur['text'] += tk['syl']; cur['end'] = tk['end']; cur['syl'].append(tk)
    return tl, sp, words
