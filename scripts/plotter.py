#!/usr/bin/env python

import sys
from typing import List

import matplotlib.pyplot as plt
import numpy as np


# Plot all lines in the same plot or not
ONE_FOR_ALL = False


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
        # The data will be organized in columns on a numpy array, each column
        # representing a column in the csv file
        initialized = False
        for l in file.readlines():
            nums = [float(n) for n in l.strip().split(separator_char)]

            if not initialized:
                data = np.array(nums)
                initialized = True
                continue
            
            data = np.vstack((data, np.array(nums)))

    if not initialized:
        error('The file {} has no data!'.format(filename))
    
    titles = ['x'] + ['col{}'.format(i) for i in range(1, data.shape[1])]

    # Plot data
    if ONE_FOR_ALL:
        plt.title('Plot for file {}'.format(filename))
        for i in range(1, len(titles)):
            plt.plot(data[:, 0], data[:, i])
        
            plt.xlim((data[:, 0][0], data[:, 0][-1]))

            plt.xlabel(titles[0])
            plt.legend(titles[1::])
            plt.grid(which='both', color='#777777', linestyle=':', linewidth=0.5)

    else:
        fig, axs = plt.subplots(len(titles) - 1, 1)
        fig.suptitle('Plot for file {}'.format(filename))
        for i in range(1, len(titles)):
            axs[i - 1].plot(data[:, 0], data[:, i])
        
            axs[i - 1].set_xlim((data[:, 0][0], data[:, 0][-1]))

            axs[i - 1].set_xlabel(titles[0])
            axs[i - 1].set_ylabel(titles[i])
            axs[i - 1].grid(which='both', color='#777777', linestyle=':', linewidth=0.5)

        fig.tight_layout()

    # Save plot to PNG file
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
