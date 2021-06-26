'''
This plugin finds the standard deviation after doing a Gaussian fit.

In the method of Segerlund, O'Sullivan, O'Connor, 1-std of a Gaussian fit
is used as the error of the count number.
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit
from snewpdag.dag import Node

class GaussianFit(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def fit_error(self, data):
        
        mu, std = norm.fit(data)

        # (for reference below) plotting it out
        '''
        plt.hist(data, bins=25, density=True, alpha=0.6, color='g')

        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        plt.plot(x, p, 'k', linewidth=2)
        title = "Gaussian fit: $\mu$ = %.2f, $\sigma$ = %.2f" % (mu, std)
        plt.title(title)
        
        plt.show()
        '''

        return std