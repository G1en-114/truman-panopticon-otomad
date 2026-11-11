import soundfile as sf, numpy as np, sys, os, json
sys.path.insert(0,'scripts'); from lyrics import SUNG, SPOKEN
PAD=0.75; GAP=0.5
os.makedirs('work/clips',exist_ok=True)
f=sf.SoundFile('src/movie.wav'); sr=f.samplerate
parts=[]; index={}; pos=0
for item in SUNG+SPOKEN:
    cid,spk,a,b=item[0],item[1],item[2],item[3]
    s=int((a-PAD)*sr); e=int((b+PAD)*sr)
    f.seek(s); x=f.read(e-s)
    index[cid]=dict(pos=pos/sr,dur=(e-s)/sr,src_a=a,src_b=b,pad=PAD,spk=spk,text=item[4])
    parts+=[x,np.zeros((int(GAP*sr),2))]; pos+=len(x)+int(GAP*sr)
y=np.concatenate(parts); sf.write('work/clips/all_raw.wav',y,sr)
json.dump(index,open('work/clips/index.json','w'),indent=1,ensure_ascii=False)
print(len(index),'clips',round(len(y)/sr,1),'s')
