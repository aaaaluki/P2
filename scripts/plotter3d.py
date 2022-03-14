#!/usr/bin/env python

import sys
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

# Constants
SAVE_IMAGE = False


# Formated info message
def info(msg: str) -> None:
    print('\033[0;32m[INFO]\033[0m {}'.format(msg))


# Formated error message and exit with error
def error(msg: str) -> None:
    print('\033[1;91m[ERROR]\033[0m {}'.format(msg))
    usage()
    sys.exit(1)


# Prints explains how to use the script, kinda...
def usage() -> None:
    print('Usage: python {} [csv_file ...]'.format(sys.argv[0]))


# Parse given arguments and set settings (command, filename)
def setup(args: List[str]) -> List[str]:
    if len(args) < 2:
        error('CSV file needed for plotting!')

    if args[1] == 'help':
        usage()
        return None

    return args[1:]


# Plot data from csv file
def plotter(filename: str) -> None:
    if filename.endswith('.csv'):
        separator_char = ','
    else:
        # Let's suppose it's a TSV file
        separator_char = '\t'

    info('Plotting data from {}'.format(filename))

    with open(filename, 'r') as file:
        # Get data
        lines = file.readlines()
        smth = lines[0].strip()

        try:
            counts = [int(c) for c in smth.split(separator_char)]
        except:
            error('The title is wrong: {}'.format(smth))

        if len(counts) < 3:
            error('There are not 3 columns!')
        elif counts[0] * counts[1] != counts[2] or counts[2] != len(lines) - 1:
            error('The title is wrong: "{}"'.format(smth))

        X = np.zeros((counts[0]))
        Y = np.zeros((counts[1]))
        Z = np.zeros((counts[1], counts[0]))
        

        x_idx = 0
        y_idx = 0
        for l in lines[1:]:
            nums = [float(n) for n in l.strip().split(separator_char)]

            X[x_idx] = nums[0]
            Y[y_idx] = nums[1]
            Z[y_idx][x_idx] = nums[2]

            # Smth with indices
            y_idx += 1
            if y_idx == counts[1]:
                x_idx = (x_idx + 1) % counts[0]
                y_idx = 0
    
    # Plot data
    X, Y = np.meshgrid(X, Y)

    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, linewidth=0,
            antialiased=False)

    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.xlabel('x')
    plt.ylabel('y')

    # Show max value
    ind = np.unravel_index(np.argmax(Z, axis=None), Z.shape)
    x_max = X[0][ind[0]]
    y_max = Y[ind[1]][0]
    z_max = Z[ind[1]][ind[0]]
    info('Max value (x,y,z) = ({}, {}, {})'.format(x_max, y_max, z_max))

    # Save plot to PNG file
    if SAVE_IMAGE:
        idx = filename.rfind('.')
        savefile ='{}.png'.format(filename[:idx])
        plt.savefig(savefile, dpi=300)
        info('Plot saved as {}'.format(savefile))


# Main
def main(args: List[str]) -> None:
    for file in args:
        plotter(file)
    plt.show()


if __name__ == '__main__':
    args = setup(sys.argv)
    if args is None:
        sys.exit(0)

    main(args)
    sys.exit(0)
