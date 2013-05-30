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

import logging, os
from pyutils.pyutils import PickleableObject


class WebuiConfig(PickleableObject):

    def __init__(self, api_nat_socket='', storage_address='', storage_fstype='',
                 storage_mountpoint='', storage_options='', storage_path='/mnt/storage',
                 storage_mount_max_retry=5, storage_mount_sleep_delay=5, hosts_file='/etc/hosts',
                 encryption_key='', proxy_ips='',
                 mysql_config_file='/etc/mysql/my.cnf', mysql_temp_path='/var/lib/mysql/tmp',
                 sites_enabled_path='/etc/apache2/sites-enabled', site_database_file='webui-db.sql',
                 site_template_file='templates/000-default',
                 htaccess_template_file='templates/htaccess.template',
                 general_template_file='templates/config.php.template',
                 database_template_file='templates/database.php.template',
                 htaccess_config_file='/var/www/.htaccess',
                 general_config_file='/var/www/application/config/config.php',
                 database_config_file='/var/www/application/config/database.php',
                 www_root_path='/var/www', www_medias_path='/var/www/medias',
                 www_uploads_path='/var/www/uploads',
                 storage_medias_path='/mnt/storage/medias',
                 storage_uploads_path='/mnt/storage/uploads'):
        self.api_nat_socket = api_nat_socket
        self.storage_address = storage_address
        self.storage_fstype = storage_fstype
        self.storage_mountpoint = storage_mountpoint
        self.storage_options = storage_options
        self.storage_path = storage_path
        self.storage_mount_max_retry = storage_mount_max_retry
        self.storage_mount_sleep_delay = storage_mount_sleep_delay
        self.hosts_file = hosts_file
        #self.encryption_key = encryption_key
        #self.proxy_ips = proxy_ips
        #self.mysql_config_file = mysql_config_file
        #self.mysql_temp_path = mysql_temp_path
        #self.sites_enabled_path = sites_enabled_path
        #self.site_database_file = site_database_file
        #self.site_template_file = site_template_file
        #self.htaccess_template_file = htaccess_template_file
        self.general_template_file = general_template_file
        self.database_template_file = database_template_file
        #self.htaccess_config_file = htaccess_config_file
        #self.general_config_file = general_config_file
        #self.database_config_file = database_config_file
        self.www_root_path = www_root_path
        self.www_medias_path = www_medias_path
        self.www_uploads_path = www_uploads_path
        self.storage_medias_path = storage_medias_path
        self.storage_uploads_path = storage_uploads_path

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
        >>> config = copy(WEBUI_CONFIG_TEST)
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

    def reset(self):
        u"""
        Reset attributes to theirs default values.

        **Example usage**:

        >>> from copy import copy
        >>> config = copy(WEBUI_CONFIG_TEST)
        >>> config._pickle_filename = 'my_file.pkl'
        >>> print(config.storage_path)
        /mnt/storage
        >>> config.storage_path = 'salut'
        >>> print(config.storage_path)
        salut
        >>> config.reset()
        >>> print(config.storage_path)
        /mnt/storage
        >>> print(config._pickle_filename)
        my_file.pkl
        """
        self.__init__()

WEBUI_CONFIG_TEST = WebuiConfig('129.194.185.47:5000', '', '10.1.1.2', 'glusterfs',
                                'medias_volume', '')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test WebuiConfig with doctest')
    import doctest
    doctest.testmod(verbose=False)
    print('OK')
    print('Write default web user interface configuration')
    WebuiConfig().write('../oscied-webui/local_config.pkl')
