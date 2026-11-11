"""Motion engine v2: keyframed world camera (with sub-frame motion blur), 3D planes, kinetic glyphs, transition devices."""
import math, functools
import numpy as np, cv2, skia
from core import *

# ---------------------------------------------------------------- easing / tracks
def in_expo(x): x = c01(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def io_expo(x):
    x = c01(x)
    if x <= 0 or x >= 1: return x
    return 2 ** (20 * x - 10) / 2 if x < 0.5 else (2 - 2 ** (-20 * x + 10)) / 2
def io_quint(x): x = c01(x); return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2
def out_elastic(x):
    x = c01(x)
    if x <= 0 or x >= 1: return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * 2 * math.pi / 3) + 1
EASE = dict(lin=c01, io=in_out, oc=out_cubic, ic=in_cubic, ox=out_expo, ix=in_expo, whip=io_expo, q=io_quint,
            ob=out_back, oq=out_quint, el=out_elastic, hold=lambda x: 0.0 if x < 1 else 1.0)

def _lerpv(a, b, k):
    if isinstance(a, tuple): return tuple(x + (y - x) * k for x, y in zip(a, b))
    return a + (b - a) * k

class Track:
    """keys: [(t, value, ease_into_this_key)]; values may be floats or tuples"""
    def __init__(self, keys): self.k = sorted(keys, key=lambda x: x[0])
    def __call__(self, t):
        k = self.k
        if t <= k[0][0]: return k[0][1]
        for (t0, v0, _), (t1, v1, e) in zip(k, k[1:]):
            if t < t1: return _lerpv(v0, v1, EASE[e]((t - t0) / (t1 - t0)))
        return k[-1][1]

# ---------------------------------------------------------------- camera
SPEED = [0.0]          # screen-space motion of the current frame (px / frame), read by the renderer for motion blur

class Cam:
    """track value = (x, y, zoom, rot_deg): world point shown at screen centre"""
    def __init__(self, keys, shake=0.0): self.tr = Track(keys); self.shake = shake
    def state(self, t):
        x, y, z, r = self.tr(t)
        if self.shake:
            x += self.shake * (math.sin(t * 7.3) + 0.5 * math.sin(t * 13.1 + 1)) / z
            y += self.shake * (math.cos(t * 6.1) + 0.5 * math.sin(t * 11.7 + 2)) / z
            r += self.shake * 0.02 * math.sin(t * 3.7)
        return x, y, z, r
    def apply(self, c, t, track_speed=True):
        x, y, z, r = self.state(t)
        if track_speed:
            x1, y1, z1, r1 = self.state(t - 1 / FPS)
            d = math.hypot(x - x1, y - y1) * z + abs(math.log(max(1e-4, z) / max(1e-4, z1))) * 900 + abs(r - r1) * 14
            SPEED[0] = max(SPEED[0], d)
        c.translate(W / 2, H / 2); c.rotate(-r); c.scale(z, z); c.translate(-x, -y)
        return z

def kick(t, hits, amt=0.06, decay=0.14):
    return sum(amt * pulse(t, h, decay) for h in hits)

# ---------------------------------------------------------------- 3D plane
def persp(c, cx, cy, rx=0.0, ry=0.0, rz=0.0, z=0.0, f=1700.0):
    """concat a homography so that local (0,0)-centred drawing appears on a plane rotated in 3D about (cx, cy)"""
    ax, ay, az = math.radians(rx), math.radians(ry), math.radians(rz)
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    R = Rx @ Ry @ Rz
    w = 1 + z / f
    m = skia.Matrix.MakeAll(R[0, 0] + cx * R[2, 0] / f, R[0, 1] + cx * R[2, 1] / f, cx * w,
                            R[1, 0] + cy * R[2, 0] / f, R[1, 1] + cy * R[2, 1] / f, cy * w,
                            R[2, 0] / f, R[2, 1] / f, w)
    c.concat(m)

# ---------------------------------------------------------------- cached imagery
@functools.lru_cache(512)
def still(mt, w=480, mode='bw', lo=INK, hi=PAPER, contrast=1.25, gamma=1.0, sat=1.0):
    fr = MOVIE.get_still(mt)
    h = int(round(w * fr.shape[0] / fr.shape[1]))
    fr = cv2.resize(fr, (w, h), interpolation=cv2.INTER_AREA)
    return to_img(grade(fr, mode, lo=lo, hi=hi, contrast=contrast, gamma=gamma, sat=sat))

def tile(c, mt, x, y, w, h, alpha=1.0, res=480, shape='rect', r=0.0, zoom=1.0, fx=0.5, fy=0.5, **gk):
    draw_img(c, still(round(mt, 2), res, **gk), x, y, w, h, alpha, shape, r, zoom, fx, fy)

# ---------------------------------------------------------------- kinetic glyphs
def _layout(runs, tracking):
    """runs: [(text, font, color)] -> [(ch, font, color, x, w)], total width"""
    out = []; x = 0.0
    for s, f, colr in runs:
        for ch in s:
            w = f.measureText(ch)
            out.append((ch, f, colr, x, w)); x += w + tracking
    return out, max(0.0, x - tracking)

def _enter(style, p, i, seed, size):
    """-> dx, dy, rot, scale, alpha, ry  (identity when p == 1)"""
    q = 1 - p; r1, r2, r3 = rnd(seed + i * 1.37), rnd(seed + i * 2.71 + 5), rnd(seed + i * 3.1 + 9)
    if style == 'fly':
        e = 1 - out_expo(p); a = (r1 * 2 - 1) * math.pi
        return math.cos(a) * size * 6 * e, math.sin(a) * size * 4 * e, (r2 * 2 - 1) * 160 * e, 1 + 1.6 * e, c01(p * 3), 0
    if style == 'drop':
        e = 1 - out_back(p, 2.2)
        return 0, -size * 3.2 * e, (r1 - 0.5) * 50 * e, 1, c01(p * 4), 0
    if style == 'rise':
        e = 1 - out_expo(p)
        return 0, size * 0.9 * e, 0, 1, c01(p * 2.5), 0
    if style == 'zoom':
        e = 1 - out_expo(p)
        return 0, 0, (r1 - 0.5) * 30 * e, 1 + 7 * e, c01(p * 2), 0
    if style == 'slam':
        e = 1 - out_expo(p)
        return 0, 0, 0, 1 + 2.4 * e, c01(p * 6), 0
    if style == 'flip':
        e = 1 - out_back(p, 1.4)
        return 0, 0, 0, 1, c01(p * 3), 90 * e
    if style == 'spin':
        e = 1 - out_back(p, 1.6)
        return 0, 0, 360 * e * (1 if r1 > 0.5 else -1), max(0.001, 1 - e), c01(p * 3), 0
    if style == 'scatter_in':
        e = 1 - out_quint(p)
        return (r1 - 0.5) * size * 5 * e, (r2 - 0.5) * size * 4 * e, (r3 - 0.5) * 220 * e, 1 + 0.5 * e, c01(p * 2), 0
    if style == 'orbit':        # spiral in around the glyph's final spot
        e = 1 - out_expo(p); a = r1 * 2 * math.pi + 4.5 * e
        return math.cos(a) * size * 4 * e, math.sin(a) * size * 2.6 * e, -300 * e, 1 + 1.2 * e, c01(p * 2.5), 0
    if style in ('split', 'wipe', 'stack'):   # geometry handled in the glyph painter
        return 0, 0, 0, 1, c01(p * 5), 0
    return 0, 0, 0, 1, 1.0 if p > 0 else 0.0, 0

def _exit(style, p, i, seed, size):
    r1, r2, r3 = rnd(seed + i * 4.1 + 2), rnd(seed + i * 5.3 + 7), rnd(seed + i * 6.7 + 1)
    if style == 'scatter':
        e = in_cubic(p)
        return (r1 - 0.5) * size * 9 * e, (r2 - 0.5) * size * 7 * e, (r3 - 0.5) * 420 * e, 1 + 1.2 * e, 1 - c01((p - 0.4) * 1.8), 0
    if style == 'fall':
        e = in_cubic(p)
        return (r1 - 0.5) * size * 1.5 * e, size * 8 * e, (r2 - 0.5) * 200 * e, 1, 1 - c01((p - 0.5) * 2), 0
    if style == 'zoom':
        e = in_expo(p)
        return 0, 0, 0, 1 + 9 * e, 1 - c01((p - 0.5) * 2), 0
    if style == 'up':
        e = in_cubic(p)
        return 0, -size * 3 * e, 0, 1, 1 - p, 0
    if style == 'flip':
        e = in_cubic(p)
        return 0, 0, 0, 1, 1 - c01((p - 0.7) * 3.3), -90 * e
    if style == 'fade':
        return 0, 0, 0, 1, 1 - p, 0
    return 0, 0, 0, 1, 1.0 if p < 1 else 0.0, 0

FX = ('blur', 'rgb', 'echo', 'float', 'flicker')      # default glyph decorations
_POOL = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&@$?!/'
CYAN = (40, 196, 214)

def _glyph(c, ch, f, gw, colr, a, style, pin, i, seed, size, fx, t, stroke, blend, main=True):
    """paint one glyph at the origin (baseline 0, centred) with entry progress pin (in units of the entry duration)"""
    q = 1 - c01(pin); qe = 1 - out_expo(c01(pin))
    if 'scramble' in fx and pin < 0.8 and ch.isalnum():
        ch = _POOL[int(rnd(seed + i * 7.7 + int(t * 30) * 1.3) * len(_POOL))]
    x0 = -gw / 2
    def paint(colr_, a_, blur=0.0, strk=stroke):
        p = skia.Paint(AntiAlias=True, Color=col(colr_, a_))
        if strk > 0: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(strk)
        if blend is not None: p.setBlendMode(blend)
        if blur > 0.3: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        return p
    bl = size * 0.11 * q ** 1.4 if 'blur' in fx else 0.0
    # landing flicker: a red block flashes behind the glyph for a few frames
    land = pin - 1.0
    flick = main and 'flicker' in fx and 0 <= land < 0.7 and int(t * 30) % 2 == 0 and rnd(seed + i * 3.3 + int(t * 15)) > 0.45
    if flick:
        rect(c, x0 - size * 0.04, -size * 0.78, gw + size * 0.08, size * 0.9, RED, a)
    if main and 'rgb' in fx and q > 0.03:
        d = size * 0.08 * q
        c.drawString(ch, x0 - d, 0, f, paint(RED, a * 0.75, bl))
        c.drawString(ch, x0 + d, d * 0.3, f, paint(CYAN, a * 0.65, bl))
    cm = PAPER if flick else colr
    if style == 'split' and qe > 0.002:
        hy = -size * 0.36; off = size * 3.5 * qe
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-gw * 4, -size * 2, gw * 4, hy)); c.drawString(ch, x0 - off, 0, f, paint(cm, a, bl)); c.restore()
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-gw * 4, hy, gw * 4, size)); c.drawString(ch, x0 + off, 0, f, paint(cm, a, bl)); c.restore()
    elif style == 'wipe' and pin < 1:
        k = out_cubic(c01(pin)); xe = x0 + (gw + size * 0.1) * k
        c.save(); c.clipRect(skia.Rect.MakeLTRB(x0 - size * 0.1, -size * 2, xe, size)); c.drawString(ch, x0, 0, f, paint(cm, a)); c.restore()
        rect(c, xe, -size * 0.8, size * 0.06, size * 0.95, RED, a)
    elif 'slice' in fx and q > 0.08:
        n = 4; hh = size * 1.1 / n
        for s in range(n):
            y0 = -size * 0.85 + s * hh; dx = (rnd(seed + i * 9.1 + s * 2.3) - 0.5) * size * 1.2 * q
            c.save(); c.clipRect(skia.Rect.MakeLTRB(-gw * 4, y0, gw * 4, y0 + hh + 0.5)); c.drawString(ch, x0 + dx, 0, f, paint(cm, a, bl)); c.restore()
    else:
        if style == 'stack' and qe > 0.01:
            for k in (3, 2, 1):
                for sgn in (-1, 1):
                    c.drawString(ch, x0, sgn * k * size * 0.95 * qe, f, paint(colr, a * 0.55 / k, bl, strk=max(stroke, 2.0) if k > 1 else stroke))
        c.drawString(ch, x0, 0, f, paint(cm, a, bl))
    # echo rings: outlined copies expanding off the glyph as it lands
    if main and 'echo' in fx and size >= 100 and 0.6 < pin < 2.6:
        for j in range(2):
            k = c01((pin - 0.6 - j * 0.35) / 1.6)
            if 0 < k < 1:
                c.save(); s = 1 + 0.55 * out_cubic(k); c.scale(s, s)
                c.drawString(ch, x0, 0, f, paint(colr if j else RED, a * 0.55 * (1 - k), 0, strk=max(1.5, size * 0.012)))
                c.restore()

def ktext(c, t, runs, x, y, t0, style='fly', anchor='l', dur=0.32, stagger=0.035, tracking=0.0, seed=0, alpha=1.0,
          out=None, out_style='scatter', out_dur=0.35, out_stagger=0.02, stroke=0.0, trail=0, times=None, shadow=None, blend=None,
          fx=None, add=(), drop=()):
    """kinetic text. runs = str | [(text, font, color)] (a single (text, font, color) tuple also accepted).
       times: optional per-glyph start times (overrides t0 + i*stagger). out: exit start time.  baseline at y.
       fx: glyph decorations (default FX); add / drop tweak the defaults."""
    if isinstance(runs, tuple): runs = [runs]
    gl, tw = _layout(runs, tracking)
    if not gl: return 0
    fx = set(FX if fx is None else fx) | set(add); fx -= set(drop)
    if style in ('type',): fx -= {'rgb', 'echo', 'blur'}
    ox = x - (tw / 2 if anchor == 'c' else (tw if anchor == 'r' else 0))
    size = max(g[1].getSize() for g in gl)
    for i, (ch, f, colr, gx, gw) in enumerate(gl):
        ti = times[i] if times is not None else t0 + i * stagger
        if t < ti or ch == ' ': continue
        samples = [0.0] + ([k * 0.018 for k in range(1, trail + 1)] if trail else [])
        for si, back in enumerate(samples[::-1] if trail else samples):
            tt = t - back
            if tt < ti: continue
            pin = (tt - ti) / dur
            dx, dy, rot, sc, a, ry = _enter(style, pin, i, seed, size)
            if 'float' in fx and pin > 1:
                kf = c01(pin - 1)
                dy += math.sin(t * 2.1 + i * 0.8 + seed) * size * 0.014 * kf; rot += math.sin(t * 1.6 + i * 1.3 + seed) * 1.2 * kf
            if out is not None and tt >= out + i * out_stagger:
                ex = _exit(out_style, (tt - out - i * out_stagger) / out_dur, i, seed, size)
                dx += ex[0]; dy += ex[1]; rot += ex[2]; sc *= ex[3]; a *= ex[4]; ry += ex[5]
            main = back == 0.0
            if not main:
                if abs(dx) + abs(dy) + abs(sc - 1) * 200 + abs(rot) < 8: continue
                a *= 0.3 * (1 - back / (0.018 * (trail + 1)))
            a *= alpha
            if a <= 0.003: continue
            cx = ox + gx + gw / 2
            c.save(); c.translate(cx + dx, y + dy)
            if ry: persp(c, 0, 0, ry=ry)
            c.rotate(rot); c.scale(sc, sc)
            if shadow is not None and main:
                sp = skia.Paint(AntiAlias=True, Color=col(shadow[2], a * shadow[3] if len(shadow) > 3 else a))
                c.drawString(ch, -gw / 2 + shadow[0], shadow[1], f, sp)
            _glyph(c, ch, f, gw, colr, a, style, pin, i, seed, size, fx if main else (fx & {'blur', 'scramble'}), t, stroke, blend, main)
            c.restore()
    return tw

def words_times(ws, t_extra=0.0):
    """per-glyph start times for a phrase given [(text, t_word)] words joined by spaces"""
    out = []
    for j, (s, tw) in enumerate(ws):
        out += [tw + t_extra + k * 0.02 for k in range(len(s))]
        if j < len(ws) - 1: out.append(1e9)
    return out

def arc_text(c, t, s, cx, cy, r, a0, f, color=INK, alpha=1.0, tracking=0.0, t0=None, t1=None, inward=False, center=True, pop=True):
    """text on a circle, revealed glyph by glyph between t0..t1 (pops out radially)"""
    ws = [f.measureText(ch) + tracking for ch in s]; tot = sum(ws)
    ang = math.radians(a0) - (tot / r / 2 if center else 0)
    p = skia.Paint(AntiAlias=True)
    n = len(s)
    for i, (ch, w) in enumerate(zip(s, ws)):
        am = ang + (w / 2) / r; ang += w / r
        if t0 is not None:
            ti = t0 + (t1 - t0) * i / max(1, n - 1)
            if t < ti: continue
            k = out_back(lin(t, ti, ti + 0.18), 2.0) if pop else 1.0
        else: k = 1.0
        if ch == ' ': continue
        rr = r + (1 - k) * f.getSize() * 1.2
        p.setColor(col(color, alpha * c01(k * 3)))
        c.save(); c.translate(cx + rr * math.sin(am), cy - rr * math.cos(am)); c.rotate(math.degrees(am) + (180 if inward else 0))
        c.drawString(ch, -(w - tracking) / 2, 0, f, p); c.restore()

# ---------------------------------------------------------------- devices
def iris(c, k, cx=W / 2, cy=H / 2, blades=7, rot=0.0, color=(14, 13, 12), edge=(70, 66, 60), alpha=1.0):
    """camera aperture. k = 0 fully open (off-screen), 1 closed."""
    if k <= 0 or alpha <= 0: return
    R = 30 + (1 - c01(k)) ** 1.6 * 1350
    tw = math.radians(rot + 60 * k)
    P = [(cx + R * math.cos(tw + 2 * math.pi * i / blades), cy + R * math.sin(tw + 2 * math.pi * i / blades)) for i in range(blades)]
    L = 4000
    for i in range(blades):
        a, b = P[i], P[(i + 1) % blades]; pv = P[i - 1]
        d1 = (b[0] - a[0], b[1] - a[1]); n1 = math.hypot(*d1) or 1; d1 = (d1[0] / n1, d1[1] / n1)
        d0 = (a[0] - pv[0], a[1] - pv[1]); n0 = math.hypot(*d0) or 1; d0 = (d0[0] / n0, d0[1] / n0)
        pth = skia.Path(); pth.moveTo(*a); pth.lineTo(*b); pth.lineTo(b[0] + d1[0] * L, b[1] + d1[1] * L)
        pth.lineTo(a[0] + d0[0] * L, a[1] + d0[1] * L); pth.close()
        shade = mixc(color, edge, 0.18 + 0.22 * (i % 2) + 0.1 * math.sin(i * 2.1))
        c.drawPath(pth, skia.Paint(AntiAlias=True, Color=col(shade, alpha)))
        lp = skia.Paint(AntiAlias=True, Color=col(edge, alpha * 0.9), StrokeWidth=2, Style=skia.Paint.kStroke_Style)
        c.drawLine(a[0], a[1], b[0] + d1[0] * L, b[1] + d1[1] * L, lp)
    if k >= 1: rect(c, -10, -10, W + 20, H + 20, color, alpha)

def slabs(c, k, ang=-28, n=5, color=BLACK, colors=None, spread=0.5):
    """diagonal slabs sweeping across the frame; k 0->1 covers, 1->2 uncovers on the other side"""
    if k <= 0 or k >= 2: return
    c.save(); c.translate(W / 2, H / 2); c.rotate(ang)
    D = math.hypot(W, H); hh = D / n
    for i in range(n):
        ki = c01((k - i / n * spread) / (1 - spread)) if k <= 1 else c01((k - 1 - i / n * spread) / (1 - spread))
        e = out_quint(ki) if k <= 1 else in_cubic(ki)
        colr = colors[i % len(colors)] if colors else color
        y0 = -D / 2 + i * hh; L = D + 20; left = -D / 2 - 10
        if k <= 1: a0, a1 = (left, left + L * e) if i % 2 == 0 else (left + L * (1 - e), left + L)
        else: a0, a1 = (left + L * e, left + L) if i % 2 == 0 else (left, left + L * (1 - e))
        if a1 > a0: rect(c, a0, y0 - 1, a1 - a0, hh + 2, colr)
    c.restore()

def xmark(c, x, y, s, k, color=RED, w=14.0, alpha=1.0, rot=0.0):
    """hand-drawn red cross, k 0..1 draws both strokes"""
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot)
    k1 = out_cubic(c01(k * 2)); k2 = out_cubic(c01(k * 2 - 1))
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha), StrokeWidth=w, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap)
    c.drawLine(-s, -s * 0.9, -s + 2 * s * k1, -s * 0.9 + 1.9 * s * k1, p)
    if k2 > 0: c.drawLine(s * 1.05, -s * 0.8, s * 1.05 - 2.1 * s * k2, -s * 0.8 + 1.85 * s * k2, p)
    c.restore()

def burst(c, cx, cy, r0, r1, n, color, alpha=1.0, rot=0.0, w=3.0):
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        line(c, cx + math.sin(a) * r0, cy - math.cos(a) * r0, cx + math.sin(a) * r1, cy - math.cos(a) * r1, color, w, alpha)

def ticks_ring(c, cx, cy, r, n, color, alpha=1.0, rot=0.0, long_every=5, l=14, w=1.5):
    for i in range(n):
        a = math.radians(rot + i * 360 / n); ll = l * (2 if i % long_every == 0 else 1)
        line(c, cx + math.sin(a) * r, cy - math.cos(a) * r, cx + math.sin(a) * (r + ll), cy - math.cos(a) * (r + ll), color, w, alpha)

def corners(c, x, y, w, h, k, color=RED, L=None, wdt=5.0, alpha=1.0):
    """viewfinder corner brackets drawing in around a box (k 0..1); they start spread out and snap inwards"""
    if k <= 0: return
    L = L or min(w, h) * 0.22; e = out_expo(k); sp = (1 - e) * 60
    for sx, sy, cx, cy in ((-1, -1, x, y), (1, -1, x + w, y), (-1, 1, x, y + h), (1, 1, x + w, y + h)):
        px, py = cx + sx * sp, cy + sy * sp
        line(c, px, py, px - sx * L * e, py, color, wdt, alpha); line(c, px, py, px, py - sy * L * e, color, wdt, alpha)

def label(c, s, x, y, size=16, color=INK, alpha=0.8, anchor='l', tracking=2.0, bold=False):
    draw_text(c, s, x, y, font('monob' if bold else 'mono', size), color, anchor, alpha, tracking)

_RF = [('anton', None, 1.0), ('bodoni', None, 1.05), ('serif', 900, 1.0), ('serifi', None, 1.1), ('monob', None, 0.85), ('anton', None, 1.25)]
_RB = [(PAPER, INK), (INK, PAPER), (RED, WHITE), (WHITE, INK), (None, INK), (INK, RED), (None, RED)]
def ransom(c, t, s, x, y, size, t0, stagger=0.04, seed=1, anchor='l', alpha=1.0, out=None):
    """dada ransom-note letters: every glyph cut from a different paper"""
    gl = []; tot = 0
    for i, ch in enumerate(s):
        fn, wg, k = _RF[int(rnd(seed + i * 1.9) * len(_RF))]
        f = font(fn, int(size * k * (0.85 + 0.3 * rnd(seed + i * 2.3))), wg)
        w = f.measureText(ch) if ch != ' ' else size * 0.35
        gl.append((ch, f, w)); tot += w + size * 0.08
    x0 = x - (tot / 2 if anchor == 'c' else (tot if anchor == 'r' else 0))
    for i, (ch, f, w) in enumerate(gl):
        ti = t0 + i * stagger
        if t < ti or ch == ' ': x0 += w + size * 0.08; continue
        p = (t - ti) / 0.22; e = 1 - out_back(p, 2.0)
        bgc, fgc = _RB[int(rnd(seed + i * 3.7) * len(_RB))]
        rot = (rnd(seed + i * 5.1) - 0.5) * 16 + e * 40 * (1 if i % 2 else -1)
        dy = (rnd(seed + i * 6.3) - 0.5) * size * 0.18
        a = alpha * c01(p * 4)
        if out is not None and t > out + i * 0.015:
            q = (t - out - i * 0.015) / 0.35; dy += size * 6 * in_cubic(q); rot += 180 * in_cubic(q) * (1 if i % 2 else -1); a *= 1 - c01(q)
        c.save(); c.translate(x0 + w / 2, y + dy); c.rotate(rot); c.scale(1 + 0.6 * e, 1 + 0.6 * e)
        fs = f.getSize()
        if bgc is not None:
            rect(c, -w / 2 - fs * 0.08, -fs * 0.82, w + fs * 0.16, fs * 1.0, bgc, a)
        draw_text(c, ch, -w / 2, 0, f, fgc, 'l', a)
        c.restore()
        x0 += w + size * 0.08
    return tot
