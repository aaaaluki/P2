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

PLOT = True
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
    file = open(filename, 'w')
    file.write('{},{},{}\n'.format(na1, na2, na1*na2))

    Z = np.zeros((na2, na1))
    for i in range(na1):
        for j in range(na2):
            result = None
            while result is None:
                result = f(alpha1[i], alpha2[j])

            Z[j][i] = result['total']

            file.write('{},{},{}\n'.format(alpha1[i], alpha2[j], Z[j][i]))

            bar.next()
    bar.finish()
    file.close()

    # Plot the surface.
    X, Y = np.meshgrid(alpha1, alpha2)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis,
                        linewidth=0, antialiased=False)

    ax.zaxis.set_major_formatter('{x:.02f}')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.xlabel('Alpha 1')
    plt.ylabel('Alpha 2')

    # Find maximum
    ind = np.unravel_index(np.argmax(Z, axis=None), Z.shape)
    alpha1_max = X[0][ind[0]]
    alpha2_max = Y[ind[1]][0]
    val_max = Z[ind[1]][ind[0]]
    print('Max value: {} -> alpha1: {}, alpha2: {}'.format(val_max, alpha1_max, alpha2_max))
    
    plt.show()

    return Z


def main(alpha1, alpha2) -> None:
    n = len(alpha1)*len(alpha2)
    best_alphas = []
    best_result = {'total':0.0}

    bar = Bar('Progress', fill='#', suffix='%(percent).2f%% - elapsed:%(elapsed)ds  eta:%(eta)ds',
                max=n)

    errors = 0
    for a1 in alpha1:
        for a2 in alpha2:
            bar.next()

            result = None
            while result is None:
                result = f(a1, a2)

            if result['total'] > best_result['total']:
                best_alphas = [a1, a2]
                best_result = result
            
    bar.finish()

    print('errors: {} -> {}%'.format(errors, 100*errors/n))
    print('alpha1 = {:.4f}'.format(best_alphas[0]))
    print('alpha2 = {:.4f}'.format(best_alphas[1]))
    print_results(result)


if __name__ == '__main__':
    alpha1 = np.linspace(-10, 10, num=10)
    alpha2 = np.linspace(0, 40, num=10)

    if PLOT:
        plot(alpha1, alpha2)
    else:
        main(alpha1, alpha2)
