import numpy as np, librosa, mido, sys
mid = mido.MidiFile('【音MAD用】圆形监狱（Panopticon）.mid')
tpb = mid.ticks_per_beat; spb = 0.344828
hop = 512; sr = 22050
fps = sr/hop
T = int(mid.length*fps)+10
C = np.zeros((12,T))
for tr in mid.tracks:
    if tr.name=='Drum kit': continue
    t=0; on={}
    for m in tr:
        t+=m.time
        if m.type=='note_on' and m.velocity>0: on[m.note]=t
        elif m.type in('note_off','note_on') and m.note in on:
            a=on.pop(m.note); s=int(a/tpb*spb*fps); e=max(s+1,int(t/tpb*spb*fps))
            C[m.note%12,s:e]+=1
C/= (np.linalg.norm(C,axis=0,keepdims=True)+1e-9)
for name in ['src/orig.wav','src/offvocal.wav']:
    y,_=librosa.load(name,sr=sr,mono=True)
    tempo,_=librosa.beat.beat_track(y=y,sr=sr,hop_length=hop)
    ch=librosa.feature.chroma_cqt(y=y,sr=sr,hop_length=hop)
    ch/= (np.linalg.norm(ch,axis=0,keepdims=True)+1e-9)
    best=[]
    for tr in range(12):
        c2=np.roll(C,tr,axis=0)
        n=ch.shape[1]-T
        sc=[ (ch[:,o:o+T]*c2).sum()/T for o in range(0,max(1,n),2)]
        o=int(np.argmax(sc)); best.append((max(sc),tr,o*2/fps))
    best.sort(reverse=True)
    print(name,'dur',round(len(y)/sr,1),'tempo',tempo,'top:',[(round(a,3),b,round(c,2)) for a,b,c in best[:4]])
