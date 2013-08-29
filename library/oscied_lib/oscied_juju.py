# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

from oscied_api import OrchestraAPIClient, init_api
from pyutils.py_juju import DeploymentScenario


class OsciedDeploymentScenario(DeploymentScenario):

    # FIXME an helper to update config passwords (generate) -> self.config

    def get_client(self, api_unit=u'oscied-orchestra/0', **kwargs):
        service, number = api_unit.split('/')
        settings = self.get_service_config(service)['settings']
        self.root = (u'root', settings['root_secret']['value'])
        hostname = self.get_unit(service, number)['public-address']
        return OrchestraAPIClient(hostname, api_unit=api_unit, auth=self.root, environment=self.environment, **kwargs)

    def init_api(self, client, api_init_csv_directory, flush=False, **kwargs):
        init_api(client, api_init_csv_directory, flush=flush)
