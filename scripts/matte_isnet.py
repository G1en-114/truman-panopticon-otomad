"""IS-Net matting on GPU (run with ~/.venvs/ml/bin/python: onnxruntime-gpu + PIL, no cv2).
   usage: matte_isnet.py <in_dir> <out_dir>   : every *.png/*.jpg in in_dir -> RGBA png in out_dir"""
import os, sys, glob
import numpy as np
from PIL import Image
import onnxruntime as ort

MODEL = os.path.expanduser('~/.rembg/models/isnet-general-use/isnet-general-use.onnx')
if not os.path.exists(MODEL):
    MODEL = glob.glob(os.path.expanduser('~/.rembg/models/isnet-general-use/*.onnx'))[0]
sess = ort.InferenceSession(MODEL, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
inp = sess.get_inputs()[0].name
print('providers', sess.get_providers(), flush=True)

def matte(im):
    rgb = im.convert('RGB')
    x = np.asarray(rgb.resize((1024, 1024), Image.BILINEAR), np.float32) / 255.0
    x = (x - 0.5) / 1.0
    x = x.transpose(2, 0, 1)[None]
    pred = sess.run(None, {inp: x})[0][0, 0]
    pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
    a = Image.fromarray((pred * 255).astype(np.uint8)).resize(rgb.size, Image.BILINEAR)
    out = rgb.copy(); out.putalpha(a)
    return out

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
fs = sorted(glob.glob(os.path.join(src, '*.png')) + glob.glob(os.path.join(src, '*.jpg')))
for f in fs:
    matte(Image.open(f)).save(os.path.join(dst, os.path.splitext(os.path.basename(f))[0] + '.png'))
print('matted', len(fs), flush=True)
