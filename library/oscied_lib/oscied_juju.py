# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

from oscied_api import OrchestraAPIClient, init_api
from pyutils.py_juju import DeploymentScenario


class OsciedDeploymentScenario(DeploymentScenario):

    # FIXME an helper to update config passwords (generate) -> self.config

    def get_client(self, api_unit=u'oscied-orchestra/0', **kwargs):
        service, number = api_unit.split('/')
        settings = self.get_service_config(service)['settings']
        self.root = (u'root', settings['root_secret']['value'])
        hostname = self.get_unit(service, number)['public-address']
        return OrchestraAPIClient(hostname, api_unit=api_unit, auth=self.root, **kwargs)

    def init_api(self, api_init_csv_directory, api_unit=u'oscied-orchestra/0', flush=False, **kwargs):
        client = self.get_client(api_unit, **kwargs)
        init_api(client, api_init_csv_directory, flush=flush)
