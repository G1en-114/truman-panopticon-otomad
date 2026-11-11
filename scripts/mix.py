"""Mixdown: backing (off-vocal) + sung stems + spoken lines + fx -> out/audio_vN.wav"""
import numpy as np, soundfile as sf, json, sys, os, warnings
warnings.filterwarnings('ignore')
from scipy.signal import butter, sosfilt, sosfiltfilt, fftconvolve
from scipy.ndimage import maximum_filter1d, uniform_filter1d
sys.path.insert(0, 'scripts')
from lyrics import SPOKEN

SR = 44100; SPB = 0.344828; PRE = 16; T0 = 183.28
END_BEAT = 204
def b2t(b): return (b + PRE) * SPB
def b2s(b): return int(round(b2t(b) * SR))
TAIL = 4.2
N = b2s(END_BEAT) + int(TAIL * SR)
rng = np.random.default_rng(7)

def db(x): return 10 ** (x / 20)
def st(x): return np.stack([x, x], 1) if x.ndim == 1 else x
def filt(x, kind, fc, order=2):
    sos = butter(order, np.array(fc) / (SR / 2), kind, output='sos')
    return sosfilt(sos, x, axis=0)
def peak_eq(x, f, gain_db, q=1.0):
    # RBJ peaking biquad
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A]); a = np.array([1 + al / A, -2 * np.cos(w), 1 - al / A])
    from scipy.signal import lfilter
    return lfilter(b / a[0], a / a[0], x, axis=0)
def env_follow(x, win=0.02):
    m = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    return np.sqrt(np.maximum(uniform_filter1d(m ** 2, int(win * SR)), 0))
def compress(x, thr_db=-20, ratio=3.0, win=0.012, makeup_db=0):
    e = env_follow(x, win) + 1e-9
    over = np.maximum(20 * np.log10(e) - thr_db, 0)
    g = db(-over * (1 - 1 / ratio))
    g = uniform_filter1d(g, int(0.03 * SR))
    return x * (g[:, None] if x.ndim == 2 else g) * db(makeup_db)
def reverb_ir(rt60=1.6, pre=0.025, lo=350, hi=7500, seed=1):
    r = np.random.default_rng(seed); n = int((rt60 + 0.3) * SR)
    t = np.arange(n) / SR
    ir = r.normal(0, 1, (n, 2)) * np.exp(-6.9 * t / rt60)[:, None]
    ir = filt(filt(ir, 'high', lo), 'low', hi)
    ir = np.concatenate([np.zeros((int(pre * SR), 2)), ir])
    return ir / np.sqrt((ir ** 2).sum(0)).mean()
def reverb(x, wet_db, **kw):
    ir = reverb_ir(**kw); x = st(x)
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in (0, 1)], 1)
    return y * db(wet_db)
def place(buf, x, t, gain=1.0):
    i = int(round(t * SR)); x = st(x)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n] * gain
def fade(x, fi=0.01, fo=0.03):
    x = x.copy(); a = int(fi * SR); b = int(fo * SR)
    sh = (slice(None), None) if x.ndim == 2 else (slice(None),)
    if a: x[:a] *= np.linspace(0, 1, a)[sh]
    if b: x[-b:] *= np.linspace(1, 0, b)[sh]
    return x

# ------------------------------------------------------------------ backing
f = sf.SoundFile('src/offvocal.wav'); f.seek(int((T0 - PRE * SPB) * SR))
bk = f.read(b2s(END_BEAT)); bk = np.concatenate([bk, np.zeros((N - len(bk), 2))])
# intro: "small TV speaker" backing, then silence for the a-cappella pickup, full band at the first downbeat
i_cut = b2s(1.4); i_in = b2s(3.0) - int(0.004 * SR)
tv = filt(filt(bk[:i_cut], 'high', 380, 2), 'low', 2600, 2)
tv = np.tanh(tv * 2.2) * 0.42
tv *= np.linspace(0.0, 1.0, len(tv))[:, None] ** 0.6
tv[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))[:, None]
bk[:i_cut] = tv; bk[i_cut:i_in] = 0
bk[i_in:i_in + 200] *= np.linspace(0, 1, 200)[:, None]
e = b2s(END_BEAT); bk[e - 300:e] *= np.linspace(1, 0, 300)[:, None]; bk[e:] = 0
bk *= db(-4.0)

# ------------------------------------------------------------------ sung vocals
def load(n):
    x, _ = sf.read(f'work/stems/{n}.wav'); return np.concatenate([x, np.zeros(max(0, N - len(x)))])[:N]
lead, harm, sub, up = load('lead'), load('harm'), load('sub'), load('up')
def vproc(x, hp=110):
    x = filt(x, 'high', hp, 2)
    x = peak_eq(x, 3200, 3.5, 0.9); x = peak_eq(x, 300, -2.5, 1.0); x = filt(x, 'low', 13000, 2)
    return compress(x, -22, 3.5, makeup_db=4)
lead_p = vproc(lead); harm_p = vproc(harm, 140); sub_p = vproc(sub, 70); up_p = vproc(up, 200)
vox = np.zeros((N, 2))
vox += st(lead_p) * 1.0
vox += st(sub_p) * 0.95
d = int(0.012 * SR)
vox[:, 0] += harm_p * 0.62; vox[d:, 1] += harm_p[:-d] * 0.62        # harmony widened (Haas)
vox[d:, 0] += up_p[:-d] * 0.8; vox[:, 1] += up_p * 0.8
# eighth-note echo on the long phrase endings
echo = np.zeros((N, 2)); dl = int(1.5 * SPB * SR)
src_e = filt(filt(vox, 'high', 500), 'low', 3500)
for k, g in enumerate((0.30, 0.17, 0.09), 1):
    echo[k * dl:] += src_e[:-k * dl][:, ::(-1 if k % 2 else 1)] * g
vox_wet = reverb(vox, -15, rt60=1.5, seed=3) + echo * 0.55

# ------------------------------------------------------------------ spoken lines
idx = json.load(open('work/clips/index.json'))
CV, _ = sf.read('work/clips/dm/htdemucs_ft/all_raw/vocals.wav')
CR, _ = sf.read('work/clips/all_raw.wav')
def clip(cid, raw=False, lead_in=0.03, tail=0.12):
    m = idx[cid]; src = CR if raw else CV
    a = int((m['pos'] + m['pad'] - lead_in) * SR); b = int((m['pos'] + m['dur'] - m['pad'] + tail) * SR)
    return fade(src[a:b].copy(), 0.015, 0.06)
def trim(x, thr=0.04):
    e = env_follow(x, 0.01); pk = e.max(); i = np.argmax(e > thr * pk)
    return x[max(0, i - int(0.012 * SR)):]
def norm(x, target=0.1):
    e = env_follow(x, 0.05); act = e > 0.25 * e.max()
    return x * (target / (np.sqrt((x[act] ** 2).mean()) + 1e-9))
def god(x):      # Christof: the voice from the sky / PA
    x = filt(filt(x, 'high', 160), 'low', 6000); x = peak_eq(x, 1800, 4, 0.8)
    return compress(x, -22, 4, makeup_db=5)
def plain(x):
    x = filt(x, 'high', 100); x = peak_eq(x, 3000, 3, 0.9)
    return compress(x, -22, 3.5, makeup_db=4)
def tvspk(x):
    x = filt(filt(x, 'high', 420, 2), 'low', 3000, 2)
    return compress(np.tanh(x * 3) * 0.5, -20, 3, makeup_db=3)

spk = np.zeros((N, 2)); spk_wet_in = np.zeros((N, 2)); spk_dry_tv = np.zeros((N, 2))
SP = []   # (id, time, text) for the video timeline
def say(cid, beat, fx, gain=1.0, wet=1.0, raw=False, target=0.1, t=None):
    x = norm(trim(clip(cid, raw)), target); x = fx(x) * gain
    tt = b2t(beat) if t is None else t
    place(spk, x, tt); place(spk_wet_in, x * wet, tt)
    SP.append(dict(id=cid, t=round(tt, 3), dur=round(len(x) / SR, 3), text=idx[cid]['text'], spk=idx[cid]['spk']))

# intro narration through a TV speaker
say('s01', -15.3, tvspk, gain=1.15, wet=0.25)
# outro: Christof pleads from the sky, Truman answers
say('s03', 123.0, god, 1.0, 1.0)      # You can't leave, Truman.
say('s04', 131.0, god, 1.0, 1.0)      # You belong here.
say('s05', 135.0, god, 1.0, 1.0)      # With me.
say('s06', 139.0, god, 1.0, 1.0)      # Talk to me.
say('s07', 143.0, god, 1.0, 1.0)      # Say something.
say('s08', 147.0, god, 1.1, 1.0)      # Say something, goddammit!
say('s09', 152.4, god, 1.1, 1.0)      # You're on television!
say('s10', 155.8, god, 1.15, 1.0)     # You're live to the whole world!
say('s11', 163.0, plain, 1.2, 0.35)   # In case I don't see ya
say('s12', 171.0, plain, 1.25, 0.35)  # Good afternoon, good evening, and good night.
t_end = b2t(END_BEAT)
say('s14', None, tvspk, 1.0, 0.3, t=t_end + 0.35)   # Cease transmission.
say('s15', None, plain, 1.0, 0.15, t=t_end + 2.15)  # What else is on?
# crowd cheer swelling under the last riff (raw movie audio, band-limited)
ch = clip('s13', raw=True, lead_in=0, tail=0)
ch = filt(filt(ch, 'high', 500), 'low', 6000)
ch = ch / (np.abs(ch).max() + 1e-9)
t_c0 = b2t(178.5); n_c = min(len(ch), b2s(END_BEAT) - int(t_c0 * SR))
envc = np.minimum(1, np.arange(n_c) / (2.5 * SR)) ** 1.5
ch = ch[:n_c] * envc[:, None]; ch[-400:] *= np.linspace(1, 0, 400)[:, None]
place(spk, ch, t_c0, 0.30)
spk_wet = reverb(spk_wet_in, -9, rt60=2.4, pre=0.06, lo=300, hi=6000, seed=5)

# ------------------------------------------------------------------ fx: tv on / off, riser, impact
fx = np.zeros((N, 2))
def noise(n): return rng.normal(0, 1, (n, 2))
n0 = int(0.42 * SR); x = filt(noise(n0), 'high', 1500) * np.exp(-np.arange(n0) / (0.09 * SR))[:, None]
place(fx, x * 0.22, 0.02)                                    # tv switch-on static
n1 = b2s(3.0) - b2s(1.4); x = filt(noise(n1), 'band', [900, 7000]) * (np.linspace(0, 1, n1) ** 3)[:, None]
place(fx, x * 0.10, b2t(1.4))                                # riser into the first downbeat
n2 = int(0.5 * SR); tt = np.arange(n2) / SR
x = (np.sin(2 * np.pi * (15700 * tt)) * np.exp(-tt / 0.05))[:, None] * np.ones((1, 2)) * 0.05 + filt(noise(n2), 'high', 2500) * np.exp(-tt / 0.03)[:, None] * 0.25
place(fx, x, t_end + 3.25)                                   # tv switch-off click

# ------------------------------------------------------------------ balance + sidechain + master
def act_rms(x, thr=0.2):
    e = env_follow(x, 0.05); a = e > thr * e.max(); return np.sqrt((x[a] ** 2).mean())
bk_r = np.sqrt((bk[b2s(4):b2s(180)] ** 2).mean())
vg = bk_r * db(+2.0) / act_rms(vox)
sg = bk_r * db(+3.5) / act_rms(spk[b2s(100):])
vox_all = (vox + vox_wet) * vg; spk_all = (spk + spk_wet) * sg
side = env_follow(vox * vg + spk * sg, 0.06); side = np.minimum(1, side / (bk_r * 1.2))
duck = 1 - 0.28 * uniform_filter1d(side, int(0.08 * SR))
bk_d = bk * duck[:, None]
# carve a little presence out of the backing where the voices sit
mid = filt(bk_d, 'band', [1200, 4200], 2)
bk_d = bk_d - mid * (0.30 * uniform_filter1d(side, int(0.08 * SR)))[:, None]
mix = bk_d + vox_all + spk_all + fx
def limiter(x, ceil=0.89, look=0.004, rel=0.12):
    pk = maximum_filter1d(np.abs(x).max(1), int(look * SR) * 2 + 1)
    g = np.minimum(1, ceil / (pk + 1e-9))
    # release smoothing: running minimum then smooth
    g = -maximum_filter1d(-g, int(rel * SR) // 2); g = uniform_filter1d(g, int(0.01 * SR))
    return x * g[:, None]
for nm_, a_ in (("bk_d", bk_d), ("vox_all", vox_all), ("spk_all", spk_all), ("fx", fx)):
    if np.isnan(a_).any(): print("NaN in", nm_, np.where(np.isnan(a_).any(1))[0][:3] / SR)
pre_pk = np.abs(mix).max()
mix = limiter(mix * 0.78)
mix = np.clip(mix, -0.98, 0.98)
ver = sys.argv[1] if len(sys.argv) > 1 else 'v1'
os.makedirs('out', exist_ok=True)
sf.write(f'out/audio_{ver}.wav', mix, SR, subtype='PCM_16')
sf.write('work/stems/vox_bus.wav', vox_all, SR); sf.write('work/stems/spk_bus.wav', spk_all, SR); sf.write('work/stems/backing_bus.wav', bk_d, SR)
json.dump(dict(spoken=SP, t_end=t_end, total=N / SR, spb=SPB, pre=PRE), open('work/spoken.json', 'w'), indent=1, ensure_ascii=False)
r = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
print(f'len {N/SR:.2f}s  pre-limit peak {pre_pk:.2f}  mix rms {r(mix[b2s(4):b2s(200)]):.1f} dBFS  vox {r(vox_all[b2s(4):b2s(118)]):.1f}  bk {r(bk_d[b2s(4):b2s(118)]):.1f}  spk {r(spk_all[b2s(120):b2s(180)]):.1f}')
for s in SP: print(f"  {s['t']:6.2f}s +{s['dur']:.2f}  {s['id']} {s['text']}")
