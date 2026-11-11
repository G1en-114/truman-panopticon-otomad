"""Frame renderer.  usage:
   render.py stills 2.0 4.6 ...        -> work/pv/still_XXXX.jpg (+ a contact sheet)
   render.py video [t0 t1] [--half]    -> out/pv_preview.mp4 / out/final
"""
import sys, os, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2, skia
from core import *
import kit, scenes_a
try:
    import scenes_b
except ImportError: scenes_b = None
try:
    import scenes_c
except ImportError: scenes_c = None

def table():
    T = [(-16, 1.4, scenes_a.s_intro), (1.4, 3.0, scenes_a.s_pickup), (3.0, 19.0, scenes_a.s_a1a)]
    for mod in (scenes_a, scenes_b, scenes_c):
        if mod is not None and hasattr(mod, 'TABLE'): T += mod.TABLE
    return sorted(T, key=lambda x: x[0])
TABLE = table()
surface = skia.Surface(W, H)

def frame(n):
    t = n / FPS; b = t2b(t)
    c = surface.getCanvas(); c.restoreToCount(1); c.resetMatrix()
    fn = None
    for b0, b1, f in TABLE:
        if b0 <= b < b1: fn = f
    if fn is None:
        c.clear(col(BLACK)); params = {}
    else:
        c.save(); params = fn(c, t, n) or {}; c.restoreToCount(1)
    arr = surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return post(arr, n, **params)

if __name__ == '__main__':
    mode = sys.argv[1]
    os.makedirs(os.path.join(ROOT, 'work', 'pv'), exist_ok=True)
    if mode == 'stills':
        ims = []
        for a in sys.argv[2:]:
            t = float(a[1:]) and b2t(float(a[1:])) if a.startswith('b') else float(a)
            im = frame(int(round(t * FPS)))
            p = os.path.join(ROOT, 'work', 'pv', f'still_{t:07.2f}.jpg')
            cv2.imwrite(p, im[:, :, ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90]); ims.append(cv2.resize(im[:, :, ::-1], (960, 540), interpolation=cv2.INTER_AREA))
        cols = 2 if len(ims) > 1 else 1
        rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]
        cv2.imwrite(os.path.join(ROOT, 'work', 'pv', 'sheet.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 82])
    else:
        args = [a for a in sys.argv[2:] if not a.startswith('--')]
        t0 = float(args[0]) if args else 0.0; t1 = float(args[1]) if len(args) > 1 else kit.TOTAL
        half = '--half' in sys.argv
        out = os.path.join(ROOT, 'out', 'pv_preview.mp4' if (half or args) else 'pv_silent.mp4')
        size = f'{W // 2}x{H // 2}' if half else f'{W}x{H}'
        cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', size, '-r', str(FPS), '-i', '-',
               '-c:v', 'h264_nvenc', '-preset', 'p6', '-rc', 'vbr', '-cq', '17' if not half else '24', '-b:v', '0', '-pix_fmt', 'yuv420p', out]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n0, n1 = int(t0 * FPS), int(t1 * FPS); st = time.time()
        for n in range(n0, n1):
            im = frame(n)
            if half: im = cv2.resize(im, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
            ff.stdin.write(np.ascontiguousarray(im).tobytes())
            if (n - n0) % 150 == 0: print(f'{n - n0}/{n1 - n0}  {(n - n0) / max(1e-6, time.time() - st):.1f} fps', flush=True)
        ff.stdin.close(); ff.wait(); print('done', out, f'{time.time() - st:.0f}s')
