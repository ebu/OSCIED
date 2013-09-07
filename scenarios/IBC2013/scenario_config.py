#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
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

u"""
Configuration of the demo scenario shown during the International Broadcasting Convention at RAI Amsterdam in 2013.

TODO

"""

import os
from scenario_events import get_full_events_table

SCENARIO_PATH = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))

ENABLE_UNITS_API = True
ENABLE_TESTING = True
TIME_RANGE = 24  # in hours
TIME_SCALE = 30  # in hours
TIME_SPEEDUP = TIME_RANGE * 60 if ENABLE_TESTING else 12  # how many times per 24H range the scenario will 'loop'

CONFIG_AMAZ = os.path.join(SCENARIO_PATH, u'config_amazon.yaml')
EVENTS_AMAZ = get_full_events_table({
     7: {u'oscied-transform': 5, u'oscied-publisher': 0},
    17: {u'oscied-transform': 0, u'oscied-publisher': 0},
    17: {u'oscied-transform': 0, u'oscied-publisher': 1},
    18: {u'oscied-transform': 4, u'oscied-publisher': 1},
    20: {u'oscied-transform': 4, u'oscied-publisher': 3},
    22: {u'oscied-transform': 4, u'oscied-publisher': 1}
}, TIME_RANGE)

CONFIG_MAAS = os.path.join(SCENARIO_PATH, u'config_maas.yaml')
EVENTS_MAAS = get_full_events_table({
     0: {u'oscied-transform': 4, u'oscied-publisher': 2},
}, TIME_RANGE)

LABELS  = {u'oscied-transform': u'encoding',        u'oscied-publisher': u'distribution'}
MAPPERS = {u'oscied-transform': u'transform_units', u'oscied-publisher': u'publisher_units'}

if __name__ == u'__main__':
    import doctest
    print(u'Test scenario_config with doctest')
    doctest.testmod()
    print(u'OK')
