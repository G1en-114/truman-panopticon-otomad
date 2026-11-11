"""v2 scenes, part B (25.9 – 46.7 s): Sylvia's warning, the watcher, 'in my head'."""
import math, skia
from core import *
from kit import WC, SPK, wt, sub, hud, blueprint
from motion import *
import lib
from lib import sticker, seq
from v2_a import B, bg_img, DARK_HI

def wbeat(cid, i): return wt(cid, i)

# ====================================================================== B1: Sylvia
def s_truman(c, t, n):
    """TRUMAN!  — the shout as a constructivist poster"""
    t0, t1 = B(59), B(60.5)
    c.clear(col(RED))
    sh = 16 * pulse(t, t0, 0.3)
    c.save(); c.translate((rnd(n) - 0.5) * sh, (rnd(n + 3) - 0.5) * sh)
    p = skia.Path(); p.moveTo(-50, H + 50); p.lineTo(W * 0.55, -50); p.lineTo(W + 50, -50); p.lineTo(W + 50, H + 50); p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(BLACK)))
    circle(c, 1430, 380, 260 * out_back(lin(t, t0, t0 + 0.3)), PAPER)
    seq(c, 's_sylvia', t, 1430, 420, fps=12, h=560, style='bw', alpha=lin(t, t0, t0 + 0.05))
    for i in range(14):
        a = math.radians(-160 + i * 9)
        k = out_expo(lin(t, t0 + i * 0.01, t0 + 0.25 + i * 0.01))
        line(c, 560 + math.cos(a) * 200, 520 + math.sin(a) * 200, 560 + math.cos(a) * (200 + 900 * k), 520 + math.sin(a) * (200 + 900 * k), PAPER, 10, 0.9)
    sticker(c, 'g_megaphone', 330, 640, h=760 * out_back(lin(t, t0, t0 + 0.25), 1.2) + 1, style='bw', rot=-12, flip=True)
    c.save(); c.translate(150, 980); c.rotate(-32)
    ktext(c, t, ('TRUMAN!', font('anton', 380), PAPER), 0, 0, t0, 'slam', stagger=0.03, tracking=12, trail=2, add=('slice',))
    c.restore()
    c.restore()
    sub(c, '楚门！', t, t0, t1, dark=True)
    hud(c, t, n, dark=True)
    return dict(grain=10, chroma=4 + 10 * pulse(t, t0, 0.2), flash=0.6 * pulse(t, t0, 0.06), zblur=0.15 * pulse(t, t0, 0.1), tvon=lin(t, t0 - 0.02, t0 + 0.12))

def s_listen(c, t, n):
    """Listen to me — each word a 90° snap"""
    ws = WC['c13']; t1 = B(63)
    k = sum(1 for w in ws if t >= w['t']) - 1
    tw = ws[max(0, k)]['t']
    rot = [0, -90, -180][max(0, k)] + 90 * (1 - out_expo(lin(t, tw, tw + 0.22)))
    c.clear(col(PAPER)); paper(c, t, 4)
    c.save(); c.translate(W / 2, H / 2); c.rotate(rot); c.translate(-W / 2, -H / 2)
    rect(c, -400, H / 2 - 170, W + 800, 340, BLACK)
    rect(c, W / 2 - 170, -400, 340, H + 800, RED)
    ktext(c, t, ('LISTEN', font('anton', 300), PAPER), W / 2 - 700, H / 2 + 110, ws[0]['t'], 'split', stagger=0.03, tracking=10, dur=0.3)
    c.save(); c.translate(W / 2, H / 2); c.rotate(90)
    ktext(c, t, ('TO', font('anton', 300), PAPER), -400, 110, ws[1]['t'], 'stack', 'c', stagger=0.03, tracking=10, dur=0.3)
    c.restore()
    c.save(); c.translate(W / 2, H / 2); c.rotate(180)
    ktext(c, t, ('ME.', font('anton', 300), INK), 380, 110, ws[2]['t'], 'slam', 'c', stagger=0.02, tracking=10, add=('slice',))
    c.restore()
    c.restore()
    footage(c, 1589.6 + (t - B(60.5)) * 0.9, W / 2 - 170, H / 2 - 170, 340, 340, key='syl', shape='circle', lo=BLACK, hi=(235, 60, 40), contrast=1.6, zoom=1.4, fy=0.35)
    circle(c, W / 2, H / 2, 170, PAPER, 1, 8)
    sub(c, '听我说！', t, ws[0]['t'], t1 - 0.05)
    hud(c, t, n)
    return dict(grain=9, chroma=6 * pulse(t, tw, 0.12), zblur=0.25 * pulse(t, tw, 0.12), flash=0.3 * pulse(t, tw, 0.05))

def s_knows(c, t, n):
    """Everybody knows everything you do — a floor of text, a wall of eyes"""
    t0, t1 = B(63), B(70)
    c.clear(col(BLACK))
    ws = WC['c14']
    # perspective floor of repeated lines rushing towards us
    c.save(); persp(c, W / 2, H * 0.62, rx=64, z=0, f=900)
    f = font('anton', 120); s = 'EVERYBODY KNOWS EVERYTHING YOU DO  ·  '
    sw = text_w(s, f, 4)
    for r in range(-12, 8):
        y = r * 150 + ((t - t0) * 520) % 150
        off = ((t - t0) * (160 if r % 2 else -160)) % sw
        x = -off - sw * 2
        while x < sw * 2:
            draw_text(c, s, x, y, f, RED if r % 4 == 0 else WHITE, 'l', 0.55, 4); x += sw
    c.restore()
    rect(c, 0, 0, W, H * 0.42, BLACK, 0.75)
    # eyes opening on the wall above
    for i in range(16):
        to = t0 + 0.1 + rnd(i * 2.3) * 2.0
        kk = out_back(lin(t, to, to + 0.2))
        if kk > 0:
            x = 80 + (i % 8) * 250 + (i // 8) * 125; y = 90 + (i // 8) * 150
            sticker(c, 'g_eye', x, y, w=230, style='ht_white', sx=1, alpha=0.8 * kk, rot=(rnd(i) - 0.5) * 10)
            c.save(); c.translate(x, y); c.scale(1, kk); c.restore()
    # truman, small, centre, in the crosshair
    sticker(c, 'truman_dark', W / 2, H * 0.78, h=380, style='ht_white', border=6)
    line(c, W / 2 - 300, H * 0.68, W / 2 + 300, H * 0.68, RED, 2, 0.8); line(c, W / 2, H * 0.68 - 300, W / 2, H * 0.68 + 300, RED, 2, 0.8)
    arc(c, W / 2, H * 0.68, 220 + 10 * math.sin(t * 6), 0, 360, RED, 3, 0.9, dash=(18, 10))
    # the words slam on top
    kpos = [(W / 2, 520, 'anton', 260, WHITE), (W / 2, 520, 'anton', 260, RED), (W / 2, 520, 'bodoni', 230, WHITE), (W / 2, 520, 'serifi', 300, WHITE), (W / 2, 520, 'anton', 360, RED)]
    cur = max(0, sum(1 for w in ws if t >= w['t']) - 1)
    if t >= ws[0]['t']:
        if cur <= 1:
            ktext(c, t, ('EVERYBODY', font('anton', 260), WHITE), W / 2, 470, ws[0]['t'], 'zoom', 'c', stagger=0.02, tracking=8, out=ws[2]['t'] - 0.04, out_style='zoom', out_dur=0.12)
            ktext(c, t, ('KNOWS', font('anton', 200), RED), W / 2, 680, ws[1]['t'], 'split', 'c', stagger=0.03, tracking=8, out=ws[2]['t'] - 0.04, out_style='zoom', out_dur=0.12)
        elif cur == 2:
            ktext(c, t, ('EVERYTHING', font('bodoni', 250), WHITE), W / 2, 520, ws[2]['t'], 'fly', 'c', stagger=0.025, trail=4, seed=7, add=('slice',))
        else:
            ktext(c, t, ('you', font('serifi', 300), WHITE), W / 2 - 60, 560, ws[3]['t'], 'orbit', 'r', dur=0.3)
            ktext(c, t, ('DO.', font('anton', 360), RED), W / 2 + 10, 560, ws[4]['t'], 'stack', stagger=0.03, tracking=8, dur=0.3)
    sub(c, '所有人都知道你的一举一动', t, t0, t1 - 0.05, dark=True)
    hud(c, t, n, dark=True)
    hit = max([w['t'] for w in ws if t >= w['t']] + [-9])
    return dict(grain=11, chroma=3 + 7 * pulse(t, hit, 0.15), zblur=0.2 * pulse(t, hit, 0.1), scan=0.3, glitch=0.25 * pulse(t, hit, 0.2))

CAST = [('meryl_smile', 'WIFE', 'raw'), ('marlon', 'BEST FRIEND', 'raw'), ('v_host', 'NEIGHBOUR', 'raw'), ('meryl_arms', 'NURSE', 'raw')]
def s_pretend(c, t, n):
    """They're PRETENDING, Truman — the cast as cut-outs, a ransom note"""
    t0, t1 = B(70), B(74.5)
    paper(c, t, 6)
    cam = Cam([(t0, (W / 2, H / 2, 1.2, 5), 'lin'), (t0 + 0.3, (W / 2, H / 2, 1.0, 0), 'oq'), (t1, (W / 2, H / 2, 1.06, -2), 'lin')], shake=5)
    c.save(); cam.apply(c, t)
    c.save(); c.translate(W / 2, H / 2); c.rotate(-18); rect(c, -1400, -120, 2800, 240, RED); c.restore()
    for i, (nm, lab, sty) in enumerate(CAST):
        ti = t0 + i * 0.09
        k = out_back(lin(t, ti, ti + 0.3), 1.4)
        if k <= 0: continue
        x = 260 + i * 470; y = 470 + (60 if i % 2 else -40)
        sticker(c, nm, x, y, h=620 * k, style='ht' if i % 2 else 'bw', border=10, shadow=12, rot=(rnd(i * 5) - 0.5) * 14)
        kx = lin(t, ti + 0.3, ti + 0.45)
        if kx > 0:
            c.save(); c.translate(x, y - 150); c.rotate((rnd(i * 5) - 0.5) * 14); rect(c, -150, -24, 300 * out_cubic(kx), 48, BLACK); c.restore()
        label(c, f'ACTOR №{i + 1:02d} — {lab}', x, y + 360, 22, INK, k, 'c', 3, bold=True)
    c.restore()
    ktext(c, t, ("They're", font('serifi', 130), INK), 120, 230, wt('c15', 0), 'rise')
    ransom(c, t, 'PRETENDING', W / 2, 930, 190, wt('c15', 1), stagger=0.03, seed=11, anchor='c')
    ktext(c, t, ('Truman.', font('serifi', 130), RED), W - 120, 230, wt('c15', 2), 'rise', 'r')
    sub(c, '他们全都在演戏，楚门', t, t0, t1 - 0.05, y=1060, size=28)
    hud(c, t, n)
    return dict(grain=8, chroma=2 + 6 * pulse(t, wt('c15', 1), 0.15), flash=0.3 * pulse(t, t0, 0.06))

def s_set(c, t, n):
    """It's a SET. It's a SHOW. — the flat falls over, backstage is a stage"""
    ws = WC['c16']; t0, t1 = B(74.5), B(78.5); tsh = ws[3]['t']
    c.clear(col(BLACK))
    kf = in_cubic(lin(t, tsh - 0.12, tsh + 0.1))          # the flat falls backwards
    # backstage / the show
    if kf > 0.3:
        for i in range(5):
            a = math.radians(-30 + i * 15 + 6 * math.sin(t * 2 + i))
            p = skia.Path(); p.moveTo(W / 2 + (i - 2) * 300, -40); p.lineTo(W / 2 + (i - 2) * 300 + math.sin(a) * 1400 - 260, H + 40); p.lineTo(W / 2 + (i - 2) * 300 + math.sin(a) * 1400 + 260, H + 40); p.close()
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(WHITE, 0.08)))
        for i in range(3):
            sticker(c, 'g_sirius', 360 + i * 600, 40, h=300, style='ht_white', rot=180 + (i - 1) * 25, ay=0.2)
        for i, s_ in enumerate(("IT'S", 'A', 'SHOW!')):
            tw_ = ws[3 + i]['t']
            ktext(c, t, (s_, font('anton', 330 if i < 2 else 420), RED if i == 2 else WHITE), [260, 760, 1000][i], 720, tw_, 'stack' if i == 2 else 'split', stagger=0.03, tracking=8, dur=0.3)
        rect(c, 0, 830, W, 18, RED)
        label(c, 'ON AIR 24 / 7  ·  NO COMMERCIAL BREAKS  ·  EVERYTHING IS FOR SALE', W / 2, 900, 26, WHITE, 0.9, 'c', 5, bold=True)
    if kf < 1:
        c.save(); persp(c, W / 2, H, rx=-82 * kf, f=1500); c.translate(-W / 2, -H)
        bg_img(c, 'gen:skywall', t, zoom=1.2, style='tint')
        rect(c, 0, 0, W, H, WHITE, 8, stroke=16)
        for i, s_ in enumerate(("IT'S", 'A', 'SET.')):
            ktext(c, t, (s_, font('anton', 360 if i < 2 else 440), INK if i < 2 else RED), [230, 780, 1030][i], 680, ws[i]['t'], 'drop', stagger=0.03, tracking=8, shadow=(10, 10, WHITE, 1))
        label(c, 'STAGE 12  ·  SKY: PAINTED  ·  SEA: 1:1 TANK  ·  SUN: 5K LAMP', W / 2, 820, 26, INK, 0.9, 'c', 5, bold=True)
        # struts on the back of the flat
        c.restore()
    sub(c, '这是布景——这是一场秀！', t, t0, t1 - 0.05, dark=kf > 0.5)
    hud(c, t, n, dark=kf > 0.5)
    return dict(grain=9, chroma=3 + 9 * pulse(t, ws[2]['t'], 0.12) + 9 * pulse(t, ws[5]['t'], 0.12), flash=0.5 * pulse(t, tsh + 0.1, 0.06),
                shake=(int(14 * pulse(t, tsh + 0.1, 0.12) * (rnd(n) - 0.5) * 2), int(14 * pulse(t, tsh + 0.1, 0.12) * (rnd(n + 3) - 0.5) * 2)))

def s_watching(c, t, n):
    """Everybody's watching YOU — rows of camera-headed viewers rush at us; one camera turns"""
    ws = WC['c16']; t0, t1 = B(78.5), B(89.5); ty = ws[8]['t']
    c.clear(col(BLACK)); paper(c, t, 3, dark=True)
    # audience rows on a z-axis tunnel
    for r in range(7, -1, -1):
        zr = (r - (t - t0) * 1.3) % 8.0          # depth 0 (at camera) .. 8 (far)
        s = 1.6 / (0.25 + zr * 0.55)
        a = c01((8 - zr) / 2) * c01(zr / 0.6)
        if a <= 0: continue
        sticker(c, 'g_audience', W / 2 + (r % 2 - 0.5) * 220 * s, H * 0.58 + 220 * s, w=1700 * s, style='ht_white' if r % 2 else 'bw', alpha=a * 0.9, ay=0.6)
    rect(c, 0, 0, W, H, BLACK, 0.25)
    kc = lin(t, ty - 1.0, ty)
    seq(c, 'b_cctv', t, W / 2, H / 2 - 20, fps=24, loop=False, t0=ty - 1.2, h=900 + 300 * in_out(lin(t, ty, t1)), style='bw', alpha=lin(t, ty - 1.25, ty - 1.1))
    # the line
    if t < ty:
        ktext(c, t, ("EVERYBODY'S", font('anton', 230), WHITE), W / 2, 300, ws[6]['t'], 'fly', 'c', stagger=0.025, tracking=8, trail=4)
        ktext(c, t, ('WATCHING', font('bodoni', 250), RED), W / 2, 980, ws[7]['t'], 'zoom', 'c', stagger=0.025, trail=3, add=('slice',))
    else:
        ke = out_back(lin(t, ty, ty + 0.25))
        ktext(c, t, ('YOU.', font('anton', 520), RED), W / 2, 760, ty, 'split', 'c', stagger=0.04, tracking=20, out=t1 - 0.5, out_style='zoom', out_dur=0.4, dur=0.35)
        corners(c, W / 2 - 560, 330, 1120, 500, lin(t, ty + 0.2, ty + 0.5), WHITE, 90, 7)
        label(c, '1.7 BILLION VIEWERS  ·  220 COUNTRIES  ·  24 HOURS A DAY', W / 2, 960, 26, WHITE, 0.85 * (1 - lin(t, t1 - 0.6, t1 - 0.3)), 'c', 5, bold=True)
    sub(c, '所有人，都在看着你', t, t0, t1 - 0.5, dark=True, y=1060, size=28)
    hud(c, t, n, dark=True)
    ki = in_cubic(lin(t, t1 - 0.45, t1 - 0.02))
    iris(c, ki, W / 2, H / 2 - 20, blades=7, rot=10)
    return dict(grain=11, scan=0.3, chroma=3 + 12 * pulse(t, ty, 0.2), glitch=0.4 * pulse(t, ty, 0.25), flash=0.5 * pulse(t, ty, 0.06), zblur=0.12 * pulse(t, ty, 0.1))

# ====================================================================== B2: the watcher
def s_who(c, t, n):
    """Who are you?"""
    t0 = B(89.5)
    c.clear(col(BLACK))
    ki = 1 - out_expo(lin(t, t0, t0 + 0.3))
    footage(c, 5541.2 + (t - t0) * 0.8, 0, 0, W, H, key='tru', lo=BLACK, hi=DARK_HI, contrast=1.35, alpha=0.7, fy=0.2, zoom=1.15 - 0.05 * lin(t, t0, t0 + 0.5))
    ktext(c, t, ('Who are you?', font('serifi', 170), WHITE), 1000, 620, 0, 'rise', times=words_times([('Who', wt('c17', 0)), ('are', wt('c17', 1)), ('you?', wt('c17', 2))]))
    iris(c, ki, W / 2, H / 2, blades=7, rot=60)
    sub(c, '你是谁？', t, t0, B(91) - 0.05, dark=True)
    hud(c, t, n, dark=True)
    return dict(grain=11, chroma=2, scan=0.2)

ORB = [(3686.0, 'BIRTH', 205), (3687.6, 'FIRST STEP', 325), (3690.5, 'SCHOOL', 85)]
def s_watch(c, t, n):
    """I have been WATCHING you your whole life / when you were born / when you took your first step"""
    b = t2b(t); t0, t1 = B(91), B(106.5)
    hits = [wt('c18', 3), wt('c19', 2), wt('c20', 2)]
    pu = sum(pulse(t, h, 0.18) for h in hits)
    tb, tf = wt('c19', 6), wt('c20', 7)
    paper(c, t, 5)
    cam = Cam([(t0, (0, 0, 1.8, -30), 'lin'), (t0 + 0.4, (0, 0, 0.72, 0), 'oq'), (tb - 0.15, (0, 0, 0.75, 8), 'lin'), (tb + 0.15, (0, 0, 0.8, 18), 'whip'),
               (tf - 0.15, (0, 0, 0.82, 22), 'lin'), (tf + 0.15, (0, 0, 0.86, 34), 'whip'), (t1 - 0.25, (0, 0, 0.9, 38), 'lin'), (t1, (0, 0, 4.5, 80), 'ix')], shake=4)
    c.save(); cam.apply(c, t)
    z = 1 + 0.05 * pu
    c.scale(z, z)
    lit = {}
    for k_, h in enumerate(hits):
        p_ = pulse(t, h, 0.5)
        if p_ > 0.02:
            for j in range(24): lit[j] = max(lit.get(j, 0), p_ * (0.35 + 0.65 * rnd(j * 1.3 + k_)))
    blueprint(c, 0, 0, 640, t * 9, INK, 1.0, cells=24, sweep=[(t * 150) % 360, (t * 150 + 120) % 360, (t * 150 + 240) % 360], weight=2.0, lit=lit)
    sticker(c, 'christof_head', 0, 30, h=460, style='bw', border=8, shadow=10)
    circle(c, 0, 0, 250, RED, min(1, pu), 6)
    for i, (mt, lab, a0) in enumerate(ORB):
        hot = 0.0
        if i == 0: hot = lin(t, tb - 0.05, tb + 0.1) * (1 - lin(t, B(99.8), B(100.2)))
        if i == 1: hot = lin(t, tf - 0.05, tf + 0.1)
        a = math.radians(a0 + t * 12); rr = 470
        x = math.sin(a) * rr; y = -math.cos(a) * rr; r = 110 + 90 * out_back(hot)
        footage(c, mt + (t - t0) * 0.25, x - r, y - r, 2 * r, 2 * r, key=f'o{i}', shape='circle', contrast=1.3, fy=0.3, zoom=1.2, lo=INK, hi=PAPER)
        circle(c, x, y, r, RED if hot > 0 else INK, 1, 6 + 4 * hot)
        draw_text(c, lab, x, y + r + 40, font('monob', 30), INK, 'c', 0.9, 4)
    # the words orbit on the rings
    ring = -t * 14
    arc_text(c, t, 'I  have  been', 0, 0, 760, ring, font('serifi', 90), INK, t0=wt('c18', 0), t1=wt('c18', 2) + 0.1)
    arc_text(c, t, 'you  your  whole  life', 0, 0, 760, ring + 180, font('serifi', 90), INK, t0=wt('c18', 4), t1=wt('c18', 7) + 0.1)
    if t >= wt('c19', 0):
        arc_text(c, t, 'I  was  watching  when  you  were', 0, 0, 900, -ring * 0.8 + 90, font('bodoni', 90), INK, t0=wt('c19', 0), t1=wt('c19', 5) + 0.1)
    if t >= wt('c20', 0):
        arc_text(c, t, 'I  was  watching  when  you  took  your', 0, 0, 1040, ring * 0.7 - 90, font('bodoni', 90), RED, t0=wt('c20', 0), t1=wt('c20', 6) + 0.1)
    c.restore()
    # WATCHING x3 : screen-space stamps
    for k_, h in enumerate(hits):
        out = hits[k_ + 1] - 0.06 if k_ < 2 else t1 - 0.3
        if h <= t < out + 0.3:
            ktext(c, t, ('WATCHING', font('anton', 300), RED), W / 2, 590, h, ['zoom', 'split', 'stack'][k_], 'c', stagger=0.025, tracking=14, out=h + 0.55, out_style='zoom', out_dur=0.25, trail=2, dur=0.3)
            sticker(c, 'g_eye', W / 2, 420, w=700 * out_back(lin(t, h, h + 0.2)) + 1, style='bw', alpha=1 - lin(t, h + 0.5, h + 0.75))
    if t >= tb:
        k = out_back(lin(t, tb, tb + 0.3))
        ktext(c, t, ('born.', font('serifi', 240), INK), 200, 980, tb, 'drop', stagger=0.04, out=wt('c20', 0) - 0.1, out_style='fall')
    if t >= tf:
        ktext(c, t, ('first step.', font('serifi', 220), RED), W - 120, 980, tf, 'drop', 'r', stagger=0.03)
    sub(c, '我一直在看着你，看了你一辈子', t, t0, B(96.4)); sub(c, '你出生的时候，我在看', t, B(96.5), B(99.95)); sub(c, '你迈出第一步的时候，我在看', t, B(100), t1 - 0.1)
    hud(c, t, n)
    return dict(grain=8, chroma=1 + 5 * pu, flash=0.6 * pulse(t, t0, 0.08), zblur=0.25 * pu + 0.5 * in_cubic(lin(t, t1 - 0.25, t1)))

def s_head(c, t, n):
    """You never had a camera — IN MY HEAD."""
    t0, t1 = B(106.5), B(119.5)
    th, th2 = wt('c21', 7), wt('c22', 2)
    ws = WC['c21']
    inv = t >= th
    if not inv:
        c.clear(col(BLACK))
        sticker(c, 'truman_dark', 1420, 600, h=900, style='ht_white', alpha=0.85, rot=-3 + 2 * math.sin(t))
        ktext(c, t, ('YOU NEVER HAD', font('anton', 200), WHITE), 110, 330, 0, 'flip', times=words_times([('YOU', ws[0]['t']), ('NEVER', ws[1]['t']), ('HAD', ws[2]['t'])]), tracking=6)
        ktext(c, t, ('A', font('anton', 200), WHITE), 110, 570, ws[3]['t'], 'slam')
        ktext(c, t, ('CAMERA', font('anton', 300), RED), 250, 600, ws[4]['t'], 'slam', stagger=0.025, tracking=10, add=('slice',))
        for k in range(6):
            kk = out_back(lin(t, ws[4]['t'] + k * 0.05, ws[4]['t'] + k * 0.05 + 0.3))
            if kk > 0: sticker(c, f'cam_{(k * 2) % 9 + 1}', 180 + k * 190, 750 + (k % 2) * 60, h=150 * kk, style='ht_white', rot=(rnd(k) - 0.5) * 30)
        ktext(c, t, ('in my', font('serifi', 170), WHITE), 120, 990, 0, 'rise', times=words_times([('in', ws[5]['t']), ('my', ws[6]['t'])]))
        sub(c, '可你从没能把摄像机装进——', t, t0, th - 0.05, dark=True, y=1060, size=28)
        hud(c, t, n, dark=True)
        return dict(grain=11, chroma=3 + 6 * pulse(t, ws[4]['t'], 0.15), scan=0.25, slice_=0.6 * lin(t, th - 0.25, th))
    paper(c, t, 6)
    z = 1 + 0.08 * lin(t, th, t1) + 0.1 * pulse(t, th, 0.12) + 0.05 * pulse(t, th2, 0.12)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.rotate(-3 + 4 * lin(t, th, t1)); c.translate(-W / 2, -H / 2)
    circle(c, W / 2 + 80, H / 2, 470, RED)
    sticker(c, 'g_head', W / 2 + 80, H / 2 + 10, h=900, style='raw', border=12, shadow=14)
    # the camera inside the head is crossed out
    xmark(c, W / 2 - 60, H / 2 - 120, 150, lin(t, th + 0.25, th + 0.5), BLACK, 26)
    for k in range(3):
        rr = out_cubic(lin(t, th2 + k * 0.08, th2 + k * 0.08 + 0.5))
        if rr > 0: circle(c, W / 2 + 80, H / 2, 470 + 120 * rr + k * 30, INK, 1 - rr, 4)
    ktext(c, t, ('IN MY', font('anton', 220), INK), 130, 380, th - 0.15, 'split', stagger=0.03, tracking=8, dur=0.25)
    ktext(c, t, ('HEAD.', font('bodoni', 360), INK), 100, 720, th, 'stack', stagger=0.035, tracking=-4, dur=0.35)
    if t >= th2:
        for j in (3, 2, 1):
            k2 = out_cubic(lin(t, th2, th2 + 0.5))
            draw_text(c, 'HEAD.', 100 + j * 18 * k2, 720 - j * 18 * k2, font('bodoni', 360), RED, 'l', 0.8 * (1 - 0.2 * j), -4, stroke=3)
    label(c, 'SIGNAL LOST — NO FEED AVAILABLE', 130, 830, 28, RED, lin(t, th + 0.4, th + 0.6), 'l', 5, bold=True)
    c.restore()
    sub(c, '——我的脑子里！', t, th, t1 - 0.4, size=36)
    hud(c, t, n, cam=0, label='SIGNAL LOST')
    ks = lin(t, t1 - 0.4, t1 + 0.0)
    slabs(c, ks * 1.0, ang=-30, n=6, colors=[BLACK, RED, BLACK])
    return dict(grain=8, flash=0.9 * pulse(t, th, 0.1) + 0.3 * pulse(t, th2, 0.08), chroma=10 * pulse(t, th, 0.15) + 5 * pulse(t, th2, 0.15),
                zblur=0.3 * pulse(t, th, 0.12), shake=(int(14 * pulse(t, th, 0.12) * (rnd(n) - 0.5) * 2), int(14 * pulse(t, th, 0.12) * (rnd(n + 5) - 0.5) * 2)))

TABLE = [(B(59), B(60.5), s_truman), (B(60.5), B(63), s_listen), (B(63), B(70), s_knows), (B(70), B(74.5), s_pretend), (B(74.5), B(78.5), s_set),
         (B(78.5), B(89.5), s_watching), (B(89.5), B(91), s_who), (B(91), B(106.5), s_watch), (B(106.5), B(119.5), s_head)]
