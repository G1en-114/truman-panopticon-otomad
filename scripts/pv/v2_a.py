"""v2 scenes, part A (0 – 25.9 s): intro narration, Christof's doctrine, Truman's morning."""
import math, skia
from core import *
from kit import WC, SPK, wt, sub, hud
from motion import *
import lib
from lib import sticker, seq

def B(b): return b2t(b)
GRID_T = [164.4, 168.7, 171.6, 201.7, 215.0, 259.0, 290.0, 292.0, 340.0, 420.0, 470.0, 555.0, 590.0, 640.0, 800.0, 870.0,
          1100.0, 1215.0, 1425.0, 1500.0, 1768.0, 1770.0, 2100.0, 2200.0, 2460.0, 2590.0, 2780.0, 2900.0, 3000.0, 3060.0,
          3250.0, 3340.0, 3500.0, 3600.0, 4204.3, 4265.0, 4310.0, 4350.0, 4420.0, 4560.0]
DARK_HI = (226, 222, 214)
NAR = 0.24 - 3696.58
def nw(mt): return mt + NAR      # narration word time

def bg_img(c, name, t, alpha=1.0, zoom=1.08, drift=12.0, rot=0.0, style='raw'):
    """full-frame background image with a slow drift (screen space)"""
    iw, ih = lib.size(name)
    s = max(W / iw, H / ih) * zoom
    c.save(); c.translate(W / 2 + drift * math.sin(t * 0.37), H / 2 + drift * math.cos(t * 0.29)); c.rotate(rot)
    sticker(c, name, 0, 0, h=ih * s, style=style, alpha=alpha)
    c.restore()

# ====================================================================== INTRO
def s_intro(c, t, n):
    c.clear(col(BLACK)); paper(c, t, 7, dark=True)
    tz0, tz1 = 1.9, 4.6
    cam = Cam([(0, (0, 30, 2.05, -3), 'lin'), (tz0, (0, 20, 1.85, -2), 'oc'), (tz1, (40, 0, 0.27, 9), 'io'), (6.0, (60, 10, 0.235, 11), 'oc')])
    c.save(); z = cam.apply(c, t)
    # ---- the wall of feeds
    TW, TH, GX, GY = 420, 236, 520, 300
    for j in range(-5, 6):
        for i in range(-7, 8):
            x, y = i * GX, j * GY; d = math.hypot(i, j * 1.5)
            if i == 0 and j == 0: ton = 0.0
            else: ton = tz0 + 0.05 + d * 0.16 + rnd(i * 7 + j * 13) * 0.25
            a = lin(t, ton, ton + 0.1)
            if a <= 0: continue
            if i == 0 and j == 0:
                footage(c, 3924.0 + t * 0.5, x - TW / 2, y - TH / 2, TW, TH, key='baby', lo=BLACK, hi=DARK_HI, contrast=1.3)
            else:
                tile(c, GRID_T[(i * 7 + j * 3) % len(GRID_T)], x - TW / 2, y - TH / 2, TW, TH, alpha=a * 0.85, lo=BLACK, hi=DARK_HI, contrast=1.15)
            rect(c, x - TW / 2, y - TH / 2, TW, TH, WHITE, a * 0.6, stroke=2 / max(z, 0.3))
            label(c, f'CAM {1 + int(rnd(i * 3.1 + j * 5.7) * 4999):04d}', x - TW / 2 + 10, y - TH / 2 + 24, 15, WHITE, a * 0.85)
            if rnd(i + j * 9.3) > 0.55: circle(c, x + TW / 2 - 18, y - TH / 2 + 18, 6, RED, a)
            # network: links to right / down neighbours
            for (di, dj) in ((1, 0), (0, 1)):
                tl = ton + 0.12
                k = out_cubic(lin(t, tl, tl + 0.35))
                if k > 0 and abs(i + di) <= 7 and abs(j + dj) <= 5:
                    x1 = x + di * (GX - TW) / 2 * 0 + di * TW / 2; y1 = y + dj * TH / 2
                    x2 = x1 + di * (GX - TW) * k; y2 = y1 + dj * (GY - TH) * k
                    line(c, x1, y1, x2, y2, RED, 3 / max(z, 0.3), 0.9 * a)
                    circle(c, x1, y1, 5 / max(z, 0.3), RED, a)
    # big outlined word across the wall
    if t > nw(3699.52):
        ktext(c, t, ('NETWORK', font('anton', 900), RED), 0, 330, nw(3699.52), 'zoom', 'c', dur=0.4, stagger=0.03, stroke=10, tracking=40, alpha=0.9)
    # words around the first feed (world space, left behind by the pull-back)
    fi = font('serifi', 46); fh = font('anton', 150)
    ktext(c, t, ('An entire', fi, WHITE), -210, -142, nw(3696.58), 'rise', times=[nw(3696.58)] * 3 + [nw(3696.82) + k * 0.02 for k in range(6)])
    ktext(c, t, ('HUMAN', fh, WHITE), -212, 262, nw(3697.26), 'split', stagger=0.035, tracking=4, dur=0.4)
    corners(c, -226, 140, 440, 140, lin(t, nw(3697.26) + 0.15, nw(3697.26) + 0.5), RED, 40, 4)
    ktext(c, t, ('life,', font('serifi', 120), RED), 225, 262, nw(3697.72), 'orbit', 'l', stagger=0.04, seed=4, dur=0.45)
    tr = nw(3698.14)
    if t >= tr:
        on = int(t * 3) % 2 == 0
        circle(c, 120, -150, 11, RED, 1.0 if on else 0.3)
        ktext(c, t, ('REC', font('monob', 30), WHITE), 140, -139, tr, 'type', stagger=0.04)
        ktext(c, t, ('recorded', font('monob', 44), WHITE), 210, -62 - 140, tr, 'flip', 'r', stagger=0.03, add=('scramble',), dur=0.45)
    c.restore()
    # ---- screen space: running sentence + the slam
    fm = font('mono', 28)
    ws = [('on', nw(3698.76)), ('an', nw(3698.98)), ('intricate', nw(3699.10)), ('network', nw(3699.52)), ('of', nw(3700.0))]
    a_s = 1 - lin(t, nw(3700.22) - 0.05, nw(3700.22) + 0.05)
    if t > ws[0][1] and a_s > 0:
        rect(c, 120, 860, 760 * out_cubic(lin(t, ws[0][1], ws[0][1] + 0.3)), 64, BLACK, 0.85 * a_s)
        ktext(c, t, (' '.join(w for w, _ in ws), fm, WHITE), 140, 902, 0, 'type', times=words_times(ws), alpha=a_s, tracking=3, add=('scramble',), dur=0.25)
    th, tc = nw(3700.22), nw(3700.44)
    if t >= th:
        ky = lin(t, th, th + 0.05)
        seq(c, 'b_cctv', t, W / 2, H / 2 + 20, fps=24, loop=False, t0=tc - 0.3, h=980, style='ht_white', alpha=ky)
        for k in range(9):
            a = math.radians(k * 40 + 15); r = 640 + 90 * (k % 3)
            kk = out_expo(lin(t, tc + k * 0.025, tc + k * 0.025 + 0.35))
            if kk > 0:
                sticker(c, f'cam_{k + 1}', W / 2 + math.cos(a) * r * kk, H / 2 + math.sin(a) * r * 0.62 * kk, h=170 + 40 * (k % 2), rot=(rnd(k) - 0.5) * 40 + 30 * (1 - kk),
                        style='ht_white', alpha=kk)
        ktext(c, t, ('HIDDEN', font('anton', 300), WHITE), W / 2, 470, th, 'zoom', 'c', stagger=0.025, tracking=10, trail=3, add=('slice',))
        ktext(c, t, ('CAMERAS', font('anton', 300), RED), W / 2, 790, tc, 'split', 'c', stagger=0.03, tracking=10, dur=0.36)
        corners(c, W / 2 - 640, 230, 1280, 600, lin(t, tc + 0.2, tc + 0.5), WHITE, 90, 6)
    # counter
    kc = in_out(lin(t, tz0, tc))
    label(c, f'{int(1 + 4999 * kc ** 2):04d} / 5000  FEEDS ONLINE', W - 70, 150, 20, WHITE, 0.85 * lin(t, 0.4, 0.8), 'r', 3)
    sub(c, '一个人的一生，被密布全镇的隐藏摄像机完整记录', t, 0.4, 5.0, dark=True)
    hud(c, t, n, dark=True, alpha=lin(t, 0.2, 0.5), cam=int(1 + 4999 * kc ** 2))
    ki = in_cubic(lin(t, 5.0, 5.8))
    iris(c, ki, W / 2, H / 2 + 20, blades=7, rot=-40)
    return dict(grain=10, scan=0.45, tvon=lin(t, 0.0, 0.4), chroma=1.5 + 6 * pulse(t, th, 0.2) + 4 * pulse(t, tc, 0.2),
                flash=0.45 * pulse(t, th, 0.08) + 0.35 * pulse(t, tc, 0.08), zblur=0.25 * pulse(t, th, 0.12) + 0.2 * pulse(t, tc, 0.12))

def s_pickup(c, t, n):
    c.clear(col(BLACK))
    t3 = B(3)
    ktext(c, t, ('We', font('serifi', 130), WHITE), W / 2 - 40, H / 2 + 40, wt('c01', 0), 'rise', 'r')
    ktext(c, t, ('ac—', font('serifi', 130), WHITE), W / 2 + 10, H / 2 + 40, WC['c01'][1]['syl'][0]['t'], 'rise')
    iris(c, 0.965 - 0.02 * lin(t, B(1.4), t3), W / 2, H / 2, blades=7, rot=-40)
    hud(c, t, n, dark=True, alpha=0.6)
    return dict(grain=10, scan=0.3, chroma=1.0)

# ====================================================================== A1: the doctrine (one continuous world)
ACC = (-720, -430, -24)      # world anchors (x, y, rot)
REA = (680, 330, 16)
def s_a1(c, t, n):
    b = t2b(t)
    t3, t4, t7, t8, t11, t13 = B(3), B(4), B(7), B(8), B(11), B(13)
    paper(c, t, 3)
    cam = Cam([(t3 - 0.01, (ACC[0] + 60, ACC[1] + 140, 1.55, ACC[2] - 14), 'lin'), (t3 + 0.35, (ACC[0] + 120, ACC[1] + 120, 1.15, ACC[2]), 'oq'),
               (t4 - 0.12, (ACC[0] + 160, ACC[1] + 110, 1.1, ACC[2] + 2), 'lin'),
               (t4 + 0.2, (REA[0], REA[1] - 40, 1.2, REA[2]), 'whip'), (t7 - 0.15, (REA[0] + 40, REA[1] - 40, 1.12, REA[2] + 3), 'lin'),
               (t8 + 0.05, (0, 60, 0.43, 0), 'whip'), (t11 - 0.1, (0, 120, 0.47, -4), 'lin'), (t11 + 0.25, (0, 330, 0.62, 3), 'oq'),
               (t13 - 0.18, (0, 320, 0.66, 4), 'lin'), (t13 + 0.12, (0, 40, 5.5, 30), 'ix')], shake=6)
    c.save(); z = cam.apply(c, t)
    # backdrop: constructivist poster as the ground of the world, Christof behind the glass dome
    c.save(); c.rotate(-8); sticker(c, 'gen:constr', 0, 100, h=3400, style='raw', alpha=0.92); c.restore()
    sticker(c, 'christof_hands', 40, -120, h=2000, style='bw', alpha=0.95, border=10, shadow=14)
    gsc = 1 + 0.04 * pulse(t, t8, 0.2)
    sticker(c, 'g_globe', 0, 140, h=1050 * gsc, style='tint', border=8, shadow=16)
    # ---- We ACCEPT  (on the red diagonal)
    c.save(); c.translate(ACC[0], ACC[1]); c.rotate(ACC[2])
    rect(c, -520, -250, 1250 * out_quint(lin(t, t3, t3 + 0.3)), 300, BLACK)
    ktext(c, t, ('We', font('serifi', 110), RED), -480, -275, t3 - 0.5, 'type')
    ktext(c, t, ('ACCEPT', font('anton', 300), PAPER), -480, 20, t3, 'flip', stagger=0.035, tracking=8)
    label(c, 'ART. 01 — THE AUDIENCE', -480, 90, 26, INK, 0.9 * lin(t, t3 + 0.2, t3 + 0.4), tracking=4, bold=True)
    c.restore()
    # ---- the REALITY  (syllable by syllable)
    c.save(); c.translate(REA[0], REA[1]); c.rotate(REA[2])
    ktext(c, t, ('the', font('serifi', 100), INK), -560, -170, wt('c01', 2), 'rise')
    syl = WC['c01'][3]['syl']; tt = [syl[0]['t']] * 2 + [syl[1]['t']] * 2 + [syl[2]['t']] + [syl[3]['t']] * 2
    kp = out_quint(lin(t, tt[0], tt[0] + 0.25))
    rect(c, -580, -140, 1180 * kp, 270, INK)
    ktext(c, t, ('REALITY', font('bodoni', 250), PAPER), -550, 95, 0, 'drop', times=tt, tracking=2, add=('slice',))
    corners(c, -600, -160, 1220, 310, lin(t, tt[-1] + 0.1, tt[-1] + 0.4), RED, 60, 6)
    for k_, s_ in enumerate(syl):
        if t >= s_['t']: circle(c, -560 + k_ * 40, 165, 10, RED, 1)
    c.restore()
    # ---- of the WORLD  (around the dome) + with which we're PRESENTED
    if t >= t7 - 0.1:
        ring = t * 9
        arc_text(c, t, 'of  the', 0, 140, 640, ring - 60, font('serifi', 110), INK, t0=wt('c01', 4), t1=wt('c01', 5))
        arc_text(c, t, 'WORLD', 0, 140, 600, ring + 12, font('anton', 380), RED, tracking=24, t0=wt('c01', 6), t1=wt('c01', 6) + 0.18)
        ticks_ring(c, 0, 140, 820, 120, INK, 0.8, -ring * 0.5, 5, 18, 3)
        ws_ = 'with  which  we\'re'
        arc_text(c, t, ws_, 0, 140, 920, 180 - ring * 0.6, font('serifi', 130), INK, t0=wt('c01', 7), t1=wt('c01', 9) + 0.1, inward=True)
    tp = wt('c01', 10)
    if t >= tp:
        kb = out_quint(lin(t, tp, tp + 0.3))
        rect(c, -900, 900, 1800 * kb, 260, RED)
        ktext(c, t, ('PRESENTED.', font('anton', 230), PAPER), 0, 1110, tp, 'stack', 'c', stagger=0.03, tracking=12, dur=0.45)
    c.restore()
    # ---- It's as simple as that  (inside the dome)
    if t >= t13 - 0.06:
        kin = lin(t, t13 - 0.06, t13 + 0.06)
        rect(c, 0, 0, W, H, PAPER, kin)
        if kin >= 1: paper(c, t, 5)
    sub(c, '我们接受眼前呈现给我们的这个世界', t, t3, t13 - 0.1)
    hud(c, t, n, dark=False)
    ki = 1 - out_expo(lin(t, t3, t3 + 0.32))
    iris(c, ki, W / 2, H / 2, blades=7, rot=-40 + 90 * (1 - ki))
    return dict(grain=8, flash=0.55 * pulse(t, t3, 0.07) + 0.25 * pulse(t, t8, 0.07), chroma=2 + 6 * pulse(t, t3, 0.12) + 4 * pulse(t, t8, 0.1),
                zblur=0.18 * pulse(t, t3, 0.1) + 0.15 * pulse(t, t8 - 0.05, 0.12) + 0.4 * in_cubic(lin(t, t13 - 0.2, t13)))

def s_simple(c, t, n):
    """It's as simple as that."""
    paper(c, t, 5)
    t13 = B(13); t16 = B(16)
    cam = Cam([(t13, (0, 0, 1.6, 8), 'lin'), (t13 + 0.3, (0, 0, 1.0, -3), 'oq'), (t16, (0, 0, 1.08, -5), 'lin')], shake=4)
    c.save(); cam.apply(c, t)
    sticker(c, 'g_globe', 560, 60, h=1180, style='tint', alpha=0.9, rot=8)
    sticker(c, 'g_puppet', 560, -520, h=900, style='bw', alpha=0.95, rot=4 + 2 * math.sin(t * 2))
    ws = [(w['text'], w['t']) for w in WC['c02']]
    strips = [4, 5, 6, 8, 5]
    for k, (s_, tw) in enumerate(ws):
        y = -330 + k * 165
        kk = out_quint(lin(t, tw, tw + 0.2))
        sticker(c, f'scrap_{strips[k]}', -800 + 30 * k, y - 44, w=(text_w(s_.upper() + '.', font('monob', 130), 6) + 160) * kk + 1, h=None, style='raw', rot=-4 + 2 * k, ax=0, alpha=kk, sx=1)
    for k, (s_, tw) in enumerate(ws):
        y = -330 + k * 165
        ktext(c, t, (s_.upper() + ('.' if k == 4 else ''), font('monob', 130), INK), -740 + 30 * k, y, tw, 'type', stagger=0.03, tracking=6, add=('scramble',), dur=0.3)
    xk = lin(t, ws[-1][1] + 0.25, ws[-1][1] + 0.5)
    xmark(c, -520, 380, 80, xk, RED, 16)
    c.restore()
    sub(c, '就这么简单', t, t13, t16 - 0.05)
    hud(c, t, n, dark=False)
    return dict(grain=8, flash=0.3 * pulse(t, t13, 0.08), zblur=0.3 * (1 - out_expo(lin(t, t13, t13 + 0.25))))

def s_real(c, t, n):
    """IT'S / ALL / REAL.  three constructivist cuts (Marlon's line)"""
    h0, h1, h2 = (wt('c03', i) for i in range(3)); t19 = B(19)
    k = 0 if t < h1 else (1 if t < h2 else 2)
    th = (h0, h1, h2)[k]
    z = 1.0 + 0.12 * (1 - out_expo(lin(t, th, th + 0.25))) + 0.02 * (t - th)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.rotate((-3, 4, -2)[k] * (1 - out_expo(lin(t, th, th + 0.3)))); c.translate(-W / 2, -H / 2)
    if k == 0:
        c.clear(col(BLACK))
        circle(c, 1320, 520, 430, RED)
        sticker(c, 'marlon', 1330, 600, h=1000, style='bw', border=10, shadow=12)
        c.save(); c.translate(260, 760); c.rotate(-14); ktext(c, t, ("IT'S", font('anton', 460), PAPER), 0, 0, h0, 'split', stagger=0.03, tracking=8, dur=0.25); c.restore()
    elif k == 1:
        c.clear(col(RED))
        p = skia.Path(); p.moveTo(0, H); p.lineTo(W * 0.62, 0); p.lineTo(W, 0); p.lineTo(W, H); p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(BLACK)))
        sticker(c, 'marlon', 520, 620, h=1150, style='ht', border=10, shadow=12, flip=True)
        ktext(c, t, ('ALL', font('anton', 620), PAPER), 960, 840, h1, 'stack', stagger=0.03, tracking=8, dur=0.3)
    else:
        paper(c, t, 9)
        sticker(c, 'g_eye', W / 2, H / 2 - 40, w=1500, style='bw', rot=-4)
        ktext(c, t, ('REAL.', font('bodoni', 520), INK), W / 2, 900, h2, 'slam', 'c', stagger=0.03, tracking=-4, add=('slice',))
        rect(c, W / 2 - 700, 940, 1400 * out_quint(lin(t, h2 + 0.1, h2 + 0.4)), 26, RED)
        label(c, 'MARLON — BEST FRIEND SINCE AGE 7 — PAID CAST MEMBER', W / 2, 1000, 22, INK, lin(t, h2 + 0.3, h2 + 0.5), 'c', 4)
    c.restore()
    sub(c, '——全都是真的', t, h0, t19 - 0.05, dark=k < 2, y=1052, size=30)
    hud(c, t, n, dark=k < 2)
    return dict(grain=9, invert=0.9 * pulse(t, th, 0.05), chroma=8 * pulse(t, th, 0.12), zblur=0.2 * pulse(t, th, 0.1))

def s_cards(c, t, n):
    """NO SCRIPTS. NO CUE CARDS."""
    t19, t225 = B(19), B(22.5)
    paper(c, t, 2)
    cam = Cam([(t19, (W / 2, H / 2 + 60, 1.25, -6), 'lin'), (t19 + 0.3, (W / 2, H / 2, 1.0, 0), 'oq'), (t225, (W / 2 + 30, H / 2, 1.05, 2), 'lin')], shake=5)
    c.save(); cam.apply(c, t)
    rect(c, -200, 760, W + 400, 400, INK)
    c.save(); c.translate(W / 2, 300); c.rotate(-12); rect(c, -1400, -60, 2800 * out_quint(lin(t, t19, t19 + 0.3)), 120, RED); c.restore()
    sticker(c, 'g_audience', W / 2, 760, w=2050, style='bw', ay=0.62)
    ws = WC['c04']; xs = [260, 640, 1060, 1380, 1700]
    out = t225 - 0.12
    for k, w in enumerate(ws):
        tw = w['t']
        if t < tw: continue
        p = (t - tw) / 0.3
        ry = 90 * (1 - out_back(p, 1.5))
        dy = 0; rot = (rnd(k * 3) - 0.5) * 10
        if t > out:
            q = (t - out) / 0.4; dy = -900 * in_cubic(q); rot += 200 * in_cubic(q) * (1 if k % 2 else -1); ry += 0
        c.save(); c.translate(xs[k], 360 + dy); persp(c, 0, 0, ry=ry); c.rotate(rot)
        fs = 120 if len(w['text']) > 3 else 150
        cw = text_w(w['text'].upper(), font('anton', fs), 4) + 70
        rect(c, -cw / 2 + 8, -105 + 10, cw, 210, BLACK, 0.35)
        rect(c, -cw / 2, -105, cw, 210, WHITE)
        draw_text(c, w['text'].upper(), 0, fs * 0.36, font('anton', fs), INK, 'c', tracking=4)
        if k in (1, 3, 4):
            tx = tw + 0.12 if k == 1 else ws[4]['t'] + 0.12
            xmark(c, 0, 0, cw * 0.42, lin(t, tx, tx + 0.22), RED, 18)
        c.restore()
    c.restore()
    sub(c, '没有剧本，没有提词卡', t, t19, t225 - 0.05)
    hud(c, t, n)
    return dict(grain=8, flash=0.4 * pulse(t, t19, 0.07), chroma=5 * pulse(t, ws[1]['t'], 0.1) + 5 * pulse(t, ws[4]['t'], 0.1))

def s_genuine(c, t, n):
    """it's genuine."""
    t225, t255 = B(22.5), B(25.5)
    c.clear(col(BLACK))
    cam = Cam([(t225, (W / 2 - 80, H / 2, 1.15, 3), 'lin'), (t225 + 0.4, (W / 2, H / 2, 1.0, 0), 'oq'), (t255, (W / 2 + 40, H / 2, 1.07, -1), 'lin')])
    c.save(); cam.apply(c, t)
    sticker(c, 'g_tv', 1330, 560, h=980, style='ht_white')
    footage(c, 36.2 + (t - t225) * 0.8, 1010, 300, 520, 410, key='chr', lo=BLACK, hi=DARK_HI, contrast=1.3, shape='round', r=60, fx=0.45, fy=0.3)
    ktext(c, t, ("it's", font('serifi', 150), WHITE), 120, 420, wt('c05', 0), 'rise')
    ktext(c, t, ('genuine.', font('serifi', 250), WHITE), 110, 700, wt('c05', 1), 'orbit', stagger=0.05, dur=0.55, seed=3, trail=4)
    line(c, 120, 760, 120 + 840 * out_cubic(lin(t, wt('c05', 1) + 0.3, wt('c05', 1) + 0.7)), 760, RED, 6)
    label(c, 'CH.01  THE CREATOR', 1040, 860, 24, WHITE, 0.85, tracking=4, bold=True)
    c.restore()
    sub(c, '——这是真实的人生', t, t225, t255 - 0.05, dark=True)
    hud(c, t, n, dark=True)
    return dict(grain=10, scan=0.3, slice_=0.5 * pulse(t, t225, 0.12), chroma=3 + 6 * pulse(t, t225, 0.15))

def s_sun(c, t, n):
    """CUE THE SUN"""
    t255, t30, t335 = B(25.5), B(30.4), B(33.5)
    c.clear(col(BLACK)); paper(c, t, 8, dark=True)
    kz = in_expo(lin(t, t30, t335 - 0.1))
    cam = Cam([(t255, (W / 2, H / 2, 1.1, -4), 'lin'), (t255 + 0.3, (W / 2, H / 2, 1.0, 0), 'oq'), (t30, (W / 2, H / 2 + 20, 1.05, 2), 'lin'),
               (t335 - 0.1, (W / 2, 470, 14.0, 25), 'ix')])
    c.save(); cam.apply(c, t)
    ksun = out_cubic(lin(t, wt('c06', 2), wt('c06', 2) + 1.4))
    sy = lerp(H + 300, 470, ksun)
    # rays = sight lines; the sun is a studio lamp
    for i in range(40):
        a = math.radians(i * 9 + t * 12)
        line(c, W / 2 + math.sin(a) * 330, sy - math.cos(a) * 330, W / 2 + math.sin(a) * (420 + 90 * (i % 3 == 0)), sy - math.cos(a) * (420 + 90 * (i % 3 == 0)), WHITE, 3, 0.75 * ksun)
    if t >= wt('c06', 2):
        footage(c, min(4812.2, 4810.2 + (t - wt('c06', 2)) * 0.55), W / 2 - 300, sy - 300, 600, 600, key='sun', shape='circle', lo=(40, 36, 30), hi=WHITE, contrast=1.5, gamma=0.8)
        circle(c, W / 2, sy, 300, WHITE, 1, 5)
    ksw = out_back(lin(t, wt('c06', 0), wt('c06', 0) + 0.6), 1.2)
    sticker(c, 'g_sirius', W / 2 + 560, -40 + 420 * ksw, h=560, style='ht_white', rot=-18 + 10 * math.sin(t * 2.2), ay=0.15, alpha=lin(t, wt('c06', 0), wt('c06', 0) + 0.05))
    pd = skia.BlendMode.kDifference
    ktext(c, t, ('CUE', font('anton', 360), WHITE), 170, 560, wt('c06', 0), 'slam', stagger=0.02, tracking=10, blend=pd, add=('slice',))
    ktext(c, t, ('the', font('serifi', 150), RED), 830, 560, wt('c06', 1), 'orbit', dur=0.3)
    ktext(c, t, ('SUN', font('anton', 360), WHITE), 1080, 560, wt('c06', 2), 'stack', stagger=0.03, tracking=10, blend=pd, dur=0.4)
    label(c, 'LUNAR ROOM — 04:12 AM — WEATHER PROGRAM: SUNRISE', W / 2, 150, 22, WHITE, 0.8 * lin(t, t255, t255 + 0.2), 'c', 4)
    c.restore()
    sub(c, '放太阳！', t, t255, t30, dark=True, size=38)
    hud(c, t, n, dark=True, alpha=1 - kz)
    return dict(grain=10, chroma=5 * pulse(t, t255, 0.12) + 6 * pulse(t, wt('c06', 2), 0.14), flash=0.4 * pulse(t, t255, 0.07) + in_cubic(lin(t, t335 - 0.45, t335)),
                zblur=0.5 * kz)

# ====================================================================== A2: the morning
def s_morning(c, t, n):
    """Good morning! (an)other beautiful day in paradise — dolly along the radio dial to the postcard"""
    t335, t35, t42 = B(33.5), B(35), B(42)
    bg_img(c, 'gen:skywall', t, zoom=1.35, drift=0, style='tint')
    par = Track([(t335, 0.0, 'lin'), (t35 - 0.1, 30.0, 'lin'), (B(41.2), 2700.0, 'io'), (t42, 2760.0, 'lin')])
    cam = Cam([(t335, (W / 2, H / 2, 1.25, -5), 'lin'), (t335 + 0.4, (W / 2, H / 2, 1.0, 0), 'oq'), (t35 - 0.1, (W / 2 + 30, H / 2, 1.0, 0), 'lin'),
               (B(41.2), (W / 2 + 2700, H / 2 - 20, 0.92, -2), 'io'), (t42 - 0.12, (W / 2 + 2760, H / 2 - 20, 0.95, -3), 'lin'),
               (t42 + 0.1, (W / 2 + 2900, H / 2 + 900, 1.4, 25), 'ix')], shake=4)
    c.save()
    # parallax sky band (moves at 30 % of the camera)
    c.save(); c.translate(-par(t) * 0.3, 0); bg_img(c, 'gen:skywall', 0, zoom=1.35, drift=0, style='tint'); c.restore()
    cam.apply(c, t)
    # Truman, waving at the neighbours
    kt = out_back(lin(t, t335, t335 + 0.35), 1.3)
    seq(c, 's_wave', t, 1500, 700, fps=12, h=760 * kt + 1, style='tint', border=12, shadow=16, alpha=c01(kt * 3))
    ktext(c, t, ('GOOD', font('anton', 330), INK), 110, 470, wt('c07', 0), 'drop', stagger=0.04, tracking=10, shadow=(10, 10, WHITE, 1))
    ktext(c, t, ('MORNING!', font('anton', 240), RED), 120, 740, wt('c07', 1), 'split', stagger=0.035, tracking=8, shadow=(8, 8, WHITE, 1), dur=0.35)
    sun_k = out_back(lin(t, wt('c07', 1), wt('c07', 1) + 0.3))
    circle(c, 900, 200, 70 * sun_k, RED); burst(c, 900, 200, 90 * sun_k, 130 * sun_k, 16, RED, 1, t * 40, 5)
    # the radio dial strip
    y0 = 880
    kd = out_quint(lin(t, t35 - 0.2, t35 + 0.2))
    rect(c, 0, y0 - 70, 3600 * kd, 150, PAPER, 0.95); rect(c, 0, y0 - 70, 3600 * kd, 150, INK, 1, stroke=4)
    for i in range(0, 180):
        x = 40 + i * 20
        if x > 3600 * kd: break
        line(c, x, y0 - 70, x, y0 - (20 if i % 5 else 0), INK, 2)
        if i % 10 == 0: draw_text(c, f'{88 + i // 10 * 1.2:.1f}', x, y0 + 50, font('mono', 26), INK, 'c')
    nx = W / 2 + par(t)
    line(c, nx, y0 - 110, nx, y0 + 90, RED, 6)
    label(c, 'WSHV 104.9  "SEAHAVEN RADIO"', nx + 20, y0 - 120, 24, RED, 0.9, tracking=3, bold=True)
    for w, x, y, f, colr, sty in (('another', 760, 560, font('serifi', 150), INK, 'wipe'), ('beautiful', 1520, 410, font('bodoni', 210), INK, 'orbit'),
                                  ('day', 2300, 640, font('anton', 260), RED, 'drop'), ('in', 3060, 560, font('serifi', 150), INK, 'rise')):
        i_ = [ww['text'] for ww in WC['c08']].index('other' if w == 'another' else w)
        ktext(c, t, (w, f, colr), x, y, wt('c08', i_) - (0.12 if w == 'another' else 0), sty, stagger=0.03, seed=x, shadow=(6, 6, WHITE, 0.9))
    tp = wt('c08', 4)
    kp = out_back(lin(t, tp, tp + 0.4), 1.1)
    PX = W / 2 + 2700
    if kp > 0:
        sticker(c, 'gen:postcard', PX, 360, w=1500 * kp, style='raw', rot=-6 + 8 * (1 - kp), border=16, shadow=20)
        ktext(c, t, ('PARADISE', font('anton', 250), RED), PX, 680, tp + 0.15, 'stack', 'c', stagger=0.03, tracking=14, shadow=(8, 8, BLACK, 0.9), dur=0.4)
        corners(c, PX - 760, 390, 1520, 360, lin(t, tp + 0.4, tp + 0.7), INK, 70, 6)
    c.restore()
    sub(c, '早上好！', t, t335, t35 - 0.05); sub(c, '又是天堂里美好的一天', t, t35, t42 - 0.1)
    hud(c, t, n, cam=1)
    return dict(grain=6, flash=0.95 * (1 - out_cubic(lin(t, t335, t335 + 0.5))), zblur=0.35 * in_cubic(lin(t, t42 - 0.12, t42)), vig=0.7)

def s_farewell(c, t, n):
    """Oh, and in case I don't see ya — good afternoon, good evening, and good night!  (the sun on its rail inside the dome)"""
    b = t2b(t); t42, t59 = B(42), B(59)
    kn = in_out(lin(b, 54.0, 55.5))
    c.clear(col(mixc(PAPER, BLACK, kn))); paper(c, t, 2, dark=kn > 0.5)
    if 0 < kn < 1: rect(c, 0, 0, W, H, BLACK, kn if kn < 0.5 else 0)
    fg = mixc(INK, WHITE, kn)
    keys = [(42.0, -78), (47.5, -40), (50.5, -10), (52.5, 40), (54.5, 70), (59, 80)]
    ang = keys[0][1]
    for (b0, a0), (b1, a1) in zip(keys, keys[1:]):
        if b >= b0: ang = lerp(a0, a1, in_out(lin(b, b0, b1)))
    cx, cy, R = 0, 0, 1000
    cam = Cam([(t42, (0, -1600, 2.0, -40), 'lin'), (t42 + 0.45, (0, -560, 0.62, 0), 'oq'), (t59, (0, -560, 0.66, 0), 'lin')], shake=5)
    c.save(); cam.apply(c, t)
    c.rotate(-ang * 0.35)
    seq(c, 'b_dome', t, cx, cy - 400, fps=24, h=1400, style='bw' if kn < 0.5 else 'ht_white', alpha=0.9)
    line(c, -2000, cy, 2000, cy, fg, 6)
    for i in range(-1, 2):
        sticker(c, 'g_globe', i * 1300, cy + 520, h=900, style='tint' if kn < 0.5 else 'ht_white', alpha=0.25 + 0.0 * i)
    arc(c, cx, cy, R, -90, 180, fg, 6)
    ticks_ring(c, cx, cy, R + 10, 72, fg, 0.7, 0, 6, 16, 2)
    f = font('mono', 30)
    draw_text_arc(c, 'OMNICAM ECOSPHERE  ·  SEAHAVEN ISLAND  ·  VISIBLE FROM SPACE', cx, cy, R + 70, 0, f, fg, 0.8, 6)
    sa = math.radians(ang); sx = cx + math.sin(sa) * (R - 110); sy = cy - math.cos(sa) * (R - 110)
    line(c, cx, cy, sx, sy, RED, 3, 0.8, dash=(20, 12))
    if kn < 1:
        circle(c, sx, sy, 80, RED, 1 - kn); burst(c, sx, sy, 100, 150, 16, RED, 1 - kn, t * 40, 6)
    if kn > 0:
        circle(c, sx, sy, 110, WHITE, kn)
        sticker(c, 'g_eye', sx, sy, w=260 * out_back(lin(b, 55.0, 56.0)) + 1, style='bw', alpha=kn)
    seq(c, 's_wave', t, cx, cy - 10, fps=10, h=620, ay=1.0, style='tint' if kn < 0.5 else 'ht_white', border=10, shadow=12)
    c.restore()
    # words
    disp = ['Oh,', 'and', 'in', 'case', 'I', "don't", 'see', 'ya']
    ws = [(d, w['t']) for d, w in zip(disp, WC['c10'][:8])]
    txt = ' '.join(disp)
    a_l = 1 - lin(t, wt('c10', 8) - 0.1, wt('c10', 8) + 0.1)
    ktext(c, t, (txt, font('serifi', 76), fg), W / 2, 160, 0, 'rise', 'c', times=words_times(ws), alpha=a_l)
    trio = [('good', 'AFTERNOON,', wt('c10', 8), wt('c10', 9), 330, 0), ('good', 'EVENING,', wt('c11', 0), wt('c11', 1), 960, 1), ('and good', 'NIGHT!', wt('c11', 2), wt('c11', 4), 1590, 2)]
    for s0, s1, ta, tb, x, k in trio:
        ktext(c, t, (s0, font('serifi', 70), fg), x, 880, ta, 'rise', 'c')
        ktext(c, t, (s1, font('anton', 104), RED if k == 2 else fg), x, 995, tb, 'split' if k == 2 else 'flip', 'c', stagger=0.03, tracking=5)
    sub(c, '哦对了，万一待会儿见不到你——', t, t42, wt('c10', 8) - 0.05, dark=kn > 0.5, y=1060, size=28)
    sub(c, '下午好，晚上好，晚安！', t, wt('c10', 8), t59 - 0.6, dark=kn > 0.5, y=1060, size=28)
    hud(c, t, n, dark=kn > 0.5)
    koff = lin(t, t59 - 0.45, t59 - 0.05)
    return dict(grain=7 + 3 * kn, chroma=3 * pulse(t, wt('c11', 4), 0.12) + 8 * pulse(t, t42, 0.15), tvoff=koff, zblur=0.4 * (1 - out_expo(lin(t, t42, t42 + 0.35))))

TABLE = [(0.0, B(1.4), s_intro), (B(1.4), B(3), s_pickup), (B(3), B(13), s_a1), (B(13), B(16), s_simple), (B(16), B(19), s_real),
         (B(19), B(22.5), s_cards), (B(22.5), B(25.5), s_genuine), (B(25.5), B(33.5), s_sun), (B(33.5), B(42), s_morning), (B(42), B(59), s_farewell)]
