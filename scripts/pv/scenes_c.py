"""Scenes: the spoken confrontation, the bow, the inverted panopticon, sign-off."""
import math, skia
from core import *
from kit import *
from scenes_a import cam_grid, sun_icon

DARK_HI = (232, 228, 220)
def st(i): return SPK[i]['t']
def sd(i): return SPK[i]['dur']

def bars(c, hb=132):
    rect(c, 0, 0, W, hb, BLACK); rect(c, 0, H - hb, W, hb, BLACK)

def sky_line(c, t, sid, en, cn, big=False):
    """Christof's voice: caption in the top bar, translation in the bottom bar"""
    t0 = st(sid); t1 = t0 + sd(sid) + 0.45
    a = lin(t, t0, t0 + 0.06) * (1 - lin(t, t1 - 0.12, t1))
    if a <= 0: return
    f = font('serif', 56, 700)
    n_ = int(len(en) * lin(t, t0, t0 + min(0.5, sd(sid) * 0.6)) + 0.999)
    full = text_w(en, f, 10)
    draw_text(c, en[:n_], W / 2 - full / 2, 96, f, WHITE, 'l', a, 10)
    draw_text(c, '▼  VOICE FROM THE SKY', W / 2, 36, font('mono', 15), RED, 'c', a * 0.9, 4)
    sub(c, cn, t, t0, t1, dark=True, y=1030, size=32)

def s_wall(c, t, n):
    """You can't leave, Truman. / You belong here. / With me. / Talk to me. / Say something."""
    b = t2b(t); t0 = b2t(119.5)
    c.clear(col(BLACK))
    cuts = [(t0, 5487.0, 1.0, 0.5), (st('s04') - 0.1, 5501.4, 1.0, 0.5), (st('s06') - 0.1, 5663.6, 0.7, 0.4)]
    cur = cuts[0]
    for cu in cuts:
        if t >= cu[0]: cur = cu
    k = lin(t, cur[0], cur[0] + 4.0)
    footage(c, cur[1] + (t - cur[0]) * cur[2], 0, 0, W, H, key='wall', lo=BLACK, hi=DARK_HI, contrast=1.3, gamma=0.9, zoom=1.04 + 0.05 * k, fy=cur[3],
            alpha=lin(t, t0, t0 + 0.5))
    bars(c)
    sky_line(c, t, 's03', "YOU CAN'T LEAVE, TRUMAN.", '你走不了的，楚门。')
    sky_line(c, t, 's04', 'YOU BELONG HERE.', '你属于这里。')
    sky_line(c, t, 's05', 'WITH ME.', '和我在一起。')
    sky_line(c, t, 's06', 'TALK TO ME.', '跟我说话。')
    sky_line(c, t, 's07', 'SAY SOMETHING.', '说点什么。')
    hud(c, t, n, dark=True, label='SIGNAL LOST — REACQUIRING', cam=0)
    fl = sum(0.25 * pulse(t, cu[0], 0.06) for cu in cuts[1:])
    return dict(grain=11, chroma=2, scan=0.3, flash=fl)

def s_slam(c, t, n):
    """SAY SOMETHING, GODDAMMIT! / YOU'RE ON TELEVISION! / YOU'RE LIVE TO THE WHOLE WORLD!"""
    c.clear(col(BLACK))
    t8, t9, t10 = st('s08'), st('s09'), st('s10')
    fa = font('anton', 300)
    sh = (0, 0); gl = 0.0; fl = 0.0
    if t < t9:
        footage(c, 5638.0 + (t - t8) * 0.6, 0, 0, W, H, key='chr', lo=BLACK, hi=(235, 44, 32), contrast=1.6, gamma=0.8, alpha=0.85, zoom=1.1 + 0.1 * lin(t, t8, t9), fx=0.6)
        pop(c, 'SAY SOMETHING,', W / 2, 450, font('anton', 250), t, t8, WHITE, 'c', grow=0.5, tracking=6)
        tg = t8 + 1.10
        pop(c, 'GODDAMMIT!', W / 2, 830, font('anton', 380), t, tg, WHITE, 'c', grow=0.7, tracking=8)
        sub(c, '说话啊，该死的！', t, t8, t9, dark=True, y=1040, size=32)
        s_ = 18 * pulse(t, tg, 0.15); sh = (int((rnd(n) - 0.5) * 2 * s_), int((rnd(n + 7) - 0.5) * 2 * s_)); gl = 0.5 * pulse(t, tg, 0.2); fl = 0.4 * pulse(t, t8, 0.05)
    elif t < t10:
        cam_grid(c, t, lambda i: t9 + rnd(i * 5.1) * 0.25, alpha=0.9, lo=BLACK, hi=(235, 44, 32))
        rect(c, 0, 330, W, 420, WHITE)
        pop(c, "YOU'RE ON", W / 2, 470, font('anton', 120), t, t9, BLACK, 'c', tracking=30)
        pop(c, 'TELEVISION!', W / 2, 722, font('anton', 250), t, t9 + 0.38, RED, 'c', grow=0.5, tracking=6)
        sub(c, '你在上电视！', t, t9, t10, dark=True, y=1040, size=32)
        fl = 0.5 * pulse(t, t9, 0.05); gl = 0.3 * pulse(t, t9, 0.2)
    else:
        k = lin(t, t10, t10 + 2.2)
        footage(c, 3719.6 + (t - t10) * 1.6, 0, 0, W, H, key='dome', lo=BLACK, hi=DARK_HI, contrast=1.5, alpha=0.9, zoom=1.05)
        rect(c, 0, 0, W, H, BLACK, 0.25)
        pop(c, "YOU'RE LIVE", 120, 380, fa, t, t10, WHITE, tracking=6)
        pop(c, 'TO THE WHOLE', 120, 640, font('anton', 220), t, t10 + 0.62, WHITE, tracking=6)
        pop(c, 'WORLD!', 120, 990, font('anton', 400), t, t10 + 1.18, RED, grow=0.6, tracking=8)
        sub(c, '全世界都在看直播！', t, t10, t10 + 2.2, dark=True, y=1050, size=30)
        s_ = 20 * pulse(t, t10 + 1.18, 0.15); sh = (int((rnd(n) - 0.5) * 2 * s_), int((rnd(n + 7) - 0.5) * 2 * s_))
        fl = 0.5 * pulse(t, t10, 0.05); gl = 0.5 * pulse(t, t10 + 1.18, 0.25)
        rect(c, 0, 0, W, H, BLACK, lin(t, t10 + 1.95, t10 + 2.3))      # breath of black before he answers
    hud(c, t, n, dark=True)
    return dict(grain=12, chroma=4 + 8 * gl, scan=0.35, shake=sh, glitch=gl, flash=fl)

def s_night(c, t, n):
    """In case I don't see ya — good afternoon, good evening, and good night.  (colour comes back)"""
    c.clear(col(BLACK))
    t11, t12 = st('s11'), st('s12')
    if t < t12 - 0.15: mt = 5689.75 + (t - t11) if t < t11 + 1.25 else 5691.0 + (t - t11 - 1.25) * 0.5
    else: mt = 5692.6 + (t - (t12 - 0.15))
    kc = in_out(lin(t, t11 - 0.3, t11 + 1.2))              # colour fades in
    footage(c, mt, 0, 0, W, H, key='tru', lo=BLACK, hi=DARK_HI, contrast=1.25, zoom=1.05 + 0.03 * lin(t, t11, t12 + 2.5), fy=0.3)
    if kc > 0: footage(c, mt, 0, 0, W, H, key='tru', mode='color', contrast=1.1, sat=1.15, zoom=1.05 + 0.03 * lin(t, t11, t12 + 2.5), fy=0.3, alpha=kc)
    bars(c)
    fi = font('serifi', 62)
    typed(c, "In case I don't see ya —", W / 2, 98, fi, t, t11, t11 + 1.0, WHITE, 'c', cursor=False, alpha=1 - lin(t, t12 - 0.3, t12 - 0.1))
    sub(c, '万一再也见不到你们——', t, t11, t12 - 0.2, dark=True, y=1030, size=32)
    # the three farewells, with the day's dial from verse two
    parts = [('good afternoon,', 0.0, 0), ('good evening,', 0.88, 1), ('and good night.', 1.36, 2)]
    f2 = font('serifi', 58); tot = sum(text_w(p[0] + '   ', f2) for p in parts) + 3 * 60; x = W / 2 - tot / 2
    for s, dt, ic in parts:
        ta = t12 + dt; a = lin(t, ta, ta + 0.08)
        if a > 0:
            if ic == 0: sun_icon(c, x + 20, 78, 13, RED, a, t * 40)
            elif ic == 1:
                c.save(); c.clipRect(skia.Rect.MakeXYWH(x, 50, 44, 30)); sun_icon(c, x + 20, 82, 13, RED, a, t * 40); c.restore(); line(c, x - 4, 81, x + 46, 81, WHITE, 2, a)
            else:
                circle(c, x + 20, 78, 14, WHITE, a); circle(c, x + 27, 73, 12, BLACK, a)
        pop(c, s, x + 60, 98, f2, t, ta, WHITE, rise=10)
        x += text_w(s + '   ', f2) + 60
    sub(c, '下午好，晚上好，晚安。', t, t12, t12 + 2.5, dark=True, y=1030, size=32)
    hud(c, t, n, dark=True, alpha=1 - kc * 0.6)
    return dict(grain=9 - 3 * kc, chroma=1, scan=0.25 * (1 - kc), vig=1.0)

RING = [5704.2, 5722.9, 5726.6, 5733.9, 5737.6, 5706.3, 5724.7, 5728.4, 5735.6, 5717.5]
def s_bow(c, t, n):
    """the bow, the door, and then the camera keeps pulling back: the watchers were the cells all along"""
    b = t2b(t); t0 = b2t(178.5)
    c.clear(col(BLACK))
    tx = t0 + 1.85; tz = t0 + 3.5            # exit starts / pull-back starts
    if t < tx: mt = 5707.55 + (t - t0)
    else: mt = min(5715.3, 5710.6 + (t - tx) * 2.6)
    kz = out_expo(lin(t, tz, tz + 1.1))
    cx, cy, R = W / 2, 500, 345
    tw, th = 250, 141
    if kz > 0:
        blueprint(c, cx, cy, R + 118, t * 4, WHITE, 0.55 * kz, cells=len(RING) * 2, labels=False, tower=False)
        circle(c, cx, cy, R - 118, WHITE, 0.4 * kz, 1.2)
        for i, mt_i in enumerate(RING):
            ti = tz + 0.15 + i * 0.07; k = out_back(lin(t, ti, ti + 0.3), 1.2)
            if k <= 0: continue
            a = 2 * math.pi * i / len(RING) + 0.25
            x = cx + math.sin(a) * R * 1.32; y = cy - math.cos(a) * R
            line(c, x, y, cx + math.sin(a) * 70, cy - math.cos(a) * 70, RED, 2, 0.7 * k, dash=(10, 8))
            footage(c, mt_i + ((t - tz) * 0.8) % 1.6, x - tw / 2 * k, y - th / 2 * k, tw * k, th * k, key=f'r{i}', mode='color', contrast=1.1, sat=1.1, shape='round', r=12, fy=0.3)
            p = skia.Paint(AntiAlias=True, Color=col(WHITE, 0.9), Style=skia.Paint.kStroke_Style, StrokeWidth=3)
            c.drawRoundRect(skia.Rect.MakeXYWH(x - tw / 2 * k, y - th / 2 * k, tw * k, th * k), 12, 12, p)
    # the door shot: full frame -> a small screen in the middle -> switched off
    koff = lin(t, tz + 2.0, tz + 2.25)
    w_ = lerp(W, 300, kz); h_ = lerp(H, 169, kz)
    if koff < 1:
        hh = h_ * (1 - koff) + 3 * koff
        footage(c, mt, cx - w_ / 2, lerp(H / 2, cy, kz) - hh / 2, w_, hh, key='tru', mode='color', contrast=1.1, sat=1.1, shape='round' if kz > 0 else 'rect', r=14 * kz, fy=0.5,
                alpha=lin(t, t0, t0 + 0.2))
        if kz > 0:
            p = skia.Paint(AntiAlias=True, Color=col(WHITE, kz), Style=skia.Paint.kStroke_Style, StrokeWidth=3)
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - w_ / 2, cy - hh / 2, w_, hh), 14 * kz, 14 * kz, p)
    # title in the emptied centre
    tt = tz + 2.35
    if t >= tt:
        pop(c, '圆形监狱', cx, cy + 22, font('cnb', 92), t, tt, WHITE, 'c', tracking=10, grow=0.3)
        draw_text(c, 'PANOPTICON', cx, cy + 78, font('serif', 34, 800), RED, 'c', lin(t, tt + 0.15, tt + 0.4), 16)
        a = lin(t, tt + 0.5, tt + 0.9)
        draw_text(c, 'The prisoner walked out.   The audience stayed.', cx, 985, font('serifi', 40), WHITE, 'c', a)
        draw_text(c, '囚徒走出去了，观众还坐在原地。', cx, 1034, font('cn', 28), WHITE, 'c', a * 0.9, 4)
        fm = font('cn', 19)
        draw_text(c, 'MUSIC   パノプティコン / r-906', 96, 520, fm, WHITE, 'l', a * 0.8, 2)
        draw_text(c, 'SOURCE   THE TRUMAN SHOW (1998)', W - 96, 520, fm, WHITE, 'r', a * 0.8, 2)
    if t < tz:
        bars(c, int(132 * (1 - lin(t, t0, t0 + 0.6))))
    hud(c, t, n, dark=True, alpha=0.4 + 0.6 * kz, label='THE TRUMAN SHOW — FINAL EPISODE')
    return dict(grain=6 + 3 * kz, chroma=1 + 8 * pulse(t, tz, 0.15), flash=0.35 * pulse(t, tz, 0.06), scan=0.2 * kz)

def s_end(c, t, n):
    """CEASE TRANSMISSION. / What else is on?"""
    c.clear(col(BLACK))
    t14, t15 = st('s14'), st('s15'); toff = T_END + 3.25
    if t < t15 - 0.1:
        typed(c, 'CEASE TRANSMISSION.', W / 2, H / 2 + 10, font('monob', 54), t, t14, t14 + 0.7, WHITE, 'c', tracking=10)
        a = lin(t, t14 + 0.8, t14 + 0.9)
        if int(t * 3) % 2 == 0: rect(c, W / 2 - 150, H / 2 + 70, 18, 18, RED, a)
        draw_text(c, 'NO SIGNAL', W / 2 - 118, H / 2 + 88, font('mono', 22), WHITE, 'l', a * 0.85, 6)
        sub(c, '停止播送。', t, t14, t15 - 0.15, dark=True)
    else:
        k = lin(t, toff, toff + 0.14); k2 = lin(t, toff + 0.14, toff + 0.3)
        w_, h_ = 880 * (1 - 0.9 * k2), 495 * (1 - k) + 4 * k
        x, y = W / 2 - w_ / 2, 420 - h_ / 2
        if k < 1:
            footage(c, 5756.9 + (t - t15), x, y, w_, h_, key='end', mode='color', contrast=1.1, shape='round', r=24 * (1 - k), fy=0.4)
            if k == 0: tv_frame(c, x, y, w_, h_, WHITE, 1.0, r=24)
        else: rect(c, x, y, w_, h_, WHITE, 1 - lin(t, toff + 0.3, toff + 0.5))
        a = 1 - k
        typed(c, 'What else is on?', W / 2, 800, font('serifi', 84), t, t15, t15 + 0.55, WHITE, 'c', cursor=False, alpha=a)
        sub(c, '“还有别的台吗？”', t, t15, toff, dark=True, y=900, size=36)
    return dict(grain=12, scan=0.5, chroma=1.5, vig=1.0)

TABLE = [(119.5, 146.4, s_wall), (146.4, 162.3, s_slam), (162.3, 178.5, s_night), (178.5, 204.0, s_bow), (204.0, 1e9, s_end)]
