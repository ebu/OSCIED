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
from pyutils.py_juju import Environment


class OsciedEnvironment(Environment):

    # FIXME an helper to update config passwords (generate) -> self.config
    def __init__(self, name, api_unit=u'oscied-orchestra/0', **kwargs):
        super(OsciedEnvironment, self).__init__(name, **kwargs)
        self.api_unit = api_unit
        self._api_client = None

    @property
    def api_client(self):
        if not self._api_client:
            service, number = self.api_unit.split('/')
            settings = self.get_service_config(service)['settings']
            root_auth = (u'root', settings['root_secret']['value'])
            host = self.get_unit(service, number)['public-address']
            self._api_client = OrchestraAPIClient(host, api_unit=self.api_unit, auth=root_auth, environment=self.name)
        return self._api_client

    def init_api(self, api_init_csv_directory, flush=False, **kwargs):
        init_api(self.api_client, api_init_csv_directory, flush=flush)
