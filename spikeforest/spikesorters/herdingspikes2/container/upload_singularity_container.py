#!/usr/bin/env python

from mountaintools import client as mt
mt.login()
sha1_path = mt.saveFile('herdingspikes2.simg', upload_to=['spikeforest.kbucket', 'spikeforest.public'])
print(sha1_path)
