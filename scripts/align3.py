import numpy as np, librosa, mido, pyworld as pw, warnings
warnings.filterwarnings('ignore')
mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
tpb = 96; spb0 = 0.344828; fp = 0.01
y,sr = librosa.load('work/demucs/htdemucs/orig/vocals.wav',sr=16000,mono=True)
f0,t = pw.harvest(y.astype(np.float64),sr,frame_period=fp*1000,f0_floor=150,f0_ceil=1100)
rms = librosa.feature.rms(y=y,frame_length=400,hop_length=160)[0]
n=min(len(f0),len(rms)); f0=f0[:n]; f0[rms[:n]<0.01]=0
pc = np.where(f0>0, np.round(69+12*np.log2(np.maximum(f0,1)/440))%12, -1)
np.save('work/orig_f0.npy',f0)
def notes(name):
    out=[]
    for tr in mid.tracks:
        if tr.name!=name: continue
        tt=0; on={}
        for m in tr:
            tt+=m.time
            if m.type=='note_on' and m.velocity>0: on[m.note]=tt
            elif m.type in('note_off','note_on') and m.note in on: out.append((on.pop(m.note)/tpb,tt/tpb,m.note))
    return out
res=[]
for name in ['Vocal1','Vocal2']:
    ns=notes(name)
    for sc in np.arange(0.90,1.101,0.0025):
        spb=spb0*sc
        T=int(120*spb/fp)+2; r=-np.ones(T)
        for a,b,p in ns: r[int(a*spb/fp):int(b*spb/fp)]=p%12
        act=r>=0
        for trn in [0]:
            for o in range(0,len(pc)-T,5):
                seg=pc[o:o+T]
                res.append(((seg[act]==r[act]).mean(),name,round(sc,4),trn,round(o*fp,2)))
res.sort(reverse=True)
for r in res[:12]: print(r)
