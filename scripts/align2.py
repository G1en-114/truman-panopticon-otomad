import numpy as np, librosa, mido, pyworld as pw, soundfile as sf
mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
tpb = mid.ticks_per_beat; spb = 0.344828
fp = 0.005
y,sr = librosa.load('work/demucs/htdemucs/orig/vocals.wav',sr=16000,mono=True)
f0,t = pw.dio(y.astype(np.float64),sr,frame_period=fp*1000,f0_floor=120,f0_ceil=1000)
f0 = pw.stonemask(y.astype(np.float64),f0,t,sr)
rms = librosa.feature.rms(y=y,frame_length=400,hop_length=80)[0]
n=min(len(f0),len(rms)); f0=f0[:n]; f0[rms[:n]<0.01]=0
pc = np.where(f0>0, np.round(69+12*np.log2(np.maximum(f0,1)/440))%12, -1)
def roll(name):
    T=int(mid.length/fp)+10; r=-np.ones(T)
    for tr in mid.tracks:
        if tr.name!=name: continue
        tt=0; on={}
        for m in tr:
            tt+=m.time
            if m.type=='note_on' and m.velocity>0: on[m.note]=tt
            elif m.type in('note_off','note_on') and m.note in on:
                a=on.pop(m.note); r[int(a/tpb*spb/fp):int(tt/tpb*spb/fp)]=m.note%12
    return r
for name in ['Vocal1','Vocal2']:
    r=roll(name); act=r>=0; T=len(r)
    res=[]
    for trn in range(12):
        rr=np.where(act,(r+trn)%12,-1)
        for o in range(0,len(pc)-T,10):
            seg=pc[o:o+T]
            res.append(((seg[act]==rr[act]).mean(),trn,o*fp))
    res.sort(reverse=True)
    print(name,[(round(a,3),b,round(c,2)) for a,b,c in res[:6]])
