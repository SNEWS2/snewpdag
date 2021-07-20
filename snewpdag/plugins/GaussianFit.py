'''
This plugin finds the mean and standard deviation after doing a Gaussian fit.
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit
from snewpdag.dag import Node

class GaussianFit(Node):
    def __init__(self, in_field, out_field, **kwargs):
        self.in_field = in_field
        self.out_field = out_field
        super().__init__(**kwargs)
    
    def alert(self, data):
        mean, std = norm.fit( data[self.in_field] )
        d = { self.out_field: (mean, std) }
        data.update(d)

        # (included below for reference) if we want to plot it out against a histogram
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

        return True