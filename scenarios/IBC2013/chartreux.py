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
from pytoolbox import juju as py_juju
from pytoolbox.datetime import datetime_now
from pytoolbox.encoding import configure_unicode
from library.oscied_lib.juju import ServiceStatistics
from scenario_config import DAEMONS_CHECKS_PER_HOUR, EVENTS_AMAZ, EVENTS_MAAS, STATISTICS_MAXLEN

SERVICES = (PUBLISHER, TRANSFORM) = (u'oscied-publisher', u'oscied-transform')

def main():
    print(__doc__)
    amazon, maas = {}, {}
    for service in SERVICES:
        amazon[service] = ServiceStatistics(environment=u'amazon', service=service, maxlen=STATISTICS_MAXLEN)
        maas[service] = ServiceStatistics(environment=u'maas', service=service, maxlen=STATISTICS_MAXLEN)
    for hour in range(STATISTICS_MAXLEN):
        for service, planned in EVENTS_AMAZ.events[hour % 24].items():
            # FIXME simulate latency of scaling (up & down)
            units = {id: {u'agent-state': py_juju.STARTED} for id in range(planned)}
            for check in range(DAEMONS_CHECKS_PER_HOUR):
                now_string = datetime_now(offset=timedelta(hours=hour, minutes=(60*check)/DAEMONS_CHECKS_PER_HOUR),
                                          append_utc=False)
                amazon[service].update(now_string=now_string, planned=planned, units=units, tasks=None)
    for service in amazon.values():
        service.generate_units_line_chart(u'charts_simulated')

if __name__ == u'__main__':
    configure_unicode()
    main()
