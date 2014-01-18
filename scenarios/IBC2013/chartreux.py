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

u"""Generate nice charts to embed into presentations about the OSCIED / the demonstrator shown during IBC 2013."""

# http://docs.mongodb.org/manual/reference/operator/
# http://pygal.org/custom_styles/

from datetime import timedelta
from pytoolbox.datetime import datetime_now
from pytoolbox.encoding import configure_unicode
from library.oscied_lib.juju import ServiceStatistics
from scenario_config import DAEMONS_CHECKS_PER_HOUR, AMAZON, MAAS, EVENTS, SERVICES, STATS, STATISTICS_MAXLEN

HOUR_SHIFT = 1


def main():
    print(__doc__)
    # Initialize statistics of all services of all environments
    for environment, services_statistics in STATS.items():
        for service, statistics in services_statistics.items():
            STATS[environment][service] =  ServiceStatistics(
                environment=environment, service=service, maxlen=STATISTICS_MAXLEN, simulate=True,
                simulated_units_start_latency_range=(10, 13), simulated_units_stop_latency_range=(1, 2),
                simulated_tasks_per_unit_range=(2, 3), simulated_tasks_divider=3)
    # Generate statistics of all services of all environments
    for hour in xrange(STATISTICS_MAXLEN):
        hour = hour + HOUR_SHIFT
        for environment, events in EVENTS.iteritems():
            for service, planned in events.events[hour % 24].iteritems():
                for check in xrange(DAEMONS_CHECKS_PER_HOUR):
                    now_string = datetime_now(offset=timedelta(hours=hour, minutes=(60*check)/DAEMONS_CHECKS_PER_HOUR),
                                              append_utc=False)
                    STATS[environment][service].update(now_string=now_string, planned=planned)
    # Generate charts of all services of all environments
    for services_statistics in STATS.itervalues():
        for statistics in services_statistics.values():
            statistics.generate_units_pie_chart_by_status(u'charts_simulated')
            statistics.generate_units_line_chart(u'charts_simulated')
            statistics.generate_tasks_line_chart(u'charts_simulated')
    # Generate sum charts of all services
    for service in SERVICES:
        statistics_list = [s[service] for s in (STATS[MAAS], STATS[AMAZON])]
        ServiceStatistics.generate_units_stacked_chart(statistics_list, u'charts_simulated', enable_current=False)


if __name__ == u'__main__':
    configure_unicode()
    main()
