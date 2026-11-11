import numpy as np, soundfile as sf, pyworld as pw, json, sys, warnings
warnings.filterwarnings('ignore')
tl=json.load(open('work/timeline.json')); 
y,sr=sf.read(sys.argv[1]); 
if y.ndim>1: y=y.mean(1)
f0,t=pw.harvest(y,sr,f0_floor=60,f0_ceil=900,frame_period=5.0)
errs=[];bad=[]
for tk in tl['tokens']:
    for nb,nd,p in tk['notes']:
        a=(nb+tl['pre'])*tl['spb']; b=min(tk['end'],a+nd*tl['spb'])
        seg=f0[int((a+0.03)*200):int((b-0.02)*200)]; seg=seg[seg>0]
        if len(seg)<3: bad.append((tk['syl'],'unvoiced')); continue
        m=69+12*np.log2(np.median(seg)/440); e=m-p
        errs.append(e)
        if abs(e)>0.5: bad.append((tk['syl'],round(float(e),2)))
errs=np.array(errs)
print('notes with pitch:',len(errs),'/',sum(len(t['notes']) for t in tl['tokens']),' |err|<0.3st: %.2f'%(np.abs(errs)<0.3).mean(),' median abs err %.3f'%np.median(np.abs(errs)))
print('off/unvoiced:',bad)
