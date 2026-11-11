"""v2 scenes, part C (46.7 – 80 s): the voice from the sky, the outburst, the farewell, the bow, sign-off."""
import math, skia
from core import *
from kit import WC, SPK, wt, sub, hud, T_END, TOTAL
from motion import *
import lib
from lib import sticker, seq
from v2_a import B, bg_img, DARK_HI

def st(i): return SPK[i]['t']
def sd(i): return SPK[i]['dur']

def bars(c, hb=120):
    rect(c, 0, 0, W, hb, BLACK); rect(c, 0, H - hb, W, hb, BLACK)

# ====================================================================== the wall
VOICE = [('s03', "YOU CAN'T LEAVE,", 'TRUMAN.', '你走不了的，楚门。', (-500, -260, -8)), ('s04', 'YOU BELONG', 'HERE.', '你属于这里。', (420, -60, 6)),
         ('s05', 'WITH', 'ME.', '和我在一起。', (-260, 160, -4)), ('s06', 'TALK', 'TO ME.', '跟我说话。', (520, 240, 8)), ('s07', 'SAY', 'SOMETHING.', '说点什么。', (0, -40, 0))]
def s_wall(c, t, n):
    t0, t1 = B(119.5), B(146.4)
    keys = [(t0, (0, 200, 0.8, 0), 'lin'), (t0 + 1.0, (0, 60, 0.95, 0), 'oc')]
    for sid, a, b_, cn, (x, y, r) in VOICE:
        ts = st(sid)
        keys += [(ts - 0.05, keys[-1][1], 'lin'), (ts + 0.3, (x * 0.6, y * 0.6, 1.05, r * 0.6), 'whip')]
    keys += [(t1 - 0.3, (0, -40, 1.12, 0), 'io'), (t1, (0, -40, 1.6, 0), 'ix')]
    cam = Cam(keys, shake=5)
    c.clear(col(BLACK))
    c.save(); cam.apply(c, t, )
    c.translate(-W / 2, -H / 2)
    bg_img(c, 'gen:skywall', t, zoom=1.5, drift=0, style='tint')
    # the creator's face in the clouds, enormous and faint
    sticker(c, 'christof_close', W / 2 + 120, H / 2 - 120, h=1500, style='ht_white', alpha=0.22 + 0.1 * math.sin(t * 1.3), rot=-4)
    seq(c, 's_wall', t, W / 2 - 120, H / 2 + 330, fps=10, h=300, style='tint', border=5, shadow=6)
    c.restore()
    for sid, a, b_, cn, (x, y, r) in VOICE:
        ts = st(sid); te = ts + sd(sid) + 0.5
        nxt = [st(v[0]) for v in VOICE if st(v[0]) > ts]
        out = (nxt[0] - 0.12) if nxt else t1 - 0.25
        if ts - 0.05 <= t < out + 0.5:
            c.save(); c.translate(W / 2, H / 2 - 40); c.rotate(r * 0.3)
            f1 = font('serif', 110, 900); f2 = font('anton', 240)
            ktext(c, t, (a, f1, WHITE), 0, -40, ts, 'drop', 'c', stagger=0.03, tracking=6, trail=4, shadow=(6, 8, BLACK, 0.5), out=out, out_style='up', out_dur=0.3)
            ktext(c, t, (b_, f2, RED), 0, 200, ts + sd(sid) * 0.45, ['split', 'stack', 'slam', 'split', 'stack'][[v[0] for v in VOICE].index(sid)], 'c', stagger=0.03, tracking=10, shadow=(8, 10, BLACK, 0.5), out=out, out_style='up', out_dur=0.3, dur=0.32)
            c.restore()
            sub(c, cn, t, ts, min(te, out + 0.2), dark=True, y=1050, size=30)
    label(c, '▼  VOICE FROM THE SKY  ·  LUNAR ROOM', W / 2, 70, 22, RED, 0.9, 'c', 6, bold=True)
    hud(c, t, n, dark=True, cam=0, label='SIGNAL LOST — REACQUIRING')
    hits = [st(v[0]) for v in VOICE]
    h = max([x for x in hits if t >= x] + [-9])
    return dict(grain=9, chroma=2 + 5 * pulse(t, h, 0.12), zblur=0.18 * pulse(t, h, 0.12) + 0.4 * in_cubic(lin(t, t1 - 0.3, t1)), flash=0.2 * pulse(t, h, 0.05))

# ====================================================================== the outburst
def tv_droste(c, cx, cy, h, depth, t, inner=None, style='ht_white'):
    """a TV whose screen holds a TV whose screen holds a TV ..."""
    for d in range(depth):
        s = 0.47 ** d
        sticker(c, 'g_tv', cx + d * 6, cy - h * 0.06 * (1 - s), h=h * s, style=style, rot=d * 3 * math.sin(t * 2))
    if inner: inner(c, cx, cy, h * 0.47 ** depth)

def s_slam(c, t, n):
    t8, t9, t10 = st('s08'), st('s09'), st('s10'); t1 = B(162.3)
    tg = t8 + 1.10
    c.clear(col(BLACK))
    sh = (0, 0); gl = 0.0; fl = 0.0; inv = 0.0; zb = 0.0; sl = 0.0
    if t < t9:
        footage(c, 5638.0 + (t - t8) * 0.6, 0, 0, W, H, key='chr', lo=BLACK, hi=(235, 44, 32), contrast=1.7, gamma=0.8, alpha=0.9, zoom=1.15 + 0.15 * lin(t, t8, t9), fx=0.6)
        for i in range(10):     # a mob of mouths: ransom echoes
            ty_ = t8 + 0.08 * i
            ransom(c, t, 'SAY SOMETHING', 80 + (i % 3) * 600, 140 + i * 95, 52, ty_, stagger=0.012, seed=30 + i, alpha=0.55)
        c.save(); c.translate(W / 2, 470); c.rotate(-6)
        ktext(c, t, ('SAY SOMETHING,', font('anton', 230), WHITE), 0, 0, t8, 'slam', 'c', stagger=0.03, tracking=6, trail=3, add=('slice',))
        c.restore()
        c.save(); c.translate(W / 2, 880); c.rotate(4)
        ktext(c, t, ('GODDAMMIT!', font('anton', 400), PAPER), 0, 0, tg, 'stack', 'c', stagger=0.045, tracking=8, shadow=(14, 14, BLACK, 1), add=('slice',), dur=0.4)
        c.restore()
        sub(c, '说话啊，该死的！', t, t8, t9, dark=True, y=1060, size=30)
        s_ = 20 * pulse(t, tg, 0.2); sh = (int((rnd(n) - 0.5) * 2 * s_), int((rnd(n + 7) - 0.5) * 2 * s_))
        gl = 0.5 * pulse(t, tg, 0.25); fl = 0.4 * pulse(t, t8, 0.05); zb = 0.3 * pulse(t, tg, 0.15); sl = 0.4 * pulse(t, tg + 0.3, 0.12)
        inv = 0.9 * sum(pulse(t, tg + k * 0.04, 0.02) for k in range(0, 10, 3))
    elif t < t10:
        c.clear(col(PAPER)); paper(c, t, 3)
        z = 1 + 2.4 * in_cubic(lin(t, t9, t10))
        c.save(); c.translate(W / 2, H / 2 + 20); c.scale(z, z); c.rotate(10 * lin(t, t9, t10)); c.translate(-W / 2, -H / 2 - 20)
        def inner(c_, x, y, h):
            footage(c_, 5487.0 + (t - t9), x - h * 0.55, y - h * 0.3, h * 1.0, h * 0.62, key='wall', lo=BLACK, hi=DARK_HI)
        tv_droste(c, W / 2, H / 2 + 30, 1000, 5, t, inner, 'bw')
        c.restore()
        rect(c, 0, 0, W, 240, BLACK); rect(c, 0, H - 260, W, 260, RED)
        ktext(c, t, ("YOU'RE ON", font('anton', 150), WHITE), W / 2, 180, t9, 'flip', 'c', stagger=0.025, tracking=30)
        ktext(c, t, ('TELEVISION!', font('anton', 230), PAPER), W / 2, H - 50, t9 + 0.38, 'split', 'c', stagger=0.035, tracking=8, dur=0.3)
        fl = 0.5 * pulse(t, t9, 0.05); gl = 0.3 * pulse(t, t9, 0.2); zb = 0.25 * pulse(t, t9 + 0.38, 0.1)
    else:
        tw = t10 + 1.18
        paper(c, t, 8, dark=True)
        cam = Cam([(t10, (W / 2, H / 2, 1.5, -20), 'lin'), (t10 + 0.4, (W / 2, H / 2, 1.0, 0), 'oq'), (tw, (W / 2, H / 2, 1.05, 4), 'lin'), (tw + 0.25, (W / 2, H / 2, 0.85, -3), 'oq'), (t1, (W / 2, H / 2, 0.8, -6), 'lin')], shake=8)
        c.save(); cam.apply(c, t)
        seq(c, 'b_dome', t, W / 2, H / 2 - 40, fps=30, h=1100, style='ht_white', alpha=0.8)
        sticker(c, 'g_globe', W / 2, H / 2 + 30, h=800, style='tint', border=8, shadow=12)
        for k in range(9):
            a = math.radians(t * 50 + k * 40); r = 640
            kk = out_back(lin(t, t10 + k * 0.05, t10 + k * 0.05 + 0.3))
            if kk > 0: sticker(c, f'cam_{k + 1}', W / 2 + math.cos(a) * r, H / 2 + math.sin(a) * r * 0.42 + 30, h=150 * kk, style='ht_white', rot=math.degrees(a) * 0.2)
        arc_text(c, t, "YOU'RE  LIVE  TO  THE  WHOLE", W / 2, H / 2 + 30, 520, -t * 20, font('anton', 100), WHITE, tracking=6, t0=t10, t1=t10 + 0.9)
        c.restore()
        ktext(c, t, ('WORLD!', font('anton', 460), RED), W / 2, H / 2 + 180, tw, 'stack', 'c', stagger=0.045, tracking=12, trail=3, shadow=(12, 12, BLACK, 1), add=('slice',), dur=0.4)
        sub(c, '全世界都在看直播！', t, t10, t10 + 2.1, dark=True, y=1060, size=30)
        s_ = 22 * pulse(t, tw, 0.15); sh = (int((rnd(n) - 0.5) * 2 * s_), int((rnd(n + 7) - 0.5) * 2 * s_))
        fl = 0.5 * pulse(t, t10, 0.05); gl = 0.5 * pulse(t, tw, 0.25); zb = 0.3 * pulse(t, tw, 0.12)
        rect(c, 0, 0, W, H, BLACK, lin(t, t10 + 1.95, t10 + 2.3))
    if t9 <= t < t10: sub(c, '你在上电视！', t, t9, t10, dark=False, y=1060, size=30)
    hud(c, t, n, dark=True)
    return dict(grain=12, chroma=4 + 8 * gl, scan=0.35, shake=sh, glitch=gl, flash=fl, invert=min(1, inv), zblur=zb, slice_=sl)

# ====================================================================== good night
def s_night(c, t, n):
    t11, t12 = st('s11'), st('s12'); t1 = B(178.5)
    c.clear(col(BLACK))
    if t < t12 - 0.15: mt = 5689.75 + (t - t11) if t < t11 + 1.25 else 5691.0 + (t - t11 - 1.25) * 0.5
    else: mt = 5692.6 + (t - (t12 - 0.15))
    kc = in_out(lin(t, t11 - 0.3, t11 + 1.2))
    zz = 1.05 + 0.04 * lin(t, t11, t1)
    footage(c, mt, 0, 0, W, H, key='tru', lo=BLACK, hi=DARK_HI, contrast=1.25, zoom=zz, fy=0.3)
    if kc > 0: footage(c, mt, 0, 0, W, H, key='tru', mode='color', contrast=1.1, sat=1.15, zoom=zz, fy=0.3, alpha=kc)
    # torn paper drifting off the frame: the collage peels away as colour comes back
    for k in range(8):
        kk = in_cubic(lin(t, t11 - 0.3 + k * 0.06, t11 + 0.45 + k * 0.06))
        if kk < 1:
            x = (k % 4) * 520 + 200; y = (k // 4) * 560 + 260
            sticker(c, f'scrap_{k % 6 + 1}', x + 400 * kk * (1 if k % 2 else -1), y - 900 * kk, w=700, style='raw', rot=(rnd(k) - 0.5) * 30 + 140 * kk, alpha=1 - kk)
    bars(c)
    ktext(c, t, ("In case I don't see ya —", font('serifi', 66), WHITE), W / 2, 86, t11, 'rise', 'c', stagger=0.03, out=t12 - 0.3, out_style='up', out_dur=0.3, fx=('blur', 'float'))
    sub(c, '万一再也见不到你们——', t, t11, t12 - 0.2, dark=True, y=1030, size=30)
    parts = [('good afternoon,', 0.0), ('good evening,', 0.88), ('and good night.', 1.36)]
    f2 = font('serifi', 60); tot = sum(text_w(p[0] + '   ', f2) for p in parts); x = W / 2 - tot / 2
    for s_, dt in parts:
        ktext(c, t, (s_, f2, WHITE), x, 86, t12 + dt, 'rise', stagger=0.02, fx=('blur', 'float'))
        x += text_w(s_ + '   ', f2)
    sub(c, '下午好，晚上好，晚安。', t, t12, t12 + 2.5, dark=True, y=1030, size=30)
    hud(c, t, n, dark=True, alpha=1 - kc * 0.7)
    return dict(grain=8 - 3 * kc, chroma=1, scan=0.25 * (1 - kc), vig=1.0)

# ====================================================================== the bow and the ring of viewers
RING = [('v_bathtub', 'tint'), ('v_ladies', 'tint'), ('christof_head', 'tint'), ('sylvia_watch', 'tint'), ('v_lady', 'tint'), ('v_host', 'tint'), ('meryl_smile', 'ht'), ('marlon', 'ht')]
def s_bow(c, t, n):
    t0 = B(178.5); tx = t0 + 1.85; tz = t0 + 3.5; t1 = T_END
    c.clear(col(BLACK))
    mt = 5707.55 + (t - t0) if t < tx else min(5715.3, 5710.6 + (t - tx) * 2.6)
    kz = out_expo(lin(t, tz, tz + 1.3))
    cx, cy = W / 2, 500
    cam_r = 8 * lin(t, tz, t1)
    c.save(); c.translate(cx, cy); c.rotate(cam_r); c.translate(-cx, -cy)
    if kz > 0:
        R = 420
        arc(c, cx, cy, R + 170, 0, 360, WHITE, 2, 0.5 * kz, dash=(6, 10))
        ticks_ring(c, cx, cy, R + 190, 96, WHITE, 0.5 * kz, t * 6, 8, 12, 1.5)
        for i, (nm, sty) in enumerate(RING):
            ti = tz + 0.15 + i * 0.07; k = out_back(lin(t, ti, ti + 0.35), 1.2)
            if k <= 0: continue
            a = 2 * math.pi * i / len(RING) + 0.2 + t * 0.05
            x = cx + math.sin(a) * R * 1.45; y = cy - math.cos(a) * R * 1.0
            line(c, x, y, cx + math.sin(a) * 160, cy - math.cos(a) * 110, RED, 2, 0.7 * k, dash=(10, 8))
            sticker(c, nm, x, y, h=230 * k, style=sty, border=6, shadow=8, rot=(rnd(i) - 0.5) * 12)
    koff = lin(t, tz + 2.0, tz + 2.25)
    w_ = lerp(W, 330, kz); h_ = lerp(H, 186, kz)
    if koff < 1:
        if kz > 0.05: sticker(c, 'g_tv', cx + 10 * kz, cy + 30 * kz, h=lerp(H * 1.9, 340, kz), style='ht_white', alpha=c01(kz * 3))
        hh = h_ * (1 - koff) + 3 * koff
        footage(c, mt, cx - w_ / 2, lerp(H / 2, cy, kz) - hh / 2, w_, hh, key='tru', mode='color', contrast=1.1, sat=1.1, shape='round' if kz > 0 else 'rect', r=18 * kz, fy=0.5)
    c.restore()
    tt = tz + 2.35
    if t >= tt:
        ktext(c, t, ('圆形监狱', font('cnb', 96), WHITE), cx, cy + 30, tt, 'split', 'c', stagger=0.08, tracking=14, dur=0.45)
        ktext(c, t, ('PANOPTICON', font('serif', 36, 800), RED), cx, cy + 92, tt + 0.2, 'type', 'c', stagger=0.03, tracking=16, add=('scramble',), dur=0.4)
        a = lin(t, tt + 0.5, tt + 0.9)
        draw_text(c, 'The prisoner walked out.   The audience stayed.', cx, 985, font('serifi', 42), WHITE, 'c', a)
        draw_text(c, '囚徒走出去了，观众还坐在原地。', cx, 1036, font('cn', 28), WHITE, 'c', a * 0.9, 4)
        draw_text(c, 'MUSIC   パノプティコン / r-906', 90, 520, font('cn', 19), WHITE, 'l', a * 0.8, 2)
        draw_text(c, 'SOURCE   THE TRUMAN SHOW (1998)', W - 90, 520, font('cn', 19), WHITE, 'r', a * 0.8, 2)
    if t < tz: bars(c, int(120 * (1 - lin(t, t0, t0 + 0.6))))
    hud(c, t, n, dark=True, alpha=0.4 + 0.6 * kz, label='THE TRUMAN SHOW — FINAL EPISODE')
    return dict(grain=6 + 3 * kz, chroma=1 + 8 * pulse(t, tz, 0.15), flash=0.35 * pulse(t, tz, 0.06), scan=0.2 * kz, zblur=0.25 * (1 - out_expo(lin(t, tz, tz + 0.5))) * (t > tz))

def s_end(c, t, n):
    t14, t15 = st('s14'), st('s15'); toff = T_END + 3.25
    c.clear(col(BLACK))
    if t < t15 - 0.1:
        ktext(c, t, ('CEASE TRANSMISSION.', font('monob', 58), WHITE), W / 2, H / 2 + 10, t14, 'type', 'c', stagger=0.035, tracking=10, add=('scramble',), dur=0.3)
        a = lin(t, t14 + 0.8, t14 + 0.9)
        if int(t * 3) % 2 == 0: rect(c, W / 2 - 150, H / 2 + 70, 18, 18, RED, a)
        label(c, 'NO SIGNAL', W / 2 - 118, H / 2 + 88, 22, WHITE, a * 0.85, 'l', 6)
        sub(c, '停止播送。', t, t14, t15 - 0.15, dark=True)
    else:
        footage(c, 5756.9 + (t - t15), W / 2 - 440, 420 - 248, 880, 495, key='end', mode='color', contrast=1.1, shape='round', r=24, fy=0.4)
        ktext(c, t, ('What else is on?', font('serifi', 84), WHITE), W / 2, 800, t15, 'rise', 'c', stagger=0.03, fx=('blur', 'float'))
        sub(c, '“还有别的台吗？”', t, t15, toff, dark=True, y=900, size=36)
    return dict(grain=12, scan=0.5, chroma=1.5, vig=1.0, tvoff=lin(t, toff, toff + 0.35))

TABLE = [(B(119.5), B(146.4), s_wall), (B(146.4), B(162.3), s_slam), (B(162.3), B(178.5), s_night), (B(178.5), T_END, s_bow), (T_END, 1e9, s_end)]
