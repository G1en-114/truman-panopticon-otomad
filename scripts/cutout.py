"""Cut-outs with rembg (BiRefNet, GPU) -> assets/cut/*.png (RGBA, trimmed).
   usage: cutout.py [name ...]   (default: all jobs)"""
import os, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pv'))
import numpy as np, cv2
from core import ROOT, MOVIE

CUT = os.path.join(ROOT, 'assets', 'cut'); GEN = os.path.join(ROOT, 'assets', 'gen')
os.makedirs(os.path.join(CUT, 'seq'), exist_ok=True)

# name: ('movie', t) | ('gen', file) | ('split', file, min_area) | ('seq', t0, dur, fps) ; optional crop (x0, y0, x1, y1) in source px
JOBS = {
    'truman_wave': ('movie', 172.0), 'truman_sirius': ('movie', 520.0), 'truman_wall': ('movie', 5490.0),
    'truman_hand': ('movie', 5402.0), 'truman_gn': ('movie', 5690.0), 'truman_door': ('movie', 5714.0),
    'truman_dark': ('movie', 5594.0),
    'christof_hands': ('movie', 38.0), 'christof_close': ('movie', 4884.0), 'christof_smile': ('movie', 5642.0),
    'christof_head': ('movie', 3556.0), 'christof_title': ('movie', 26.0),
    'meryl_arms': ('movie', 3220.0), 'meryl_smile': ('movie', 86.0), 'marlon': ('movie', 122.0),
    'sylvia': ('movie', 1452.0), 'sylvia_watch': ('movie', 5680.0),
    'v_bathtub': ('movie', 5728.0), 'v_lady': ('movie', 3626.0), 'v_bar': ('movie', 4926.0), 'v_host': ('movie', 3734.0),
    'v_ladies': ('movie', 4932.0),
    'g_iris': ('gen', 'iris.png'), 'g_globe': ('gen', 'globe.png'), 'g_puppet': ('gen', 'puppet.png'),
    'g_eye': ('gen', 'eye.png'), 'g_head': ('gen', 'head.png'), 'g_sirius': ('gen', 'sirius.png'),
    'g_audience': ('gen', 'audience.png'), 'g_megaphone': ('gen', 'megaphone.png'), 'g_tv': ('gen', 'tv.png'),
    'cam': ('split', 'cams.png', 4000), 'scrap': ('split', 'scraps.png', 6000),
    's_wave': ('seq', 171.2, 2.5, 12), 's_christof': ('seq', 36.0, 3.0, 12), 's_bow': ('seq', 5704.0, 2.0, 12),
    's_meryl': ('seq', 3252.0, 2.5, 12), 's_wall': ('seq', 5489.0, 2.5, 12), 's_gn': ('seq', 5689.5, 2.0, 12),
    's_sylvia': ('seq', 1452.0, 1.3, 12), 's_marlon': ('seq', 120.5, 2.0, 12),
}

ML_GEN = {'eye.png'}      # backgrounds that are not flat enough for keying

def wkey(bgr, tol=34):
    """key out a flat light background connected to the image border (for generated assets); bg colour = border median"""
    edge = np.concatenate([bgr[:4].reshape(-1, 3), bgr[-4:].reshape(-1, 3), bgr[:, :4].reshape(-1, 3), bgr[:, -4:].reshape(-1, 3)])
    ref = np.median(edge, 0)
    d = np.abs(bgr.astype(np.float32) - ref[None, None]).max(2)
    cand = (d < tol).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    a = (~bg).astype(np.uint8) * 255
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(cv2.erode(a, np.ones((2, 2), np.uint8)), (0, 0), 0.9)
    return np.concatenate([bgr, a[:, :, None]], 2)

ML_PY = os.path.expanduser('~/.venvs/ml/bin/python')
def matte_batch(frames):
    """IS-Net on the GPU in the ml venv; frames: list of BGR -> list of BGRA"""
    import subprocess, tempfile, shutil
    d = tempfile.mkdtemp(prefix='cut_', dir=os.path.join(ROOT, 'work'))
    src, dst = os.path.join(d, 'in'), os.path.join(d, 'out'); os.makedirs(src)
    for i, f in enumerate(frames): cv2.imwrite(os.path.join(src, f'{i:04d}.png'), f)
    nv = os.path.expanduser('~/.venvs/ml/lib/python3.13/site-packages/nvidia')
    env = dict(os.environ, LD_LIBRARY_PATH=':'.join([os.path.join(ROOT, 'tools', 'cudnn_shim'), nv + '/cudnn/lib', nv + '/cu13/lib', os.environ.get('LD_LIBRARY_PATH', '')]))
    subprocess.run([ML_PY, os.path.join(ROOT, 'scripts', 'matte_isnet.py'), src, dst], check=True, env=env)
    out = [cv2.imread(os.path.join(dst, f'{i:04d}.png'), cv2.IMREAD_UNCHANGED) for i in range(len(frames))]
    shutil.rmtree(d)
    return out

def matte(bgr):
    return matte_batch([bgr])[0]

def trim(bgra, pad=6):
    a = bgra[:, :, 3]; ys, xs = np.where(a > 12)
    if len(xs) == 0: return bgra
    y0, y1, x0, x1 = max(0, ys.min() - pad), min(a.shape[0], ys.max() + pad), max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad)
    return bgra[y0:y1, x0:x1]

def movie_frame(t):
    """frame-accurate decode via ffmpeg (OpenCV seeking in the mkv drifts), top 600 px (subtitles cropped)"""
    import subprocess
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', os.path.join(ROOT, 'src', 'movie.mkv'), '-frames:v', '1',
                          '-vf', 'crop=1280:600:0:0', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(600, 1280, 3).copy()

def run(name, job):
    kind = job[0]
    if kind == 'movie':
        cv2.imwrite(os.path.join(CUT, name + '.png'), trim(matte(movie_frame(job[1]))))
    elif kind == 'gen':
        cv2.imwrite(os.path.join(CUT, name + '.png'), trim(wkey(cv2.imread(os.path.join(GEN, job[1]))) if job[1] not in ML_GEN else matte(cv2.imread(os.path.join(GEN, job[1])))))
    elif kind == 'split':
        m = wkey(cv2.imread(os.path.join(GEN, job[1])))
        a = (m[:, :, 3] > 30).astype(np.uint8)
        a = cv2.dilate(a, np.ones((9, 9), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(a)
        k = 0
        for i in sorted(range(1, n), key=lambda i: (stats[i][1] // 300, stats[i][0])):
            x, y, w, h, area = stats[i]
            if area < job[2]: continue
            sub = m[y:y + h, x:x + w].copy(); sub[:, :, 3] = sub[:, :, 3] * (lab[y:y + h, x:x + w] == i)
            k += 1; cv2.imwrite(os.path.join(CUT, f'{name}_{k}.png'), trim(sub))
        print(name, k, 'pieces')
    elif kind == 'seq':
        t0, dur, fps = job[1:4]
        d = os.path.join(CUT, 'seq', name); os.makedirs(d, exist_ok=True)
        for f in glob.glob(os.path.join(d, '*.png')): os.remove(f)
        frames = matte_batch([movie_frame(t0 + i / fps) for i in range(int(dur * fps))])
        # common bbox so the loop doesn't jitter
        A = np.max([f[:, :, 3] for f in frames], 0); ys, xs = np.where(A > 12)
        y0, y1, x0, x1 = max(0, ys.min() - 6), ys.max() + 6, max(0, xs.min() - 6), xs.max() + 6
        for i, f in enumerate(frames):
            sub = f[y0:y1, x0:x1]
            if sub.shape[1] > 720: sub = cv2.resize(sub, (720, int(sub.shape[0] * 720 / sub.shape[1])), interpolation=cv2.INTER_AREA)
            cv2.imwrite(os.path.join(d, f'{i:03d}.png'), sub)
    print('ok', name, flush=True)

if __name__ == '__main__':
    names = sys.argv[1:] or list(JOBS)
    stills = [nm for nm in names if JOBS[nm][0] == 'movie']
    if stills:      # one GPU session for all movie stills
        for nm, m in zip(stills, matte_batch([movie_frame(JOBS[nm][1]) for nm in stills])):
            cv2.imwrite(os.path.join(CUT, nm + '.png'), trim(m)); print('ok', nm)
    for nm in names:
        if nm not in stills: run(nm, JOBS[nm])
