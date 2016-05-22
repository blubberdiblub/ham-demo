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

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont


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


def blit(dst, src, dst_x=0, dst_y=0, mask=None, op=np.logical_and):
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

    clipped = src[yoff:yoff + h, xoff:xoff + w]

    if ma.is_masked(clipped):
        where = ma.where if ma.isMaskedArray(dst) else np.where
        dst[y1:y2, x1:x2] = where(ma.getmaskarray(clipped),
                                  dst[y1:y2, x1:x2], clipped)
    else:
        dst[y1:y2, x1:x2] = clipped

    if mask is None:
        return

    if not isinstance(mask, np.ndarray) or mask.ndim < 2:
        result = np.empty_like(dst, dtype=np.bool_)
        result[:, :] = mask
        mask = result

    result = np.empty_like(dst, dtype=np.bool_)
    result[:, :] = op(mask, True)
    result[y1:y2, x1:x2] = op(mask[yoff:yoff + h, xoff:xoff + w],
                              ma.getmask(clipped))

    return result


def render(canvas, palette, vehicle=None, position=(0, 0)):
    if vehicle is not None:
        canvas = canvas.copy()
        blit(canvas, vehicle,
             dst_x=int(round(position[0])),
             dst_y=int(round(position[1])))

    rgb8 = Image.fromarray(from_ham6(canvas, palette, background=0))
    return rgb8.resize((rgb8.width * 2, rgb8.height * 2),
                       resample=Image.NEAREST)


def ham6_to_image(ham6, palette, background=None):
    image = Image.fromarray(from_ham6(ham6, palette, background=background))
    return image.resize((image.width * 2, image.height * 2),
                        resample=Image.NEAREST)


def highest_contrast(reference, choice=((0, 0, 0), (255, 255, 255))):
    reference = np.asanyarray(reference)
    max_dist = None
    best_color = None

    for color in choice:
        d = color_distance(reference, np.asanyarray(color))
        if max_dist is None or d > max_dist:
            max_dist = d
            best_color = color

    return best_color


def render_zoom(canvas, src_box, dst_box, ham6, cmp6, mask,
                palette, background=None,
                t=1, color=(255, 255, 255),
                title_font=None, plain_font=None, spacing=0):
    src_x, src_y, src_r, src_b = src_box
    src_w = src_r - src_x
    src_h = src_b - src_y

    dst_x, dst_y, dst_r, dst_b = dst_box
    dst_w = dst_r - dst_x
    dst_h = dst_b - dst_y

    box_w = dst_w / src_w
    box_h = dst_h / src_h

    canvas = canvas.copy()
    ratio_x = canvas.width / ham6.shape[1]
    ratio_y = canvas.height / ham6.shape[0]
    crop_box = (int(round(src_x * ratio_x)),
                int(round(src_y * ratio_y)),
                int(round(src_r * ratio_x)),
                int(round(src_b * ratio_y)))
    crop = canvas.crop(crop_box)
    zoom = crop.resize((dst_w, dst_h), resample=Image.NEAREST)

    if plain_font is None:
        plain_font = ImageFont.load_default()
    if title_font is None:
        title_font = plain_font

    draw = ImageDraw.Draw(zoom, 'RGBA')

    real = from_ham6(ham6[src_y:src_b, :src_r], palette, background=background)
    real = real[:, src_x:]

    cmp = from_ham6(cmp6[src_y:src_b, :src_r], palette, background=background)
    cmp = cmp[:, src_x:]

    ascender, descender = title_font.getmetrics()
    title_height = ascender + descender
    ascender, descender = plain_font.getmetrics()
    plain_height = ascender + descender
    empty_height = box_h - title_height - plain_height * 3 - spacing * 2
    title_y = empty_height / 3
    plain_y = empty_height * 2 / 3 + title_height

    for i in range(src_h):
        y = i + src_y
        box_y = i * box_h
        for j in range(src_w):
            x = j + src_x
            box_x = j * box_w

            src_value = ham6[y, x]
            dst_color = real[i, j]

            if mask is not None and not mask[y, x]:
                title = 'Blit'
                title_colors = (
                    (0xFF, 0x00, 0x00),
                    (0xFF, 0x55, 0x55),
                )
            elif np.array_equiv(cmp[i, j], dst_color):
                title = 'OK'
                title_colors = (
                    (0x00, 0xFF, 0x00),
                    (0x00, 0xAA, 0x00),
                )
            else:
                title = 'bleeding'
                title_colors = (
                    (0xFF, 0x00, 0xFF),
                    (0xFF, 0xAA, 0x00),
                )

            lines = [
                "Value $%02X" % (src_value,),
                (
                    "⇒ Pal. #%d",
                    "Blue ⇒ $%X",
                    "Red ⇒ $%X",
                    "Green ⇒ $%X",
                )[src_value >> 4] % (src_value & 0xF,),
                "Color $%X%X%X" % tuple(value >> 4 for value in dst_color),
            ]

            contrast = highest_contrast(dst_color, title_colors)
            w = draw.textsize(title, font=title_font)[0]
            draw.text((box_x + (box_w - w) / 2, box_y + title_y), title,
                      fill=contrast, font=title_font)

            contrast = highest_contrast(dst_color, ((0x66, 0x66, 0x66),
                                                    (0xFF, 0xFF, 0xFF)))
            for row, line in enumerate(lines):
                w = draw.textsize(line, font=plain_font)[0]
                draw.text((box_x + (box_w - w) / 2,
                           box_y + plain_y + row * (plain_height + spacing)),
                          line, fill=contrast, font=plain_font)

    x1 = int(round(crop_box[0] * (1 - t) + dst_x * t))
    y1 = int(round(crop_box[1] * (1 - t) + dst_y * t))
    x2 = int(round(crop_box[2] * (1 - t) + dst_r * t))
    y2 = int(round(crop_box[3] * (1 - t) + dst_b * t))
    zoom = zoom.resize((x2 - x1, y2 - y1), resample=Image.NEAREST)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((crop_box[0] - 0.5, crop_box[1] - 0.5,
                    crop_box[2] + 0.5, crop_box[3] + 0.5),
                   outline=color)
    draw.rectangle((x1 - 0.5, y1 - 0.5, x2 + 0.5, y2 + 0.5),
                   outline=color)
    draw.line((crop_box[0] - 0.5, crop_box[1] - 0.5, x1 - 0.5, y1 - 0.5),
              fill=color)
    draw.line((crop_box[2] + 0.5, crop_box[1] - 0.5, x2 + 0.5, y1 - 0.5),
              fill=color)
    draw.line((crop_box[0] - 0.5, crop_box[3] + 0.5, x1 - 0.5, y2 + 0.5),
              fill=color)
    draw.line((crop_box[2] + 0.5, crop_box[3] + 0.5, x2 + 0.5, y2 + 0.5),
              fill=color)

    canvas.paste(zoom, (x1, y1))
    return canvas


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
        ( 9, 16, 0),
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
    fig.figimage(ham6_to_image(background, palette, background=0))
    plt.show(block=False)

    title_font = ImageFont.truetype('DejaVuSansCondensed-Bold', 13)
    plain_font = ImageFont.truetype('DejaVuSansCondensed', 12)

    file_name = ('generated/frame%03d.png' % (i,) for i in itertools.count())

    def render_frame(period=1):
        counter = 0
        while True:
            yield counter < 1
            counter = (counter + 1) % period

    frame_skip = render_frame(period=1)

    position = np.array((-56.0, 20.0))
    p1 = position.copy()

    for direction, steps, speed in script:
        for step in range(steps):
            x, y = position
            if speed > 0:
                position += velocities[direction] * speed

            fname = next(file_name)
            if not next(frame_skip):
                continue

            ham6 = background.copy()
            if speed <= 0 and 6 <= step <= steps - 6 and not ((step - 6) & 1):
                mask = None
            else:
                mask = blit(ham6, vehicles[direction],
                            dst_x=int(round(x)),
                            dst_y=int(round(y)),
                            mask=True if speed <= 0 else None)

            image = ham6_to_image(ham6, palette, background=0)

            if speed <= 0:
                if step < 5:
                    t = step / 5
                elif step > steps - 5:
                    t = (steps - step) / 5
                else:
                    t = 1.0

                image = render_zoom(image,
                                    (100, 100, 104, 101),
                                    (240, 150, 496, 214),
                                    ham6, background, mask,
                                    palette, background=0,
                                    t=t, color=(0x66, 0x77, 0xFF),
                                    title_font=title_font,
                                    plain_font=plain_font)

            image.save(fp=fname)

            fig.clf()
            fig.figimage(image)
            fig.canvas.draw()

    fname = next(file_name)
    if next(frame_skip):
        image = ham6_to_image(background, palette, background=0)
        image.save(fp=fname)

        fig.clf()
        fig.figimage(image)
        fig.canvas.draw()

    p2 = position.copy()
    print("position = %s" % (position,))
    print("average = %s" % ((p1 + p2 + [0.0, 52.0]) / 2,))

    # plt.show(block=True)


if __name__ == '__main__':
    main()
