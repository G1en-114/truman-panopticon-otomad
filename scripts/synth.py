"""WORLD-based resampler: turns movie-dialogue syllables into the sung melody.
Outputs dry stems to work/stems/*.wav and the note/syllable timeline to work/timeline.json
"""
import numpy as np, soundfile as sf, json, sys, os, warnings, mido
warnings.filterwarnings('ignore')
import pyworld as pw
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, 'scripts')
from lyrics import SUNG, PHRASES, parse

SR = 44100; FP = 5.0; FPS = 1000 / FP
SPB = 0.344828; PRE = 16            # beats of pre-roll before MIDI beat 0
TOTAL_BEATS = PRE + 204 + 12
def b2t(b): return (b + PRE) * SPB

SPK = {  # per-speaker rendering options
 'christof': dict(sub=True,  lead=0.75, harm=0.8),
 'marlon':   dict(sub=False, gain=1.0),
 'truman':   dict(sub=False, gain=1.0),
 'radio':    dict(sub=False, gain=1.0),
 'sylvia':   dict(sub=False, up=True, dev=0.45, up_g=0.5),
}

def midi_notes(name):
    mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
    out = []
    for tr in mid.tracks:
        if tr.name != name: continue
        t = 0; on = {}
        for m in tr:
            t += m.time
            if m.type == 'note_on' and m.velocity > 0: on[m.note] = t
            elif m.type in ('note_off', 'note_on') and m.note in on:
                a = on.pop(m.note); out.append((a / 96, (t - a) / 96, m.note))
    out.sort()
    # drop duplicates / overlaps at the same onset (keep highest)
    ded = []
    for n in out:
        if ded and abs(ded[-1][0] - n[0]) < 1e-6:
            if n[2] > ded[-1][2]: ded[-1] = n
        else: ded.append(n)
    return ded

F0R = {'christof': (60, 260), 'sylvia': (170, 720), 'truman': (85, 620), 'radio': (80, 420), 'marlon': (70, 400)}
OCT = {'c07': 0}   # per-chunk octave override (semitones)
LEAD = midi_notes('Vocal2'); HARM = midi_notes('Vocal1')
def harm_pitch(beat):
    for a, d, p in HARM:
        if a - 0.01 <= beat < a + d - 0.01: return p
    # nearest onset within a quarter beat
    c = [(abs(a - beat), p) for a, d, p in HARM if abs(a - beat) <= 0.26]
    return min(c)[1] if c else None

idx = json.load(open('work/clips/index.json'))
ali = json.load(open('work/clips/align.json'))
VOC, vsr = sf.read('work/clips/dm/htdemucs_ft/all_raw/vocals.wav'); VOC = VOC.mean(1)
assert vsr == SR
chunkmeta = {c[0]: c for c in SUNG}

# ---------- build token list: every syllable gets its notes ----------
tokens = []   # dict(cid, si, syl, notes=[(beat,dur,pitch)...], shift)
ni = 0
for pname, cids, shift in PHRASES:
    for cid in cids:
        text = chunkmeta[cid][4]; si = 0
        for it in parse(text):
            if it[0] == 'skip': ni += 1; continue
            if it[0] == 'tie': tokens[-1]['notes'].append(LEAD[ni]); ni += 1; continue
            _, sy, new_word, same = it
            if same:   # share the previous syllable's note: split it in two
                pb, pd, pp = tokens[-1]['notes'][-1]
                tokens[-1]['notes'][-1] = (pb, pd * 0.5, pp); note = (pb + pd * 0.5, pd * 0.5, pp)
            else:
                note = LEAD[ni]; ni += 1
            tokens.append(dict(cid=cid, si=si, syl=sy, notes=[note], shift=OCT.get(cid, shift), phrase=pname, spk=chunkmeta[cid][1], nw=new_word))
            si += 1
print('lead notes', len(LEAD), 'consumed', ni)
assert ni == len(LEAD), 'syllable/note count mismatch'

# ---------- per-chunk analysis ----------
def analyze(cid):
    m = idx[cid]; a = ali[cid]
    c0 = max(0.0, a[0]['start'] - 0.25); c1 = min(m['dur'], a[-1]['end'] + 0.55)
    x = VOC[int((m['pos'] + c0) * SR): int((m['pos'] + c1) * SR)].astype(np.float64)
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    lo_, hi_ = F0R.get(m['spk'], (65, 750))
    f0, t = pw.harvest(x, SR, f0_floor=lo_, f0_ceil=hi_, frame_period=FP)
    f0 = pw.stonemask(x, f0, t, SR)
    sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    n = len(f0)
    env = np.sqrt(np.convolve(x ** 2, np.ones(441) / 441, 'same'))[::int(SR / FPS)][:n]
    if len(env) < n: env = np.pad(env, (0, n - len(env)))
    # fill short unvoiced gaps
    v = f0 > 0; i = 0
    while i < n:
        if not v[i]:
            j = i
            while j < n and not v[j]: j += 1
            if 0 < i and j < n and (j - i) <= 6 and env[i:j].min() > 0.25 * max(env[i - 1], env[j]):
                f0[i:j] = np.interp(np.arange(i, j), [i - 1, j], [f0[i - 1], f0[j]])
            i = j
        else: i += 1
    syl = []
    for k, s in enumerate(a):
        st = s['start'] - c0 - 0.025
        en = (a[k + 1]['start'] - c0 - 0.025) if k + 1 < len(a) else None
        syl.append([st, en])
    # last syllable end: energy falls
    st = syl[-1][0]; i0 = int(st * FPS); pk = env[i0:i0 + 80].max() if i0 < n else 0
    j = min(n - 1, int((a[-1]['end'] - c0) * FPS))
    jmax = j + int(0.22 * FPS)
    while j < n - 1 and env[j] > 0.12 * pk and j < jmax: j += 1
    syl[-1][1] = j / FPS
    out = []
    for st, en in syl:
        i0 = max(0, int(st * FPS)); i1 = min(n, max(i0 + 4, int(en * FPS)))
        e = env[i0:i1]; pk = e.max() + 1e-9; vv = f0[i0:i1] > 0
        cand = np.where(vv & (e >= 0.3 * pk))[0]
        if len(cand) == 0: cand = np.where(e >= 0.35 * pk)[0]
        von = i0 + cand[0]; nend = i0 + cand[-1] + 1
        # contiguous voiced run from von
        vf0 = f0[von:nend]; med = np.median(vf0[vf0 > 0]) if (vf0 > 0).any() else 0
        out.append(dict(s=i0, v=von, n=max(nend, von + 2), e=i1, med=med, rms=float(np.sqrt((e[cand] ** 2).mean()))))
    return dict(f0=f0, sp=sp, ap=ap, env=env, syl=out, n=n)

AN = {c[0]: analyze(c[0]) for c in SUNG}

# ---------- target layout ----------
for i, tk in enumerate(tokens):
    tk['T'] = b2t(tk['notes'][0][0]); tk['Tend'] = b2t(tk['notes'][-1][0] + tk['notes'][-1][1])
    sy = AN[tk['cid']]['syl'][tk['si']]
    tk['pre_src'] = (sy['v'] - sy['s']) / FPS
for i, tk in enumerate(tokens):
    prev = tokens[i - 1] if i else None
    first = (prev is None) or prev['cid'] != tk['cid'] or tk['T'] - prev['Tend'] > 0.03
    room = 0.22 if first else 0.5 * (tk['T'] - prev['T'])
    tk['pre'] = max(0.0, min(tk['pre_src'], 0.14, room)); tk['first'] = first
for i, tk in enumerate(tokens):
    nx = tokens[i + 1] if i + 1 < len(tokens) else None
    if nx is not None and nx['T'] - tk['Tend'] < 0.03:
        tk['Bend'] = nx['T'] - nx['pre']; tk['last'] = nx['cid'] != tk['cid']
    else:
        tk['Bend'] = tk['Tend']; tk['last'] = True

def render_chunk(cid, toks, mode):
    """mode: 'lead' | 'harm' | 'sub'  -> (start_time, waveform)"""
    A = AN[cid]; f0s, sp, ap = A['f0'], A['sp'], A['ap']
    t0 = toks[0]['T'] - toks[0]['pre'] - 0.01
    t1 = toks[-1]['Bend'] + 0.10
    nfr = int((t1 - t0) * FPS) + 1
    src = np.zeros(nfr); tf0 = np.zeros(nfr); gain = np.zeros(nfr); dev = np.zeros(nfr); nuc = np.zeros(nfr, bool)
    for k, tk in enumerate(toks):
        sy = A['syl'][tk['si']]
        s, v, nn, e = sy['s'] / FPS, sy['v'] / FPS, sy['n'] / FPS, sy['e'] / FPS
        Ln = max(nn - v, 0.01)
        nxt = toks[k + 1] if k + 1 < len(toks) else None
        joined = (nxt is not None) and (not tk['last'])
        if joined:   # anchor interval: this vowel onset -> next vowel onset
            sy2 = A['syl'][nxt['si']]; v2 = sy2['v'] / FPS
            S_end = v2; T_end = nxt['T']
        else:
            S_end = e; T_end = tk['Bend']
        Ds = max(S_end - v, 0.02); Dt = T_end - tk['T']; r = Dt / Ds
        xs = [tk['T'] - tk['pre'], tk['T']]; ys = [v - tk['pre'], v]
        if 0.55 <= r <= 1.9:
            xs += [T_end]; ys += [S_end]                      # natural co-articulation, mild stretch
        elif r > 1.9:                                         # hold the vowel centre
            a_s = v + 0.35 * Ln; b_s = v + 0.65 * Ln
            head_t = min((a_s - v) * 1.2, 0.3 * Dt)
            tail_s = S_end - b_s
            tail_t = min(tail_s * 1.25, 0.45 * Dt)
            xs += [tk['T'] + head_t, T_end - tail_t, T_end]; ys += [a_s, b_s, S_end]
        else:                                                 # too much material: keep the onset, drop the rest
            keep_t = Dt - (nxt['pre'] if joined else 0.0)
            xs += [tk['T'] + max(keep_t, 0.01)]; ys += [v + max(keep_t, 0.01) / 0.6]
            if joined: xs += [T_end]; ys += [S_end]
        if not joined:  # natural release
            xs += [T_end + 0.08]; ys += [ys[-1] + 0.08]
        xs = np.array(xs); ys = np.array(ys)
        i0 = int(round((xs[0] - t0) * FPS)) if (k == 0 or toks[k - 1]['last']) else int(round((tk['T'] - t0) * FPS))
        i1 = min(nfr, int(round((xs[-1] - t0) * FPS)))
        tt = t0 + np.arange(i0, i1) / FPS
        src[i0:i1] = np.interp(tt, xs, ys)
        nuc[i0:i1] |= (src[i0:i1] >= v) & (src[i0:i1] <= nn)
        tail = not joined
        # the pitch of a syllable starts a little before its vowel (during the consonant)
        p0 = i0 if (k == 0 or toks[k - 1]['last']) else max(0, i0 - int(tk['pre'] * FPS))
        # pitch per frame from (possibly tied) notes
        for (nb, nd, npitch) in tk['notes']:
            if mode == 'harm':
                hp = harm_pitch(nb)
                p = None if hp is None else hp + tk['shift']
            elif mode == 'sub': p = npitch + tk['shift'] - 12
            elif mode == 'up': p = npitch + tk['shift'] + 12
            else: p = npitch + tk['shift']
            j0 = max(i0, int(round((b2t(nb) - t0) * FPS))) if (nb, nd, npitch) != tk['notes'][0] else p0
            if p is None: tf0[j0:i1] = -1
            else: tf0[j0:i1] = 440 * 2 ** ((p - 69) / 12)
        g = min(3.2, max(0.35, (0.11 / (sy['rms'] + 1e-6)) ** 0.75))
        gain[i0:i1] = g
        fade = min(3, (i1 - i0) // 2)
        if tk['first'] and fade: gain[i0:i0 + fade] *= np.linspace(0, 1, fade)
        if tail:
            kk = int(0.08 * FPS); gain[max(i0, i1 - kk):i1] *= np.linspace(1, 0, min(kk, i1 - i0))
        # original expressive deviation (in semitones, relative to syllable median)
        if sy['med'] > 0:
            sidx = np.clip((src[i0:i1] * FPS).astype(int), 0, A['n'] - 1)
            sf0 = f0s[sidx]
            d = np.where(sf0 > 0, 12 * np.log2(np.maximum(sf0, 1) / sy['med']), 0)
            dev[i0:i1] = np.clip(d, -2.5, 2.5) * SPK[tk['spk']].get('dev', 0.2)
    # interpolate WORLD params
    pos = np.clip(src * FPS, 0, A['n'] - 1.001); lo = pos.astype(int); fr = (pos - lo)[:, None]
    spo = sp[lo] * (1 - fr) + sp[lo + 1] * fr; apo = ap[lo] * (1 - fr) + ap[lo + 1] * fr
    voiced = ((f0s[lo] > 0) & (f0s[np.minimum(lo + 1, A['n'] - 1)] > 0)) | nuc
    fbin = np.linspace(0, SR / 2, apo.shape[1])
    cap = np.clip(0.30 + 0.70 * fbin / 6500.0, 0, 1)[None, :]
    apo = np.where(nuc[:, None], np.minimum(apo, cap), apo)
    mute = tf0 < 0
    tf0s = np.where(tf0 > 0, tf0, np.nan)
    # fill & smooth pitch (portamento)
    good = ~np.isnan(tf0s)
    if good.any():
        tf0s = np.interp(np.arange(nfr), np.where(good)[0], np.log2(tf0s[good]))
        tf0s = gaussian_filter1d(tf0s, 2.2)
    else: tf0s = np.full(nfr, np.log2(220.0))
    dev = gaussian_filter1d(dev, 1.5)
    # vibrato on long notes
    vib = np.zeros(nfr)
    for tk in toks:
        nb, nd, _ = tk['notes'][-1]
        if nd >= 1.5:
            a = int((b2t(nb) + 0.32 - t0) * FPS); b = int((tk['Bend'] - t0) * FPS)
            if b > a:
                tt = np.arange(b - a) / FPS
                vib[a:b] = np.minimum(1, tt / 0.35) * 0.28 * np.sin(2 * np.pi * 5.4 * tt)
    rng = np.random.default_rng(abs(hash(cid)) % 9999)
    jit = gaussian_filter1d(rng.normal(0, 1, nfr), 14) * 0.9      # slow drift, ~±10 cents
    for tk in toks:
        nb, nd, _ = tk['notes'][-1]
        dur = tk['Bend'] - tk['T']
        if dur > 0.75:
            a = int((tk['T'] + 0.45 * dur - t0) * FPS); b = int((tk['Bend'] - t0) * FPS)
            gain[a:b] *= np.linspace(1, 0.28, b - a) ** 1.3
    f0o = np.where(voiced & (gain > 0), 2 ** (tf0s + (dev + vib + jit * 0.12) / 12), 0.0)
    if os.environ.get('NOPITCH'): f0o = np.where(f0s[lo] > 0, f0s[lo], 0.0) * (gain > 0)
    y = pw.synthesize(f0o.astype(np.float64), np.ascontiguousarray(spo), np.ascontiguousarray(apo), SR, FP)
    g = np.interp(np.arange(len(y)) / SR * FPS, np.arange(nfr), gaussian_filter1d(np.where(mute, 0, gain), 1.2))
    return t0, y * g

L = int(TOTAL_BEATS * SPB * SR)
stems = {k: np.zeros(L) for k in ('lead', 'harm', 'sub', 'up')}
bychunk = {}
for tk in tokens: bychunk.setdefault(tk['cid'], []).append(tk)
for cid, toks in bychunk.items():
    spk = toks[0]['spk']
    modes = ['lead', 'harm'] + (['sub'] if SPK[spk].get('sub') else []) + (['up'] if SPK[spk].get('up') else [])
    for mode in modes:
        t0, y = render_chunk(cid, toks, mode)
        i = int(t0 * SR); stems[mode][i:i + len(y)] += y[:L - i] * SPK[spk].get(mode, 1.0) * (SPK[spk].get('up_g', 1.0) if mode == 'up' else 1.0)
os.makedirs('work/stems', exist_ok=True)
for k, v in stems.items():
    sf.write(f'work/stems/{k}.wav', v, SR)
    print(k, 'peak', round(float(np.abs(v).max()), 3), 'rms', round(float(np.sqrt((v ** 2).mean())), 4))
tl = [dict(cid=t['cid'], nw=t['nw'], syl=t['syl'], spk=t['spk'], phrase=t['phrase'], t=round(t['T'], 4), end=round(t['Bend'], 4),
           beat=t['notes'][0][0], pitch=t['notes'][0][2] + t['shift'], notes=[[n[0], n[1], n[2] + t['shift']] for n in t['notes']]) for t in tokens]
json.dump(dict(spb=SPB, pre=PRE, tokens=tl), open('work/timeline.json', 'w'), indent=0)
for pname, _, _ in PHRASES:
    tt = [t for t in tokens if t['phrase'] == pname]
    print(pname, len(tt), 'syll', round(tt[0]['T'], 2), '→', round(tt[-1]['Bend'], 2), '|', ' '.join(t['syl'] for t in tt))
if '--debug' in sys.argv:
    for tk in tokens:
        sy = AN[tk['cid']]['syl'][tk['si']]
        Ln = (sy['n'] - sy['v']) / FPS; Db = tk['Bend'] - tk['T']
        tgt = tk['notes'][0][2] + tk['shift']
        srcm = 69 + 12 * np.log2(sy['med'] / 440) if sy['med'] > 0 else float('nan')
        print(f"{tk['cid']} {tk['syl']:8s} pre={tk['pre']*1000:4.0f}ms nuc={Ln*1000:4.0f}ms body={Db*1000:4.0f}ms ratio={Db/max(Ln,1e-3):4.1f} src={srcm:5.1f} tgt={tgt} shift={tgt-srcm:+5.1f}")
