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

import logging
from pyutils.pyutils import PickleableObject


class PublisherConfig(PickleableObject):

    def __init__(self, api_nat_socket='', storage_address='', storage_fstype='',
                 storage_mountpoint='', storage_options='', storage_path='/mnt/storage',
                 storage_mount_max_retry=5, storage_mount_sleep_delay=5,
                 hosts_file='/etc/hosts', celery_config_file='lib/celeryconfig.py',
                 celery_template_file='templates/celeryconfig.py.template',
                 apache_config_file='/etc/apache2/apache2.conf',
                 publish_uri='', publish_path='/var/www'):
        self.api_nat_socket = api_nat_socket
        self.storage_address = storage_address
        self.storage_fstype = storage_fstype
        self.storage_mountpoint = storage_mountpoint
        self.storage_options = storage_options
        self.storage_path = storage_path
        self.storage_mount_max_retry = storage_mount_max_retry
        self.storage_mount_sleep_delay = storage_mount_sleep_delay
        self.hosts_file = hosts_file
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file
        self.apache_config_file = apache_config_file
        self.publish_uri = publish_uri
        self.publish_path = publish_path

    def __repr__(self):
        return str(self.__dict__)

    @property
    def log_level(self):
        return logging.DEBUG if self.verbose else logging.INFO

    @property
    def storage_uri(self):
        u"""
        Returns storage URI.

        **Example usage**:

        >>> from copy import copy
        >>> config = copy(PUBLISHER_CONFIG_TEST)
        >>> print(config.storage_uri)
        glusterfs://10.1.1.2/medias_volume
        >>> config.storage_fstype = ''
        >>> print(config.storage_uri)
        None
        >>> config.storage_fstype = 'nfs'
        >>> config.storage_address = ''
        >>> print(config.storage_uri)
        None
        >>> config.storage_address = '30.0.0.1'
        >>> print(config.storage_uri)
        nfs://30.0.0.1/medias_volume
        """
        if self.storage_fstype and self.storage_address and self.storage_mountpoint:
            return '%s://%s/%s' % (
                self.storage_fstype, self.storage_address, self.storage_mountpoint)
        return None

    def update_publish_uri(self, public_address):
        self.publish_uri = 'http://%s' % public_address

    def reset(self, reset_publish_uri=False):
        self.api_nat_socket = ''
        self.storage_address = ''
        self.storage_fstype = ''
        self.storage_mountpoint = ''
        self.storage_options = ''
        self.storage_path = '/mnt/storage'
        self.hosts_file = '/etc/hosts'
        self.celery_config_file = 'lib/celeryconfig.py'
        self.celery_template_file = 'templates/celeryconfig.py.template'
        self.apache_config_file = '/etc/apache2/apache2.conf'
        if reset_publish_uri:
            self.publish_uri = ''
        self.publish_path = '/var/www'

PUBLISHER_CONFIG_TEST = PublisherConfig('129.194.185.47:5000', '10.1.1.2', 'glusterfs',
                                        'medias_volume', '')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test PublisherConfig with doctest')
    import doctest
    doctest.testmod(verbose=False)
    print('OK')
    print('Write default publisher configuration')
    PublisherConfig().write('../oscied-publisher/local_config.pkl')
