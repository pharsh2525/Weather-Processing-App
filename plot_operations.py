"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 30 November 2023
 Project: Weather Processing App
"""

import matplotlib.pyplot as plt
import numpy as np


class PlotOperations:

    # fake up some data
    spread = np.random.rand(50) * 100
    center = np.ones(25) * 50
    flier_high = np.random.rand(10) * 100 + 100
    flier_low = np.random.rand(10) * -100
    data = np.concatenate((spread, center, flier_high, flier_low), 0)

    # don't show outlier points
    plt.figure()
    plt.boxplot(data, False, '')
    plt.boxplot(data, False, '')
    plt.boxplot(data, False, '')
    plt.boxplot(data, False, '')

    plt.show()
