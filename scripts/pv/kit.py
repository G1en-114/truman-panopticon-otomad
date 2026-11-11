"""Shared drawing pieces: word pops, subtitles, HUD, panopticon blueprint, icons."""
import math, skia
from core import *

TL, SP, WORDS = load_timeline()
WC = {}
for w in WORDS: WC.setdefault(w['cid'], []).append(w)
SPK = {s['id']: s for s in SP['spoken']}
T_END = SP['t_end']; TOTAL = SP['total']
def wt(cid, i): return WC[cid][i]['t']
def we(cid, i): return WC[cid][i]['end']

def pop(c, s, x, y, f, t, t0, color=INK, anchor='l', rise=26, d=0.13, tracking=0.0, rot=0.0, grow=0.22, alpha=1.0, out=None, stroke=0.0):
    """word appears at t0 with a quick overshoot; optional out=(t1, dur) fade"""
    if t < t0: return
    k = lin(t, t0, t0 + d); e = out_expo(k)
    a = out_cubic(lin(t, t0, t0 + d * 0.6)) * alpha
    if out is not None: a *= 1 - lin(t, out[0], out[0] + out[1])
    if a <= 0: return
    w = text_w(s, f, tracking)
    ax = x + (w / 2 if anchor == 'l' else (-w / 2 if anchor == 'r' else 0))
    c.save(); c.translate(ax, y + (1 - e) * rise); c.rotate(rot + (1 - e) * 2.0)
    sc = 1 + grow * (1 - e); c.scale(sc, sc)
    draw_text(c, s, 0, 0, f, color, 'c', a, tracking, stroke)
    c.restore()

def typed(c, s, x, y, f, t, t0, t1, color=INK, anchor='l', alpha=1.0, cursor=True, tracking=0.0):
    """typewriter reveal between t0..t1"""
    if t < t0: return
    n = int(len(s) * lin(t, t0, t1) + 0.999)
    full_w = text_w(s, f, tracking)
    x0 = x - (full_w / 2 if anchor == 'c' else (full_w if anchor == 'r' else 0))
    w = draw_text(c, s[:n], x0, y, f, color, 'l', alpha, tracking)
    if cursor and n < len(s) or (cursor and int(t * 4) % 2 == 0 and t < t1 + 0.6):
        rect(c, x0 + w + 4, y - f.getSize() * 0.72, f.getSize() * 0.07 + 2, f.getSize() * 0.8, color, alpha)

def sub(c, s, t, t0, t1, dark=False, y=1012, size=33):
    """Chinese translation line"""
    a = out_cubic(lin(t, t0, t0 + 0.12)) * (1 - lin(t, t1 - 0.1, t1))
    if a <= 0: return
    f = font('cn', size); colr = WHITE if dark else INK
    w = text_w(s, f, 3)
    draw_text(c, s, W / 2, y, f, colr, 'c', a * 0.92, 3)
    line(c, W / 2 - w / 2 - 46, y - 11, W / 2 - w / 2 - 18, y - 11, RED, 2, a)
    line(c, W / 2 + w / 2 + 18, y - 11, W / 2 + w / 2 + 46, y - 11, RED, 2, a)

def hud(c, t, frame, dark=False, alpha=1.0, cam=None, rec=True, label='THE TRUMAN SHOW'):
    colr = WHITE if dark else INK; a = 0.72 * alpha
    if a <= 0: return
    f = font('mono', 17); fb = font('monob', 17)
    m = 44; L = 26
    for (x, y, sx, sy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        line(c, x, y, x + sx * L, y, colr, 2, a); line(c, x, y, x, y + sy * L, colr, 2, a)
    if rec:
        on = int(t * 2) % 2 == 0
        circle(c, m + 22, m + 28, 6, RED, alpha if on else 0.25 * alpha)
        draw_text(c, 'LIVE', m + 36, m + 34, fb, colr, 'l', a, 2)
    draw_text(c, label, m + 110, m + 34, f, colr, 'l', a * 0.8, 2)
    n = cam if cam is not None else 1 + int(t * 7.3) % 5000
    draw_text(c, f'CAM {n:04d} / 5000', W - m - 18, m + 34, f, colr, 'r', a, 2)
    secs = 10909 * 0 + t; ff = frame % 30
    tc = f'DAY 10,909   {int(6 + secs // 3600):02d}:{int(secs // 60) % 60:02d}:{int(secs) % 60:02d}:{ff:02d}'
    draw_text(c, tc, m + 18, H - m - 18, f, colr, 'l', a, 2)
    draw_text(c, 'PANOPTICON  /  r-906', W - m - 18, H - m - 18, f, colr, 'r', a * 0.8, 2)

def blueprint(c, cx, cy, R, rot=0.0, color=INK, alpha=1.0, cells=24, sweep=None, t=0.0, weight=1.0, labels=True, tower=True, lit=None):
    """Bentham-style plan: outer ring of cells, annular void, central inspection tower."""
    if alpha <= 0: return
    c.save(); c.translate(cx, cy); c.rotate(rot)
    w = max(1.0, 2.0 * weight)
    circle(c, 0, 0, R, color, alpha, w * 1.4); circle(c, 0, 0, R * 0.80, color, alpha, w)
    circle(c, 0, 0, R * 0.74, color, alpha * 0.5, 1); circle(c, 0, 0, R * 1.045, color, alpha * 0.45, 1)
    arc(c, 0, 0, R * 0.56, 0, 360, color, 1.2, alpha * 0.6, dash=(10, 9))
    arc(c, 0, 0, R * 0.34, 0, 360, color, 1.2, alpha * 0.5, dash=(3, 7))
    for i in range(cells):
        a = 2 * math.pi * i / cells; s, co = math.sin(a), -math.cos(a)
        line(c, s * R * 0.80, co * R * 0.80, s * R, co * R, color, w, alpha)
        if lit is not None and i in lit:
            p = skia.Path(); a2 = 2 * math.pi * (i + 1) / cells
            p.moveTo(s * R * 0.80, co * R * 0.80); p.lineTo(s * R, co * R)
            p.arcTo(skia.Rect.MakeLTRB(-R, -R, R, R), math.degrees(a) - 90, 360 / cells, False)
            p.lineTo(math.sin(a2) * R * 0.80, -math.cos(a2) * R * 0.80)
            p.arcTo(skia.Rect.MakeLTRB(-R * 0.8, -R * 0.8, R * 0.8, R * 0.8), math.degrees(a2) - 90, -360 / cells, False)
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(RED, alpha * lit[i])))
    for i in range(cells * 4):
        a = 2 * math.pi * i / (cells * 4); s, co = math.sin(a), -math.cos(a)
        k = 1.045 if i % 4 else 1.075
        line(c, s * R * 1.0, co * R * 1.0, s * R * k, co * R * k, color, 1, alpha * 0.6)
    if tower:
        circle(c, 0, 0, R * 0.17, color, alpha, w * 1.2); circle(c, 0, 0, R * 0.115, color, alpha * 0.7, 1)
        for i in range(8):
            a = 2 * math.pi * i / 8; s, co = math.sin(a), -math.cos(a)
            line(c, s * R * 0.115, co * R * 0.115, s * R * 0.17, co * R * 0.17, color, 1.2, alpha)
    if sweep is not None:   # sight lines from the tower
        for k, a in enumerate(sweep):
            s, co = math.sin(math.radians(a)), -math.cos(math.radians(a))
            line(c, s * R * 0.17, co * R * 0.17, s * R * 0.80, co * R * 0.80, RED, 2, alpha * 0.9, dash=(14, 8))
    if labels:
        f = font('mono', max(11, R * 0.028))
        draw_text_arc(c, 'CELLS · 囚室', 0, 0, R * 1.10, 28, f, color, alpha * 0.8, 3)
        draw_text_arc(c, 'INSPECTION LODGE · 监视塔', 0, 0, R * 0.22, 0, f, color, alpha * 0.8, 2)
        draw_text_arc(c, 'ANNULAR AREA', 0, 0, R * 0.60, 200, f, color, alpha * 0.6, 3)
    c.restore()

def eye(c, cx, cy, w, open_=1.0, color=INK, alpha=1.0, pupil=RED, look=(0, 0), stroke=3.0, fill=None):
    if alpha <= 0: return
    h = w * 0.27 * max(0.02, open_)
    p = skia.Path(); p.moveTo(cx - w / 2, cy); p.quadTo(cx, cy - h * 2, cx + w / 2, cy); p.quadTo(cx, cy + h * 2, cx - w / 2, cy); p.close()
    if fill is not None: c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(fill, alpha)))
    c.save(); c.clipPath(p, True)
    r = w * 0.17
    circle(c, cx + look[0] * w * 0.1, cy + look[1] * w * 0.05, r, color, alpha, stroke)
    circle(c, cx + look[0] * w * 0.1, cy + look[1] * w * 0.05, r * 0.46, pupil, alpha)
    c.restore()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(color, alpha), Style=skia.Paint.kStroke_Style, StrokeWidth=stroke))

def cctv(c, cx, cy, s=1.0, color=INK, alpha=1.0, flip=False, lens=RED):
    """little surveillance camera, ~120px wide at s=1, pointing right-down"""
    if alpha <= 0: return
    c.save(); c.translate(cx, cy); c.scale(-s if flip else s, s)
    pa = skia.Paint(AntiAlias=True, Color=col(color, alpha))
    c.drawRect(skia.Rect.MakeXYWH(-70, -62, 14, 60), pa); c.drawRect(skia.Rect.MakeXYWH(-70, -62, 50, 10), pa)
    c.drawRect(skia.Rect.MakeXYWH(-30, -58, 10, 30), pa)
    c.save(); c.rotate(18)
    c.drawRoundRect(skia.Rect.MakeXYWH(-52, -26, 100, 44), 6, 6, pa)
    c.drawRect(skia.Rect.MakeXYWH(-60, -32, 118, 10), pa)
    c.drawRect(skia.Rect.MakeXYWH(48, -18, 14, 28), pa)
    c.drawCircle(60, -4, 8, skia.Paint(AntiAlias=True, Color=col(lens, alpha)))
    c.restore(); c.restore()

def strike(c, x, y, w, h, k, color=RED, alpha=1.0):
    """censor bar wiping left->right"""
    if k <= 0: return
    rect(c, x, y, w * k, h, color, alpha)

def tv_frame(c, x, y, w, h, color=INK, alpha=1.0, r=26, label=None, dark=False):
    """rounded CRT bezel drawn around a footage window"""
    p = skia.Paint(AntiAlias=True, Color=col(color, alpha), Style=skia.Paint.kStroke_Style, StrokeWidth=5)
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, p)
    p.setStrokeWidth(1.5)
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 12, y - 12, w + 24, h + 24), r + 10, r + 10, p)
    if label:
        f = font('mono', 15)
        draw_text(c, label, x + 4, y + h + 34, f, color, 'l', alpha * 0.85, 2)

def crosshair(c, x, y, s, color, alpha=1.0, w=1.5):
    line(c, x - s, y, x + s, y, color, w, alpha); line(c, x, y - s, x, y + s, color, w, alpha)
