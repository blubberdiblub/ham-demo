#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import math
import numpy as np


VELOCITIES = np.array([
    (1,                         0),
    (np.sqrt(1/2+np.sqrt(1/8)), np.sqrt(1/6-np.sqrt(1/72))),
    (np.sqrt(1/2),              np.sqrt(1/6)),
    (np.sqrt(1/2-np.sqrt(1/8)), np.sqrt(1/6+np.sqrt(1/72))),
    (0,                         np.sqrt(1/3))
])

VELOCITIES.flags.writeable = False

assert np.allclose(np.square(VELOCITIES * [1, np.sqrt(3)]).sum(axis=1), 1)


def distance(velocities):
    rounded = velocities.round()
    delta = velocities - rounded
    squared = np.square(delta)
    return math.fsum(squared.flat)


# def distance(velocities):
#     rounded = (velocities + 0.5).round() - 0.5
#     delta = velocities - rounded
#     processed = 1 / (np.square(delta) + 1)
#     return processed.sum()


def main():
    last_q = 0 / 1000000
    last_d = distance(VELOCITIES * last_q)
    improving = False

    for i in range(1, 6000001):
        q = i / 1000000
        d = distance(VELOCITIES * q)

        if d < last_d:
            if not improving:
                improving = True
        elif d > last_d:
            if improving:
                improving = False
                print("%.6f: %.7g" % (last_q, last_d))

        last_q = q
        last_d = d


if __name__ == '__main__':
    main()
