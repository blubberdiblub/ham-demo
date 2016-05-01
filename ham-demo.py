#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import collections
import itertools
import numbers
import os.path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma

from PIL import Image


def load_palette(fname, mtime=False):
    with open(fname, 'r') as f:
        n = int(f.readline(), base=0)
        palette = np.empty((n, 3), dtype=np.uint8)

        for i in range(n):
            rgb = f.readline().split(',')
            palette[i] = [int(component, base=0) for component in rgb]

    if not mtime:
        return palette

    return palette, os.path.getmtime(fname)


def load_image(fname, masked=False, format=None):
    img = mpimg.imread(fname, format=format)

    if img.ndim != 3:
        raise Exception("wrong number of image dimensions")

    if not 3 <= img.shape[-1] <= 4:
        raise Exception("wrong number of image channels")

    if np.issubdtype(img.dtype, np.floating):
        rgb = img[..., :3] * 255
        threshold = 0.5
    elif np.issubdtype(img.dtype, np.uint8):
        rgb = img[..., :3]
        threshold = 128
    else:
        raise Exception("wrong data type of image pixels")

    if not masked or img.shape[-1] < 4:
        return rgb

    return ma.masked_array(rgb, mask=np.dstack([img[..., 3] < threshold] * 3))


def load_ham6(fname, palette, background=None, mtimes=None, format=None):
    stem, __ = os.path.splitext(fname)
    fname_cache = stem + '.cache'

    masked = background is None or ma.is_masked(background)

    if mtimes is None:
        mtimes = ()
    elif not isinstance(mtimes, collections.Iterable):
        mtimes = (mtimes,)

    try:
        if os.path.exists(fname):
            mtimes = itertools.chain(mtimes, (os.path.getmtime(fname),))

        for mtime in mtimes:
            if os.path.getmtime(fname_cache) < mtime:
                raise OSError("cache file out of date")

        ham6 = np.genfromtxt(fname_cache, dtype=np.uint8,
                             missing_values=masked and '--',
                             usemask=masked, loose=False, invalid_raise=True)
    except OSError:
        rgb = load_image(fname, masked=masked, format=format)
        ham6 = to_ham6(rgb, palette, background=background)
        out = np.array(ham6, dtype=np.str_)
        if masked:
            out[ma.getmaskarray(ham6)] = '--'
        np.savetxt(fname_cache, out, fmt='%2s', delimiter=' ')

    return ham6


def color_distance(rgb1, rgb2):
    r1, g1, b1 = rgb1.tolist()
    r2, g2, b2 = rgb2.tolist()
    rmean = (r1 + r2) / 510
    return ((r2 - r1)**2 * (2 + rmean) +
            (g2 - g1)**2 * 4 +
            (b2 - b1)**2 * (3 - rmean))


def ham6_nearest(pixel, palette, last_color=None):
    if pixel is None or ma.is_masked(pixel):
        return ma.masked, ma.masked

    min_dist = None
    best_index = ma.masked
    best_color = ma.masked

    for i, c in enumerate(palette[:16]):
        d = color_distance(pixel, c)
        if min_dist is None or d < min_dist:
            if d == 0:
                return i, c
            min_dist = d
            best_index = i
            best_color = c

    if last_color is None or ma.is_masked(last_color):
        return best_index, best_color

    c = last_color.copy()

    for i in range(16):
        c[2] = i * 0x11
        d = color_distance(pixel, c)
        if d < min_dist:
            if d == 0:
                return i + 0x10, c
            min_dist = d
            best_index = i + 0x10
            best_color = c.copy()

    c = last_color.copy()

    for i in range(16):
        c[0] = i * 0x11
        d = color_distance(pixel, c)
        if d < min_dist:
            if d == 0:
                return i + 0x20, c
            min_dist = d
            best_index = i + 0x20
            best_color = c.copy()

    c = last_color.copy()

    for i in range(16):
        c[1] = i * 0x11
        d = color_distance(pixel, c)
        if d < min_dist:
            if d == 0:
                return i + 0x30, c
            min_dist = d
            best_index = i + 0x30
            best_color = c.copy()

    return best_index, best_color


def to_ham6(img, palette, background=None, out=None):
    _debug_array(img)

    if background is None:
        background = ma.masked
    elif isinstance(background, numbers.Integral):
        background = palette[background]

    if not ma.is_masked(background) and ma.isMaskedArray(img):
        img = img.filled(background)

    if ma.isMaskedArray(img):
        ham6 = ma.empty(img.shape[:2], dtype=np.uint8)
    else:
        ham6 = np.empty(img.shape[:2], dtype=np.uint8)

    for y in range(img.shape[0]):
        c = background
        for x in range(img.shape[1]):
            i, c = ham6_nearest(img[y, x], palette, c)
            ham6[y, x] = i
            if out is not None:
                out[y, x] = c

    _debug_array(ham6)
    return ham6


def from_ham6(ham6, palette, background=None):
    if background is None:
        background = ma.masked
    elif isinstance(background, numbers.Integral):
        background = palette[background]

    if ma.is_masked(background) or ma.isMaskedArray(ham6):
        rgb8 = ma.empty(ham6.shape[:2] + (3,), dtype=np.uint8)
    else:
        rgb8 = np.empty(ham6.shape[:2] + (3,), dtype=np.uint8)

    for y in range(rgb8.shape[0]):
        c = background
        for x in range(rgb8.shape[1]):
            i = ham6[y, x]
            if i is ma.masked:
                ham6[y, x] = ma.masked
                continue

            if i < 0x10:
                c = palette[i]
            else:
                c = c.copy()
                c[(None, 2, 0, 1)[i >> 4]] = (i & 0xF) * 0x11

            rgb8[y, x] = c

    return rgb8


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

    intermediate = src[yoff:yoff + h, xoff:xoff + w]

    if ma.is_masked(intermediate):
        where = ma.where if ma.isMaskedArray(dst) else np.where
        intermediate = where(ma.getmaskarray(intermediate),
                             dst[y1:y2, x1:x2], intermediate)

    dst[y1:y2, x1:x2] = intermediate


def render(canvas, palette, vehicle, position,
           fname=None, format=None, fig=None, frame_skip=None):
    render_frame = frame_skip is None or next(frame_skip)
    if not render_frame:
        return

    if not fname and not fig:
        return

    ham6 = canvas.copy()
    blit(ham6, vehicle,
         dst_x=int(round(position[0])),
         dst_y=int(round(position[1])))
    rgb8 = (from_ham6(ham6, palette, background=0)
            .repeat(2, axis=1)
            .repeat(2, axis=0))

    if fname:
        Image.fromarray(rgb8).save(fname, format=format)

    if fig is not None:
        fig.clf()
        fig.figimage(rgb8)
        fig.canvas.draw()


def _debug_array(a):
    print("%s%s: %d * %d [%d] dtype=%s" % (a.__class__.__name__, a.shape,
                                           a.size, a.itemsize, a.nbytes,
                                           a.dtype))


def main():
    palette, palette_mtime = load_palette('resources/palette.txt', mtime=True)
    palette = (palette[:16] / 0x11).round().astype(dtype=np.uint8) * 0x11
    palette.flags.writeable = False

    velocities = np.array([
        ( 0,                         -np.sqrt(1/3)),
        (-np.sqrt(1/2-np.sqrt(1/8)), -np.sqrt(1/6+np.sqrt(1/72))),
        (-np.sqrt(1/2),              -np.sqrt(1/6)),
        (-np.sqrt(1/2+np.sqrt(1/8)), -np.sqrt(1/6-np.sqrt(1/72))),
        (-1,                          0),
        (-np.sqrt(1/2+np.sqrt(1/8)),  np.sqrt(1/6-np.sqrt(1/72))),
        (-np.sqrt(1/2),               np.sqrt(1/6)),
        (-np.sqrt(1/2-np.sqrt(1/8)),  np.sqrt(1/6+np.sqrt(1/72))),
        ( 0,                          np.sqrt(1/3)),
        ( np.sqrt(1/2-np.sqrt(1/8)),  np.sqrt(1/6+np.sqrt(1/72))),
        ( np.sqrt(1/2),               np.sqrt(1/6)),
        ( np.sqrt(1/2+np.sqrt(1/8)),  np.sqrt(1/6-np.sqrt(1/72))),
        ( 1,                          0),
        ( np.sqrt(1/2+np.sqrt(1/8)), -np.sqrt(1/6-np.sqrt(1/72))),
        ( np.sqrt(1/2),              -np.sqrt(1/6)),
        ( np.sqrt(1/2-np.sqrt(1/8)), -np.sqrt(1/6+np.sqrt(1/72))),
    ]) * 3.125769299218172
    velocities.flags.writeable = False

    script = (
        (12, 11, 1),
        (11, 12, 1),
        (10, 12, 1),
        ( 9, 12, 1),
        ( 8, 12, 1),
        ( 9,  2, 1),
        ( 9, 10, 1),
        (10, 12, 1),
        (11, 12, 1),
        (12, 13, 1),
        (13, 12, 1),
        (14, 12, 1),
        (15, 12, 1),
        ( 0, 12, 1),
        ( 1, 12, 1),
        ( 2, 12, 1),
        ( 3, 12, 1),
        ( 4, 13, 1),
        ( 5, 12, 1),
        ( 6, 12, 1),
        ( 7, 12, 1),
        ( 8, 12, 1),
        ( 7, 12, 1),
        ( 6, 12, 1),
        ( 5, 12, 1),
        ( 4, 11, 1),
    )

    background = load_ham6('generated/background.png', palette, background=0,
                           mtimes=(palette_mtime,))
    background.flags.writeable = False

    vehicles = [load_ham6('generated/vehicle%02d.png' % (i,), palette,
                          mtimes=(palette_mtime,)) for i in range(16)]
    for vehicle in vehicles:
        vehicle.flags.writeable = False

    fig = plt.figure()
    fig.figimage(from_ham6(background, palette, background=0)
                 .repeat(2, axis=1).repeat(2, axis=0), resize=True)
    plt.show(block=False)

    file_name = ('generated/frame%03d.png' % (i,) for i in itertools.count())

    def render_frame(period=1):
        counter = 0
        while True:
            yield counter < 1
            counter = (counter + 1) % period

    frame_skip = render_frame(period=12)

    position = np.array((-56.0, 20.0))
    p1 = position.copy()

    for direction, steps, speed in script:
        for step in range(steps):
            render(background, palette, vehicles[direction], position,
                   fname=next(file_name), fig=fig, frame_skip=frame_skip)
            position += velocities[direction] * speed

    render(background, palette, vehicles[script[-1][0]], position,
           fname=next(file_name), fig=fig, frame_skip=frame_skip)

    p2 = position.copy()
    print("position = %s" % (position,))
    print("average = %s" % ((p1 + p2 + [0.0, 52.0]) / 2,))

    # plt.show(block=True)


if __name__ == '__main__':
    main()
