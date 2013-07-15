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

from os.path import join
from CharmConfig_Storage import CharmConfig_Storage, MEDIAS_PATH


class PublisherConfig(CharmConfig_Storage):

    def __init__(self, api_nat_socket='', proxy_ips=[], celery_config_file='celeryconfig.py',
                 celery_template_file='templates/celeryconfig.py.template',
                 apache_config_file='/etc/apache2/apache2.conf', publish_uri='',
                 publish_path='/var/www', **kwargs):
        super(PublisherConfig, self).__init__(**kwargs)
        self.api_nat_socket = api_nat_socket
        self.proxy_ips = proxy_ips
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file
        self.apache_config_file = apache_config_file
        self.publish_uri = publish_uri
        self.publish_path = publish_path

    def publish_point(self, media):
        common = join(MEDIAS_PATH, media.user_id, media._id, media.filename)
        return (join(self.publish_path, common), join(self.publish_uri, common))

    def update_publish_uri(self, public_address):
        self.publish_uri = 'http://%s' % public_address

PUBLISHER_CONFIG_TEST = PublisherConfig(api_nat_socket='129.194.185.47:5000',
    storage_address='10.1.1.2', storage_fstype='glusterfs', storage_mountpoint='medias_volume')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test PublisherConfig with doctest')
    import doctest
    doctest.testmod(verbose=False)
    print('OK')
    print('Write default publisher configuration')
    PublisherConfig().write('../oscied-publisher/local_config.pkl')
