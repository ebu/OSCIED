#!/usr/bin/env python2
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

from os.path import expanduser, join
from CharmConfig_Storage import CharmConfig_Storage


class OrchestraConfig(CharmConfig_Storage):

    def __init__(self, api_url=u'', root_secret=u'', nodes_secret=u'', mongo_admin_connection=u'',
                 mongo_nodes_connection=u'', rabbit_connection=u'',
                 celery_config_file=u'celeryconfig.py',
                 celery_template_file=u'templates/celeryconfig.py.template',
                 mongo_config_file=u'/etc/mongodb.conf', ssh_config_path=u'~/.ssh',
                 ssh_template_path=u'ssh', juju_config_file=u'~/.juju/environments.yaml',
                 juju_template_file=u'environments.yaml', charms_config=u'config.yaml',
                 charms_release=u'raring', charms_repository=u'charms', **kwargs):
        super(OrchestraConfig, self).__init__(**kwargs)
        self.api_url = api_url
        self.root_secret = root_secret
        self.nodes_secret = nodes_secret
        self.mongo_admin_connection = mongo_admin_connection
        self.mongo_nodes_connection = mongo_nodes_connection
        self.rabbit_connection = rabbit_connection
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file
        self.mongo_config_file = mongo_config_file
        self.ssh_config_path = expanduser(ssh_config_path)
        self.ssh_template_path = ssh_template_path
        self.juju_config_file = expanduser(juju_config_file)
        self.juju_template_file = juju_template_file
        self.charms_config = charms_config
        self.charms_release = charms_release
        self.charms_repository = charms_repository

    @property
    def transform_queues(self):
        return (u'transform_private', u'transform_amazon',)

    @property
    def publisher_queues(self):
        return (u'publisher_private', u'publisher_amazon',)

    @property
    def orchestra_service(self):
        return u'oscied-orchestra'

    @property
    def storage_service(self):
        return u'oscied-storage'

    @property
    def transform_service(self):
        return u'oscied-transform'

    @property
    def transform_config(self):
        return join(self.charms_repository, self.charms_release, self.transform_service, u'config.yaml')

ORCHESTRA_CONFIG_TEST = OrchestraConfig(
    storage_address=u'127.0.0.1', storage_fstype=u'glusterfs', storage_mountpoint=u'medias_volume_0',
    api_url=u'http://127.0.0.1:5000', root_secret=u'toto', nodes_secret=u'abcd', mongo_admin_connection=u'',
    mongo_nodes_connection=u'...', rabbit_connection=u'...')

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    print(u'Test OrchestraConfig with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print(u'OK')
    print(u'Write default orchestra configuration')
    OrchestraConfig().write(u'../oscied-orchestra/local_config.pkl')
