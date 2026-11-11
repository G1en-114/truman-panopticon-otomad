import numpy as np, librosa, pyworld as pw, warnings, sys, cv2
warnings.filterwarnings('ignore')
def analyze(path, out, t0=0, dur=None):
    y,sr = librosa.load(path,sr=16000,mono=True,offset=t0,duration=dur)
    fp=0.005
    f0,t = pw.harvest(y.astype(np.float64),sr,frame_period=fp*1000,f0_floor=70,f0_ceil=900)
    rms = librosa.feature.rms(y=y,frame_length=400,hop_length=80)[0]
    n=min(len(f0),len(rms)); f0=f0[:n].copy(); rms=rms[:n]
    f0[rms<0.012]=0
    v=f0>0
    midi=69+12*np.log2(np.maximum(f0,1)/440)
    dev=np.abs(midi-np.round(midi))[v]
    # stability: local std over 60ms
    st=[]
    w=12
    for i in range(0,n-w,w):
        seg=midi[i:i+w]
        if (f0[i:i+w]>0).all(): st.append(seg.std())
    st=np.array(st)
    print(path.split('/')[-2], 'voiced%%=%.2f within25c=%.2f flat(<0.15st)=%.2f median midi=%.1f p5-p95=%.1f..%.1f'%(v.mean(),(dev<0.25).mean(),(st<0.15).mean(),np.median(midi[v]),np.percentile(midi[v],5),np.percentile(midi[v],95)))
    # plot
    W=min(n,6000); H=480; img=np.full((H,W,3),255,np.uint8)
    lo,hi=40,84
    for s in range(lo,hi+1):
        yy=int(H-(s-lo)/(hi-lo)*H); cv2.line(img,(0,yy),(W,yy),(225,225,225) if s%12 else (150,150,255),1)
    for i in range(W):
        if f0[i]>0:
            yy=int(H-(midi[i]-lo)/(hi-lo)*H)
            if 0<=yy<H: img[max(0,yy-1):yy+2,i]=(0,0,0)
    img=cv2.resize(img,(1500,H),interpolation=cv2.INTER_AREA)
    cv2.imwrite(out,img)
analyze('work/demucs/htdemucs/phony/vocals.wav','work/f0_phony.png',30,30)
analyze('work/demucs/htdemucs/BV1pQvfBxEjH/vocals.wav','work/f0_otl.png',5,30)
analyze('work/demucs/htdemucs/BV1iME1zJEUH/vocals.wav','work/f0_edi.png',5,30)
analyze('work/demucs/htdemucs/BV1TvfbYUE8m/vocals.wav','work/f0_ark.png',10,30)
