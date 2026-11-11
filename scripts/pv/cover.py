"""PV cover / thumbnail -> out/cover.png (1920x1080) and out/cover_4x3.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2, skia
from core import *
from motion import *
from lib import sticker
import kit

S = skia.Surface(W, H); c = S.getCanvas()
T = 100.0                     # far after every entry: all glyphs settled
STILL = ()                    # no glyph decorations on the cover

c.clear(col(PAPER)); paper(c, 3.0, 3)
# constructivist ground
c.save(); c.translate(W / 2, H / 2); c.rotate(-10); sticker(c, 'gen:constr', 0, 0, h=1700, style='raw', alpha=0.55); c.restore()
# the watcher: Christof, enormous and faint, top right
sticker(c, 'christof_close', 1460, 330, h=980, style='ht', alpha=0.55, rot=4)
# red sun / lens behind Truman
circle(c, 760, 560, 430, RED)
ticks_ring(c, 760, 560, 450, 120, INK, 0.9, 0, 5, 18, 3)
arc(c, 760, 560, 520, 0, 360, INK, 2, 0.7, dash=(10, 8))
# Truman, in colour, the only colour in the frame
sticker(c, 'truman_gn', 760, 600, h=760, style='tint', border=14, shadow=18, rot=-3)
# censor bar over the eyes would hide him; instead a crosshair
line(c, 760 - 520, 470, 760 + 520, 470, RED, 3, 0.9); line(c, 760, 40, 760, 1040, RED, 3, 0.9)
corners(c, 420, 210, 680, 700, 1, WHITE, 80, 8)
# the town under glass, cameras around
sticker(c, 'g_globe', 1500, 760, h=520, style='tint', border=10, shadow=14, rot=6)
for k, (x, y, h, r) in enumerate([(240, 200, 170, -20), (1180, 150, 150, 18), (210, 880, 160, 12), (1250, 960, 140, -14), (1780, 420, 150, 25), (1080, 560, 120, -8)]):
    sticker(c, f'cam_{[1, 3, 9, 2, 7, 4][k]}', x, y, h=h, style='bw', rot=r, border=6, shadow=8)
sticker(c, 'g_eye', 1660, 140, w=380, style='bw', rot=-6, border=6, shadow=8)
# ---- title block
c.save(); c.translate(70, 1000); c.rotate(-8)
rect(c, -40, -150, 1180, 190, BLACK)
ktext(c, T, ('THE TRUMAN SHOW', font('anton', 150), PAPER), 0, 10, 0, 'slam', tracking=10, fx=STILL)
c.restore()
ransom(c, T, 'PANOPTICON', 1330, 615, 112, 0, seed=23, anchor='c')
ktext(c, T, ('パノプティコン', font('jpb', 118), INK), 1330, 455, 0, 'slam', 'c', tracking=2, fx=STILL, shadow=(7, 7, WHITE, 1))
rect(c, 1010, 650, 640, 70, RED)
ktext(c, T, ('楚门的世界 × 圆形监狱', font('cnb', 46), PAPER), 1330, 702, 0, 'slam', 'c', tracking=6, fx=STILL)
# HUD + small print
kit.hud(c, 3.0, 90, dark=False, cam=1, label='THE TRUMAN SHOW — LIVE')
label(c, 'r-906 / PANOPTICON  ·  THE TRUMAN SHOW (1998)  ·  TEXT PV', W - 70, 1040, 20, INK, 0.9, 'r', 3, bold=True)
arr = S.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
im = post(arr, 7, grain=6, vig=0.8, chroma=1.5)
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
cv2.imwrite(os.path.join(ROOT, 'out', 'cover.png'), im[:, :, ::-1])
x0 = (W - H * 4 // 3) // 2 + 120
cv2.imwrite(os.path.join(ROOT, 'out', 'cover_4x3.png'), im[:, x0:x0 + H * 4 // 3, ::-1])
print('ok')
