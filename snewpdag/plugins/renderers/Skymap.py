"""
Skymap - render an LMap

Note that an LMap is stored in nested order.
"""
import matplotlib.pyplot as plt
import numpy as np
import healpy as hp
import json
import requests
import os


from snewpdag.dag import Node
from snewpdag.values import LMap

class Skymap(Node):
  def __init__(self, in_field, title, filename, **kwargs):
    self.in_field = in_field
    self.title = title
    self.filename = filename
    self.count = 0
    super().__init__(**kwargs)

  def alert(self, data):
    print(data)
    self.filename = data['coinc_id']
    self.title = data['coinc_id']
    burst_id = data.get('burst_id', 0) # TODO: decide if burstid = coincid
    m = data.get(self.in_field, None)
    if np.any(m):
      # replace a lot of these options later
      hp.mollview(m,
                  coord=["G", "E"],
                  title=self.title,
                  unit="mK",
                  norm="hist",
                  min=-1,
                  max=1,
                  nest=True,
                 )
      hp.graticule()
      fname = self.filename.format(self.name, self.count, burst_id)
      plt.savefig(fname)
      plt.show()


      ##################testing uploading on google drive
      #headers = {
      #    "Authorization": "ya29.A0ARrdaM949LsML0sxxLn7UaWUQcDrpO9hwW9yxK-bVeXfhNVLaR-1egT4MewfAAkBB3uUMuEcoqSEYrizmXTNo0qeNTnIxNoxm-NACw2RKaPr3ppiLNyLgGsV_Ue5VY4BdhRZyc3W3EAqkdYxWwfGl9mMMMA3"}
      #para = {
      #    "name": self.title,
#
      #}
#
      #files = {
      #    'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
#
      #    'file': open("./" + self.filename + '.png', "rb")
      #}
      #r = requests.post(
      #    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
      #    headers=headers,
      #    files=files
      #)
      #print(r.text)

      self.count += 1

    return True

