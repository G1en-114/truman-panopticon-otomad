"""contact sheet of cut-outs over green, to judge mattes.  usage: cutcheck.py [glob]"""
import cv2, numpy as np, glob, os, sys
fs = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else 'assets/cut/*.png'))
tiles = []
for f in fs:
    im = cv2.imread(f, cv2.IMREAD_UNCHANGED); h, w = im.shape[:2]; s = 200 / max(h, w)
    im = cv2.resize(im, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA)
    bg = np.full((210, 210, 3), (90, 170, 90), np.uint8)
    a = im[:, :, 3:] / 255.0; y0 = (210 - im.shape[0]) // 2; x0 = (210 - im.shape[1]) // 2
    reg = bg[y0:y0 + im.shape[0], x0:x0 + im.shape[1]]
    reg[:] = (im[:, :, :3] * a + reg * (1 - a)).astype(np.uint8)
    cv2.putText(bg, os.path.basename(f)[:-4], (3, 205), 0, 0.4, (0, 0, 0), 1)
    tiles.append(bg)
while len(tiles) % 9: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite('work/cut_check.jpg', np.vstack([np.hstack(tiles[i:i + 9]) for i in range(0, len(tiles), 9)]))
