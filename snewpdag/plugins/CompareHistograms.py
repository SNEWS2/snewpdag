"""
CompareHistograms - compare count vs a probability map

Arguments:
  in_count_field: name of field containing histogram of event counts
  in_prob_field: name of field containing probability map
  out_field: field to contain diff/err

Input payload (alert):
  in_prob_field: probability map
  Consumes alert.

Input payload (report):
  in_count_field: histogram of event counts
  in_prob_field (optional): probability map

Output payload (report only):
  out_field: diff/err map
"""
import logging
import numpy as np

from snewpdag.dag import Node

class CompareHistograms(Node):
  def __init__(self, in_count_field, in_prob_field, out_field, **kwargs):
    self.in_count_field = in_count_field
    self.in_prob_field = in_prob_field
    self.out_field = out_field
    self.prob = np.array([]) # null array
    super().__init__(**kwargs)

  def alert(self, data):
    logging.debug('{}: alert'.format(self.name))
    # probability map may come in on alert or report
    if self.in_prob_field in data:
      logging.debug('{}: probability map registered'.format(self.name))
      self.prob = np.array(data[self.in_prob_field], copy=True)
    return False # count map will come with report

  def report(self, data):
    logging.debug('{}: report'.format(self.name))
    # probability map may come in on alert or report
    if self.in_prob_field in data:
      self.prob = np.array(data[self.in_prob_field], copy=True)
    if len(self.prob) == 0:
      logging.debug('{}: no probability map'.format(self.name))
      return False
    if self.in_count_field in data:
      logging.debug('{}: histogram map registered'.format(self.name))
      hist = np.array(data[self.in_count_field])
    else:
      logging.debug('{}: no histogram map'.format(self.name))
      return False
    # normalize probability map to agree in overall counts
    factor = hist.sum() / self.prob.sum()
    pred = self.prob * factor
    # errors:  take max of pred or count (may still be 0)
    err = np.sqrt(np.maximum(pred, hist))
    # comparison - nan if 0 in both counts and prediction
    chi = (hist - pred) / err
    data[self.out_field] = chi
    logging.debug('{}: success!'.format(self.name))
    return data

