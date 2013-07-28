#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
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
# Retrieved from https://github.com/ebu/OSCIED

from CharmConfig_Storage import CharmConfig_Storage


class WebuiConfig(CharmConfig_Storage):

    def __init__(self, api_url='', encryption_key='', proxy_ips=[],
                 sites_enabled_path='/etc/apache2/sites-enabled', site_database_file='webui-db.sql',
                 site_template_file='templates/000-default',
                 htaccess_template_file='templates/htaccess.template',
                 general_template_file='templates/config.php.template',
                 database_template_file='templates/database.php.template',
                 htaccess_config_file='/var/www/.htaccess',
                 general_config_file='/var/www/application/config/config.php',
                 database_config_file='/var/www/application/config/database.php',
                 www_root_path='/var/www', www_medias_path='/var/www/medias',
                 www_uploads_path='/var/www/uploads', **kwargs):
        super(WebuiConfig, self).__init__(**kwargs)
        self.api_url = api_url
        self.encryption_key = encryption_key
        self.proxy_ips = proxy_ips
        self.sites_enabled_path = sites_enabled_path
        self.site_database_file = site_database_file
        self.site_template_file = site_template_file
        self.htaccess_template_file = htaccess_template_file
        self.general_template_file = general_template_file
        self.database_template_file = database_template_file
        self.htaccess_config_file = htaccess_config_file
        self.general_config_file = general_config_file
        self.database_config_file = database_config_file
        self.www_root_path = www_root_path
        self.www_medias_path = www_medias_path
        self.www_uploads_path = www_uploads_path

WEBUI_CONFIG_TEST = WebuiConfig(api_url='10.10.4.3:5000', storage_address='10.1.1.2',
    storage_fstype='glusterfs', storage_mountpoint='medias_volume')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test WebuiConfig with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print('OK')
    print('Write default web user interface configuration')
    WebuiConfig().write('../oscied-webui/local_config.pkl')
