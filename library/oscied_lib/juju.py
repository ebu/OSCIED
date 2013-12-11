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

from __future__ import absolute_import, division, print_function, unicode_literals

import os, random, string
from pytoolbox.filesystem import from_template
from pytoolbox.juju import Environment

from .api import OrchestraAPIClient, init_api


class OsciedEnvironment(Environment):

    def __init__(self, name, api_unit=u'oscied-orchestra/0', **kwargs):
        super(OsciedEnvironment, self).__init__(name, **kwargs)
        self.api_unit = api_unit
        self._api_client = None

    @property
    def api_client(self):
        if not self._api_client:
            service, number = self.api_unit.split(u'/')
            settings = self.get_service_config(service)[u'settings']
            root_auth = (u'root', settings[u'root_secret'][u'value'])
            host = self.get_unit(service, number)[u'public-address']
            self._api_client = OrchestraAPIClient(host, api_unit=self.api_unit, auth=root_auth, environment=self.name)
        return self._api_client

    @property
    def config_passwords(self):
        return (
            u'root_secret', u'node_secret', u'mongo_admin_password', u'mongo_node_password', u'rabbit_password',
            u'mysql_root_password', u'mysql_user_password'
        )

    @property
    def config_template(self):
        return u'{0}.template'.format(self.config)

    def generate_config_from_template(self, overwrite=False, **kwargs):
        if not os.path.exists(self.config) or overwrite:
            chars, size = string.ascii_letters + string.digits, 16
            params = {p: u''.join(random.choice(chars) for i in xrange(size)) for p in self.config_passwords}
            params.update({u'charms_release': self.release})
            params.update(kwargs)
            from_template(self.config_template, self.config, params)

    def init_api(self, api_init_csv_directory, **kwargs):
        init_api(self.api_client, api_init_csv_directory, **kwargs)
