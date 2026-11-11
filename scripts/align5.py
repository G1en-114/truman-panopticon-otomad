import numpy as np, librosa, mido, warnings
warnings.filterwarnings('ignore')
mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
tpb=96; spb=0.344828; sr=11025; hop=64; fps=sr/hop
def notes(name):
    out=[]
    for tr in mid.tracks:
        if tr.name!=name: continue
        tt=0; on={}
        for m in tr:
            tt+=m.time
            if m.type=='note_on' and m.velocity>0: on[m.note]=tt
            elif m.type in('note_off','note_on') and m.note in on: out.append((on.pop(m.note)/tpb*spb,tt/tpb*spb,m.note))
    return out
ns=notes('bass')
T=int(65*fps); R=np.zeros((12,T))
for a,b,p in ns: R[p%12,int(a*fps):int(b*fps)]=1
y,_=librosa.load('src/offvocal.wav',sr=sr,mono=True)
C=np.abs(librosa.cqt(y,sr=sr,hop_length=hop,fmin=librosa.note_to_hz('C1'),n_bins=36,bins_per_octave=12))
ch=C[:12]+C[12:24]+C[24:36]
ch=ch/(ch.sum(0,keepdims=True)+1e-9)
sc=np.array([ (ch[:,o:o+T]*R).sum()/R.sum() for o in range(0,ch.shape[1]-T,2)])
idx=np.argsort(sc)[::-1]; seen=[]
for i in idx:
    if all(abs(i-j)>fps*0.25 for j in seen):
        seen.append(i)
        if len(seen)>=8: break
print([(round(i*2/fps,3),round(float(sc[i]),4)) for i in seen])
print('mean',sc.mean())
