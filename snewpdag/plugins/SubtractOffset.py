"""
SubtractOffset - subtract an offset from an array

configuration arguments:
  offset: string or number. If string, then it's an input field name.
  in_field: string, name of field to extract from alert data
  out_field: string. Can be the same as in_field (which is the default)

payload input:
  [in_field]: the input data.
  [offset]: number, if configuration 'offset' was a string
"""
import logging
import numpy as np

from snewpdag.dag import Node

class SubtractOffset(Node):
  def __init__(self, offset, in_field, **kwargs):
    self.in_field = in_field
    self.out_field = kwargs.pop('out_field', in_field)
    self.use_offset_field = isinstance(offset, str)
    if self.use_offset_field:
      self.offset_field = offset
    else:
      self.offset = offset
    super().__init__(**kwargs)

  def alert(self, data):
    if self.use_offset_field:
      offset = data[self.offset_field]
    else:
      offset = self.offset
    nfield = np.array(data[self.in_field]) # will make copy
    data[self.out_field] = nfield - offset
    return True

