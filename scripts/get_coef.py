#!/usr/bin/python3
#-*- coding:utf-8 -*-

import os
import subprocess
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from progress.bar import Bar

PLOT = False
SAVE_DATA = False
TO_OPTIMIZE = 'total'
DIR = Path(os.path.realpath(__file__)).parent.parent.absolute()
CMD = DIR.as_posix() + '/scripts/run_vad_opt.sh'


def f(a1:float, a2:float) -> Dict[str, float]:
    cmd = [CMD, str(a1), str(a2)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = proc.communicate()

    lines = [l.split(';') for l in out.decode().strip().split('\n')]
    if len(lines) < 2:
        return None

    result = {}
    for k, v in zip(lines[0], lines[1]):
        result[k] = float(v)

    return result


def print_results(result: Dict[str, float]) -> None:
    for k, v in result.items():
        print('{}: {}'.format(k, v))


def plot(alpha1: np.ndarray, alpha2: np.ndarray) -> np.ndarray:
    na1 = np.shape(alpha1)[0]
    na2 = np.shape(alpha2)[0]

    bar = Bar('Progress', fill='#', suffix='%(percent).2f%% [%(elapsed)d / %(eta)d]s',
                max=na1*na2)

    filename = 'data_{}:{}:{}_{}:{}:{}.csv'.format(
        alpha1[0], alpha1[-1], len(alpha1),
        alpha2[0], alpha2[-1], len(alpha2))
    
    if SAVE_DATA:
        file = open(filename, 'w')
        file.write('{},{},{}\n'.format(na1, na2, na1*na2))

    # Vars for finding max
    alpha1_max_idx = 0
    alpha2_max_idx = 0
    val_max = 0

    Z = np.zeros((na2, na1))
    for i in range(na1):
        for j in range(na2):
            result = None
            while result is None:
                result = f(alpha1[i], alpha2[j])

            if result[TO_OPTIMIZE] > val_max:
                val_max = result[TO_OPTIMIZE]
                alpha1_max_idx = i
                alpha2_max_idx = j

            Z[j][i] = result[TO_OPTIMIZE]

            if SAVE_DATA:
                file.write('{},{},{}\n'.format(alpha1[i], alpha2[j], Z[j][i]))

            bar.next()
    bar.finish()
    if SAVE_DATA:
        file.close()

    # Show maximum
    print('Max value: {} -> alpha1: {}, alpha2: {}'.format(val_max, alpha1[alpha1_max_idx], alpha2[alpha2_max_idx]))
    print('Alpha1: {} - {}'.format(alpha1[alpha1_max_idx - 1], alpha1[alpha1_max_idx + 1]))
    print('Alpha2: {} - {}'.format(alpha2[alpha2_max_idx - 1], alpha2[alpha2_max_idx + 1]))

    if not PLOT:
        return

    # Plot the surface.
    X, Y = np.meshgrid(alpha1, alpha2)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis,
                        linewidth=0, antialiased=False)

    ax.zaxis.set_major_formatter('{x:.02f}')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.xlabel('Alpha 1')
    plt.ylabel('Alpha 2')
    
    plt.show()

    return Z


if __name__ == '__main__':
    alpha1 = np.linspace(0, 10, num=10)
    alpha2 = np.linspace(0, 10, num=10)

    plot(alpha1, alpha2)
