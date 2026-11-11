import numpy as np, librosa, mido, warnings
warnings.filterwarnings('ignore')
mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
tpb=96; spb=0.344828; sr=22050; hop=64; fps=sr/hop
on=[]
for tr in mid.tracks:
    if tr.name not in('Drum kit','bass','Piano 2'): continue
    tt=0
    for m in tr:
        tt+=m.time
        if m.type=='note_on' and m.velocity>0: on.append(tt/tpb*spb)
on=np.array(on); T=int(66*fps); tmpl=np.zeros(T)
for o in on: tmpl[int(o*fps)]+=1
tmpl=np.convolve(tmpl,np.hanning(9),'same')
for name in ['src/orig.wav','src/offvocal.wav']:
    y,_=librosa.load(name,sr=sr,mono=True)
    env=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
    env=env/env.max()
    best=[]
    for o in range(0,len(env)-T):
        pass
    cc=np.correlate(env,tmpl,'valid')
    idx=np.argsort(cc)[::-1]
    seen=[]
    for i in idx:
        if all(abs(i-j)>fps*0.3 for j in seen):
            seen.append(i)
            if len(seen)>=5: break
    print(name,[(round(i/fps,3),round(float(cc[i]),1)) for i in seen], 'len',round(len(y)/sr,2))
