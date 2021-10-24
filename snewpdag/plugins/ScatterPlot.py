'''
ScatterPlot: combines 2 inputs into separate arrays unpon alerts; add to payload upon report
    Only notifies downstream plugins on report

Constructor arguments:
    x_in_field: string, name of field with data on the x axis
    y_in_field: string, name of field with data on the y axis
    x_out_field: string, name of field for the combined array on the x axis (optional) (default: x_array)
    y_out_field: string, name of field for the combined array on the y axis (optional) (default: y_array)

'''

import logging
import numpy as np
from snewpdag.dag import Node

class ScatterPlot(Node):
    def __init__(self, x_in_field, y_in_field, **kwargs):
        self.x_in_field = x_in_field
        self.y_in_field = y_in_field
        self.x_out_field = kwargs.pop("x_out_field", "x_array")
        self.y_out_field = kwargs.pop("y_out_field", "y_array")
        super().__init__(**kwargs)
        self.x_array = []
        self.y_array = []

    def alert(self, data):
        x = data[self.x_in_field]
        y = data[self.y_in_field]
        self.x_array.append(x)
        self.y_array.append(y)

        return False

    def report(self, data):
        data[self.x_out_field] = np.asarray(self.x_array)
        data[self.y_out_field] = np.asarray(self.y_array)

        return True