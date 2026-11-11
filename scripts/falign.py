import torch, torchaudio, json, sys, re, numpy as np, soundfile as sf, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'scripts'); from lyrics import SUNG, parse
idx=json.load(open('work/clips/index.json'))
y,sr=sf.read('work/clips/dm/htdemucs_ft/all_raw/vocals.wav'); y=y.mean(1).astype(np.float32)
b=torchaudio.pipelines.WAV2VEC2_ASR_LARGE_LV60K_960H if len(sys.argv)>1 else torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model=b.get_model().cuda().eval(); labels=b.get_labels(); L={c:i for i,c in enumerate(labels)}
def viterbi(em, toks, blank=0):
    T,C=em.shape; N=len(toks)
    ext=[blank]
    for t in toks: ext+=[t,blank]
    S=len(ext); NEG=-1e30
    dp=np.full((T,S),NEG); bp=np.zeros((T,S),np.int8)
    dp[0,0]=em[0,ext[0]]; dp[0,1]=em[0,ext[1]]
    for t in range(1,T):
        for s in range(S):
            c=[dp[t-1,s], dp[t-1,s-1] if s>0 else NEG, dp[t-1,s-2] if s>1 and ext[s]!=blank and ext[s]!=ext[s-2] else NEG]
            k=int(np.argmax(c)); dp[t,s]=c[k]+em[t,ext[s]]; bp[t,s]=k
    s=S-1 if dp[T-1,S-1]>dp[T-1,S-2] else S-2
    path=[]
    for t in range(T-1,-1,-1):
        path.append(s); s-=bp[t,s]
    path=path[::-1]
    spans=[[None,None] for _ in toks]
    for t,s in enumerate(path):
        if s%2==1:
            i=s//2
            if spans[i][0] is None: spans[i][0]=t
            spans[i][1]=t+1
    return spans
out={}
for cid,spk,a,bb,text in SUNG:
    m=idx[cid]; s0=int((m['pos']+m['pad']-0.12)*sr); s1=int((m['pos']+m['dur']-m['pad']+0.12)*sr)
    off=m['pad']-0.12
    x=torch.tensor(y[s0:s1])[None]
    x=torchaudio.functional.resample(x,sr,16000)
    x=x/(x.abs().max()+1e-6)*0.8
    with torch.inference_mode(): em,_=model(x.cuda())
    em=torch.log_softmax(em[0],-1).cpu().numpy()
    syls=[]; toks=[]
    for it in parse(text):
        if it[0]!='syl': continue
        _,sy,new_word,same=it
        if new_word and toks: toks.append(L['|'])
        chars=[c for c in sy.upper() if c in L]
        syls.append((sy,len(toks),len(toks)+len(chars))); toks+=[L[c] for c in chars]
    spans=viterbi(em,toks)
    ft=x.shape[1]/16000/em.shape[0]
    res=[]
    for sy,i0,i1 in syls:
        st=spans[i0][0]*ft+off; en=spans[i1-1][1]*ft+off
        # first vowel char time
        vi=next((k for k in range(i0,i1) if labels[toks[k]] in 'AEIOUY'),i0)
        res.append(dict(syl=sy,start=round(st,3),end=round(en,3),vowel=round(spans[vi][0]*ft+off,3)))
    out[cid]=res
    print(cid,' '.join(f"{r['syl']}[{r['start']:.2f}-{r['end']:.2f}]" for r in res))
json.dump(out,open('work/clips/align.json','w'),indent=1)
