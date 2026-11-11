"""Scenes: B1 (Sylvia's warning) and B2 (the watcher / the answer)."""
import math, skia
from core import *
from kit import *

DARK_HI = (232, 228, 220)

def s_b1a(c, t, n):
    """TRUMAN! LISTEN TO ME — EVERYBODY KNOWS EVERYTHING YOU DO"""
    b = t2b(t); t0 = b2t(59)
    c.clear(col(BLACK))
    if b < 63:
        footage(c, 1589.6 + (t - t0) * 0.9, 0, 0, W, H, key='syl', lo=BLACK, hi=(235, 40, 30), contrast=1.7, gamma=0.8, alpha=0.75, zoom=1.08 + 0.04 * lin(b, 59, 63))
        fa = font('anton', 400)
        sh = 14 * pulse(t, t0, 0.25)
        c.save(); c.translate(rnd(n) * sh - sh / 2, rnd(n + 9) * sh - sh / 2)
        pop(c, 'TRUMAN!', W / 2, 520, fa, t, t0, WHITE, 'c', grow=0.5, tracking=10)
        c.restore()
        fl = font('anton', 150); x = 330
        rect(c, 300, 640, 1320 * out_cubic(lin(t, wt('c13', 0), wt('c13', 0) + 0.3)), 190, WHITE)
        for i, s in enumerate(('LISTEN', 'TO', 'ME')):
            pop(c, s, x, 792, fl, t, wt('c13', i), BLACK if i < 2 else RED, tracking=14); x += text_w(s + '  ', fl, 14)
        sub(c, '楚门！听我说！', t, t0, b2t(62.9), dark=True)
        g = 0.6 * pulse(t, t0, 0.3)
    else:
        # eyes open across the whole wall
        for i in range(60):
            x = 96 + (i % 10) * 192; y = 110 + (i // 10) * 172
            to = b2t(63 + rnd(i * 2.3) * 6.0)
            o = out_back(lin(t, to, to + 0.18))
            if o > 0:
                dx = (W / 2 - x) / W * 2; dy = (H / 2 - y) / H * 2
                eye(c, x, y, 150, open_=o, color=WHITE, alpha=0.42, pupil=RED, look=(dx, dy), stroke=2)
        fb = font('serif', 205, 900)
        pop(c, 'EVERYBODY', 110, 330, fb, t, wt('c14', 0), WHITE, tracking=-2)
        pop(c, 'KNOWS', 1300, 335, font('anton', 205), t, wt('c14', 1), RED, tracking=6)
        pop(c, 'EVERYTHING', 110, 610, fb, t, wt('c14', 2), WHITE, tracking=-4)
        fi = font('serifi', 190)
        pop(c, 'you', 110, 880, fi, t, wt('c14', 3), WHITE)
        pop(c, 'do.', 110 + text_w('you ', fi), 880, fi, t, wt('c14', 4), WHITE)
        k = out_cubic(lin(t, wt('c14', 4), wt('c14', 4) + 0.4))
        line(c, 110, 915, 110 + 760 * k, 915, RED, 8)
        sub(c, '所有人都知道你的一举一动', t, b2t(63), b2t(69.9), dark=True)
        g = 0.35 * pulse(t, b2t(63), 0.2)
    hud(c, t, n, dark=True)
    return dict(grain=11, chroma=3 + 9 * pulse(t, t0, 0.2) + 6 * pulse(t, b2t(63), 0.15), glitch=g, flash=0.5 * pulse(t, t0, 0.06), scan=0.3)

CAST = [(165.9, 'NEIGHBOUR', 0.38), (288.0, 'PASSER-BY', 0.5), (290.2, 'TWIN  A / B', 0.3), (1229.6, 'WIFE', 0.5), (601.5, 'BEST FRIEND', 0.5), (1001.0, 'MOTHER', 0.5)]
def s_b1b(c, t, n):
    """They're pretending, Truman."""
    b = t2b(t); t0 = b2t(70)
    paper(c, t, 4, dark=True)
    cw, ch = 262, 330
    for i, (mt, lab, fx) in enumerate(CAST):
        ti = t0 + i * 0.105
        k = out_expo(lin(t, ti, ti + 0.2))
        if k <= 0: continue
        x = 100 + i * (cw + 30); y = 110 + (1 - k) * 60
        footage(c, mt, x, y, cw, ch, still=True, lo=BLACK, hi=DARK_HI, contrast=1.25, fx=fx, fy=0.3, zoom=1.5, alpha=k)
        rect(c, x, y, cw, ch, WHITE, k, stroke=2)
        draw_text(c, f'ACTOR  №{i + 1:02d}', x, y + ch + 30, font('monob', 17), WHITE, 'l', k, 2)
        draw_text(c, lab, x, y + ch + 54, font('mono', 15), WHITE, 'l', k * 0.75, 2)
        kx = lin(t, ti + 0.25, ti + 0.4)
        if kx > 0:
            rect(c, x + 14, y + ch * 0.36, (cw - 28) * out_cubic(kx), 26, BLACK, 0.92)      # eyes redacted
    fi = font('serifi', 110); fb = font('serif', 215, 900)
    pop(c, "They're", 100, 700, fi, t, wt('c15', 0), WHITE)
    pop(c, '“PRETENDING,”', 80, 915, fb, t, wt('c15', 1), RED, tracking=-5, grow=0.3)
    pop(c, 'Truman.', 1390, 700, fi, t, wt('c15', 2), WHITE)
    sub(c, '他们全都在演戏，楚门', t, t0, b2t(74.3), dark=True, y=1040, size=30)
    hud(c, t, n, dark=True)
    return dict(grain=10, chroma=2 + 8 * pulse(t, t0, 0.15), glitch=0.3 * pulse(t, t0, 0.2), scan=0.25)

def s_b1c(c, t, n):
    """IT'S A SET. / IT'S A SHOW."""
    b = t2b(t)
    show = b >= 76.0
    bg, fg = (BLACK, WHITE) if show else (PAPER, INK)
    c.clear(col(bg))
    if not show:
        paper(c, t, 3)
        footage(c, 3715.5 + (t - b2t(74.5)) * 1.2, 0, 0, W, H, key='dome', lo=(120, 116, 108), hi=PAPER, contrast=1.5, alpha=0.75, zoom=1.05)
    else:
        footage(c, 3701.2 + (t - b2t(76)) * 0.6, 0, 0, W, H, key='mon', lo=BLACK, hi=(150, 30, 24), contrast=1.4, alpha=0.9, zoom=1.05)
    cid = 'c16'
    idx = (3, 4, 5) if show else (0, 1, 2)
    wd = ("IT'S", 'A', 'SHOW.') if show else ("IT'S", 'A', 'SET.')
    fa = font('anton', 470); tot = text_w(' '.join(wd), fa, 6)
    if tot > 1720: fa = font('anton', int(470 * 1720 / tot)); tot = text_w(' '.join(wd), fa, 6)
    x = W / 2 - tot / 2
    for i, s in zip(idx, wd):
        ti = wt(cid, i)
        colr = RED if s in ('SET.', 'SHOW.') else fg
        pop(c, s, x, 720, fa, t, ti, colr, grow=0.6, d=0.1, tracking=6); x += text_w(s + ' ', fa, 6)
    f = font('mono', 20)
    draw_text(c, 'STAGE 12  ·  SKY: PAINTED  ·  SEA: 1 : 1 TANK  ·  SUN: 5K LAMP' if not show else 'ON AIR 24 / 7  ·  NO COMMERCIAL BREAKS  ·  EVERYTHING IS FOR SALE', W / 2, 860, f, fg, 'c', 0.85, 4)
    sub(c, '这是布景——' if not show else '这是一场秀！', t, b2t(74.5) if not show else b2t(76), b2t(76) if not show else b2t(78.4), dark=show)
    hud(c, t, n, dark=show)
    th = b2t(76); ts = wt(cid, 2); tw = wt(cid, 5)
    return dict(grain=10, chroma=3 + 10 * pulse(t, ts, 0.12) + 10 * pulse(t, tw, 0.12), flash=0.6 * pulse(t, th, 0.05),
                shake=(int(10 * pulse(t, ts, 0.1) * (rnd(n) - 0.5) * 2), int(10 * pulse(t, tw, 0.1) * (rnd(n + 3) - 0.5) * 2)), glitch=0.4 * pulse(t, tw, 0.2))

def s_b1d(c, t, n):
    """EVERYBODY'S WATCHING YOU"""
    b = t2b(t); t0 = b2t(78.5); ty = wt('c16', 8)
    c.clear(col(BLACK))
    ky = lin(t, ty - 0.05, ty + 0.1)
    fa = font('anton', 150); s = "EVERYBODY'S WATCHING YOU   ·   "
    sw = text_w(s, fa, 6)
    a_rows = 1 - ky
    if a_rows > 0:
        for r in range(7):
            y = 150 + r * 150 - 6
            if r == 3: continue
            off = ((t - t0) * (90 + 30 * r) * (1 if r % 2 else -1)) % sw
            x = -off - sw
            while x < W:
                draw_text(c, s, x, y, fa, WHITE, 'l', 0.5 * a_rows * lin(t, t0 + r * 0.03, t0 + r * 0.03 + 0.1), 6, stroke=2); x += sw
        rect(c, 0, 468, W, 164, WHITE, a_rows)
        x = W / 2 - text_w("EVERYBODY'S WATCHING YOU", fa, 6) / 2
        for i, wd in ((6, "EVERYBODY'S"), (7, 'WATCHING'), (8, 'YOU')):
            pop(c, wd, x, 606, fa, t, wt('c16', i), RED if wd == 'WATCHING' else BLACK, tracking=6, alpha=a_rows); x += text_w(wd + ' ', fa, 6)
    if ky > 0:
        # the eye: its iris is the feed
        z = 1 + 0.5 * in_out(lin(b, 82.5, 89.5))
        ew = 1500 * z; o = out_back(lin(t, ty, ty + 0.3), 1.2)
        Rr = ew * 0.17
        eye(c, W / 2, 450, ew, open_=o, color=WHITE, alpha=ky, pupil=BLACK, stroke=5, fill=BLACK)
        c.save()
        h = ew * 0.27 * max(0.02, o)
        p = skia.Path(); p.moveTo(W / 2 - ew / 2, 450); p.quadTo(W / 2, 450 - h * 2, W / 2 + ew / 2, 450); p.quadTo(W / 2, 450 + h * 2, W / 2 - ew / 2, 450); p.close()
        c.clipPath(p, True)
        footage(c, 1616.3 + (t - ty) * 0.12, W / 2 - Rr, 450 - Rr, 2 * Rr, 2 * Rr, key='syl', shape='circle', lo=BLACK, hi=DARK_HI, contrast=1.5, fx=0.42, fy=0.3, zoom=1.7, alpha=ky)
        circle(c, W / 2, 450, Rr, WHITE, ky, 4); circle(c, W / 2, 450, Rr * 1.12, RED, ky, 2)
        for i in range(48):
            a = math.radians(i * 7.5 + t * 10)
            line(c, W / 2 + math.sin(a) * Rr * 1.16, 450 - math.cos(a) * Rr * 1.16, W / 2 + math.sin(a) * Rr * 1.5, 450 - math.cos(a) * Rr * 1.5, WHITE, 1.5, 0.5 * ky)
        c.restore()
        a_txt = ky * (1 - lin(b, 88.3, 89.3))
        fy = font('serif', 190, 900)
        pop(c, 'YOU', W / 2, 965, fy, t, ty, RED, 'c', grow=0.5, alpha=a_txt, tracking=30)
        f = font('mono', 20)
        draw_text(c, '1.7 BILLION VIEWERS', 150, 930, f, WHITE, 'l', a_txt * 0.85, 4); draw_text(c, '220 COUNTRIES · 24 HOURS A DAY', W - 150, 930, f, WHITE, 'r', a_txt * 0.85, 4)
    sub(c, '所有人，都在看着你', t, t0, b2t(88.2), dark=True, y=1046, size=28)
    hud(c, t, n, dark=True)
    return dict(grain=11, chroma=3 + 12 * pulse(t, ty, 0.2), glitch=0.5 * pulse(t, ty, 0.25) + 0.25 * pulse(t, t0, 0.2), flash=0.4 * pulse(t, t0, 0.05), scan=0.3)

# ------------------------------------------------------------------ B2
ORB = [(3684.3, 'BIRTH', 205), (3687.6, 'FIRST STEP', 325), (3690.5, 'SCHOOL', 85)]
def s_b2p(c, t, n):
    """Who are you?"""
    t0 = b2t(89.5)
    c.clear(col(BLACK))
    footage(c, 5541.2 + (t - t0) * 0.8, 0, 0, W, H, key='tru', lo=BLACK, hi=DARK_HI, contrast=1.35, alpha=0.85, fy=0.2, zoom=1.06)
    rect(c, 0, 0, W, H, BLACK, 0.25)
    fi = font('serifi', 150); x = 1000
    for i, s in enumerate(('Who', 'are', 'you?')):
        pop(c, s, x, 620, fi, t, wt('c17', i), WHITE); x += text_w(s + ' ', fi)
    sub(c, '你是谁？', t, t0, b2t(90.95), dark=True)
    hud(c, t, n, dark=True)
    return dict(grain=11, chroma=2, scan=0.2, flash=0.3 * pulse(t, t0, 0.08))

def s_b2a(c, t, n):
    """I have been WATCHING you your whole life / when you were born / when you took your first step"""
    b = t2b(t); t0 = b2t(91)
    paper(c, t, 5)
    hits = [wt('c18', 3), wt('c19', 2), wt('c20', 2)]
    pu = sum(pulse(t, h, 0.16) for h in hits)
    cx, cy, R = 1380, 545, 440
    z = 1 + 0.04 * pu
    lit = {}
    for k_, h in enumerate(hits):
        p_ = pulse(t, h, 0.5)
        if p_ > 0.02:
            for j in range(24): lit[j] = max(lit.get(j, 0), p_ * (0.35 + 0.65 * rnd(j * 1.3 + k_)))
    c.save(); c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)
    blueprint(c, cx, cy, R, t * 9, INK, 1.0, cells=24, sweep=[(t * 150) % 360, (t * 150 + 120) % 360, (t * 150 + 240) % 360] if pu > 0.05 else [(t * 60) % 360], weight=1.3, lit=lit)
    # the tower: the creator's eye
    footage(c, 5558.0 + (t - t0) * 0.5, cx - 150, cy - 150, 300, 300, key='chr', shape='circle', contrast=1.3, gamma=0.6, fx=0.8, fy=0.35, zoom=1.35)
    circle(c, cx, cy, 150, INK, 1, 5); circle(c, cx, cy, 162, RED, min(1, pu), 3)
    # three cells of memory orbiting
    for i, (mt, lab, a0) in enumerate(ORB):
        hot = 0.0
        if i == 0: hot = lin(t, wt('c19', 6) - 0.05, wt('c19', 6) + 0.1) * (1 - lin(b, 99.8, 100.2))
        if i == 1: hot = lin(t, wt('c20', 7) - 0.05, wt('c20', 7) + 0.1)
        a = math.radians(a0 + t * 9); rr = R * 0.56
        x = cx + math.sin(a) * rr; y = cy - math.cos(a) * rr; r = 78 + 62 * out_back(hot)
        footage(c, mt + (t - t0) * 0.25, x - r, y - r, 2 * r, 2 * r, key=f'o{i}', shape='circle', contrast=1.3, fy=0.3, zoom=1.2)
        circle(c, x, y, r, RED if hot > 0 else INK, 1, 4 + 3 * hot)
        draw_text(c, lab, x, y + r + 24, font('monob', 16), INK, 'c', 0.9, 2)
    c.restore()
    # the chant, rebuilt for each phrase
    fi = font('serifi', 84); fw = font('serif', 178, 900); fe = font('serif', 132, 900)
    def phrase(cid, l1, iw, l3, l4, t_out):
        out = (t_out - 0.07, 0.07); x = 105
        for i, s in l1:
            pop(c, s, x, 250, fi, t, wt(cid, i), INK, out=out); x += text_w(s + ' ', fi)
        tw = wt(cid, iw)
        pop(c, 'WATCHING', 100, 440, fw, t, tw, RED, out=out, grow=0.4, tracking=-3)
        if t >= tw and t < t_out:
            eye(c, 100 + text_w('WATCHING', fw, -3) - 20, 275, 110, open_=out_back(lin(t, tw, tw + 0.2)), color=INK, alpha=1, pupil=RED, stroke=3)
        x = 105
        for i, s in l3:
            pop(c, s, x, 580, fi, t, wt(cid, i), INK, out=out); x += text_w(s + ' ', fi)
        x = 100
        for i, s in l4:
            pop(c, s, x, 760, fe, t, wt(cid, i), INK, out=out, grow=0.3); x += text_w(s + ' ', fe)
    if b < 96.4: phrase('c18', ((0, 'I'), (1, 'have'), (2, 'been')), 3, ((4, 'you'), (5, 'your')), ((6, 'whole'), (7, 'life.')), b2t(96.4))
    elif b < 99.95: phrase('c19', ((0, 'I'), (1, 'was')), 2, ((3, 'when'), (4, 'you'), (5, 'were')), ((6, 'born.'),), b2t(99.95))
    else: phrase('c20', ((0, 'I'), (1, 'was')), 2, ((3, 'when'), (4, 'you'), (5, 'took'), (6, 'your')), ((7, 'first'), (8, 'step.')), b2t(106.45))
    sub(c, '我一直在看着你，看了你一辈子', t, t0, b2t(96.3)); sub(c, '你出生的时候，我在看', t, b2t(96.5), b2t(99.9)); sub(c, '你迈出第一步的时候，我在看', t, b2t(100), b2t(106.3))
    hud(c, t, n, dark=False)
    return dict(grain=8, chroma=1 + 5 * pu, flash=0.75 * pulse(t, t0, 0.08))

CAMS = [(170, 190, False), (470, 150, False), (1450, 150, True), (1750, 190, True), (150, 800, False), (1770, 800, True), (800, 130, False), (1120, 130, True)]
def s_b2b(c, t, n):
    """You never had a camera — IN MY HEAD."""
    b = t2b(t); t0 = b2t(106.5); th = wt('c21', 7); th2 = wt('c22', 2)
    inv = t >= th
    if not inv:
        c.clear(col(BLACK))
        footage(c, 5596.9 + (t - t0) * 0.7, 0, 0, W, H, key='tru', lo=BLACK, hi=DARK_HI, contrast=1.4, alpha=0.7, zoom=1.05 + 0.04 * lin(b, 106.5, 111.5), fy=0.3)
        fa = font('anton', 250); x = 110
        for i, s in ((0, 'YOU'), (1, 'NEVER'), (2, 'HAD')):
            pop(c, s, x, 400, fa, t, wt('c21', i), WHITE, tracking=6); x += text_w(s + ' ', fa, 6)
        x = 110
        pop(c, 'A', x, 680, fa, t, wt('c21', 3), WHITE, tracking=6); x += text_w('A ', fa, 6)
        pop(c, 'CAMERA', x, 680, fa, t, wt('c21', 4), RED, tracking=6)
        k = lin(t, wt('c21', 4), wt('c21', 4) + 0.1)
        cctv(c, x + text_w('CAMERA', fa, 6) + 150, 610, 1.9, WHITE, k)
        fi = font('serifi', 150); x = 110
        pop(c, 'in', x, 900, fi, t, wt('c21', 5), WHITE); x += text_w('in ', fi)
        pop(c, 'my', x, 900, fi, t, wt('c21', 6), WHITE)
        sub(c, '可你从没能把摄像机装进——', t, t0, th - 0.05, dark=True, y=1040, size=30)
        hud(c, t, n, dark=True)
        return dict(grain=11, chroma=3 + 6 * pulse(t, t0 + 0.17, 0.15), scan=0.25, glitch=0.3 * lin(b, 110.6, 111.4))
    paper(c, t, 6)
    z = 1 + 0.06 * lin(t, th, b2t(119.5)) + 0.08 * pulse(t, th, 0.12) + 0.05 * pulse(t, th2, 0.12)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    blueprint(c, W / 2, H / 2, 620, -t * 5, INK, 0.22, cells=32, labels=False)
    # the cameras go dark one by one
    for i, (x, y, fl) in enumerate(CAMS):
        td = th + 0.25 + i * 0.42
        dead = t >= td
        cctv(c, x, y, 1.0, INK, 0.9 if not dead else 0.35, flip=fl, lens=RED if not dead else GREY)
        if dead:
            k = out_cubic(lin(t, td, td + 0.12)); s_ = 46
            line(c, x - s_, y - s_ - 10, x - s_ + 2 * s_ * k, y - s_ - 10 + 2 * s_ * k, RED, 7); line(c, x + s_, y - s_ - 10, x + s_ - 2 * s_ * k, y - s_ - 10 + 2 * s_ * k, RED, 7)
    fi = font('serifi', 130); fb = font('serif', 400, 900)
    draw_text(c, 'in my', W / 2, 400, fi, INK, 'c')
    e = out_expo(lin(t, th, th + 0.14))
    c.save(); c.translate(W / 2, 760); c.scale(1 + 0.5 * (1 - e), 1 + 0.5 * (1 - e))
    # echo of the second "in my head": outlines peel away
    k2 = out_cubic(lin(t, th2, th2 + 0.5))
    for j in (3, 2, 1):
        if k2 > 0: draw_text(c, 'HEAD.', j * 16 * k2, -j * 16 * k2, fb, RED, 'c', 0.9 * (1 - 0.2 * j), tracking=-6, stroke=3)
    draw_text(c, 'HEAD.', 0, 0, fb, INK, 'c', tracking=-6)
    c.restore()
    c.restore()
    nd = sum(1 for i in range(len(CAMS)) if t >= th + 0.25 + i * 0.42)
    sub(c, '——我的脑子里！', t, th, b2t(119.2), size=36)
    hud(c, t, n, dark=False, cam=max(0, 5000 - nd * 625), label='SIGNAL LOST' if nd >= len(CAMS) else 'THE TRUMAN SHOW')
    return dict(grain=8, flash=0.95 * pulse(t, th, 0.1) + 0.3 * pulse(t, th2, 0.08), chroma=10 * pulse(t, th, 0.15) + 5 * pulse(t, th2, 0.15),
                shake=(int(14 * pulse(t, th, 0.12) * (rnd(n) - 0.5) * 2), int(14 * pulse(t, th, 0.12) * (rnd(n + 5) - 0.5) * 2)))

TABLE = [(59.0, 70.0, s_b1a), (70.0, 74.5, s_b1b), (74.5, 78.5, s_b1c), (78.5, 89.5, s_b1d),
         (89.5, 91.0, s_b2p), (91.0, 106.5, s_b2a), (106.5, 119.5, s_b2b)]
