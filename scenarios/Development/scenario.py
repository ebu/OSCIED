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
from pytoolbox.juju import DeploymentScenario, C1_MEDIUM
from library.oscied_lib.juju import OsciedEnvironment


description = u'Launch oscied (nano setup) on Amazon for developments purposes'

SCENARIO_PATH = dirname(__file__)
CONFIG = join(SCENARIO_PATH, u'config.yaml')


class Dev(DeploymentScenario):

    def run(self):
        print(description)

        self.dev.symlink_local_charms()
        self.dev.generate_config_from_template()

        if confirm(u'Deploy the platform now', default=True):
            do_merge = confirm(u'Merge services (takes more time to setup, cost less if running for hours)', default=False)

            print(u'')
            self.dev.bootstrap(wait_started=True)

            self.dev.auto = True
            ensure_num_units = self.dev.ensure_num_units
            ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, constraints=C1_MEDIUM, expose=True)
            ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, constraints=C1_MEDIUM)
            ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, constraints=C1_MEDIUM)
            ensure_num_units(u'oscied-webui',     u'oscied-webui',     local=True, constraints=C1_MEDIUM, to=1 if do_merge else None, expose=True)
            ensure_num_units(u'oscied-publisher', u'oscied-publisher', local=True, constraints=C1_MEDIUM, to=2 if do_merge else None, expose=True)

            for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
                self.dev.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
            self.dev.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
            self.dev.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
            self.dev.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')
            self.dev.auto = False

        #self.dev.check_status(raise_if_errors=True, wait_all_started=True)

        if confirm(u'Initialize orchestra (will wait until orchestra is ready)', default=True):
            self.dev.init_api(SCENARIO_PATH, flush=True)#, wait_started=True)

if __name__ == u'__main__':
    configure_unicode()
    Dev(environments=[OsciedEnvironment(u'dev', config=CONFIG, release=u'raring')]).run()
