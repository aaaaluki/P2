#!/usr/bin/python3
#-*- coding:utf-8 -*-

import datetime
import itertools
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
from progress.bar import Bar

TO_OPTIMIZE = 'total'
N_SAMPLES = 4
N_ITERS = 3

DIR = Path(os.path.realpath(__file__)).parent.parent.absolute()
CMD = DIR.as_posix() + '/scripts/run_vad_opt.sh'
T_EXEC = 0.3    # Machine dependant (in seconds)
N_COEFS = 6

def f(a1:float, a2:float, min_v:int, min_s:int, n_init:int, gamma:float) -> Dict[str, float]:
    cmd = [CMD, str(a1), str(a2), str(min_v), str(min_s), str(n_init), str(gamma)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = proc.communicate()

    if error:
        print('[ERROR]: {}'.format(error.decode().strip()))
        exit(1)

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


def calc(alpha1: List[float], alpha2: List[float], min_v:List[int], min_s:List[int], n_init:List[int], gamma:List[int]):
    # Vars for finding max
    indices = [0, 0, 0, 0, 0, 0]
    val_max = 0

    alphas_combinations = itertools.product(alpha1, alpha2, min_v, min_s, n_init, gamma)
    bar = Bar('Progress', fill='#', suffix='%(percent).2f%% [%(elapsed)d / %(eta)d]s',
                max=N_SAMPLES ** N_COEFS)

    for coefs in alphas_combinations:
        result = None
        while result is None:
            result = f(coefs[0], coefs[1], coefs[2], coefs[3], coefs[4], coefs[5])

        if result[TO_OPTIMIZE] > val_max:
            val_max = result[TO_OPTIMIZE]
            indices[0] = alpha1.index(coefs[0])
            indices[1] = alpha2.index(coefs[1])
            indices[2] = min_v.index(coefs[2])
            indices[3] = min_s.index(coefs[3])
            indices[4] = n_init.index(coefs[4])
            indices[5] = gamma.index(coefs[5])
            print('\t Actual Max value: {:.4f} % -> a1: {:.4f}, a2: {:.4f}, minV: {:.4f}, minS: {:.4f}, nInit: {:.4f}, gamma: {:.4f}'.format(
                    val_max, coefs[0], coefs[1], coefs[2], coefs[3], coefs[4], coefs[5]))


        bar.next()
    bar.finish()

    # Show maximum
    alphas_range = ((alpha1[max(indices[0] - 1, 0)], alpha1[min(indices[0] + 1, N_SAMPLES - 1)]),
                    (alpha2[max(indices[1] - 1, 0)], alpha2[min(indices[1] + 1, N_SAMPLES - 1)]),
                    (min_v[max(indices[2] - 1, 0)],  min_v[min(indices[2] + 1, N_SAMPLES - 1)]),
                    (min_s[max(indices[3] - 1, 0)],  min_s[min(indices[3] + 1, N_SAMPLES - 1)]),
                    (n_init[max(indices[4] - 1, 0)], n_init[min(indices[4] + 1, N_SAMPLES - 1)]),
                    (gamma[max(indices[5] - 1, 0)],   gamma[min(indices[5] + 1, N_SAMPLES - 1)]))

    print('Max value: {:.4f} % -> a1: {:.4f}, a2: {:.4f}, minV: {:.4f}, minS: {:.4f}, nInit: {:.4f}, gamma: {:.4f}'.format(val_max,
            alpha1[indices[0]],
            alpha2[indices[1]],
            min_v[indices[2]],
            min_s[indices[3]],
            n_init[indices[4]],
            gamma[indices[5]]))

    print('    Alpha1 Range: {:.4f} - {:.4f}'.format(alphas_range[0][0], alphas_range[0][1]))
    print('    Alpha2 Range: {:.4f} - {:.4f}'.format(alphas_range[1][0], alphas_range[1][1]))
    print('    Min Vo Range: {:.4f} - {:.4f}'.format(alphas_range[2][0], alphas_range[2][1]))
    print('    Max Si Range: {:.4f} - {:.4f}'.format(alphas_range[3][0], alphas_range[3][1]))
    print('    N Init Range: {:.4f} - {:.4f}'.format(alphas_range[4][0], alphas_range[4][1]))
    print('    Gamma  Range: {:.4f} - {:.4f}'.format(alphas_range[5][0], alphas_range[5][1]))

    return alphas_range


if __name__ == '__main__':
    # segurament hi haura una manera mes eficient que anar fent una variable
    # per cada alfa
    alpha1 = list(np.linspace(0, 10, num=N_SAMPLES))
    alpha2 = list(np.linspace(0, 10, num=N_SAMPLES))
    min_v = list(np.linspace(0, 20, num=N_SAMPLES))
    min_s = list(np.linspace(0, 20, num=N_SAMPLES))
    n_init = list(np.linspace(0, 20, num=N_SAMPLES))
    gamma = list(np.linspace(-500, 500, num=N_SAMPLES))

    nIters = N_ITERS
    if len(sys.argv) > 1:
        nIters = int(sys.argv[1])

    print('Time estimation: {}'.format(str(datetime.timedelta(seconds=T_EXEC * nIters * N_SAMPLES**N_COEFS))))

    for i in range(nIters):
        print('Iteration {}/{}'.format(i+1, nIters))

        alphas_range = calc(alpha1, alpha2, min_v, min_s, n_init, gamma)
        
        alpha1 = list(np.linspace((alphas_range[0][0]), (alphas_range[0][1]), num=N_SAMPLES))
        alpha2 = list(np.linspace((alphas_range[1][0]), (alphas_range[1][1]), num=N_SAMPLES))
        min_v = list(np.linspace((alphas_range[2][0]), (alphas_range[2][1]), num=N_SAMPLES))
        min_s = list(np.linspace((alphas_range[3][0]), (alphas_range[3][1]), num=N_SAMPLES))
        n_init = list(np.linspace((alphas_range[4][0]), (alphas_range[4][1]), num=N_SAMPLES))
        gamma = list(np.linspace((alphas_range[5][0]), (alphas_range[5][1]), num=N_SAMPLES))
