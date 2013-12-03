#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Co-Developer    : Dimitri Racordon (dimitri.racordon@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

import json
import logging
import shutil
import threading
import time

class Source(object):
    u""" Interface for the raw data source of statistics. """

    def read(self):
    u""" Method called by the Statistics object to read the raw data. """
        raise NotImplementedError(u'Source data must be returned here.')

class Statistics(object):
    u"""
    Abstract class for statistics processing.

    The intend of this class is to gather raw data from an arbitrary source and then process
    it using an user-defined implementation. Processed data are written in an internal list,
    each key corresponding to a sample.
    """

    def __init__(self, source, sampling_period=1.0):
        u"""
        Class constructor.
        
        Arguments:
        source          -- the source object
        sampling_period -- period with with which data samples are processed
        """
        self.source          = source
        self.sampling_period = sampling_period
        self._data           = []

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def _process(self, sample):
        u""" Data processing method: should return the processing of a single sample. """
        raise NotImplementedError(u'Data processing not implemented.')

    def get(self):
        return self._data

    def save(self, filename):
        u""" Saves the processed data samples into the filesystem. """
        with open('_' + filename, 'w') as fp:
            json.dump(self._data, fp)
        shutil.move('_' + filename, filename)

class OfflineStatistics(Statistics):

    def __init__(self, source, sampling_period=1.0):
        Statistics.__init__(self, source, sampling_period)
        
        raw_data = self.source.read()
        for s in self._sample(raw_data):
            self._data.append(self._process(s))

    def _sample(self, raw_data):
        raise NotImplementedError(u'Data sampling not implemented.')

class OnlineStatistics(Statistics):

    def __init__(self, source, sampling_period=1.0, backup_file=None, backup_every=0):
        Statistics.__init__(self, source, sampling_period)
        self._backup_every = backup_every
        self._backup_file  = backup_file
        self._update_count = 0
        
        t = threading.Thread(target=self._update)
        t.daemon = True
        t.start()
    
    def _update(self):
        while True:
            self._data.append(self._process(self.source.read()))
            time.sleep(self.sampling_period)

            self._update_count += 1
            if self._backup_every and (self._update_count % self._backup_every == 0):
                self.save(self._backup_file)




# ===== Trash code starts here ===== #

class MySource(Source):
    def read(self):
        return range(60)
class MySource2(Source):
    def read(self):
        import random
        return random.random()

class MyOfflineStats(OfflineStatistics):
    def _process(self, sample):
        return (time.asctime(), sample)

    def _sample(self, raw_data):
        idx = 0
        while idx < len(raw_data):
            yield raw_data[idx]
            idx += int(self.sampling_period)

class MyOnlineStats(OnlineStatistics):
    def _process(self, sample):
        return sample

mos = MyOfflineStats(MySource(), 5)
# print mos.get()

mis = MyOnlineStats(MySource2())
time.sleep(5)
print mis.get()