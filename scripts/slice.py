import soundfile as sf, sys
y,sr=sf.read('work/stems/lead.wav')
for n,(a,b) in {'A1':(4.6,15.6),'A2':(15.6,24.6),'B1':(24.6,34.9),'B2':(34.9,47)}.items(): sf.write(f'work/stems/q_{n}.wav',y[int(a*sr):int(b*sr)],sr)
