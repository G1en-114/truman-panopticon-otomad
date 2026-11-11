"""movie contact sheet with time labels. usage: msheet.py out.jpg cols width t1 t2 t3 ...  (or a:b:n ranges)"""
import cv2, sys, numpy as np
out=sys.argv[1]; cols=int(sys.argv[2]); w=int(sys.argv[3]); ts=[]
for a in sys.argv[4:]:
    if ':' in a:
        s,e,n=a.split(':'); ts+=list(np.linspace(float(s),float(e),int(n)))
    else: ts.append(float(a))
cap=cv2.VideoCapture('src/movie.mkv'); fps=cap.get(cv2.CAP_PROP_FPS)
ims=[]
for t in ts:
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,f=cap.read()
    if not ok: f=np.zeros((720,1280,3),np.uint8)
    f=cv2.resize(f[:600],(w,int(w*600/1280)))
    cv2.rectangle(f,(0,0),(78,16),(0,0,0),-1); cv2.putText(f,f'{t:.1f}',(2,13),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),1,cv2.LINE_AA)
    ims.append(f)
rows=[]
for i in range(0,len(ims),cols):
    r=ims[i:i+cols]; r+= [np.zeros_like(ims[0])]*(cols-len(r)); rows.append(np.hstack(r))
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,80])
