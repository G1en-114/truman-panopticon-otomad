"""v2 renderer (kinetic collage).  usage:
   render2.py stills 2.0 4.6 ...          -> work/pv2/still_XXXX.jpg + sheet.jpg
   render2.py video [t0 t1] [--half]      -> out/pv2_preview.mp4 (or out/pv2_silent.mp4 for the full 1080p pass)
"""
import sys, os, subprocess, time, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2, skia
from core import *
import motion, kit

MODS = ['v2_a', 'v2_b', 'v2_c']
def table():
    T = []
    for m in MODS:
        try: mod = importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name == m: continue
            raise
        T += mod.TABLE
    return sorted(T, key=lambda x: x[0])
TABLE = table()
surface = skia.Surface(W, H)
SHUTTER = 0.9            # fraction of a frame the virtual shutter stays open

def draw(t, n):
    c = surface.getCanvas(); c.restoreToCount(1); c.resetMatrix()
    fn = None
    for t0, t1, f in TABLE:
        if t0 <= t < t1: fn = f
    if fn is None: c.clear(col(BLACK)); params = {}
    else:
        c.save(); params = fn(c, t, n) or {}; c.restoreToCount(1)
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), params

def frame(n, mb=True):
    t = n / FPS
    motion.SPEED[0] = 0.0
    arr, params = draw(t, n)
    sp = motion.SPEED[0]
    N = params.get('mb', int(min(12, 1 + sp / 9)))
    if mb and N > 1:
        acc = arr.astype(np.float32)
        for k in range(1, N):
            dt = (k / (N - 1) - 0.5) * SHUTTER / FPS
            a2, _ = draw(t + dt, n); acc += a2
        arr = (acc / N).astype(np.uint8)
    return post(arr, n, **params)

if __name__ == '__main__':
    mode = sys.argv[1]
    od = os.path.join(ROOT, 'work', 'pv2'); os.makedirs(od, exist_ok=True)
    if mode == 'stills':
        ims = []
        for a in sys.argv[2:]:
            t = b2t(float(a[1:])) if a.startswith('b') else float(a)
            im = frame(int(round(t * FPS)))
            cv2.imwrite(os.path.join(od, f'still_{t:07.2f}.jpg'), im[:, :, ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
            ims.append(cv2.resize(im[:, :, ::-1], (960, 540), interpolation=cv2.INTER_AREA))
        cols = 2 if len(ims) > 1 else 1
        rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]
        cv2.imwrite(os.path.join(od, 'sheet.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 82])
    elif mode == 'strip':      # dense strip around a moment to judge motion: strip t0 t1 step
        t0, t1, st = map(float, sys.argv[2:5]); ims = []
        t = t0
        while t <= t1 + 1e-6:
            im = frame(int(round(t * FPS)))
            ims.append(cv2.resize(im[:, :, ::-1], (480, 270), interpolation=cv2.INTER_AREA)); t += st
        cols = 4
        while len(ims) % cols: ims.append(np.zeros_like(ims[0]))
        cv2.imwrite(os.path.join(od, 'strip.jpg'), np.vstack([np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 80])
    else:
        args = [a for a in sys.argv[2:] if not a.startswith('--')]
        t0 = float(args[0]) if args else 0.0; t1 = float(args[1]) if len(args) > 1 else kit.TOTAL
        half = '--half' in sys.argv
        out = os.path.join(ROOT, 'out', 'pv2_preview.mp4' if (half or args) else 'pv2_silent.mp4')
        size = f'{W // 2}x{H // 2}' if half else f'{W}x{H}'
        cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', size, '-r', str(FPS), '-i', '-',
               '-c:v', 'h264_nvenc', '-preset', 'p6', '-rc', 'vbr', '-cq', '17' if not half else '23', '-b:v', '0', '-pix_fmt', 'yuv420p', out]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n0, n1 = int(t0 * FPS), int(t1 * FPS); st = time.time()
        for n in range(n0, n1):
            im = frame(n)
            if half: im = cv2.resize(im, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
            ff.stdin.write(np.ascontiguousarray(im).tobytes())
            if (n - n0) % 150 == 0: print(f'{n - n0}/{n1 - n0}  {(n - n0) / max(1e-6, time.time() - st):.1f} fps', flush=True)
        ff.stdin.close(); ff.wait(); print('done', out, f'{time.time() - st:.0f}s')
