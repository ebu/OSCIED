#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/EBU-TI/OSCIED

import os
from CharmConfig_Storage import CharmConfig_Storage


class OrchestraConfig(CharmConfig_Storage):

    def __init__(self, api_url='', root_secret='', nodes_secret='', mongo_connection='',
                 rabbit_connection='', ssh_config_file='~/.ssh/config',
                 ssh_template_file='templates/config.template',
                 celery_config_file='celeryconfig.py',
                 celery_template_file='templates/celeryconfig.py.template',
                 mongo_config_file='/etc/mongodb.conf', **kwargs):
        super(OrchestraConfig, self).__init__(**kwargs)
        self.api_url = api_url
        self.root_secret = root_secret
        self.nodes_secret = nodes_secret
        self.mongo_connection = mongo_connection
        self.rabbit_connection = rabbit_connection
        self.ssh_config_file = os.path.expanduser(ssh_config_file)
        self.ssh_template_file = ssh_template_file
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file
        self.mongo_config_file = mongo_config_file

    @property
    def transform_queues(self):
        return ('transform_private', 'transform_amazon',)

    @property
    def publisher_queues(self):
        return ('publisher_private', 'publisher_amazon',)

ORCHESTRA_CONFIG_TEST = OrchestraConfig(storage_address='127.0.0.1', storage_fstype='glusterfs',
    storage_mountpoint='medias_volume_0', api_url='http://127.0.0.1:5000', root_secret='toto',
    nodes_secret='abcd', mongo_connection='...', rabbit_connection='...')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test OrchestraConfig with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print('OK')
    print('Write default orchestra configuration')
    OrchestraConfig().write('../oscied-orchestra/local_config.pkl')
