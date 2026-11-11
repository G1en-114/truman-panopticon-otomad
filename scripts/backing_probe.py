import numpy as np, librosa, mido, warnings
warnings.filterwarnings('ignore')
mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
tpb=96; spb=0.344828; sr=44100; hop=32; fps=sr/hop
y,_=librosa.load('src/offvocal.wav',sr=sr,mono=True,offset=170,duration=85.1)
env=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
# drum onsets from midi
on=[]
for tr in mid.tracks:
    if tr.name!='Drum kit': continue
    tt=0
    for m in tr:
        tt+=m.time
        if m.type=='note_on' and m.velocity>0: on.append(tt/tpb*spb)
on=np.array(sorted(set(on)))
best=[]
for off in np.arange(13.0,13.6,0.002):
    idx=((on+off)*fps).astype(int); idx=idx[idx<len(env)]
    best.append((env[idx].mean(),off))
best.sort(reverse=True); print('best offsets (rel 170s):',[(round(float(a),3),round(float(b)+170,3)) for a,b in best[:5]])
T0=best[0][1]
# per-beat rms from T0-8 beats to end
rms=[]
for b in range(-12,210):
    s=int((T0+b*spb)*sr); e=int((T0+(b+1)*spb)*sr)
    if s<0 or e>len(y): rms.append(None); continue
    rms.append(20*np.log10(np.sqrt((y[s:e]**2).mean())+1e-9))
for b0 in range(-12,210,16):
    print(f'beat {b0:4d}:',' '.join('  --' if r is None else f'{r:5.1f}' for r in rms[b0+12:b0+28]))
print('file end beat', (85.1-T0)/spb)
