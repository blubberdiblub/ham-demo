#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import numpy as np


def load_palette(fname):
    with open(fname, 'r') as f:
        n = int(f.readline())

        palette = np.empty((n, 3), dtype=np.float32)

        for i in range(n):
            rgb = f.readline().split(',')
            palette[i] = [int(component, base=0) for component in rgb]

    palette /= 255
    return palette


def save_palette(fname, palette):
    lines = [str(len(palette))]

    for rgb in palette:
        rgb = (int(round(component * 255)) for component in rgb)
        lines.append("0x%02X,0x%02X,0x%02X" % tuple(rgb))

    with open(fname, 'w') as f:
        for line in lines:
            f.write(line + "\n")


def main():
    pal8 = load_palette('resources/palette.txt')
    pal4 = np.round(pal8 * 15) / 15
    save_palette('resources/palette.txt', pal4)


if __name__ == '__main__':
    main()
