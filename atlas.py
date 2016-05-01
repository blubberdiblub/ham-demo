#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma


def load_premultiplied(fname, format=None):
    img = mpimg.imread(fname, format=format)

    if img.ndim == 2:
        return np.dstack((img,) * 3 + (np.ones_like(img),))

    if img.ndim != 3:
        raise Exception("wrong number of image dimensions")

    if img.shape[-1] == 3:
        return np.dstack((img, np.ones_like(img[..., 0])))

    if img.shape[-1] != 4:
        raise Exception("wrong number of image channels")

    img[..., :3] *= img[..., 3:4]
    return img


def save_premultiplied(fname, img, format=None):
    arr = img.copy()
    arr[..., :3] /= arr[..., 3:4]
    mpimg.imsave(fname, arr, format=format)


def blit(dst, src, dst_x=0, dst_y=0):
    x1 = max(dst_x, 0)
    y1 = max(dst_y, 0)
    xoff = x1 - dst_x
    yoff = y1 - dst_y
    w = src.shape[1] - xoff
    h = src.shape[0] - yoff
    x2 = min(x1 + w, dst.shape[1])
    y2 = min(y1 + h, dst.shape[0])
    w = x2 - x1
    h = y2 - y1

    if w <= 0 or h <= 0:
        return

    src = src[yoff:yoff+h, xoff:xoff+w]
    dst[y1:y2, x1:x2] = dst[y1:y2, x1:x2] * (1 - src[..., 3:4]) + src


# 1.0 * (1 - 1.0) + 1.0 = 0.0  + 1.0 = 1.0
# 0.3 * (1 - 1.0) + 1.0 = 0.0  + 1.0 = 1.0
# 0.0 * (1 - 1.0) + 1.0 = 0.0  + 1.0 = 1.0

# 1.0 * (1 - 0.6) + 0.6 = 0.4  + 0.6 = 1.0
# 0.3 * (1 - 0.6) + 0.6 = 0.12 + 0.6 = 0.72
# 0.0 * (1 - 0.6) + 0.6 = 0.0  + 0.6 = 0.6

# 1.0 * (1 - 0.0) + 0.0 = 1.0  + 0.0 = 1.0
# 0.3 * (1 - 0.0) + 0.0 = 0.3  + 0.0 = 0.3
# 0.0 * (1 - 0.0) + 0.0 = 0.0  + 0.0 = 0.0


atlas = np.zeros((400, 320, 4), dtype=np.float32)

background = load_premultiplied('generated/background.png')
vehicles = [load_premultiplied('generated/vehicle%02d.png' % (i,))
            for i in range(16)]

blit(atlas, background, 0, 0)

for y in range(4):
    for x in range(4):
        blit(atlas, vehicles[15-x*4-y], x * 64 + y * 24 - 4, y * 50 + 200)

save_premultiplied('generated/atlas.png', atlas)
