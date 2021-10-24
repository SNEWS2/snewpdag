'''
Residual: calculates residuals, accumulates into arrays on alerts, add to payload on report
    Only notify downstream plugins on report

Constructor arguments:
    true_in_field: string, name of field with true value
    calc_in_field: string, name of field with calculated value
    x_out_field: string, name of field for the combined array on the x axis (default: x_array)
    y_out_field: string, name of field for the combined array on the y axis (default: y_array)

'''

import logging
import matplotlib.pyplot as plt
import numpy as np
from snewpdag.dag import Node

class Residual(Node):
    def __init__(self, true_in_field, calc_in_field, **kwargs):
        self.true_in_field = true_in_field
        self.calc_in_field = calc_in_field
        self.x_out_field = kwargs.pop("x_out_field", "x_array")
        self.y_out_field = kwargs.pop("y_out_field", "y_array")
        super().__init__(**kwargs)
        self.true_array = []
        self.res_array =[]

    def alert(self, data):
        true = data[self.true_in_field]
        calc = data[self.calc_in_field]
        res = calc - true
        self.true_array.append(true)
        self.res_array.append(res)

        return False

    def report(self, data):
        data[self.x_out_field] = np.asarray(self.true_array)
        data[self.y_out_field] = np.asarray(self.res_array)

        return True