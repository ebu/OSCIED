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

from CharmConfig_Storage import CharmConfig_Storage


class TransformConfig(CharmConfig_Storage):

    def __init__(self, api_nat_socket='', celery_config_file='celeryconfig.py',
                 celery_template_file='templates/celeryconfig.py.template', **kwargs):
        super(TransformConfig, self).__init__(**kwargs)
        self.api_nat_socket = api_nat_socket
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file

TRANSFORM_CONFIG_TEST = TransformConfig(api_nat_socket='129.194.185.47:5000',
    storage_address='10.1.1.2', storage_fstype='glusterfs', storage_mountpoint='medias_volume')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test TransformConfig with doctest')
    import doctest
    doctest.testmod(verbose=False)
    print('OK')
    print('Write default transform configuration')
    TransformConfig().write('../oscied-transform/local_config.pkl')
