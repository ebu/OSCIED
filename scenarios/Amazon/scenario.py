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

from os.path import dirname, join
from library.oscied_lib.juju import OsciedEnvironment
from library.oscied_lib.pytoolbox.console import confirm
from library.oscied_lib.pytoolbox.encoding import configure_unicode
from library.oscied_lib.pytoolbox.juju import DeploymentScenario

description = u'Launch oscied (nano setup) on Amazon'

SCENARIO_PATH = dirname(__file__)
CONFIG = join(SCENARIO_PATH, u'config.yaml')


class Amazon(DeploymentScenario):

    def run(self):
        print(description)
        self.amazon.bootstrap(wait_started=True)
        self.amazon.ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
        self.amazon.ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True)
        self.amazon.ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, to=2)
        self.amazon.ensure_num_units(u'oscied-webui',     u'oscied-webui',     local=True, to=1, expose=True)
        self.amazon.ensure_num_units(u'oscied-publisher', u'oscied-publisher', local=True, to=2, expose=True)
        has_proxy = self.amazon.ensure_num_units(u'haproxy', u'haproxy', expose=True, release=u'precise',
                                                 required=False)[0]

        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.amazon.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.amazon.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.amazon.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
        self.amazon.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')
        if has_proxy:
            if self.amazon.add_relation(u'haproxy', u'oscied-webui'):
                self.amazon.unexpose_service(u'oscied-webui')

        if confirm(u'Initialize orchestra'):
            self.amazon.init_api(SCENARIO_PATH, flush=True)

if __name__ == u'__main__':
    configure_unicode()
    Amazon().main(environments=[OsciedEnvironment(u'amazon', config=CONFIG)])
