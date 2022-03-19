#!/usr/bin/python3
#-*- coding:utf-8 -*-

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from progress.bar import Bar

PLOT = False
SAVE_DATA = False
TO_OPTIMIZE = 'total'
N_SAMPLES = 11
N_ITERS = 3

DIR = Path(os.path.realpath(__file__)).parent.parent.absolute()
CMD = DIR.as_posix() + '/scripts/run_vad_opt.sh'
T_EXEC = 0.22    # Machine dependant (in seconds)

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
    alpha1_range = alpha1[alpha1_max_idx - 1], alpha1[alpha1_max_idx + 1]
    alpha2_range = alpha2[alpha2_max_idx - 1], alpha2[alpha2_max_idx + 1]
    alphas_range = (alpha1_range, alpha2_range)

    print('Max value: {:.4f} % -> alpha1: {:.4f}, alpha2: {:.4f}'.format(val_max, alpha1[alpha1_max_idx], alpha2[alpha2_max_idx]))
    print('Alpha1 Range: {:.4f} - {:.4f}'.format(alpha1_range[0], alpha1_range[1]))
    print('Alpha2 Range: {:.4f} - {:.4f}'.format(alpha2_range[0], alpha2_range[1]))

    if PLOT:
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

    return alphas_range


if __name__ == '__main__':
    alpha1 = np.linspace(0, 10, num=N_SAMPLES)
    alpha2 = np.linspace(0, 20, num=N_SAMPLES)

    nIters = N_ITERS
    if len(sys.argv) > 1:
        nIters = int(sys.argv[1])

    print('Time estimation: {:.2f} s'.format(T_EXEC* N_SAMPLES*N_SAMPLES*nIters))

    for i in range(nIters):
        print('Iteration {}/{}'.format(i, nIters))

        alphas_range = plot(alpha1, alpha2)
        
        alpha1 = np.linspace((alphas_range[0][0]), (alphas_range[0][1]), num=N_SAMPLES)
        alpha2 = np.linspace((alphas_range[1][0]), (alphas_range[1][1]), num=N_SAMPLES)
