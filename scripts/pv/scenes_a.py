"""Scenes: intro, A1 (Christof's doctrine), A2 (the daily loop)."""
import math, skia
from core import *
from kit import *

GRID_T = [164.4, 168.7, 171.6, 201.7, 215.0, 259.0, 290.0, 292.0, 340.0, 420.0, 470.0, 555.0, 590.0, 640.0, 800.0, 870.0,
          1100.0, 1215.0, 1425.0, 1500.0, 1768.0, 1770.0, 2100.0, 2200.0, 2460.0, 2590.0, 2780.0, 2900.0, 3000.0, 3060.0,
          3250.0, 3340.0, 3500.0, 3600.0, 4204.3, 4265.0, 4310.0, 4350.0, 4420.0, 4560.0]

def cam_grid(c, t, on_t, off_t=None, cols=8, rows=5, alpha=1.0, dark=True, seed=3, lo=BLACK, hi=(200, 200, 196)):
    """wall of hidden-camera feeds; on_t(i)/off_t(i) give each tile its switch times"""
    gw = W / cols; gh = H / rows; f = font('mono', 13)
    for i in range(cols * rows):
        a = lin(t, on_t(i), on_t(i) + 0.08)
        if off_t is not None: a *= 1 - lin(t, off_t(i), off_t(i) + 0.05)
        if a <= 0: continue
        x = (i % cols) * gw; y = (i // cols) * gh
        footage(c, GRID_T[i % len(GRID_T)], x + 5, y + 5, gw - 10, gh - 10, mode='bw', alpha=a * alpha, still=True, lo=lo, hi=hi, contrast=1.1)
        draw_text(c, f'CAM {1 + int(rnd(i + seed) * 4999):04d}', x + 14, y + 26, f, WHITE if dark else INK, 'l', a * alpha * 0.9, 1.5)
        if rnd(i * 3.3 + seed) > 0.6: circle(c, x + gw - 22, y + 21, 4, RED, a * alpha)

def s_intro(c, t, n):
    c.clear(col(BLACK))
    NAR = 0.24 - 3696.58          # narration clock: movie-time + NAR = video time
    w = lambda mt: mt + NAR
    # crt power-on
    k = out_expo(lin(t, 0.02, 0.32))
    off = lambda i: 5.05 + rnd(i * 1.7) * 0.75
    cam_grid(c, t, lambda i: 0.35 + rnd(i * 7.1) * 3.4, off, alpha=0.5)
    if t < 0.5:
        rect(c, W / 2 - W / 2 * k, H / 2 - 2 - 6 * (1 - k), W * k, 4 + 12 * (1 - k), WHITE, 1 - lin(t, 0.3, 0.5))
    # caption plate
    a_pl = lin(t, 0.2, 0.4) * (1 - lin(t, 5.45, 5.7))
    rect(c, 330, 250, 1260, 560, BLACK, 0.86 * a_pl)
    rect(c, 330, 250, 1260, 560, WHITE, 0.5 * a_pl, stroke=1.5)
    fi = font('serifi', 62); fb = font('serif', 128, 900); fa = font('anton', 168)
    out = (5.45, 0.2)
    x = 400
    for s, mt in (('An', 3696.58), ('entire', 3696.82), ('human', 3697.26), ('life,', 3697.72)):
        pop(c, s, x, 360, fi, t, w(mt), WHITE, out=out); x += text_w(s + ' ', fi)
    pop(c, 'recorded', 400, 500, fb, t, w(3698.14), WHITE, out=out, grow=0.3)
    rk = lin(t, w(3698.2), w(3698.3)) * (1 - lin(t, *(5.45, 5.65)))
    if rk > 0 and int(t * 3) % 2 == 0: circle(c, 400 + text_w('recorded', fb) + 52, 458, 20, RED, rk)
    x = 400
    for s, mt in (('on', 3698.76), ('an', 3698.98), ('intricate', 3699.10), ('network', 3699.52), ('of', 3700.0)):
        pop(c, s, x, 590, fi, t, w(mt), WHITE, out=out); x += text_w(s + ' ', fi)
    pop(c, 'HIDDEN', 400, 770, fa, t, w(3700.22), WHITE, out=out, tracking=6)
    pop(c, 'CAMERAS', 400 + text_w('HIDDEN ', fa, 6) + 10, 770, fa, t, w(3700.44), RED, out=out, tracking=6)
    # camera counter
    kc = in_out(lin(t, 0.4, w(3700.6)))
    fm = font('monob', 30)
    draw_text(c, f'{int(1 + 4999 * kc ** 2):04d} / 5000 CAMERAS ONLINE', 1560, 300, font('mono', 18), WHITE, 'r', a_pl * 0.8, 2)
    sub(c, '一个人的一生，被密布全镇的隐藏摄像机完整记录', t, 0.5, 5.4, dark=True)
    hud(c, t, n, dark=True, alpha=lin(t, 0.3, 0.6), cam=int(1 + 4999 * kc ** 2))
    fl = pulse(t, w(3700.44), 0.12) * 0.35
    return dict(grain=9, scan=0.55, chroma=1.2 + 6 * pulse(t, 0.0, 0.2) + 5 * pulse(t, 5.05, 0.25), flash=fl, glitch=0.5 * lin(t, 5.0, 5.2) * (1 - lin(t, 5.8, 5.95)), vig=1.0)

def s_pickup(c, t, n):
    """a-cappella 'We ac-' on black, an iris closing in"""
    c.clear(col(BLACK))
    b = t2b(t)
    fi = font('serifi', 96)
    pop(c, 'We', W / 2 - 150, H / 2 + 30, fi, t, wt('c01', 0), WHITE, 'c')
    pop(c, 'ac—', W / 2 + 60, H / 2 + 30, fi, t, WC['c01'][1]['syl'][0]['t'], WHITE, 'c')
    k = in_cubic(lin(b, 1.4, 3.0))
    circle(c, W / 2, H / 2, 900 * (1 - k) + 190, WHITE, 0.8, 2)
    circle(c, W / 2, H / 2, 1200 * (1 - k) + 230, WHITE, 0.35, 1)
    hud(c, t, n, dark=True)
    return dict(grain=9, scan=0.4, chroma=1.0)

def christof_window(c, t, cx, cy, R, mt, rot, alpha=1.0, color=INK):
    footage(c, mt, cx - R, cy - R, 2 * R, 2 * R, key='chr', shape='circle', alpha=alpha, fx=0.42, zoom=1.15, contrast=1.35)
    circle(c, cx, cy, R, color, alpha, 5)
    blueprint(c, cx, cy, R * 1.36, rot, color, alpha * 0.9, cells=28, labels=False, tower=False)
    f = font('mono', 17)
    draw_text_arc(c, 'CHRISTOF  ·  THE CREATOR  ·  LUNAR ROOM 221F', cx, cy, R * 1.52, -rot * 0.0 + 40, f, color, alpha * 0.85, 4)

def s_a1a(c, t, n):
    """We ACCEPT the reality of the WORLD with which we're presented. It's as simple as that. It's all real."""
    b = t2b(t); t3 = b2t(3)
    paper(c, t, 1)
    z = 1.0 + 0.035 * lin(b, 3, 19) + 0.05 * pulse(t, t3, 0.12) + 0.03 * pulse(t, wt('c03', 2), 0.12)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    # creator window (right)
    mt = min(3972.85, 3969.25 + (t - t3) * 0.62)
    christof_window(c, t, 1560, 410, 228, mt, t * 6, alpha=out_cubic(lin(t, t3, t3 + 0.25)))
    fi = font('serifi', 74); fh = font('serif', 250, 900)
    draw_text(c, 'We', 120, 330, font('serifi', 96), INK)
    # ACCEPT slams in on the downbeat
    k = out_expo(lin(t, t3, t3 + 0.16)); c.save(); c.translate(290, 350); c.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    draw_text(c, 'ACCEPT', 0, 0, fh, INK, 'l', lin(t, t3, t3 + 0.03), tracking=-4); c.restore()
    line(c, 120, 392, 120 + 1010 * out_cubic(lin(t, t3 + 0.05, t3 + 0.5)), 392, INK, 3)
    # the REALITY (inverted plate, grows with the syllables)
    pop(c, 'the', 120, 545, fi, t, wt('c01', 2))
    r0 = wt('c01', 3); fr = font('serif', 150, 900)
    wr = text_w('REALITY', fr, 2)
    kk = out_cubic(lin(t, r0, r0 + 0.5))
    if t >= r0:
        rect(c, 262, 420, (wr + 56) * kk, 160, INK)
        c.save(); c.clipRect(skia.Rect.MakeXYWH(262, 420, (wr + 56) * kk, 160))
        draw_text(c, 'REALITY', 290, 552, fr, PAPER, tracking=2); c.restore()
    # of the WORLD (the O is the dome plan)
    pop(c, 'of', 120, 770, fi, t, wt('c01', 4)); pop(c, 'the', 205, 770, fi, t, wt('c01', 5))
    w0 = wt('c01', 6); fw = font('serif', 235, 900)
    if t >= w0:
        e = out_expo(lin(t, w0, w0 + 0.18)); a = lin(t, w0, w0 + 0.05)
        x = 345; y = 790 + 30 * (1 - e)
        x += draw_text(c, 'W', x, y, fw, INK, alpha=a) + 8
        ro = 88; blueprint(c, x + ro, y - 86, ro * (0.6 + 0.4 * e), t * 40, INK, a, cells=12, labels=False, weight=1.6, sweep=[t * 120 % 360])
        circle(c, x + ro, y - 86, 9, RED, a)
        x += 2 * ro + 10
        draw_text(c, 'RLD', x, y, fw, INK, alpha=a)
    x = 120
    for i, s in ((7, 'with'), (8, 'which'), (9, "we're")):
        pop(c, s, x, 930, font('serifi', 64), t, wt('c01', i)); x += text_w(s + ' ', font('serifi', 64))
    p0 = wt('c01', 10); fp = font('serif', 104, 900)
    pop(c, 'presented.', x + 8, 930, fp, t, p0, INK, grow=0.3)
    line(c, x + 8, 950, x + 8 + text_w('presented.', fp) * out_cubic(lin(t, p0 + 0.15, p0 + 0.6)), 950, RED, 6)
    # It's as simple as that.
    s0 = wt('c02', 0)
    typed(c, "It's as simple as that.", 1262, 775, font('serifi', 58), t, s0, wt('c02', 4) + 0.12, INK)
    # IT'S ALL REAL — stamp
    for i, (s, dx) in enumerate((("IT'S", 0), ('ALL', 205), ('REAL.', 372))):
        ts = wt('c03', i)
        if t >= ts:
            e = out_expo(lin(t, ts, ts + 0.12)); c.save(); c.translate(1262 + dx, 955); c.rotate(-5); c.scale(1 + 0.8 * (1 - e), 1 + 0.8 * (1 - e))
            draw_text(c, s, 0, 0, font('anton', 122), RED, 'l', lin(t, ts, ts + 0.04) * 0.94, 3); c.restore()
    c.restore()
    sub(c, '我们接受眼前呈现给我们的这个世界', t, t3, b2t(12.9), y=1040, size=30)
    sub(c, '就这么简单', t, b2t(13), b2t(15.9), y=1040, size=30)
    sub(c, '——全都是真的', t, b2t(16), b2t(18.9), y=1040, size=30)
    hud(c, t, n, dark=False)
    return dict(grain=8, flash=0.85 * pulse(t, t3, 0.09), chroma=4 * pulse(t, t3, 0.1) + 3 * pulse(t, wt('c03', 2), 0.1))


def s_a1b(c, t, n):
    """NO SCRIPTS. NO CUE CARDS. it's genuine.  CUE THE SUN"""
    b = t2b(t); t0 = b2t(19)
    paper(c, t, 4, dark=True)
    tc = wt('c06', 0); ts = wt('c06', 2)
    fa = font('anton', 215); out = (tc - 0.06, 0.08)
    a_out = 1 - lin(t, tc - 0.06, tc + 0.02)
    z = 1 + 0.03 * lin(b, 19, 25.5) + 0.05 * pulse(t, t0, 0.1)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    if a_out > 0:
        # Christof, head-on, in a monitor
        x, y, w, h = 1230, 190, 560, 350
        mt = 36.2 + (t - t0) * 0.8
        footage(c, mt, x, y, w, h, key='chr', shape='round', r=22, alpha=a_out * lin(t, t0, t0 + 0.2), lo=BLACK, hi=(235, 232, 225), contrast=1.3, fy=0.3)
        tv_frame(c, x, y, w, h, WHITE, a_out * 0.9, r=22, label='CH.01  THE CREATOR — "IT IS GENUINE. IT IS A LIFE."')
        pop(c, 'NO', 130, 400, fa, t, wt('c04', 0), WHITE, out=out, tracking=4)
        pop(c, 'SCRIPTS', 130 + text_w('NO ', fa, 4), 400, fa, t, wt('c04', 1), WHITE, out=out, tracking=4)
        k = out_cubic(lin(t, wt('c04', 1) + 0.09, wt('c04', 1) + 0.24))
        strike(c, 130 + text_w('NO ', fa, 4) - 14, 292, (text_w('SCRIPTS', fa, 4) + 28), 34, k, RED, a_out)
        pop(c, 'NO', 130, 650, fa, t, wt('c04', 2), WHITE, out=out, tracking=4)
        pop(c, 'CUE', 130 + text_w('NO ', fa, 4), 650, fa, t, wt('c04', 3), WHITE, out=out, tracking=4)
        pop(c, 'CARDS', 130 + text_w('NO CUE ', fa, 4), 650, fa, t, wt('c04', 4), WHITE, out=out, tracking=4)
        k = out_cubic(lin(t, wt('c04', 4) + 0.12, wt('c04', 4) + 0.3))
        strike(c, 130 + text_w('NO ', fa, 4) - 14, 542, (text_w('CUE CARDS', fa, 4) + 28), 34, k, RED, a_out)
        fi = font('serifi', 104)
        pop(c, "it's", 136, 850, fi, t, wt('c05', 0), WHITE, out=out)
        pop(c, 'genuine.', 136 + text_w("it's ", fi), 850, fi, t, wt('c05', 1), WHITE, out=out)
        line(c, 136, 880, 136 + text_w("it's genuine.", fi) * out_cubic(lin(t, wt('c05', 1) + 0.2, wt('c05', 1) + 0.6)), 880, WHITE, 2, a_out)
    c.restore()
    # ---- CUE THE SUN
    if t >= tc - 0.05:
        ksun = lin(b, 26.5, 30.2); kfill = in_cubic(lin(b, 30.4, 33.3))
        cy = lerp(H + 260, 560, out_cubic(ksun)); R = 215 + 40 * ksun + 1900 * kfill
        if t >= ts:
            footage(c, min(4812.2, 4810.2 + (t - ts) * 0.55), W / 2 - R, cy - R, 2 * R, 2 * R, key='sun', shape='circle', lo=(40, 36, 30), hi=WHITE, contrast=1.5, gamma=0.8, alpha=1 - kfill)
            circle(c, W / 2, cy, R, PAPER, kfill)
            circle(c, W / 2, cy, R, WHITE, 1 - kfill, 4)
            for i in range(36):      # rays = sight lines
                a = math.radians(i * 10 + t * 14); r0 = R + 26; r1 = R + 60 + 50 * (i % 3 == 0)
                line(c, W / 2 + math.sin(a) * r0, cy - math.cos(a) * r0, W / 2 + math.sin(a) * r1, cy - math.cos(a) * r1, WHITE, 2, (1 - kfill) * 0.8 * ksun)
        fb = font('serif', 300, 900)
        pd = skia.Paint(AntiAlias=True, Color=col(WHITE), BlendMode=skia.BlendMode.kDifference)
        a_t = 1 - lin(b, 31.2, 32.6)
        for s, x, ti, f in (('CUE', 250, tc, fb), ('THE', 830, wt('c06', 1), font('serifi', 120)), ('SUN', 1080, ts, fb)):
            if t >= ti and a_t > 0:
                e = out_expo(lin(t, ti, ti + 0.14)); c.save(); c.translate(x, 470 + (1 - e) * 40); c.scale(1 + 0.3 * (1 - e), 1 + 0.3 * (1 - e))
                pd.setAlphaf(a_t); c.drawString(s, 0, 0, f, pd); c.restore()
        draw_text(c, 'LUNAR ROOM  —  04:12 AM  —  WEATHER PROGRAM: SUNRISE', W / 2, 150, font('mono', 20), WHITE, 'c', lin(t, tc, tc + 0.2) * (1 - lin(b, 29.5, 30.5)) * 0.8, 4)
    sub(c, '没有剧本，没有提词卡', t, t0, b2t(22.4), dark=True)
    sub(c, '——这是真实的人生', t, b2t(22.5), b2t(25.4), dark=True)
    sub(c, '放太阳！', t, b2t(25.5), b2t(30.5), dark=True, size=38, y=250)
    hud(c, t, n, dark=b < 31)
    return dict(grain=9, chroma=5 * pulse(t, t0, 0.1) + 6 * pulse(t, ts, 0.14), flash=0.5 * pulse(t, t0, 0.07) + 0.4 * pulse(t, tc, 0.07), shake=(0, 0))

def sun_icon(c, x, y, r, color, alpha=1.0, rot=0.0, rays=12):
    circle(c, x, y, r, color, alpha)
    for i in range(rays):
        a = math.radians(i * 360 / rays + rot)
        line(c, x + math.sin(a) * r * 1.35, y - math.cos(a) * r * 1.35, x + math.sin(a) * r * 1.8, y - math.cos(a) * r * 1.8, color, max(2, r * 0.09), alpha)

def s_a2a(c, t, n):
    """Good morning! another beautiful day in PARADISE"""
    b = t2b(t); t0 = b2t(33.5)
    paper(c, t, 2)
    slide = in_cubic(lin(b, 41.3, 42.0))
    c.save(); c.translate(-W * 1.05 * slide, 0)
    z = 1 + 0.03 * lin(b, 33.5, 42)
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    x, y, w, h = 120, 170, 780, 470
    footage(c, 167.55 + (t - t0), x, y, w, h, key='tru', shape='round', r=30, fy=0.35, contrast=1.3)
    tv_frame(c, x, y, w, h, INK, 1.0, r=30, label='CAM 0001  FRONT DOOR — 36 LANCASTER SQ.')
    fb = font('serif', 200, 900)
    pop(c, 'Good', 980, 330, fb, t, wt('c07', 0), INK, grow=0.35)
    pop(c, 'morning!', 980, 520, fb, t, wt('c07', 1), INK, grow=0.35)
    sun_icon(c, 1700, 215, 46 * out_back(lin(t, wt('c07', 1), wt('c07', 1) + 0.25)), RED, 1.0, t * 50)
    fi = font('serifi', 84)
    pop(c, 'another', 130, 800, fi, t, wt('c08', 0))
    pop(c, 'beautiful', 130 + text_w('another ', fi), 800, font('serif', 96, 800), t, wt('c08', 1))
    pop(c, 'day', 130 + text_w('another ', fi) + text_w('beautiful ', font('serif', 96, 800)), 800, fi, t, wt('c08', 2))
    pop(c, 'in', 980, 800, fi, t, wt('c08', 3))
    p0 = wt('c08', 4); fp = font('anton', 186)
    if t >= p0:
        kk = out_cubic(lin(t, p0, p0 + 0.45)); wpl = text_w('PARADISE', fp, 8) + 70
        rect(c, 1090, 680, wpl * kk, 225, INK)
        c.save(); c.clipRect(skia.Rect.MakeXYWH(1090, 680, wpl * kk, 225)); draw_text(c, 'PARADISE', 1125, 872, fp, PAPER, tracking=8); c.restore()
        draw_text(c, '( SEAHAVEN ISLAND — THE LARGEST STUDIO EVER CONSTRUCTED )', 1090, 950, font('mono', 17), INK, 'l', lin(t, p0 + 0.3, p0 + 0.5) * 0.8, 2)
    c.restore()
    sub(c, '早上好！', t, t0, b2t(34.9)); sub(c, '又是天堂里美好的一天', t, b2t(35), b2t(41.6))
    hud(c, t, n, dark=False, cam=1)
    return dict(grain=7, flash=0.9 * (1 - lin(b, 33.3, 34.6)) ** 2, chroma=3 * pulse(t, t0, 0.1) + 10 * slide)

def s_a2b(c, t, n):
    """Oh, and in case I don't see ya — good afternoon, good evening, and good night!  (the sun on its track inside the dome)"""
    b = t2b(t)
    kn = in_out(lin(b, 54.5, 56.2))            # night falls
    bg = mixc(PAPER, BLACK, kn); fg = mixc(INK, WHITE, kn)
    paper(c, t, 2)
    if kn > 0: rect(c, 0, 0, W, H, BLACK, kn * 0.96)
    slide = 1 - out_expo(lin(b, 42.0, 43.0))
    c.save(); c.translate(W * 0.9 * slide, 0)
    cx, cy, R = W / 2, 815, 540
    # the dome
    arc(c, cx, cy, R, -90, 180, fg, 5); arc(c, cx, cy, R + 22, -90, 180, fg, 1.2, 0.6)
    arc(c, cx, cy, R - 60, -90, 180, fg, 1.2, 0.5, dash=(4, 10))
    line(c, cx - R - 90, cy, cx + R + 90, cy, fg, 4)
    for i in range(37):
        a = math.radians(-90 + i * 5); k = 1.0 + (0.035 if i % 3 else 0.06)
        line(c, cx + math.sin(a) * R, cy - math.cos(a) * R, cx + math.sin(a) * R * k, cy - math.cos(a) * R * k, fg, 1.5, 0.7)
    f = font('mono', 17)
    draw_text_arc(c, 'OMNICAM ECOSPHERE  ·  ONE OF ONLY TWO MAN-MADE STRUCTURES VISIBLE FROM SPACE', cx, cy, R + 44, 0, f, fg, 0.8, 3)
    # the sun rides its rail:  morning(-72) -> afternoon(-18) -> evening(48) -> night(80)
    keys = [(42.0, -72), (48.0, -30), (50.5, -8), (52.0, 44), (54.5, 74), (59, 78)]
    ang = keys[0][1]
    for (b0, a0), (b1, a1) in zip(keys, keys[1:]):
        if b >= b0: ang = lerp(a0, a1, in_out(lin(b, b0, b1)))
    sa = math.radians(ang); sx = cx + math.sin(sa) * (R - 60); sy = cy - math.cos(sa) * (R - 60)
    line(c, cx, cy, sx, sy, RED, 2, 0.75, dash=(12, 8))
    if kn < 1: sun_icon(c, sx, sy, 44, RED, 1 - kn, t * 40)
    if kn > 0:   # moon = the control room = an eye
        circle(c, sx, sy, 58, WHITE, kn); eye(c, sx, sy, 86, open_=out_back(lin(b, 55.6, 56.6)), color=BLACK, alpha=kn, pupil=RED, stroke=3)
        draw_text(c, 'LUNAR ROOM', sx - 80, sy + 100, f, WHITE, 'r', kn * 0.8, 3)
    # truman in the middle of his world
    footage(c, 170.0 + (t - b2t(42)) * 0.5, cx - 190, cy - 380, 380, 380, key='tru', shape='circle', fx=0.5, fy=0.3, zoom=1.25, contrast=1.3,
            lo=mixc(INK, BLACK, kn), hi=mixc(PAPER, (225, 222, 215), kn))
    circle(c, cx, cy - 190, 190, fg, 1, 4)
    crosshair(c, cx, cy - 190, 232, RED, 0.8)
    # words
    typed(c, "Oh, and in case I don't see ya —", cx, 168, font('serifi', 70), t, wt('c10', 0), wt('c10', 7) + 0.15, fg, 'c', cursor=False)
    fb = font('serif', 92, 900); fi = font('serifi', 60)
    for (ci, i0, i1, s0, s1, x) in (('c10', 8, 9, 'good', 'AFTERNOON,', 400), ('c11', 0, 1, 'good', 'EVENING,', 960), ('c11', 3, 4, 'and good', 'NIGHT!', 1520)):
        ta = wt(ci, i0) if s0 != 'and good' else wt(ci, 2)
        pop(c, s0, x, 895, fi, t, ta, fg, 'c', rise=14)
        pop(c, s1, x, 968, font('serif', 62, 900), t, wt(ci, i1), RED if s1 == 'NIGHT!' else fg, 'c', rise=14, tracking=3)
    c.restore()
    sub(c, '哦对了，万一待会儿见不到你——', t, b2t(42.2), b2t(47.3), dark=kn > 0.5, y=1040, size=30)
    sub(c, '下午好，晚上好，晚安！', t, b2t(47.5), b2t(58.6), dark=kn > 0.5, y=1040, size=30)
    hud(c, t, n, dark=kn > 0.5)
    return dict(grain=7 + 2 * kn, chroma=10 * slide + 3 * pulse(t, wt('c11', 4), 0.12), flash=0.0)

TABLE = [(19.0, 33.5, s_a1b), (33.5, 42.0, s_a2a), (42.0, 59.0, s_a2b)]
