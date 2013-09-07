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
Events helpers of the demo scenario shown during the International Broadcasting Convention at RAI Amsterdam in 2013.

TODO

"""

from __future__ import division

import math, numbers


def get_full_events_table(sparse_events_table, time_range):
    u"""Scan (table[i] with i = [0;60[) a spare events table and replace missing entry by previous (non empty) entry."""
    previous_event = {u'oscied-transform': 0, u'oscied-publisher': 0}
    events = {}
    for index in range(time_range):
        event = sparse_events_table.get(index, previous_event)
        events[index] = event
        previous_event = event
    return events


def total_seconds(time):
    u"""
    >>> from datetime import datetime
    >>> from nose.tools import assert_equal
    >>> assert_equal(total_seconds(143.2), 143.2)
    >>> assert_equal(total_seconds(datetime(2010, 6, 10, 14, 15, 23)), 51323)
    >>> assert_equal(total_seconds(datetime(2010, 6, 10, 23, 59, 59)), 86399)
    """
    return time if isinstance(time, numbers.Number) else ((time.hour * 60 + time.minute) * 60) + time.second


def get_index(time, time_range, time_speedup):
    u"""
    >>> from nose.tools import assert_equal
    >>> def test_get_index(time_range, time_speedup):
    ...     modulo = previous = 0
    ...     for t in range(24*3600+1):
    ...         index = get_index(t+2*60, time_range, time_speedup)
    ...         if previous > index:
    ...             modulo += 1
    ...         assert(0 <= index < time_range)
    ...         previous = index
    ...     assert_equal(modulo, time_speedup)

    Test get_index with a speedup of 1440 (maps 1 minute to 24 hours):
    >>> test_get_index(24, 24 * 60)

    Test get_index with a speedup of 12 (maps 2 hours to 24 hours):
    >>> test_get_index(24, 12)
    """
    return int((total_seconds(time) * (time_speedup / 3600) % time_range))


def get_sleep_time(time, time_range, time_speedup):
    u"""
    >>> from nose.tools import assert_equal
    >>> assert_equal(get_sleep_time( 3590, 24,  1),   10)
    >>> assert_equal(get_sleep_time(    1, 24, 60),   59)
    >>> assert_equal(get_sleep_time(   58, 24, 60),    2)
    >>> assert_equal(get_sleep_time(   60, 24, 60),   60)
    >>> assert_equal(get_sleep_time(   62, 24, 60),   58)
    >>> assert_equal(get_sleep_time(12543, 24,  1), 1857)
    >>> assert_equal(get_sleep_time(    1,  1,  1),  149)
    """
    d = (time_range / 24) * 3600 / time_speedup
    return math.ceil(d - (total_seconds(time) % d))

if __name__ == u'__main__':
    import doctest
    print(u'Test scenario_config with doctest')
    doctest.testmod()
    print(u'OK')
