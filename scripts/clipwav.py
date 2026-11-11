import soundfile as sf, json, sys
idx=json.load(open('work/clips/index.json'))
y,sr=sf.read('work/clips/dm/htdemucs_ft/all_raw/vocals.wav')
for cid in sys.argv[1:]:
    m=idx[cid]; sf.write(f'work/clips/{cid}.wav', y[int((m["pos"]+m["pad"]-0.1)*sr):int((m["pos"]+m["dur"]-m["pad"]+0.1)*sr)], sr)
