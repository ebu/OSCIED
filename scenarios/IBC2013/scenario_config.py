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


def get_full_events_table(sparse_events_table):
    u"""Scan (table[i] with i = [0;60[) a spare events table and replace missing entry by previous (non empty) entry."""
    previous_event = {u'oscied-transform': 0, u'oscied-publisher': 0}
    events = {}
    for index in range(60):
        event = sparse_events_table.get(index, previous_event)
        events[index] = event
        previous_event = event
    return events

TIME_SCALE = 70
ENABLE_UNITS_API = True
ENABLE_TESTING = False
SCENARIO_PATH = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))

CONFIG_AMAZ = os.path.join(SCENARIO_PATH, u'config_amazon.yaml')
EVENTS_AMAZ = get_full_events_table({
     0: {u'oscied-transform': 5, u'oscied-publisher': 0},
    17: {u'oscied-transform': 0, u'oscied-publisher': 0},
    43: {u'oscied-transform': 0, u'oscied-publisher': 1},
    45: {u'oscied-transform': 4, u'oscied-publisher': 1},
    50: {u'oscied-transform': 4, u'oscied-publisher': 3},
    55: {u'oscied-transform': 4, u'oscied-publisher': 1}
})

CONFIG_MAAS = os.path.join(SCENARIO_PATH, u'config_maas.yaml')
EVENTS_MAAS = get_full_events_table({
     0: {u'oscied-transform': 4, u'oscied-publisher': 2},
})

LABELS  = {u'oscied-transform': u'encoding',        u'oscied-publisher': u'distribution'}
MAPPERS = {u'oscied-transform': u'transform_units', u'oscied-publisher': u'publisher_units'}
