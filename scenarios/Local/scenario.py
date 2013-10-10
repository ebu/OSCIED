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
from pytoolbox.console import confirm
from pytoolbox.encoding import configure_unicode
from pytoolbox.juju import DeploymentScenario
from library.oscied_lib.juju import OsciedEnvironment


description = u'Launch oscied (minimal setup) locally (LXC provider)'

SCENARIO_PATH = dirname(__file__)
CONFIG = join(SCENARIO_PATH, u'config.yaml')


class Local(DeploymentScenario):

    def run(self):
        print(description)
        self.local.bootstrap(wait_started=True)
        self.local.generate_config_from_template()
        ensure_num_units = self.local.ensure_num_units
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True)
        ensure_num_units(u'oscied-publisher', u'oscied-publisher', local=True, expose=True)
        ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
        ensure_num_units(u'oscied-webui',     u'oscied-webui',     local=True, expose=True)
        ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True)
        has_proxy = ensure_num_units(u'haproxy', u'haproxy', expose=True, release=u'precise', required=False)[0]

        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.local.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.local.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.local.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
        self.local.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')
        if has_proxy:
            if self.local.add_relation(u'haproxy', u'oscied-webui'):
                self.local.unexpose_service(u'oscied-webui')

        if confirm(u'Initialize orchestra'):
            self.local.init_api(SCENARIO_PATH, flush=True)

if __name__ == u'__main__':
    configure_unicode()
    Local().main(environments=[OsciedEnvironment(u'local', config=CONFIG)])
